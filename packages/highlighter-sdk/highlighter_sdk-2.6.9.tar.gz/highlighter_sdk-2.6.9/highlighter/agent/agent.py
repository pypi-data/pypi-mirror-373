import json
import logging
import os
import time
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from queue import Empty, Queue
from tempfile import mkdtemp
from threading import Thread
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

import aiko_services as aiko
import yaml
from aiko_services import process as aiko_process
from aiko_services.main import aiko as aiko_main
from aiko_services.main import generate, parse

from highlighter import MachineAgentVersion
from highlighter.client.agents import create_pipeline_instance, update_pipeline_instance
from highlighter.client.base_models.base_models import UserType
from highlighter.client.gql_client import HLClient
from highlighter.client.json_tools import HLJSONEncoder
from highlighter.client.tasks import (
    Task,
    TaskStatus,
    lease_task,
    lease_tasks_from_steps,
    update_task,
)
from highlighter.core.database.database import Database
from highlighter.core.hl_base_model import GQLBaseModel
from highlighter.core.shutdown import runtime_stop_event

__all__ = [
    "HLAgent",
    "set_mock_aiko_messager",
    "SExpression",
]


# The stream timeout counts from the most recent process_frame call in a pipeline
STREAM_TIMEOUT_GRACE_TIME_SECONDS = 20
# The pipeline timeout counts from the most recent frame returned on queue_response
TASK_RE_LEASE_EXPIRY_BUFFER_SECONDS = 20


class SExpression:

    @staticmethod
    def encode(cmd: Optional[str], parameters: Union[Dict, List, Tuple]) -> str:
        if cmd:
            return generate(cmd, parameters)
        else:
            return generate(parameters[0], parameters[1:])

    @staticmethod
    def decode(s: str) -> Any:
        return parse(s)


def load_pipeline_definition(path) -> Dict:
    path = Path(path)
    suffix = path.suffix

    if suffix in (".json",):
        with path.open("r") as f:
            pipeline_def = json.load(f)
    elif suffix in (".yml", ".yaml"):
        with path.open("r") as f:
            pipeline_def = yaml.safe_load(f)
    else:
        raise NotImplementedError(
            f"Unsupported pipeline_definition file, '{path}'." " Expected .json|.yml|.yaml"
        )

    def remove_dict_keys_starting_with_a_hash(data):
        if isinstance(data, dict):
            # Create a new dictionary excluding keys starting with "#"
            return {
                key: remove_dict_keys_starting_with_a_hash(value)
                for key, value in data.items()
                if not key.startswith("#")
            }
        elif isinstance(data, list):
            # If the item is a list, recursively apply the function to each element
            return [remove_dict_keys_starting_with_a_hash(item) for item in data]
        else:
            # If the item is neither a dict nor a list, return it as-is
            return data

    pipeline_def = remove_dict_keys_starting_with_a_hash(pipeline_def)
    return pipeline_def


def _validate_uuid(s):
    try:
        u = UUID(s)
        return u
    except Exception as e:
        return None


def _validate_path(s) -> Optional[Path]:
    try:
        p = Path(s)
        if p.exists():
            return p
    except Exception as e:
        return None


class AgentError(Exception):
    """Exception raised for fatal errors in the Highlighter agent.

    This exception indicates a serious problem within the agent
    that prevents normal operation
    """


class HLAgent:

    def __init__(
        self,
        pipeline_definition: Union[str, dict, os.PathLike],
        name: str = "agent",
        dump_definition: Optional[os.PathLike] = None,
        timeout_secs: float = 60.0,
        task_lease_duration_secs: float = 60.0,
        task_polling_period_secs: float = 5.0,
    ):
        self.logger = logging.getLogger(__name__)

        if dump_definition is not None:
            pipeline_path = Path(dump_definition)
        else:
            pipeline_path = Path(mkdtemp()) / "pipeline_def.json"

        self.machine_agent_version_id = None

        if pipeline_definition_path := _validate_path(pipeline_definition):
            definition_dict = load_pipeline_definition(pipeline_definition_path)
            if name is None:
                name = pipeline_definition_path.name

        elif def_uuid := _validate_uuid(pipeline_definition):
            result = HLClient.get_client().machine_agent_version(
                return_type=MachineAgentVersion,
                id=str(def_uuid),
            )
            definition_dict = result.agent_definition
            name = result.title
            self.machine_agent_version_id = def_uuid
        elif isinstance(pipeline_definition, dict):
            if name is None:
                raise ValueError(
                    "If pipeline_definition is a dict you must provide the 'name' arg to HLAgent.__init__"
                )
            definition_dict = pipeline_definition

        else:
            if Path(pipeline_definition).suffix not in (".json", ".yml", ".yaml"):
                raise SystemExit(f"pipeline_definition '{pipeline_definition}' path does not exist")
            else:
                raise SystemExit(f"pipeline_definition '{pipeline_definition}' id does not exist")

        self._dump_definition(definition_dict, pipeline_path)

        parsed_definition = aiko.PipelineImpl.parse_pipeline_definition(pipeline_path)

        init_args = aiko.pipeline_args(
            name,
            protocol=aiko.PROTOCOL_PIPELINE,
            definition=parsed_definition,
            definition_pathname=pipeline_path,
        )
        pipeline = aiko.compose_instance(aiko.PipelineImpl, init_args)

        self.pipeline = pipeline
        self.pipeline_definition = parsed_definition
        self.timeout_secs = timeout_secs
        self.task_lease_duration_secs = task_lease_duration_secs
        self.task_polling_period_secs = task_polling_period_secs

        self.db = Database()

        self.enable_create_stream = True
        self.aiko_event_loop_thread = None

    def get_data_source_capabilities(self) -> List[aiko.source_target.DataSource]:
        data_source_elements = [
            node
            for node in self.pipeline.pipeline_graph.nodes()
            if isinstance(node.element, aiko.source_target.DataSource)
        ]
        return data_source_elements

    def _dump_definition(self, pipeline_def: Dict, path: Path):
        with path.open("w") as f:
            json.dump(pipeline_def, f, sort_keys=True, indent=2, cls=HLJSONEncoder)

    def run_in_new_thread(self, mqtt_connection_required=False):
        if aiko_process.running:
            raise AgentError("Aiko event-loop thread is already running")
        self.aiko_event_loop_thread = Thread(
            target=self.pipeline.run,
            daemon=True,
            kwargs={"mqtt_connection_required": mqtt_connection_required},
        )
        self.aiko_event_loop_thread.start()
        start_time = time.time()
        timeout_seconds = 3
        while not aiko.process.running:
            if time.time() - start_time > timeout_seconds:
                self.logger.warning("Aiko event-loop thread not started")
                break
            time.sleep(0.1)

    def stop_all_streams(self, graceful=False):
        """Stop all streams"""
        try:
            stream_ids = list(self.pipeline.stream_leases.keys())
            for stream_id in stream_ids:
                self.logger.info(f"Agent stopping {stream_id} stream, graceful={graceful}")
                try:
                    # TODO: Remove thread_local/lock shenanigans once we've moved
                    # the process_frame calls in loop_over_proces_frame to the
                    # Aiko event-loop thread
                    reset_thread_local = False
                    if getattr(self.pipeline.thread_local, "stream", None):
                        stream, _ = self.pipeline.get_stream()
                        self.logger.debug(f"Disabling thread_local for stream {stream_id}")
                        self.pipeline._disable_thread_local("HLAgent.stop_all_streams()")
                        self.logger.debug(f"Releasing lock for stream {stream_id}")
                        stream.lock.release()
                        reset_thread_local = True

                    self.pipeline.destroy_stream(stream_id, graceful=graceful)

                    if reset_thread_local:
                        self.logger.debug(f"Acquiring lock for stream {stream_id}")
                        stream.lock.acquire("HLAgent.stop_all_streams()")
                        # HACK: Workaround for process_frame not liking
                        # destroy_stream to be called mid-way through via signal interrupt
                        if not graceful:
                            lease = aiko.Lease(lease_time=0, lease_uuid=uuid4())
                            lease.stream = stream
                            self.pipeline.stream_leases[stream_id] = lease
                        self.logger.debug(f"Enabling thread_local for stream {stream_id}")
                        self.pipeline._enable_thread_local("HLAgent.stop_all_streams()", stream_id)
                        if not graceful:
                            del self.pipeline.stream_leases[stream_id]
                except Exception as e:
                    self.logger.warn(
                        f"Warning: Agent could not destroy stream {stream_id}: {type(e).__qualname__}: {e}"
                    )
            self.logger.info(f"Agent stopped {len(stream_ids)} streams")
        except Exception as e:
            self.logger.error(f"Error when agent accessing stream leases: {type(e).__qualname__}: {e}")

    def disable_create_stream(self):
        self.enable_create_stream = False

    def stop(self):
        self.enable_create_stream = False
        self.pipeline.stop()
        if self.aiko_event_loop_thread is not None:
            self.aiko_event_loop_thread.join(timeout=5)  # Wait for current frame to be processed
            if self.aiko_event_loop_thread.is_alive():
                self.logger.warning("Aiko event-loop thread not stopped")

    def get_head_data_source_capability(self):
        head_capability = [x for x in self.pipeline.pipeline_graph][0]
        if hasattr(head_capability.element, "_is_data_source"):
            return head_capability
        return None

    def set_callback(self, callback_name: str, callback: Callable):
        setattr(self.pipeline, callback_name, callback)

    def process_frame(self, frame_data, stream_id=0, frame_id=0) -> bool:
        stream = {
            "stream_id": stream_id,
            "frame_id": frame_id,
        }
        return self.pipeline.process_frame(stream, frame_data)

    def _set_agent_data_source_stream_parameters(self, data_sources, stream_parameters):

        data_source_capabilities = self.get_data_source_capabilities()
        if len(data_source_capabilities) == 1:
            data_source_capability_name = data_source_capabilities[0].name
        elif len(data_source_capabilities) > 1:
            raise NotImplementedError(
                f"hl agent start cannot yet support Agents with multiple DataSource Capabilities, got: {data_source_capabilities}"
            )
        else:
            raise NotImplementedError(
                "hl agent start cannot yet support Agents with no DataSource Capabilities"
            )

        input_name = f"{data_source_capability_name}.data_sources"
        stream_parameters[input_name] = data_sources
        return stream_parameters

    # ToDo: Now that I am not accepting cli passed stream params. Is this needed,
    # or is it just handled by the aiko pipeline
    def parse_stream_parameters(self, agent_definition) -> dict:

        stream_parameters = {}
        for node in self.pipeline.pipeline_graph.nodes():
            node_name = node.name

            # If default_stream_parameters is not present, we are likely
            # working with an aiko.PipelineElement. In this case, we can assume
            # that parameter validation is handled manually.
            if not hasattr(node.element, "default_stream_parameters"):
                continue

            # Start with in code params
            default_stream_parameters = node.element.default_stream_parameters()

            # Overwite with global pipeline definition params
            global_pipeline_definition_params = {
                k: v
                for k, v in agent_definition.parameters.items()
                if k in node.element.DefaultStreamParameters.model_fields
            }
            default_stream_parameters.update(global_pipeline_definition_params)

            # Overwite with per element pipeline definition paras
            element_definition = [e for e in agent_definition.elements if e.name == node_name][0]
            pipeline_element_definition_params = {
                k.replace(f"{node_name}.", ""): v
                for k, v in element_definition.parameters.items()
                if k.replace(f"{node_name}.", "") in node.element.DefaultStreamParameters.model_fields
            }
            node.element.parameters = pipeline_element_definition_params
            default_stream_parameters.update(pipeline_element_definition_params)

            ele_stream_parameters = node.element.DefaultStreamParameters(
                **default_stream_parameters
            ).model_dump()

            stream_parameters.update(
                {f"{element_definition.name}.{k}": v for k, v in ele_stream_parameters.items()}
            )

        return stream_parameters

    def process_data_sources(
        self,
        stream_id,
        data_sources,
        _hlagent_cli_runner_queue_response,
        queue_response_max_size=100,
        timeout_secs=120,
    ):
        stream_parameters: dict = self.parse_stream_parameters(
            self.pipeline_definition,
        )

        stream_parameters["database"] = self.db

        if data_sources:
            data_source_sexp = SExpression.encode(None, data_sources)
            stream_parameters = self._set_agent_data_source_stream_parameters(
                data_source_sexp, stream_parameters
            )

        queue_response = Queue(maxsize=queue_response_max_size)
        self.pipeline.create_stream(stream_id, parameters=stream_parameters, queue_response=queue_response)

        self.logger.info(f"Created stream {stream_id}")

        last_item_ts = time.monotonic()
        while not runtime_stop_event.is_set():
            try:
                stream_event, result = queue_response.get(
                    timeout=0.5
                )  # TODO: what is the best timeout? use global?
                last_item_ts = time.monotonic()  # <-- reset the timer
            except Empty:
                if (time.monotonic() - last_item_ts) < timeout_secs:
                    continue  # next frame
                else:
                    raise TimeoutError(f"No items received for {timeout_secs}s; aborting processing.")

            self.logger.debug(f"stream_event: {stream_event}, queue_response size: {queue_response.qsize()}")

            # This should only run if running via the HLAgentCliRunner
            if _hlagent_cli_runner_queue_response is not None:
                _hlagent_cli_runner_queue_response.put((stream_event, result))
                if _hlagent_cli_runner_queue_response.qsize() > queue_response_max_size:
                    raise ValueError(
                        f"_hlagent_cli_runner_queue_response size is > {queue_response_max_size}"
                    )

            if stream_event["state"] in [aiko.StreamEvent.STOP, aiko.StreamEvent.ERROR]:
                break

    def loop_over_process_frame(self, stream_id, frame_datas, queue_response):
        from highlighter.core.data_models import DataSample

        # This function can be removed once
        # the issue it's solving is resolved.
        # See to function's doc string for more info
        set_mock_aiko_messager()

        if isinstance(frame_datas, dict):
            frame_datas = [frame_datas]

        stream_parameters: dict = self.parse_stream_parameters(
            self.pipeline_definition,
        )

        self.pipeline.create_stream(stream_id, parameters=stream_parameters, queue_response=queue_response)
        for frame_id, frame in enumerate(frame_datas):
            if runtime_stop_event.is_set() or not self.enable_create_stream:
                break
            stream = {
                "stream_id": stream_id,
                "frame_id": frame_id,
            }

            data_samples = [
                DataSample(
                    data_file_id=uuid4(),
                    content=frame["content"],
                    media_frame_index=0,
                    content_type="text",
                )
            ]
            self.pipeline.process_frame(stream, {"data_samples": data_samples})
        self.pipeline.destroy_stream(stream_id)

    def check_user_is_machine(self):
        current_user = HLClient.get_client().current_user(return_type=UserType)
        if current_user.machine_agent_version_id is None:
            raise AgentError(
                "Running agent as non-machine user. To run the agent as a machine user, use "
                "`hl agent create-token` and set HL_WEB_GRAPHQL_API_TOKEN with the returned value before running `hl agent start. "
                "To run the agent as the current user, pass `allow_non_machine_user=True`."
            )

    def poll_for_tasks_loop(self, step_id: Union[str, UUID], allow_non_machine_user: bool = False):
        if not self.enable_create_stream:
            raise AgentError("Cannot process tasks when creating streams is disabled")

        if not allow_non_machine_user:
            self.check_user_is_machine()

        step_id = UUID(step_id)

        # Report running agent to hl web
        self.pipeline_instance_id = create_pipeline_instance(
            str(self.machine_agent_version_id),
            str(step_id),
        )
        try:
            while not runtime_stop_event.is_set():
                if not self.enable_create_stream:
                    update_pipeline_instance(self.pipeline_instance_id, status="STOPPED")
                    break

                update_pipeline_instance(self.pipeline_instance_id, status="RUNNING")

                if self.machine_agent_version_id is not None:

                    class TaskResponse(GQLBaseModel):
                        errors: List[Any]
                        tasks: List[Task]

                    leased_until = (
                        datetime.now(UTC) + timedelta(seconds=self.task_lease_duration_secs)
                    ).isoformat()
                    response = HLClient.get_client().lease_tasks_for_agent(
                        return_type=TaskResponse,
                        agentId=str(self.machine_agent_version_id),
                        leasedUntil=leased_until,
                        count=1,
                    )
                    if len(response.errors) > 0:
                        raise ValueError(response.errors)
                    else:
                        tasks = response.tasks
                else:
                    tasks = lease_tasks_from_steps(
                        HLClient.get_client(),
                        [step_id],
                        lease_sec=self.task_lease_duration_secs,
                    )
                for task in tasks:
                    self._process_task(task)
                if len(tasks) == 0:
                    time.sleep(self.task_polling_period_secs)
        except Exception as e:
            update_pipeline_instance(self.pipeline_instance_id, status="FAILED", message=str(e))
            raise e

    def _process_task(self, task: Task):
        self.logger.info(f"Processing task {task.id}")
        stream_id = task.id
        stream_result_queue = Queue()
        update_task(
            client=HLClient.get_client(),
            task_id=task.id,
            status=TaskStatus.RUNNING,
        )
        self.pipeline.create_stream(
            stream_id,
            parameters=task.parameters,
            queue_response=stream_result_queue,
            grace_time=STREAM_TIMEOUT_GRACE_TIME_SECONDS,
        )
        while not runtime_stop_event.is_set():
            try:
                stream_info, frame_data = stream_result_queue.get(timeout=self.timeout_secs)
            except Empty:
                diagnostic = (
                    f"Timeout: Agent has not produced a value for more than {self.timeout_secs} seconds"
                )
                update_task(
                    client=HLClient.get_client(),
                    task_id=task.id,
                    status=TaskStatus.FAILED,
                    message=diagnostic,
                )
                raise ValueError(diagnostic)
            if stream_info["state"] == aiko.StreamEvent.STOP:
                self.logger.info(f"Completed task {task.id}")
                update_task(
                    client=HLClient.get_client(),
                    task_id=task.id,
                    status=TaskStatus.SUCCESS,
                )
                break
            if stream_info["state"] == aiko.StreamEvent.ERROR:
                self.logger.error(f"Error in task {task.id}: {frame_data.get('diagnostic')}")
                update_task(
                    client=HLClient.get_client(),
                    task_id=task.id,
                    status=TaskStatus.FAILED,
                    message=frame_data.get("diagnostic"),
                )
                break
            if (
                task.leased_until.timestamp()
                < datetime.now(timezone.utc).timestamp() + TASK_RE_LEASE_EXPIRY_BUFFER_SECONDS
            ):
                # Re-lease task
                self.logger.info(f"Extending lease for task {task.id}")
                task = lease_task(
                    client=HLClient.get_client(),
                    task_id=task.id,
                    lease_sec=self.task_lease_duration_secs,
                )


def set_mock_aiko_messager():
    # ToDo: Chat with Andy about if this is a requirement. The issue is
    # in pipeline.py +999 causes an error because if I use `process_frame`
    # directly, without setting the aiko.message object to something I
    # get an attribute error when .publish is called
    class MockMessage:
        def publish(self, *args, **kwargs):
            pass

        def subscribe(self, *args, **kwargs):
            pass

        def unsubscribe(self, *args, **kwargs):
            pass

    aiko_main.message = MockMessage()
