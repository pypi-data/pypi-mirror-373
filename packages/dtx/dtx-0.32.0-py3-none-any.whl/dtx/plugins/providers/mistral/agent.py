from dtx_models.providers.mistral import MistralProvider
from dtx_models.template.prompts.base import BasePromptTemplateRepo
from ..base.agent import BaseCustomLiteLLMAgent


class MistralAgent(BaseCustomLiteLLMAgent):
    def __init__(
        self,
        provider: MistralProvider,
        prompt_template: BasePromptTemplateRepo = None,
    ):
        super().__init__(
            model_backend_name="mistral",  # used as LiteLLM model prefix
            provider_config=provider.config,
            prompt_template=prompt_template,
        )