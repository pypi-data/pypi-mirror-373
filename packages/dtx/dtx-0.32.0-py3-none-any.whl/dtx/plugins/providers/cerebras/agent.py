from dtx_models.providers.cerebras import CerebrasProvider
from dtx_models.template.prompts.base import BasePromptTemplateRepo
from ..base.agent import BaseCustomLiteLLMAgent


class CerebrasAgent(BaseCustomLiteLLMAgent):
    def __init__(
        self,
        provider: CerebrasProvider,
        prompt_template: BasePromptTemplateRepo = None,
    ):
        super().__init__(
            model_backend_name="cerebras",  # used as LiteLLM model prefix
            provider_config=provider.config,
            prompt_template=prompt_template,
        )