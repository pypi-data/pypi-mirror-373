import json
from queue import Queue
from tempfile import TemporaryDirectory
from typing import Dict

from click.testing import CliRunner

from highlighter.cli.highlighter import highlighter_group

__all__ = ["HLAgentCliRunner"]


class HLAgentCliRunner:

    def __init__(self, definition: Dict):
        self._tmpdir = TemporaryDirectory()

        self.definition = definition
        self.definition_path = f"{self._tmpdir.name}/definition.json"
        with open(self.definition_path, "w") as f:
            json.dump(self.definition, f)

        self.queue_response = Queue()

    def hl_agent_start(self, opts: str, args: str, click_invoke_input=None, **click_runner_kwargs):
        runner = CliRunner(**click_runner_kwargs)
        cli_cmd = f"agent start {opts} {self.definition_path} {args}"
        result = runner.invoke(
            highlighter_group,
            cli_cmd.split(),
            obj={"queue_response": self.queue_response},
            input=click_invoke_input,
            catch_exceptions=False,
        )
        return result
