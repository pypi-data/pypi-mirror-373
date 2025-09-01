import os

from pydantic import BaseModel, HttpUrl, field_validator


class OllamaLlamaGuardConfig(BaseModel):
    """
    Configuration class for Ollama LlamaGuard.

    Attributes:
        base_url (str): The base URL of the Ollama service.
        model_name (str): The name of the model to be used, must start with 'llama-guard'.
        temperature (float): The temperature setting for the model.
    """

    base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name: str = os.getenv("OLLAMA_MODEL_NAME", "llama-guard3:1b")
    temperature: float = float(os.getenv("OLLAMA_TEMPERATURE", 0.0))

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, value: str) -> str:
        try:
            HttpUrl(value)  # Validate the URL format
        except ValueError as e:
            raise ValueError(f"Invalid base_url: {value}") from e
        return value

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, value: str) -> str:
        if not value.startswith("llama-guard"):
            raise ValueError("model_name must start with 'llama-guard'")
        return value


class OpenAIConfig(BaseModel):
    """
    Configuration class for OpenAI API.

    Attributes:
        api_key (str): The API key for OpenAI.
        model_name (str): The name of the OpenAI model.
        temperature (float): The temperature setting for the model.
    """

    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model_name: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4")
    temperature: float = float(os.getenv("OPENAI_TEMPERATURE", 0.7))
    open_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/")
