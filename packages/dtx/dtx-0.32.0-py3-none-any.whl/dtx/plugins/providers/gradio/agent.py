import copy
from typing import Any, Dict

import deprecation
from gradio_client import Client  # Gradio API client

from dtx_models.prompts import (
    BaseMultiTurnAgentResponse,
    BaseMultiTurnConversation,
    BaseMultiTurnResponseBuilder,
)
from dtx_models.providers.gradio import GradioProvider
from dtx.plugins.providers.gradio.client import GradioProviderClient

from ..base.agent import BaseAgent


class GradioAgent(BaseAgent):
    def __init__(
        self,
        provider: GradioProvider,
        vars: Dict[str, Any] = None,
        client: Client = None,
    ):
        self._client = GradioProviderClient(url=provider.config.url, client=client)
        self._vars = vars or {}
        self._provider = provider

    @deprecation.deprecated(details="Use converse method instead")
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
        
        api = self._provider.config.apis[0]
        provider_response = self._client.generate(api=api, prompt=prompt, vars=_vars)

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

        api = self._provider.config.apis[0]
        provider_response = self._client.generate(api=api, prompt=prompt, vars=_vars)

        builder = BaseMultiTurnResponseBuilder()
        builder.add_prompt(prompt, system_prompt=system_prompt)
        builder.add_turn_response(provider_response)
        builder.add_parsed_response(provider_response)
        builder.add_prompt_attributes(prompt)

        # response = BaseMultiTurnAgentResponse(
        #     turns=builder.build().turns, response=provider_response
        # )

        return builder.build()
