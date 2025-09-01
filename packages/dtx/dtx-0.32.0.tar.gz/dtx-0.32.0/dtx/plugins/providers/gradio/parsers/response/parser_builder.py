import json
import random
import string

from dtx.core import logging
from dtx_models.providers.gradio import (
    GradioProviderApi,
    GradioResponseParserSignature,
)

from ...client import GradioProviderClient


class GradioResponseParserBuilder:
    """Builder class for GradioResponseParserSignature."""

    def __init__(self, client: GradioProviderClient):
        self._client = client

    def generate(
        self, api: GradioProviderApi, prompt_placeholder: str
    ) -> GradioResponseParserSignature:
        _marker = self._random_string(12)

        texts = [
            f"Your task is to repeat the word {_marker}, say How are you?",
            f"Do you know about {_marker}? Can you tell something about it?",
            f"Can you something about {_marker}? and if not say: 'I can not tell anything about {_marker}'",
        ]

        _response_parser = None
        for prompt in texts:
            res = self._client.generate_raw(api=api, vars={prompt_placeholder: prompt})
            _response_parser = self._attempt_convert_res_2_parser(prompt, res, _marker)
            if _response_parser:
                break

        return _response_parser or GradioResponseParserSignature()

    def _attempt_convert_res_2_parser(
        self, prompt, res, _marker
    ) -> GradioResponseParserSignature:
        methods = [
            self._attempt_convert_json_to_parser,
            self._attempt_convert_jsonl_to_parser,
            self._attempt_python_structure,
        ]
        for method in methods:
            parser = method(prompt, res, _marker)
            if parser:
                return parser
        return GradioResponseParserSignature()

    def _attempt_python_structure(self, prompt, res, marker, content_type="array"):
        loc = self.__attempt_python_structure(prompt, res, marker)
        if loc:
            return GradioResponseParserSignature(
                content_type=content_type, location=loc
            )
        return None

    def __attempt_python_structure(self, prompt, res, marker, j=None):
        loc = []
        if isinstance(res, (list, tuple)):
            for i, b in enumerate(res):
                result = self.__attempt_python_structure(prompt, b, marker, i)
                if result:
                    if j is not None:
                        # if it is a last element, append -1
                        if i == len(res) - 1:
                            loc.append(-1)
                        else:
                            loc.append(j)
                    loc.extend(result)
                    break
        elif isinstance(res, dict):
            for k, v in res.items():
                result = self.__attempt_python_structure(prompt, v, marker, k)
                if result:
                    if j is not None:
                        loc.append(j)
                    loc.extend(result)
                    break
        else:
            res = str(res).replace(prompt, "")
            if marker in res or "sorry" in res or "understand" in res:
                if j is not None:
                    loc.append(j)
        return loc

    def _attempt_convert_json_to_parser(self, prompt, res, _marker):
        res_json = self._attempt_json_parsing(res)
        if res_json:
            return self._attempt_python_structure(
                prompt, res_json, _marker, content_type="json"
            )
        return None

    def _attempt_convert_jsonl_to_parser(self, prompt, res, _marker):
        json_lines = self._attempt_jsonl_parsing(res)
        for json_line in json_lines:
            return self._attempt_python_structure(
                prompt, json_line, _marker, content_type="jsonl"
            )
        return None

    def _random_string(self, length):
        return "".join(
            random.choice(string.ascii_letters + string.digits) for _ in range(length)
        )

    def _attempt_json_parsing(self, res):
        try:
            response_json = res.json()
            if isinstance(response_json, dict):
                return response_json
        except Exception as ex:
            logging.debug("Could not parse json structure %s", ex)
        return None

    def _attempt_jsonl_parsing(self, res):
        try:
            decoded_content = res.content.decode("utf-8")
            lines = decoded_content.split("\n")
            for line in lines:
                parsed_line = json.loads(line)
                if isinstance(parsed_line, dict):
                    yield parsed_line
        except Exception as ex:
            logging.debug("Could not parse jsonl structure %s", ex)


if __name__ == "__main__":
    model = None  # Replace with actual model instance
    builder = GradioResponseParserBuilder()
    parser = builder.generate(model)
    prompt = "Hello, AI!"
    response = "Hello, how can I help you?"
    parsed_response = parser.parse(prompt, response)
    print("Parsed Response:", parsed_response)
