import os
import logging
from typing import Any, List, Union

import litellm
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from litellm import RateLimitError

from dtx_models.providers.litellm import LitellmProvider
from dtx_models.template.prompts.base import BasePromptTemplateRepo
from dtx_models.providers.openai import ProviderParams

from ..base.exceptions import InvalidInputException
from ..openai.base import BaseChatAgent


class BaseLiteLLMCompatibleAgent(BaseChatAgent):
    def __init__(
        self,
        provider: LitellmProvider,
        prompt_template: BasePromptTemplateRepo = None,
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing BaseLiteLLMCompatibleAgent...")

        if not provider.config.model:
            self.logger.error("Model name is missing in provider config.")
            raise InvalidInputException("Model name must be provided for the AgentInfo.")

        self._model = provider.config.model
        self._provider = provider
        self._available = False

        # Extract provider name from model (e.g., "groq/llama3-70b" → "groq")
        self._provider_name = self._model.split("/")[0].lower() if "/" in self._model else "default"

        self.set_prompt_template(prompt_template)
        self._init_client()

    def _init_client(self):
        try:
            endpoint = self._provider.config.endpoint
            if endpoint:
                os.environ["LITELLM_API_BASE"] = endpoint
                self.logger.info(f"Set LiteLLM endpoint to: {endpoint}")

            self.logger.debug("Pinging model for availability test...")
            litellm.completion(
                model=self._model,
                messages=[{"role": "user", "content": "ping"}],
                temperature=0.0,
                max_tokens=1,
                custom_llm_provider=self._provider_name if self._provider_name != "openai" else None,
            )
            self._available = True
            self.logger.info(f"LiteLLM model '{self._model}' is available.")
        except Exception as e:
            self.logger.error(f"Failed to initialize LiteLLM client: {e}")
            self._available = False

    def _build_options(self) -> dict:
        # Get the ProviderParams instance or create a default one if None
        config = self._provider.config.params
        if config is None:
            config = ProviderParams(extra_params={})

        extra = config.extra_params or {}

        options = {
            "temperature": config.temperature if config.temperature is not None else 0.7,
            "top_p": config.top_p if config.top_p is not None else 0.9,
            "max_tokens": config.max_tokens if config.max_tokens is not None else 512,
            "stop": extra.get("stop", []),
        }

        if self._provider_name not in {"groq", "openai"}:
            options["top_k"] = config.top_k if config.top_k is not None else 40

        if self._provider_name in {"groq", "openai"}:
            options["presence_penalty"] = config.repeat_penalty if config.repeat_penalty is not None else 1.1

        self.logger.debug(f"Built LiteLLM call options for {self._provider_name}: {options}")
        return options


    def _format_messages(self, messages: List[dict]) -> Union[List[dict], str]:
        if self._provider_name == "anthropic":
            prompt = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in messages)
            return f"{prompt}\n\nAssistant:"
        return messages

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True
    )
    def _safe_completion(self, completion_args: dict) -> Any:
        self.logger.warning("Retrying LiteLLM request due to rate limiting...")
        return litellm.completion(**completion_args)

    def _chat_completion(self, messages: list) -> Any:
        self.logger.info(f"Sending chat completion request to model: {self._model}")

        try:
            formatted_messages = self._format_messages(messages)
            completion_args = {
                "model": self._model,
                "messages": formatted_messages if isinstance(formatted_messages, list) else None,
                "prompt": formatted_messages if isinstance(formatted_messages, str) else None,
                "custom_llm_provider": self._provider_name if self._provider_name != "openai" else None,
                **self._build_options(),
            }

            # Remove None values (e.g., if "prompt" or "messages" is not needed)
            completion_args = {k: v for k, v in completion_args.items() if v is not None}

            response = self._safe_completion(completion_args)
            self.logger.debug("Received response from LiteLLM.")
            return response
        except Exception as e:
            self.logger.error(f"LiteLLM chat completion failed: {e}")
            raise

    def _extract_response_content(self, response: Any) -> str:
        self.logger.debug("Extracting response content...")
        return response["choices"][0]["message"]["content"]


class LitellmAgent(BaseLiteLLMCompatibleAgent):
    def __init__(
        self,
        provider: LitellmProvider,
        prompt_template: BasePromptTemplateRepo = None,
    ):
        super().__init__(provider=provider, prompt_template=prompt_template)
        self.logger.info("LitellmAgent initialized successfully.")
