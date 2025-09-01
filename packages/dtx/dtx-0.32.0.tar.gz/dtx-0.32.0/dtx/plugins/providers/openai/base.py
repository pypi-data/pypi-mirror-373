import os
from typing import Any, Optional

import litellm
import openai

from dtx.core import logging
from dtx_models.prompts import (
    BaseMultiTurnAgentResponse,
    BaseMultiTurnConversation,
    BaseMultiTurnResponseBuilder,
    RoleType,
    Turn,
)
from dtx_models.providers.litellm import LitellmProvider
from dtx_models.providers.openai import ModelTaskType
from dtx_models.template.prompts.base import BasePromptTemplateRepo
from dtx.plugins.prompts.template.resolver import PromptTemplateResolver

from ..base.agent import BaseAgent
from ..base.exceptions import InvalidInputException


class BaseChatAgent(BaseAgent):
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        provider,
        client: Optional[Any] = None,
        prompt_template: BasePromptTemplateRepo = None,
    ):
        if not provider.config.model:
            raise InvalidInputException("Model name must be provided for the AgentInfo.")

        self._model = provider.config.model
        self._provider = provider
        self._available = False
        self._client = client
        # Optional Prompt Template to customize the prompt before sending to the provider
        self._prompt_template: BasePromptTemplateRepo = prompt_template

        self._init_client()

    def _init_client(self):
        """
        Implemented by subclasses to initialize the client.
        """
        raise NotImplementedError

    def set_prompt_template(self, template: BasePromptTemplateRepo):
        self._prompt_template = template

    def is_available(self) -> bool:
        return self._available

    def _build_options(self) -> dict:
        options = {}
        params = self._provider.config.params
        if not params:
            return options

        if params.temperature is not None:
            options["temperature"] = params.temperature
        if params.top_k is not None:
            options["top_k"] = params.top_k
        if params.top_p is not None:
            options["top_p"] = params.top_p
        if params.repeat_penalty is not None:
            options["presence_penalty"] = params.repeat_penalty
        if params.max_tokens is not None:
            options["max_tokens"] = params.max_tokens
        if params.num_return_sequences is not None:
            options["n"] = params.num_return_sequences

        if params.extra_params:
            options.update(
                {k: v for k, v in params.extra_params.items() if v is not None}
            )

        return options

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        builder = BaseMultiTurnResponseBuilder().add_prompt(prompt, system_prompt)
        formatted_prompt = builder.build()
        messages = formatted_prompt.to_openai_format()

        response = self._chat_completion(messages)
        return self._extract_response_content(response)

    def converse(self, prompt: BaseMultiTurnConversation) -> BaseMultiTurnAgentResponse:
        task = self._provider.config.task or ModelTaskType.GENERATION

        if task == ModelTaskType.CLASSIFICATION:
            return self._handle_classification(prompt)
        else:
            return self._handle_generation(prompt)

    def _handle_classification(
        self, prompt: BaseMultiTurnConversation
    ) -> BaseMultiTurnAgentResponse:
        builder = BaseMultiTurnResponseBuilder()
        builder.add_prompt_attributes(prompt)

        for turn in prompt.turns:
            builder.add_turn(turn)

        formatted_prompt = builder.build()
        messages = formatted_prompt.to_openai_format()

        response = self._chat_completion(messages)

        final_parsed_response = {"content": self._extract_response_content(response)}
        builder.add_parsed_response(final_parsed_response)

        return builder.build()

    def _handle_generation(
        self, prompt: BaseMultiTurnConversation
    ) -> BaseMultiTurnAgentResponse:
        if self._prompt_template:
            return self._handle_generation_with_prompt_template(prompt=prompt)
        else:
            return self._handle_generation_with_no_prompt_template(prompt=prompt)

    def _handle_generation_with_prompt_template(
        self, prompt: BaseMultiTurnConversation
    ) -> BaseMultiTurnAgentResponse:
        builder = BaseMultiTurnResponseBuilder()
        builder.add_prompt_attributes(prompt)

        resolver = PromptTemplateResolver(self._prompt_template)
        enriched_conversation = resolver.convert(prompt)

        if enriched_conversation.has_system_turn():
            builder.add_turn(prompt.get_system_turn())

        last_response = {}
        for turn in enriched_conversation.get_user_turns():
            builder.add_turn(turn)
            formatted_prompt = builder.build()
            messages = formatted_prompt.to_openai_format()

            response = self._chat_completion(messages)

            assistant_response = self._extract_response_content(response) or "Empty Response"
            last_response["content"] = assistant_response
            builder.add_turn(Turn(role=RoleType.ASSISTANT, message=assistant_response))

        builder.add_parsed_response(last_response)
        return builder.build()

    def _handle_generation_with_no_prompt_template(
        self, prompt: BaseMultiTurnConversation
    ) -> BaseMultiTurnAgentResponse:
        builder = BaseMultiTurnResponseBuilder()
        builder.add_prompt_attributes(prompt)

        if prompt.has_system_turn():
            builder.add_turn(prompt.get_system_turn())

        last_response = {}
        for turn in prompt.get_user_turns():
            builder.add_turn(turn)
            formatted_prompt = builder.build()
            messages = formatted_prompt.to_openai_format()

            response = self._chat_completion(messages)

            assistant_response = self._extract_response_content(response) or "Empty Response"
            last_response["content"] = assistant_response
            builder.add_turn(Turn(role=RoleType.ASSISTANT, message=assistant_response))

        builder.add_parsed_response(last_response)
        return builder.build()

    def _chat_completion(self, messages: list) -> Any:
        raise NotImplementedError

    def _extract_response_content(self, response: Any) -> str:
        raise NotImplementedError


class BaseOpenAICompatibleAgent(BaseChatAgent):
    def _init_client(self):
        if self._client:
            # Test mode, use injected client
            self._available = True
            return

        try:
            if self._provider.config.endpoint:
                self._client = openai.OpenAI(base_url=self._provider.config.endpoint)
            else:
                self._client = openai.OpenAI()

            self._client.models.list()  # Test availability
            self._available = True
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI-compatible client: {e}")
            self._available = False

    def _chat_completion(self, messages: list) -> Any:
        return self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            **self._build_options(),
        )

    def _extract_response_content(self, response: Any) -> str:
        return response.choices[0].message.content


class BaseLiteLLMCompatibleAgent(BaseChatAgent):
    def __init__(self, provider: LitellmProvider):
        if not provider.config.model:
            raise InvalidInputException("Model name must be provided for the AgentInfo.")

        self._model = provider.config.model
        self._provider = provider
        self._available = False
        self._init_client()

    def _init_client(self):
        try:
            endpoint = self._provider.config.endpoint
            if endpoint:
                os.environ["LITELLM_API_BASE"] = endpoint

            # Test availability
            litellm.completion(
                model=self._model,
                messages=[{"role": "user", "content": "ping"}],
                temperature=0.0,
                max_tokens=1,
            )
            self._available = True

        except Exception as e:
            self.logger.error(f"Failed to initialize LiteLLM client: {e}")
            self._available = False

    def _chat_completion(self, messages: list) -> Any:
        return litellm.completion(
            model=self._model,
            messages=messages,
            **self._build_options(),
        )

    def _extract_response_content(self, response: Any) -> str:
        return response["choices"][0]["message"]["content"]
