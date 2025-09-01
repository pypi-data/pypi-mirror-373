from dtx.core.builders.provider_vars import ProviderVarsBuilder
from dtx_models.repo.models import ModelRegistry, ModelNotFoundError
from dtx_models.providers.base import ProviderType
from dtx_models.providers.litellm import LitellmProvider, LitellmProviderConfig
from dtx_models.providers.ollama import OllamaProvider, OllamaProviderConfig
from dtx_models.providers.openai import OpenaiProvider, OpenaiProviderConfig
from dtx_models.providers.groq import GroqProvider, GroqProviderConfig
from dtx_models.providers.anthropic import AnthropicProvider
from dtx_models.providers.mistral import MistralProvider
from dtx_models.providers.gemini import GeminiProvider
from dtx_models.providers.cerebras import CerebrasProvider
from dtx_models.scope import RedTeamScope
from dtx.plugins.providers.dummy.echo import EchoAgent
from dtx.plugins.providers.eliza.agent import ElizaAgent
from dtx.plugins.providers.gradio.agent import GradioAgent
from dtx.plugins.providers.http.agent import HttpAgent
from dtx.plugins.providers.litellm.agent import LitellmAgent
from dtx.plugins.providers.ollama.agent import OllamaAgent
from dtx.plugins.providers.openai.agent import OpenAIAgent
from dtx.plugins.providers.groq.agent import GroqAgent
from dtx.plugins.providers.anthropic.agent import AnthropicAgent
from dtx.plugins.providers.mistral.agent import MistralAgent
from dtx.plugins.providers.gemini.agent import GeminiAgent
from dtx.plugins.providers.cerebras.agent import CerebrasAgent


class ProviderFactory:
    """
    Factory class responsible for creating provider agent instances
    based on the given provider type and model configuration.
    Supports multiple provider types including OpenAI, Ollama, LiteLLM, HF, etc.
    """

    def __init__(self, load_env_vars=False):
        """
        :param load_env_vars: Flag to indicate if env variables should be loaded
                              into provider configs automatically.
        """
        self._load_env_vars = load_env_vars

    def _build_env_vars(self, scope):
        """
        Extracts environment variable dictionary from scope.
        Only the first environment is considered (if available).

        :param scope: RedTeamScope
        :return: dict of environment variables
        """
        env_vars = {}
        if scope.environments:
            env_vars = next(ProviderVarsBuilder(scope.environments[0]).build(), {})
        return env_vars

    def get_agent(
        self,
        scope: RedTeamScope,
        provider_type: ProviderType,
        url: str = "",
    ):
        """
        Main factory method to return a configured Agent for the requested provider.

        :param scope: RedTeamScope containing prompt, environment, and provider info.
        :param provider_type: Enum value indicating provider type (e.g., OPENAI, OLLAMA).
        :param url: The model name or endpoint identifier for the provider.
        :return: Instantiated and configured Agent
        """
        from dtx.config import globals
        from dtx.plugins.providers.hf.agent import HFAgent

        # ---- INIT registry once -----
        model_registry = ModelRegistry()

        # Handle local dummy providers
        if provider_type == ProviderType.ECHO:
            return EchoAgent()

        elif provider_type == ProviderType.ELIZA:
            return ElizaAgent(url)

        # Handle HuggingFace inference models
        elif provider_type == ProviderType.HF:
            model = globals.get_llm_models().get_huggingface_model(url)
            return HFAgent(model)

        # Handle external HTTP-based LLM agents
        elif provider_type == ProviderType.HTTP:
            env_vars = self._build_env_vars(scope)
            return HttpAgent(provider=scope.providers[0], vars=env_vars)

        # Gradio-hosted models
        elif provider_type == ProviderType.GRADIO:
            env_vars = self._build_env_vars(scope)
            return GradioAgent(provider=scope.providers[0], vars=env_vars)

        # Ollama (local LLM runner)
        elif provider_type == ProviderType.OLLAMA:
            config = OllamaProviderConfig(model=url)
            if self._load_env_vars:
                config.load_from_env()  # Load local endpoint from env (if set)
            provider = OllamaProvider(config=config)
            return OllamaAgent(provider)

        # OpenAI API (e.g., gpt-4o, gpt-3.5-turbo)
        elif provider_type == ProviderType.OPENAI:
            config = OpenaiProviderConfig(model=url)
            if self._load_env_vars:
                config.load_from_env()  # Load API key & endpoint
            provider = OpenaiProvider(config=config)

            prompt_template = scope.prompts[0] if scope.prompts else None
            return OpenAIAgent(provider, prompt_template=prompt_template)

        # LiteLLM gateway (routes to OpenAI, Groq, etc.)
        elif provider_type == ProviderType.LITE_LLM:
            prompt_template = scope.prompts[0] if scope.prompts else None
            config = LitellmProviderConfig(model=url)

            if self._load_env_vars:
                config.load_from_env()  # Determine upstream provider and apply env vars

            provider = LitellmProvider(config=config)
            return LitellmAgent(provider, prompt_template=prompt_template)

        # Placeholder for potential future Groq integration
        elif provider_type == ProviderType.GROQ:
            config = GroqProviderConfig(model=url)
            if self._load_env_vars:
                config.load_from_env()  # Determine upstream provider and apply env vars

            provider = GroqProvider(config=config)
            return GroqAgent(provider)
        
        # Handle case when the selected provider is Anthropic
        elif provider_type == ProviderType.ANTHROPIC:
            try:
                config = model_registry.get_model(url, provider="anthropic")
            except ModelNotFoundError:
                mistral_models = model_registry.get_all_models_by_provider(provider="gemini")
                available_model_names = [model.model for model in mistral_models]
                raise ValueError(
                    f"[MISTRAL] Model '{url}' is not registered!\n"
                    f"Available Mistral Models: {available_model_names}"
                )
            if self._load_env_vars:
                config.load_from_env()   # Loads ANTHROPIC_API_KEY from env
            
            provider = AnthropicProvider(config=config)
            return AnthropicAgent(provider)
        
        # Handle case when the selected provider is Mistral
        elif provider_type == ProviderType.MISTRAL:
            try:
                config = model_registry.get_model(url, provider="mistral")
            except ModelNotFoundError:
                mistral_models = model_registry.get_all_models_by_provider(provider="gemini")
                available_model_names = [model.model for model in mistral_models]
                raise ValueError(
                    f"[MISTRAL] Model '{url}' is not registered!\n"
                    f"Available Mistral Models: {available_model_names}"
                )
            if self._load_env_vars:
                config.load_from_env()    # Loads MISTRAL_API_KEY from env
            provider = MistralProvider(config=config)
            return MistralAgent(provider)
        
        # Handle case when the selected provider is Gemini 
        elif provider_type == ProviderType.GEMINI:
            try:
                config = model_registry.get_model(url, provider="gemini")
            except ModelNotFoundError:
                mistral_models = model_registry.get_all_models_by_provider(provider="gemini")
                available_model_names = [model.model for model in mistral_models]
                raise ValueError(
                    f"[MISTRAL] Model '{url}' is not registered!\n"
                    f"Available Mistral Models: {available_model_names}"
                )
            if self._load_env_vars:
                config.load_from_env()    # Loads GEMINI_API_KEY from env
            provider = GeminiProvider(config=config)
            return GeminiAgent(provider)
        
        # Handle case when the selected provider is Cerebras 
        elif provider_type == ProviderType.CEREBRAS:
            try:
                config = model_registry.get_model(url, provider="cerebras")
            except ModelNotFoundError:
                mistral_models = model_registry.get_all_models_by_provider(provider="cerebras")
                available_model_names = [model.model for model in mistral_models]
                raise ValueError(
                    f"[MISTRAL] Model '{url}' is not registered!\n"
                    f"Available Mistral Models: {available_model_names}"
                )
            if self._load_env_vars:
                config.load_from_env()    # Loads CEREBRAS_API_KEY from env
            provider = CerebrasProvider(config=config)
            return CerebrasAgent(provider)

        # Fallback for unsupported provider types
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")
