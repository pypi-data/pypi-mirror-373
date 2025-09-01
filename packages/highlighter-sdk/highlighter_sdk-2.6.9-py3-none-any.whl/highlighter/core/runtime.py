"""Highlighter Runtime
===========================

This module provides the core runtime infrastructure for the Highlighter SDK, including
the main Runtime class that orchestrates agent execution, signal handling, configuration
management, and data processing workflows.

The Runtime class serves as the primary entry point for executing Highlighter agents,
handling various input sources (files, URLs, raw data), and managing the lifecycle
of processing tasks.

Key Components:
    - Runtime: Main class for orchestrating agent execution
    - Signal handling for graceful shutdown and configuration reloading
    - Network retry logic with circuit breaker patterns
    - Data source parsing and validation
    - Integration with Aiko Services framework

Example:
    Basic usage of the Runtime class:

    >>> from highlighter.core.runtime import Runtime
    >>> runtime = Runtime(
    ...     agent_definition="path/to/agent.json",
    ...     input_data=["path/to/image.jpg"],
    ...     expect_filepaths=True
    ... )
    >>> runtime.run()
"""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urlparse

import aiohttp
import requests
from aiko_services.main import DEFAULT_STREAM_ID
from gql.transport.exceptions import TransportError
from pybreaker import CircuitBreaker, CircuitBreakerError
from tenacity import (
    after_log,
    before_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

import highlighter.core.decorators as decorators
from highlighter.agent.agent import HLAgent
from highlighter.cli.logging import configure_root_logger
from highlighter.client.tasks import lease_task
from highlighter.core.config import (
    HighlighterRuntimeConfig,
)
from highlighter.core.shutdown import runtime_stop_event
from highlighter.core.thread_watch import dump_stacks, join_all, patch_threading
from highlighter.io.url import is_url_scheme

# ────────────────────────────────────────────
# Section 1: helpers originally inside _start
# ────────────────────────────────────────────

# Runtime configuration constants
DEFAULT_FILEPATH_SEPARATOR = "\n"  # Default separator for parsing file paths from input
DEFAULT_CONTENT_SEPARATOR = b"===END=="  # Default separator for raw content data
THREAD_GRACEFUL_TIMEOUT = 5  # seconds per thread on shutdown


def _is_url(p: str) -> bool:
    """Check if a string is a valid URL with scheme and netloc.

    Args:
        p: String to check for URL format

    Returns:
        True if the string is a valid URL, False otherwise
    """
    u = urlparse(p)
    return bool(u.scheme and u.netloc)


def _reading_raw_data_from_stdin_buffer(input_data, expect_filepaths, seperator):
    """Determine if we should read raw data from stdin buffer.

    Args:
        input_data: Input data specification
        expect_filepaths: Whether input should be treated as file paths
        seperator: Data separator (unused in this function)

    Returns:
        True if conditions indicate raw data should be read from stdin
    """
    return (input_data == "--") and (not sys.stdin.isatty() and (not expect_filepaths))


def _read_filepaths(input_data, seperator, encoding):
    """Parse and validate file paths or URLs from input data.

    This function processes input data to extract file paths or URLs, validates them,
    and converts them to appropriate URI schemes. It supports both local file paths
    and HTTP/RTSP URLs, ensuring all inputs use the same scheme type.

    Args:
        input_data: Either "--" to read from stdin, or iterable of paths/URLs
        seperator: String separator for splitting stdin input
        encoding: Text encoding for decoding stdin bytes

    Returns:
        List of URI-formatted sources with appropriate schemes:
        - Local files: "file://path"
        - HTTP/HTTPS/RTSP URLs: "hlhttp://url"

    Raises:
        ValueError: If mixed schemes are detected or invalid input provided
        NotImplementedError: If unsupported data scheme is encountered

    Note:
        All sources must use the same scheme type within a single call.
    """
    if input_data == "--":
        # Read raw bytes from stdin
        byte_input = sys.stdin.buffer.read()
        # Decode bytes to string using specified encoding
        text_input = byte_input.decode(encoding)
        # Split on separator and yield non-empty paths

        inputs = text_input.strip().split(seperator)
    else:
        inputs = input_data

    # Take the first scheme and assume and assume all future schemes are the same
    scheme = None

    sources = []
    for path_url in inputs:
        path_url = str(path_url).strip()

        if Path(path_url).exists():  # Skip empty strings
            if scheme is None:
                scheme = "file"
            elif scheme != "file":
                raise ValueError("All schemes must be the same expected file")
            sources.append(f"file://{path_url}")
        elif is_url_scheme(str(path_url), ["http", "https", "rtsp", "rtsps"]):
            if scheme is None:
                scheme = "hlhttp"
            elif scheme != "hlhttp":
                raise ValueError("All schemes must be the same expected hlhttp")
            sources.append(f"hlhttp://{path_url}")
        else:
            raise NotImplementedError(f"Data scheme not implemented for input '{path_url}'")

    assert len(sources) > 0
    return sources


def _data_sources_are_specified_in_agent_definition(agent):
    """Check if data sources are predefined in the agent definition.

    Args:
        agent: HLAgent instance to check

    Returns:
        True if any data source capability has predefined data_sources parameter
    """
    data_source_capabilities = agent.get_data_source_capabilities()
    for data_source_capability in data_source_capabilities:
        if data_source_capability.element.definition.parameters.get("data_sources"):
            return True
    return False


def _make_network_fn_decorator(config, logger):
    """Create a decorator for network calls with retry logic and circuit breaker.

    This function creates a decorator that adds robust error handling to network
    operations, including exponential backoff retries and circuit breaker patterns
    to prevent cascading failures.

    Args:
        config: HighlighterRuntimeConfig instance with network settings
        logger: Logger instance for retry/failure reporting

    Returns:
        Decorator function that can be applied to network-calling functions

    The decorator handles:
        - Exponential backoff retry with configurable max attempts
        - Circuit breaker pattern to fail fast during outages
        - Logging of retry attempts and failures
        - Multiple exception types (Transport, Connection, Timeout errors)
    """
    breaker = CircuitBreaker(
        fail_max=1,  # consider if we need adjustable fail max config.network.fail_max. Set to 1 to fail, and retry after reset_timeout
        reset_timeout=config.network.reset_timeout,
    )

    def decorator(fn):
        retry_decorated = retry(
            wait=wait_exponential(multiplier=0.2, max=10),
            stop=stop_after_attempt(config.network.max_retries),
            retry=retry_if_exception_type(
                (
                    TransportError,
                    aiohttp.ClientConnectionError,  # aiohttp network errors
                    requests.ConnectionError,  # requests network errors
                    TimeoutError,  # Python built-in TimeoutError
                )
            ),
            before=before_log(logger, logging.DEBUG),
            after=after_log(logger, logging.DEBUG),
        )(fn)

        def wrapped(*args, **kwargs):
            last_exception = None

            def capture_and_call(*args, **kwargs):
                nonlocal last_exception
                try:
                    return retry_decorated(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    raise

            try:
                return breaker.call(capture_and_call, *args, **kwargs)
            except CircuitBreakerError as cbe:
                # If we have a captured exception, re-raise with it as the second argument
                if last_exception is not None:
                    raise CircuitBreakerError(
                        f"Circuit breaker opened due to: {last_exception}", last_exception
                    ) from last_exception
                # Otherwise, propagate the original circuit breaker error
                raise

        return wrapped

    return decorator


class Runtime:
    """Core runtime class for executing Highlighter agents.

    The Runtime class orchestrates the execution of Highlighter agents, managing
    configuration, signal handling, data input processing, and agent lifecycle.
    It supports multiple execution modes including file processing, task polling,
    and direct data processing.

    Attributes:
        logger: Logger instance for runtime operations
        agent: HLAgent instance for processing
        agent_definition: Path to agent definition file
        input_data: Input data specification
        expect_filepaths: Whether input should be treated as file paths
        separator: Data separator for input parsing
        step_task_ids: Comma-separated task IDs for direct task processing
        step_id: Step ID for task polling mode
        stream_id: Stream identifier for data processing
        dump_definition: Optional path for dumping agent definition
        allow_non_machine_user: Whether to allow non-machine user tasks
        hl_cfg: Runtime configuration instance
        hl_client: Highlighter client for API communication
        queue_response: Response queue for test harness integration
    """

    def __init__(
        self,
        agent_definition: str,
        input_data: Iterable[str] | str,
        expect_filepaths: bool,
        separator: Optional[str] = None,
        step_task_ids: str | None = None,
        step_id: str | None = None,
        stream_id: str = DEFAULT_STREAM_ID,
        dump_definition: Optional[str] = None,
        allow_non_machine_user: bool = False,
        hl_cfg: Optional[HighlighterRuntimeConfig] = None,
        hl_client=None,
        queue_response=None,  # ← test harness or HLAgentCli
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize the Runtime instance.

        Args:
            agent_definition: Path to the agent definition JSON file
            input_data: Input data specification (paths, URLs, or raw data)
            expect_filepaths: Whether input_data contains file paths
            separator: Optional separator for parsing input data
            step_task_ids: Comma-separated task IDs for direct execution
            step_id: Step ID for polling-based task execution
            stream_id: Stream identifier for data processing
            dump_definition: Optional path to dump processed agent definition
            allow_non_machine_user: Allow processing tasks from non-machine users
            hl_cfg: Pre-configured runtime configuration
            hl_client: Highlighter client for API communication
            queue_response: Response queue for test integration
            logger: Optional logger instance

        Raises:
            ValueError: If both step_id and step_task_ids are provided
        """

        self._install_signal_handlers()
        patch_threading()

        if not input_data:
            input_data = "--"

        if (separator is None) and (expect_filepaths):
            separator = DEFAULT_FILEPATH_SEPARATOR
        elif (separator is None) and (not expect_filepaths):
            separator = DEFAULT_CONTENT_SEPARATOR

        if step_id and step_task_ids:
            raise ValueError("--step-id and --step-task-ids are mutually exclusive")

        if logger:
            self.logger = logger
        else:
            configure_root_logger()
            self.logger = logging.getLogger(__name__)
        self.agent = None
        self.agent_definition = agent_definition
        self.input_data = input_data
        self.expect_filepaths = expect_filepaths
        self.separator = separator
        self.step_task_ids = step_task_ids
        self.step_id = step_id
        self.stream_id = stream_id
        self.dump_definition = dump_definition
        self.allow_non_machine_user = allow_non_machine_user
        self.hl_cfg = hl_cfg
        self.hl_client = hl_client
        self.queue_response = queue_response

    # ─────────────────────── signal handling section ───────────────────────
    def _complete_queued_work_then_shutdown(self, signum, frame):
        """Handle SIGTERM signal for graceful shutdown.

        This handler prevents new streams from being created and allows
        current queued work to complete before stopping the agent.

        Args:
            signum: Signal number received
            frame: Current stack frame (unused)
        """
        name = signal.Signals(signum).name
        self.logger.info(
            "%s received – preventing new streams, and stopping agent after current queued work", name
        )
        self.agent.disable_create_stream()
        # Stop all streams after processing process_frame calls on the Aiko event queue
        self.agent.stop_all_streams(graceful=True)

    def _interrupt_and_shutdown(self, signum, frame):
        """Handle SIGINT signal for immediate shutdown.

        This handler stops all streams immediately and drains worker threads.
        Currently processing frames will complete but no new work will start.

        Args:
            signum: Signal number received
            frame: Current stack frame (unused)
        """
        name = signal.Signals(signum).name
        self.logger.info(
            "%s received – stopping all streams, draining worker threads and stopping agent", name
        )
        self.agent.disable_create_stream()
        # Stop all streams immediately.
        # NOTE: If a frame is currently being processed it won't be interrupted.
        self.agent.stop_all_streams(graceful=False)
        signal.signal(signum, signal.SIG_DFL)

    def _quick_abort(self, signum, frame):
        """Handle SIGABRT/SIGQUIT signals for emergency abort.

        This handler dumps thread stacks for debugging and then allows
        the default signal behavior (usually core dump) to proceed.

        Args:
            signum: Signal number received (SIGABRT or SIGQUIT)
            frame: Current stack frame (unused)
        """
        name = signal.Signals(signum).name
        self.logger.error("%s received – dumping stacks, exiting HARD!", name)
        dump_stacks(level=logging.ERROR)
        # Re-raise default behaviour so the OS still gets a core dump / stack trace
        signal.signal(signum, signal.SIG_DFL)
        signal.raise_signal(signum)

    def reload_config(self, signum=None, frame=None):
        """Reload configuration at runtime.

        Can be called explicitly or as a signal handler (SIGHUP).
        Reloads the HighlighterRuntimeConfig from disk.

        Args:
            signum: Signal number (when used as signal handler)
            frame: Current stack frame (when used as signal handler)
        """
        self.logger.info("Reloading configuration...")
        try:
            self.load_config()
            self.logger.info("Reload complete.")
        except Exception as e:
            self.logger.error(f"Error reloading config: {e}")

    def _install_signal_handlers(self) -> None:
        """Register OS-level signal handlers.

        Registers handlers for graceful shutdown, configuration reload,
        and emergency abort. Must be called from the main thread.

        Signals handled:
            - SIGINT: Immediate shutdown
            - SIGTERM: Graceful shutdown after current work
            - SIGQUIT/SIGABRT: Emergency abort with diagnostics
            - SIGHUP: Configuration reload (Unix only)
        """
        signal.signal(signal.SIGINT, self._interrupt_and_shutdown)
        signal.signal(signal.SIGTERM, self._complete_queued_work_then_shutdown)
        signal.signal(signal.SIGQUIT, self._quick_abort)
        signal.signal(signal.SIGABRT, self._quick_abort)
        try:  # not present on Windows
            signal.signal(signal.SIGHUP, self.reload_config)
        except AttributeError:
            pass

    def load_config(self):
        """Load or reload the runtime configuration.

        Loads HighlighterRuntimeConfig from the standard configuration
        sources. Updates the instance's hl_cfg attribute.

        Raises:
            Exception: If configuration loading fails
        """
        try:
            self.hl_cfg = HighlighterRuntimeConfig.load()
            self.logger.info("Configuration loaded/reloaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise

    def start(self):
        """Start the runtime and initialize the agent.

        This method:
        1. Clears any previous stop events
        2. Loads configuration
        3. Sets up network decorators
        4. Creates and starts the HLAgent in a new thread
        """
        self.logger.info(f"Starting runtime on pid {os.getpid()}")
        runtime_stop_event.clear()
        self.load_config()

        decorators.network_fn_decorator = _make_network_fn_decorator(self.hl_cfg, self.logger)

        self.agent = HLAgent(
            self.agent_definition,
            dump_definition=self.dump_definition,
            timeout_secs=self.hl_cfg.agent.timeout_secs,
            task_lease_duration_secs=self.hl_cfg.agent.task_lease_duration_secs,
            task_polling_period_secs=self.hl_cfg.agent.task_polling_period_secs,
        )
        self.logger.info("Starting agent thread …")
        self.agent.run_in_new_thread()

    def shutdown(self):
        """Shutdown the runtime gracefully.

        This method:
        1. Stops all agent streams
        2. Stops the agent
        3. Sets the runtime stop event
        4. Dumps thread stacks for debugging
        5. Waits for all threads to join with timeout
        """
        self.agent.stop_all_streams()
        self.agent.stop()
        runtime_stop_event.set()  # broadcast the shutdown request
        dump_stacks(level=logging.INFO)
        join_all(timeout=THREAD_GRACEFUL_TIMEOUT)
        self.logger.info("Runtime shutdown complete.")

    def run(self) -> None:
        """Execute the runtime's main processing loop.

        This is the primary entry point for runtime execution. It:
        1. Starts the agent
        2. Determines execution mode based on configuration
        3. Processes data according to the chosen mode:
           - File/URL processing from input paths
           - Task polling by step ID
           - Direct task execution by task IDs
           - Raw data processing from stdin
        4. Shuts down gracefully after completion

        Execution Modes:
            - File processing: When expect_filepaths=True
            - Task polling: When step_id is provided
            - Direct tasks: When step_task_ids is provided
            - Raw data: When reading from stdin with raw data
            - Inline JSON: When input contains JSON frame data
        """

        self.start()  # start agent

        # 3. Decide execution mode (verbatim from old _start) -----------------
        data_sources = None
        if self.expect_filepaths:
            data_sources = _read_filepaths(self.input_data, self.separator, "utf-8")

        elif _reading_raw_data_from_stdin_buffer(
            self.input_data, self.expect_filepaths, self.separator
        ) and not _data_sources_are_specified_in_agent_definition(self.agent):
            data_sources = ["hlpipe://"]

        if self.step_id:
            self.agent.poll_for_tasks_loop(self.step_id, allow_non_machine_user=self.allow_non_machine_user)

        elif self.step_task_ids:
            if not self.allow_non_machine_user:
                self.agent.check_user_is_machine()
            # TODO: load hl client if not passed in
            for task_id in [t.strip() for t in self.step_task_ids.split(",")]:
                task = lease_task(
                    self.hl_client,
                    task_id=task_id,
                    lease_sec=self.hl_cfg.agent.task_lease_duration_secs,
                    set_status_to="RUNNING",
                )
                self.agent._process_task(task)

        elif data_sources or _data_sources_are_specified_in_agent_definition(self.agent):
            self.agent.process_data_sources(
                self.stream_id,
                data_sources,
                self.queue_response,
                self.hl_cfg.agent.queue_response_max_size,
                timeout_secs=self.hl_cfg.agent.timeout_secs,
            )

        else:
            # assume process_frame data is passed directly
            try:
                if self.input_data == "--":
                    frame_datas = json.load(sys.stdin.buffer)
                else:
                    frame_datas = json.loads(self.input_data[0])
            except Exception as e:
                raise ValueError(f"Failed to parse inline frame data: {e}") from e

            self.agent.loop_over_process_frame(self.stream_id, frame_datas, self.queue_response)

        self.logger.info("Finished processing, joining worker threads")
        self.shutdown()
