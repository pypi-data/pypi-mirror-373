from dtx_models.providers.groq import GroqProvider
from dtx_models.template.prompts.base import BasePromptTemplateRepo
from ..base.agent import BaseCustomLiteLLMAgent  # Reusable base agent you created


class GroqAgent(BaseCustomLiteLLMAgent):
    """
    A custom DetoxIO-compatible agent that uses Groq via LiteLLM.

    This class wraps the GroqProvider and configures the LiteLLM-compatible model 
    (e.g., 'groq/llama-3.1-8b-instant') for use in the red-team evaluation pipeline.
    """

    def __init__(
        self,
        provider: GroqProvider,  # Provider containing config (model name, endpoint, API key, etc.)
        prompt_template: BasePromptTemplateRepo = None,  # Optional prompt templates
    ):
        # Initialize the base agent using the Groq backend
        super().__init__(
            model_backend_name="groq",  # Used as prefix: 'groq/<model>'
            provider_config=provider.config,  # The GroqProviderConfig instance
            prompt_template=prompt_template,
        )
