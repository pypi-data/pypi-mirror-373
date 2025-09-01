from typing import Optional

from ollama import Client

from dtx.core import logging
from dtx_models.prompts import (
    BaseMultiTurnAgentResponse,
    BaseMultiTurnConversation,
    BaseMultiTurnResponseBuilder,
    RoleType,
    Turn,
)
from dtx_models.providers.ollama import OllamaProvider, OllamaTask

from ..base.agent import BaseAgent
from ..base.exceptions import InvalidInputException


class OllamaAgent(BaseAgent):
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        provider: OllamaProvider,
        client: Optional[Client] = None,
    ):
        if not provider.config.model:
            raise InvalidInputException("Model name must be provided for OllamaAgent.")

        self._model = provider.config.model
        self._provider = provider
        self._client = None
        self._available = False

        endpoint = provider.config.endpoint or "http://localhost:11434"

        if client:
            self._client = client
        else:
            try:
                self._client = Client(host=endpoint)
            except Exception as e:
                self.logger.error(f"Failed to initialize Ollama client: {e}")
                self._available = False
                return

        # Test availability by sending a ping message
        try:
            test_messages = [{"role": "user", "content": "ping"}]
            self._client.chat(model=self._model, messages=test_messages)
            self._available = True
        except Exception as e:
            self.logger.error(f"Ping test failed during initialization: {e}")
            self._available = False

    def _build_options(self) -> dict:
        """
        Build generation options from the provider params.
        """
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
            options["repeat_penalty"] = params.repeat_penalty
        if params.max_tokens is not None:
            options["num_predict"] = params.max_tokens
        if params.num_return_sequences is not None:
            options["num_return_sequences"] = params.num_return_sequences

        if params.extra_params:
            options.update(
                {k: v for k, v in params.extra_params.items() if v is not None}
            )

        return options

    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generates a single-turn response from Ollama.
        """
        builder = BaseMultiTurnResponseBuilder().add_prompt(prompt, system_prompt)
        formatted_prompt = builder.build()

        messages = formatted_prompt.to_openai_format()

        response = self._client.chat(
            model=self._model, messages=messages, options=self._build_options()
        )
        return response["message"]["content"]

    def converse(self, prompt: BaseMultiTurnConversation) -> BaseMultiTurnAgentResponse:
        """
        Routes multi-turn conversation to appropriate handler based on task type.
        """
        task = self._provider.config.task or OllamaTask.TEXT_CLASSIFICATION

        if task == OllamaTask.TEXT_CLASSIFICATION:
            return self._handle_classification(prompt)
        else:
            return self._handle_generation(prompt)

    def is_available(self) -> bool:
        """
        Check if the Ollama server is available.
        """
        return self._available

    def _handle_classification(
        self, prompt: BaseMultiTurnConversation
    ) -> BaseMultiTurnAgentResponse:
        builder = BaseMultiTurnResponseBuilder()
        builder.add_prompt_attributes(prompt)

        for turn in prompt.turns:
            builder.add_turn(turn)

        formatted_prompt = builder.build()
        messages = formatted_prompt.to_openai_format()

        response = self._client.chat(
            model=self._model, messages=messages, options=self._build_options()
        )
        final_parsed_response = {"content": response["message"]["content"]}
        builder.add_parsed_response(final_parsed_response)
        return builder.build()

    def _handle_generation(
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

            response = self._client.chat(
                model=self._model, messages=messages, options=self._build_options()
            )
            assistant_response = response["message"]["content"] or "Empty Response"
            last_response["content"] = assistant_response
            builder.add_turn(Turn(role=RoleType.ASSISTANT, message=assistant_response))
        builder.add_parsed_response(last_response)
        return builder.build()


if __name__ == "__main__":
    from dtx_models.providers.ollama import (
        OllamaProvider,
        OllamaProviderConfig,
        OllamaProviderParams,
    )
    from dtx.plugins.providers.ollama.agent import OllamaAgent

    # Step 1: Create a provider for llama-guard3
    provider_config = OllamaProviderConfig(
        model="llama-guard3:1b-q3_K_S",
        endpoint="http://localhost:11434",  # Optional if default
        config=OllamaProviderParams(
            temperature=0.7,
        ),
    )

    provider = OllamaProvider(config=provider_config)

    # Step 2: Instantiate the agent
    agent = OllamaAgent(provider)

    # 3. Create a multi-turn conversation
    conversation = BaseMultiTurnConversation(
        turns=[
            Turn(role=RoleType.SYSTEM, message="You are a helpful assistant."),
            Turn(role=RoleType.USER, message="Hi, who won the World Cup in 2022?"),
            Turn(role=RoleType.USER, message="Where was it held?"),
        ],
    )
    response = agent.converse(conversation)
    print(response)
