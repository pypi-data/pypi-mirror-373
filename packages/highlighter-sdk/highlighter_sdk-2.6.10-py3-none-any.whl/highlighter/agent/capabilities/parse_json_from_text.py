import json
from typing import Dict, Tuple, Union

from highlighter.agent.capabilities import Capability, StreamEvent
from highlighter.client.json_tools import find_valid_json

__all__ = ["ParseJsonFromText"]


class ParseJsonFromText(Capability):
    """
    Parse json from the provided text
    """

    def process_frame(self, stream, text: str) -> Tuple[StreamEvent, Union[Dict, str]]:
        """

        text: str

        """
        try:
            results = find_valid_json(text)

            if len(results) == 0:
                text = "null"
            else:
                text = json.dumps(results[0])

        except json.decoder.JSONDecodeError as e:
            self.logger.error(f"LLM: Error calling find_valid_json on {text}: {e}")
            results = {}

        return StreamEvent.OKAY, {"text": text, "input_text": text}
