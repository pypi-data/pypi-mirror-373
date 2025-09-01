import os
import re
from typing import Any, Dict, Iterator, List

from pydantic import BaseModel, Field


class EnvVariableNotFound(Exception):
    """Custom exception raised when an environment variable is not found."""

    def __init__(self, env_var: str):
        super().__init__(f"Environment variable '{env_var}' not found!")


class ProviderVars(BaseModel):
    """
    Holds a list of dictionaries where values may include `{{env.ENV_NAME}}` placeholders.
    """

    vars: List[Dict[str, Any]] = Field(
        description="List of key-value dictionaries that may include environment variable placeholders",
        default_factory=list,
    )


class ProviderVarsBuilder:
    """
    Resolves environment variables in a ProviderVars object.
    - If an `{{env.ENV_NAME}}` variable is not found, raises `EnvVariableNotFound`.
    """

    ENV_PATTERN = re.compile(r"{{env\.([A-Za-z_][A-Za-z0-9_]*)}}")

    def __init__(self, provider_vars: ProviderVars):
        """
        Initializes the resolver with a ProviderVars instance.
        """
        self.provider_vars = provider_vars

    def build(self) -> Iterator[Dict[str, Any]]:
        """
        Resolves environment variables in each dictionary inside `provider_vars.vars`
        and yields fully resolved dictionaries.
        """
        var_dict = self.provider_vars.vars
        resolved_dict = {
            key: self._resolve_value(value) for key, value in var_dict.items()
        }
        yield resolved_dict  # Yield the whole resolved dictionary

    def _resolve_value(self, value: Any) -> Any:
        """
        Replaces `{{env.ENV_NAME}}` placeholders with actual environment values or raises an error if not found.
        """
        if isinstance(value, str):
            matches = self.ENV_PATTERN.findall(value)
            for match in matches:
                env_value = os.getenv(match)
                if env_value is None:
                    raise EnvVariableNotFound(
                        match
                    )  # Raise exception if env variable is missing
                value = value.replace(f"{{{{env.{match}}}}}", env_value)

        return value


# Example Usage
if __name__ == "__main__":
    os.environ["BASE_URL"] = "https://api.example.com"  # Set environment variable
    os.environ["API_KEY"] = "super-secret-key"  # Set another environment variable

    example_vars = ProviderVars(
        vars=[
            {"api_url": "{{env.BASE_URL}}/v1", "token": "{{env.API_KEY}}"},
            {"debug": "true", "log_level": "info"},
            {"service_url": "{{env.BASE_URL}}/service"},
        ]
    )

    resolver = ProviderVarsBuilder(example_vars)

    try:
        resolved_vars = resolver.build()
        for resolved in resolved_vars:
            print(resolved)  # Prints resolved dictionaries
    except EnvVariableNotFound as e:
        print(f"Error: {e}")  # Prints error if any environment variable is missing
