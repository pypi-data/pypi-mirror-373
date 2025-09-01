import re
from typing import Iterator, List

from dtx_models.analysis import PromptVariable
from dtx_models.prompts import BaseMultiTurnResponse, RoleType, Turn


class PromptVariableSubstitutor:
    def __init__(self, variable_sets: List[PromptVariable]):
        """
        Constructor for the PromptVariableSubstitutor.

        :param variable_sets: List of PromptVariable containing the variable names and their possible values
        """
        self.variable_sets = (
            variable_sets  # List of variable sets (PromptVariable objects)
        )

    def convert(self, prompt: str) -> Iterator[str]:
        """
        Replaces placeholders in the prompt with the corresponding values, including formats:
        - {variable_name}
        - {{variable_name}}
        - variable_name (without curly braces)

        This method returns a generator that yields the prompt with values substituted in place of the placeholders.

        :param prompt: The text prompt to apply variable replacements to
        :return: A generator that yields each modified prompt with values replaced
        """
        # Ensure that we generate one combination per value set for each placeholder
        from itertools import product

        # Create a list of all variable names and values
        replacements = [
            (variable_set.name, variable_set.values)
            for variable_set in self.variable_sets
        ]

        # Generate combinations of all possible values for each placeholder
        for value_combination in product(
            *[replacements[i][1] for i in range(len(replacements))]
        ):
            prompt_with_values = prompt
            # Replace each variable in the prompt with the respective value
            for idx, (name, value) in enumerate(
                zip([r[0] for r in replacements], value_combination)
            ):
                prompt_with_values = re.sub(
                    rf"{{{{\s*{name}\s*}}}}", value, prompt_with_values
                )  # For {{variable_name}}
                prompt_with_values = re.sub(
                    rf"{{\s*{name}\s*}}", value, prompt_with_values
                )  # For {variable_name}
                prompt_with_values = re.sub(
                    rf"\b{name}\b", value, prompt_with_values
                )  # For variable_name without braces

            yield prompt_with_values


class Str2BaseMultiTurnResponse:
    def convert(cls, prompt: str, response: str) -> BaseMultiTurnResponse:
        turns = [
            Turn(role=RoleType.USER, message=prompt),
            Turn(role=RoleType.ASSISTANT, message=response),
        ]
        return BaseMultiTurnResponse(turns=turns)
