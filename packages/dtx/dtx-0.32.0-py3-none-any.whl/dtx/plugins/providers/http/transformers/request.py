import importlib
import importlib.util
import json
import os
from copy import deepcopy
from typing import Any, Callable, Dict, Union

from jinja2 import Template


class RequestTransformer:
    """
    Handles request transformation in two steps:

    1. **First, transform the 'prompt' value in `vars`** using Jinja2, lambda, or file.
    2. **Then, replace placeholders in `transform_request` using the updated `vars`**.

    Supports:
    - **Jinja2 Template Strings** (`'{"text": "{{prompt}}"}'`)
    - **Lambda Functions** (`'lambda prompt: {...}'`)
    - **File-Based Transformations** (`'file://path/to/file.py'`)
    """

    def __init__(self, transform_request: str, vars: Dict[str, Any]):
        """
        Initializes the transformer.

        Args:
            transform_request (str): Jinja2 string template, lambda function, or file path.
            vars (Dict[str, Any]): Variables for placeholder replacement.
        """
        self.vars = deepcopy(vars) or {}
        self.transform_request = (
            transform_request if transform_request else "{{ prompt }}"
        )
        self._transform_vars()

    def _transform_vars(self) -> None:
        """Applies transformation to `prompt` in `vars`."""
        if "prompt" not in self.vars:
            raise KeyError("vars dictionary must contain a 'prompt' key.")

        transformed_prompt = self._transform_prompt(self.vars["prompt"])

        # If the transformation result is a string, attempt to convert it to JSON
        if isinstance(transformed_prompt, str):
            try:
                transformed_prompt = json.loads(transformed_prompt)
            except json.JSONDecodeError:
                pass  # Keep it as a string if it's not valid JSON

        # Store the transformed result
        self.vars["prompt"] = transformed_prompt

    def _transform_prompt(self, prompt: str) -> Union[str, Dict]:
        """Applies transformation to the `prompt` key using Jinja2, function-based, or file-based logic."""
        if self.transform_request.startswith("lambda "):
            return self._evaluate_inline_function(self.transform_request, prompt)

        if self.transform_request.startswith("file://"):
            return self._load_from_file(self.transform_request, prompt)

        return self._apply_string_template(self.transform_request, prompt=prompt)

    def _load_from_file(self, file_path: str, prompt: str) -> str:
        """Loads a transformation function from a Python file."""
        file_path = file_path.replace("file://", "")

        if ":" in file_path:  # Specified function in the file
            file_path, function_name = file_path.split(":")
        else:
            function_name = "transform_request"

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Transform file '{file_path}' not found.")

        # Dynamically load the module
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, function_name):
            raise AttributeError(
                f"Function '{function_name}' not found in '{file_path}'."
            )

        transform_function: Callable[[str], Dict] = getattr(module, function_name)
        return json.dumps(transform_function(prompt))  # Pass only prompt

    def _apply_string_template(self, template: str, **kwargs) -> str:
        """Applies Jinja2 template transformation on a string."""
        if not template.strip():  # If template is empty, return prompt as-is
            return kwargs.get("prompt", "")

        try:
            template_obj = Template(template)
            result = template_obj.render(**{**self.vars, **kwargs})

            # Ensure correct JSON output for nested objects
            try:
                return json.loads(result)  # Convert to JSON if it's valid
            except json.JSONDecodeError:
                return result  # Otherwise, return as a string
        except Exception as e:
            raise ValueError(f"Error in string template transformation: {e}")

    def _evaluate_inline_function(self, function_str: str, prompt: str) -> Dict:
        """Evaluates an inline Python lambda function."""
        try:
            local_vars = {
                "prompt": str(prompt),
                "json": json,
            }  # Ensure prompt is string
            exec(f"transform_fn = {function_str}", {}, local_vars)
            return local_vars["transform_fn"](local_vars["prompt"])  # Execute function
        except Exception as e:
            raise ValueError(f"Error in inline function transformation: {e}")

    def apply_transform_dict_any(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively applies transformation to a dictionary, handling lists, dicts, and strings."""

        def transform(value):
            if isinstance(value, str):
                return self._apply_string_template(value)
            elif isinstance(value, dict):
                return self.apply_transform_dict_any(
                    value
                )  # Recursively transform dictionaries
            elif isinstance(value, list):
                return [
                    transform(item) for item in value
                ]  # Recursively transform lists
            return value  # Return other types (int, float, bool, None) as is

        return {key: transform(value) for key, value in data.items()}

    def apply_transform_str(self, data: str) -> str:
        """Applies transformation to a string using Jinja2."""
        return self._apply_string_template(data)

    def apply_transform_dict_str(self, data: Dict[str, str]) -> Dict[str, str]:
        """Applies transformation to a dictionary with string values."""
        return {key: self._apply_string_template(value) for key, value in data.items()}


# ✅ **Example Usage**
if __name__ == "__main__":
    transformer1 = RequestTransformer(
        '{"text": "{{prompt }}"}', {"prompt": "Hello, World!"}
    )
    print(transformer1.vars)  # {"prompt": {"text": "Hello, World!"}}

    transformer2 = RequestTransformer(
        '{"message": "{{prompt }}", "user": "{{user}}"}',
        {"prompt": "Hi", "user": "Alice"},
    )
    print(transformer2.vars)  # {"prompt": {"message": "Hi", "user": "Alice"}}

    transformer3 = RequestTransformer(
        "lambda prompt: {'text': prompt.upper(), 'timestamp': 1710792984000}",
        {"prompt": "Hello"},
    )
    print(
        transformer3.vars
    )  # {"prompt": {"text": "HELLO", "timestamp": 1710792984000}}

    print(
        transformer1.apply_transform_str("Hello, {{prompt}}!")
    )  # "Hello, Hello, World!!"

    print(
        transformer2.apply_transform_dict_str(
            {"greeting": "Hey, {{user}}!", "message": "{{prompt}}"}
        )
    )
    # {'greeting': 'Hey, Alice!', 'message': {'message': 'Hi', 'user': 'Alice'}}

    body = {
        "message": {"text": "{{prompt | tojson}}", "length": 12},
        "metadata": {"created_by": "{{user}}"},
    }
    print(transformer1.apply_transform_dict_any(body))
    # {"message": {"text": {"text": "Hello, World!"}, "length": 12}, "metadata": {"created_by": "Alice"}}
