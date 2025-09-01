import os
import random
import re
from copy import deepcopy
from typing import Callable, Dict

from dtx_models.template.prompts.base import (
    BaseMultiTurnConversation,
    BasePromptTemplateRepo,
)


class MetaPromptParamResolver:
    """
    Resolves meta-template param values.
    Supports:
    - Arbitrary text with multiple {{variable}} or {variable} placeholders
    - {{file://path/to/file.txt}} or {file://path/to/file.txt} for including file contents
    """

    # Pattern to capture anything inside {{variable}} or {variable}
    VARIABLE_PATTERN = re.compile(r"\{\{\s*(.*?)\s*\}\}|\{\s*(.*?)\s*\}")

    def __init__(self, variable_provider: Dict[str, Callable[[], str]]):
        """
        :param variable_provider: A mapping of variable names to functions that return their value.
        Example:
            {
                "prompt": lambda: last_user_prompt,
                "context": lambda: generate_random_context(),
            }
        """
        self.variable_provider = variable_provider

    def resolve(self, raw_params: Dict[str, str]) -> Dict[str, str]:
        """
        Resolves all parameters into final string values.
        """
        resolved = {}
        for param_name, raw_value in raw_params.items():
            resolved_value = self._resolve_text(raw_value)
            resolved[param_name] = resolved_value
        return resolved

    def _resolve_text(self, text: str) -> str:
        """
        Resolve all {{...}} or {...} variables inside the text.
        """

        def replace(match):
            # match.group(1) is for {{...}}, group(2) is for {...}
            variable_content = (match.group(1) or match.group(2)).strip()

            # Handle file includes
            if variable_content.startswith("file://"):
                return self._load_file(variable_content[len("file://") :])

            # Handle known variables from the provider
            if variable_content in self.variable_provider:
                return self.variable_provider[variable_content]()

            raise ValueError(f"Unknown variable: '{{ {variable_content} }}'")

        return self.VARIABLE_PATTERN.sub(replace, text)

    def _load_file(self, filepath: str) -> str:
        """
        Load file contents safely.
        """
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()


class PromptTemplateResolver:
    """
    Translates a prompt template repository into a conversation with injected parameters.
    Requires a BasePromptTemplateRepo (like LangHubPromptTemplate).
    """

    def __init__(self, template_repo: BasePromptTemplateRepo):
        if not isinstance(template_repo, BasePromptTemplateRepo):
            raise TypeError(
                f"PromptTemplateResolver expects an instance of BasePromptTemplateRepo, got {type(template_repo).__name__}"
            )
        self.template_repo = template_repo
        self.template = template_repo.get_template()

    def convert(
        self, conversation: BaseMultiTurnConversation
    ) -> BaseMultiTurnConversation:
        last_user_prompt = conversation.last_user_prompt()

        variable_provider = {
            "prompt": lambda: last_user_prompt,
            "context": self._generate_random_context,
        }

        resolver = MetaPromptParamResolver(variable_provider)

        raw_params = self._extract_raw_params()
        resolved_params = resolver.resolve(raw_params)

        new_conversation = deepcopy(self.template.conversation)

        for turn in new_conversation.turns:
            turn.message = self._inject_params_into_text(turn.message, resolved_params)

        return new_conversation

    def _extract_raw_params(self) -> Dict[str, str]:
        params = {}
        param_list = self.template_repo.get_params() or []
        for param in param_list:
            params[param.name] = str(param.value)
        return params

    def _inject_params_into_text(self, text: str, params: Dict[str, str]) -> str:
        import re

        def replacer(match):
            var_name = match.group(1) or match.group(2)
            var_name = var_name.strip()
            if var_name in params:
                return params[var_name]
            raise ValueError(f"Missing value for template variable: '{var_name}'")

        # Match both {param} and {{param}}
        pattern = re.compile(r"\{\{\s*(\w+)\s*\}\}|\{\s*(\w+)\s*\}")

        return pattern.sub(replacer, text)

    def _generate_random_context(self) -> str:
        sample_contexts = [
            "The capital of France is Paris.",
            "Water boils at 100 degrees Celsius.",
            "The sun rises in the east and sets in the west.",
            "OpenAI developed ChatGPT for natural language understanding.",
            "Python is a popular programming language for AI and data science.",
        ]
        return random.choice(sample_contexts)
