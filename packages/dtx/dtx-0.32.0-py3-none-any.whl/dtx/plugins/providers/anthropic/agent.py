from dtx_models.providers.anthropic import AnthropicProvider
from dtx_models.template.prompts.base import BasePromptTemplateRepo
from ..base.agent import BaseCustomLiteLLMAgent


class AnthropicAgent(BaseCustomLiteLLMAgent):
    def __init__(
        self,
        provider: AnthropicProvider,
        prompt_template: BasePromptTemplateRepo = None,
    ):
        super().__init__(
            model_backend_name="anthropic",  # used as LiteLLM model prefix
            provider_config=provider.config,
            prompt_template=prompt_template,
        )