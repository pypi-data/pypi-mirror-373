import copy
from typing import Any, Dict

from dtx_models.prompts import (
    BaseMultiTurnAgentResponse,
    BaseMultiTurnConversation,
    BaseMultiTurnResponseBuilder,
)
from dtx_models.providers.http import HttpProvider
from dtx.plugins.providers.http.provider_client import HttpProviderClient

from ..base.agent import BaseAgent


class HttpAgent(BaseAgent):
    def __init__(self, provider: HttpProvider, vars: Dict[str, Any] = None):
        self._client = HttpProviderClient()
        self._vars = vars or {}
        self._provider = provider

    def generate(
        self, prompt: str, system_prompt: str = None
    ) -> BaseMultiTurnAgentResponse:
        """
        Generates a response using the Hugging Face pipeline for single-turn text generation or classification.
        """
        _vars = copy.deepcopy(self._vars)
        _vars["prompt"] = prompt
        if system_prompt:
            _vars["system_prompt"] = system_prompt

        provider_response = self._client.generate(provider=self._provider, vars=_vars)

        builder = BaseMultiTurnResponseBuilder()
        builder.add_prompt(prompt, system_prompt=system_prompt)
        builder.add_turn_response(provider_response)

        response = BaseMultiTurnAgentResponse(
            turns=builder.build().turns, response=provider_response
        )

        return response

    def converse(self, prompt: BaseMultiTurnConversation) -> BaseMultiTurnAgentResponse:
        """
        Handles multi-turn conversations based on the task type and format.
        Returns:
            - `BaseMultiTurnResponse` for text-generation tasks.
            - `BaseMultiTurnAgentResponse` for classification tasks.
        """
        system_prompt = prompt.first_system_prompt()

        prompt = prompt.first_user_prompt()

        _vars = copy.deepcopy(self._vars)
        _vars["prompt"] = prompt
        if system_prompt:
            _vars["system_prompt"] = system_prompt

        provider_response = self._client.generate(provider=self._provider, vars=_vars)

        builder = BaseMultiTurnResponseBuilder()
        builder.add_prompt(prompt, system_prompt=system_prompt)
        builder.add_turn_response(provider_response)
        builder.add_parsed_response(provider_response)
        builder.add_prompt_attributes(prompt)
        # response = BaseMultiTurnAgentResponse(
        #     turns=builder.build().turns, response=provider_response
        # )

        return builder.build()
