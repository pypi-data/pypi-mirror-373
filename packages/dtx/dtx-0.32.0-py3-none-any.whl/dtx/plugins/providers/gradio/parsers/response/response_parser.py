import json
from typing import Any

from dtx.core import logging
from dtx_models.providers.gradio import (
    GradioResponseParserSignature,
)


class GradioResponseParser:
    def __init__(
        self,
        signature: Any = None,
    ):
        if signature is not None:
            if isinstance(signature, GradioResponseParserSignature):
                self.parser = GradioResponseSignatureBasedParser(signature)
        else:
            self.parser = None

    def parse(self, prompt, response):
        if self.parser is None:
            return response

        if isinstance(self.parser, GradioResponseSignatureBasedParser):
            response_with_prompt, response = self.parser.parse(prompt, response)
            return response or response_with_prompt


class GradioResponseSignatureBasedParser:
    """A class to parse model responses and extract relevant information."""

    def __init__(
        self,
        signature: GradioResponseParserSignature = None,
    ):
        self._content_type = signature.content_type
        self._location = signature.location

    def parse(self, prompt, response):
        if isinstance(response, (str, int)):
            return str(response).replace(prompt, ""), ""
        elif isinstance(response, (tuple, dict, list)):
            return str(response).replace(prompt, ""), self._attempt_list_parsing(
                prompt, response
            )
        else:
            content_text = str(response.content)
            content_text_without_prompt = content_text.replace(prompt, "")
            if self._content_type == "json":
                return content_text_without_prompt, self._attempt_json_parsing(
                    prompt, response
                )
            elif self._content_type == "jsonl":
                return content_text_without_prompt, self._attempt_jsonl_parsing(
                    prompt, response
                )
            else:
                return content_text_without_prompt, ""

    def _attempt_list_parsing(self, prompt, response):
        if not self._location:
            return ""
        res = response
        for i in self._location:
            res = res[i]
        return res

    def _attempt_json_parsing(self, prompt, response):
        try:
            res_json = response.json()
            return self._attempt_list_parsing(prompt, res_json)
        except Exception as ex:
            logging.exception("Error while parsing JSON", exc_info=ex)
        return ""

    def _attempt_jsonl_parsing(self, prompt, res):
        try:
            decoded_content = res.content.decode("utf-8")
            lines = decoded_content.split("\n")
            for line in lines:
                parsed_line = json.loads(line)
                txt = self._attempt_list_parsing(prompt, parsed_line)
                if txt:
                    return str(txt)
        except Exception as ex:
            logging.exception("Error while parsing JSON", exc_info=ex)
        return ""
