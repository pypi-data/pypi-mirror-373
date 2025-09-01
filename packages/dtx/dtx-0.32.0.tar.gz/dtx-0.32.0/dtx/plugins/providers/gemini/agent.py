from dtx_models.providers.gemini import GeminiProvider
from dtx_models.template.prompts.base import BasePromptTemplateRepo
from ..base.agent import BaseCustomLiteLLMAgent


class GeminiAgent(BaseCustomLiteLLMAgent):
    def __init__(
        self,
        provider: GeminiProvider,
        prompt_template: BasePromptTemplateRepo = None,
    ):
        super().__init__(
            model_backend_name="gemini",  # used as LiteLLM model prefix
            provider_config=provider.config,
            prompt_template=prompt_template,
        )