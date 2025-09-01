from typing import Optional

import os
import logging
from typing import Any, Dict, List

import litellm
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from litellm import RateLimitError


from dtx_models.evaluator import EvaluatorInScope
from dtx_models.prompts import (
    BaseMultiTurnConversation,
    BaseMultiTurnResponse,
)

from dtx_models.template.prompts.base import BasePromptTemplateRepo
from dtx_models.providers.openai import ProviderParams
from dtx_models.prompts import BaseMultiTurnAgentResponse, RoleType, Turn


class BaseAgent:
    def generate(self, prompt: str) -> str:
        raise ValueError("Not Implemented Error")

    def converse(self, prompt: BaseMultiTurnConversation) -> BaseMultiTurnResponse:
        """
        Perform Multi turn conversation with the agent
        """
        raise ValueError("Not Implemented Error")

    def get_preferred_evaluator(self) -> Optional[EvaluatorInScope]:
        """
        Return Preferred Evaluator if exists
        """
        return None

    def is_available(self) -> bool:
        """
        Check if the Ollama server is available.
        """
        return True


# base_custom_litellm_agent.py

class BaseCustomLiteLLMAgent(BaseAgent):
    def __init__(
        self,
        model_backend_name: str,  # e.g., "groq"
        provider_config: Any,  # Must have `.model` and `.params`
        prompt_template: Optional[BasePromptTemplateRepo] = None,
    ):
        self.logger = logging.getLogger(__name__)
        self._provider_name = model_backend_name
        self._provider_config = provider_config
        self._prompt_template = prompt_template

        self._model = f"{model_backend_name}/{provider_config.model}"  # e.g., groq/llama-3.1-8b-instant
        self._available = False

        self.logger.debug(f"Final model identifier: {self._model}")
        self._init_client()

    def _init_client(self):
        try:
            endpoint = self._provider_config.endpoint
            if endpoint:
                os.environ["LITELLM_API_BASE"] = endpoint
                self.logger.info(f"Set LiteLLM endpoint to: {endpoint}")

            litellm.completion(
                model=self._model,
                messages=[{"role": "user", "content": "ping"}],
                temperature=0.0,
                max_tokens=1,
                custom_llm_provider=self._provider_name,
            )
            self._available = True
            self.logger.info(f"Model '{self._model}' is available.")
        except Exception as e:
            self.logger.error(f"Failed to initialize LiteLLM model: {e}")
            self._available = False

    def _build_options(self) -> dict:
        config: ProviderParams = self._provider_config.params or ProviderParams()
        extra = config.extra_params or {}

        options = {
            "temperature": config.temperature or 0.7,
            "top_p": config.top_p or 0.9,
            "max_tokens": config.max_tokens or 4096,
            "stop": extra.get("stop", []),
            "custom_llm_provider": self._provider_name,
        }

        # Optional Groq/Mistral-style additions
        if config.top_k is not None:
            options["top_k"] = config.top_k
        if config.repeat_penalty is not None:
            options["presence_penalty"] = config.repeat_penalty

        return options

    def _format_messages(self, turns: List[Turn]) -> List[Dict[str, str]]:
        return [{"role": turn.role.value.lower(), "content": turn.message} for turn in turns]

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _safe_completion(self, completion_args: dict) -> Any:
        return litellm.completion(**completion_args)

    def converse(self, prompt: BaseMultiTurnConversation) -> BaseMultiTurnAgentResponse:
        messages = self._format_messages(prompt.turns)

        completion_args = {
            "model": self._model,
            "messages": messages,
            **self._build_options(),
        }

        self.logger.debug(f"Calling LiteLLM with args: {completion_args}")

        try:
            # response = self._safe_completion(completion_args)
            # content = response["choices"][0]["message"]["content"]
            # turns = prompt.turns + [Turn(role=RoleType.ASSISTANT, message=content)]
            # return BaseMultiTurnAgentResponse(turns=turns)
            response = self._safe_completion(completion_args)
            content = response["choices"][0]["message"].get("content")

            if not content:
                self.logger.warning(f"Model returned insufficient content.")
                content = "I'm unable to provide a proper answer at the moment."  # fallback

            turns = prompt.turns + [Turn(role=RoleType.ASSISTANT, message=content)]

            agent_response = BaseMultiTurnAgentResponse(turns=turns)

            # Attach and log policy
            if hasattr(prompt, "policy") and prompt.policy:
                agent_response.policy = prompt.policy
                self.logger.debug(f"Attaching policy to response: {prompt.policy}")
            else:
                self.logger.warning("No policy specified on prompt; response.policy left unset")

            # Attach and log goal
            if hasattr(prompt, "goal") and prompt.goal:
                agent_response.goal = prompt.goal
                self.logger.debug(f"Attaching goal to response: {prompt.goal}")
            else:
                self.logger.warning("No goal specified on prompt; response.goal left unset")

            return agent_response

        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise
