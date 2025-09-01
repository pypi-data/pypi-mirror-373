import importlib.util
import os
from typing import Any, Callable, Dict, Optional, Union

from dtx.plugins.providers.http.exceptions import (
    FileLoadingError,
    InlineFunctionEvaluationError,
    InvalidTransformResponseError,
    StringExpressionEvaluationError,
)


class ResponseParser:
    """
    Handles transformation of API responses.

    Supported Transformations:
    1. **String-Based Expression Evaluation**
       - Example: `'json.choices[0].message.content'`
    2. **Inline Python Lambda Function**
       - Example: `'lambda json, text, context: json["message"].upper()'`
    3. **File-Based Response Transformation**
       - Example: `'file://path/to/parser.py:function_name'`
    4. **Direct Function Call**
       - Example: `lambda json, text, context: json.get("output", text)`

    Usage:
    ```python
    parser = ResponseParser('json["message"].upper()')
    parsed_response = parser.apply_parser({"message": "hello"}, "hello", {})
    print(parsed_response)  # Output: "HELLO"
    ```

    Attributes:
        transform_response (Optional[Union[str, Callable]]): The transformation logic.
    """

    def __init__(self, transform_response: Optional[Union[str, Callable]]):
        """
        Initializes the response parser.

        Args:
            transform_response: A string expression, function, or file path defining the transformation logic.

        Raises:
            InvalidTransformResponseError: If transform_response is not a string, function, or None.
        """
        if not isinstance(transform_response, (str, Callable, type(None))):
            raise InvalidTransformResponseError(
                "transform_response must be a string, function, or None."
            )

        self.transform_response = transform_response

    def apply_parser(
        self, response_json: Dict[str, Any], response_text: str, context: Dict[str, Any]
    ) -> Any:
        """
        Applies the response transformation to extract relevant data.

        Args:
            response_json: Parsed JSON response.
            response_text: Raw text response.
            context: Additional response metadata (e.g., headers, status).

        Returns:
            The transformed response.

        Raises:
            StringExpressionEvaluationError: If there is an error evaluating a string-based expression.
            InlineFunctionEvaluationError: If an inline function evaluation fails.
            FileLoadingError: If a file-based response transformation fails.
        """
        if self.transform_response is None:
            return response_json  # No transformation applied

        if isinstance(self.transform_response, str):
            if self.transform_response.startswith("file://"):
                return self._load_from_file(
                    self.transform_response, response_json, response_text, context
                )
            if self.transform_response.startswith("lambda "):  # Inline function
                return self._evaluate_inline_function(
                    self.transform_response, response_json, response_text, context
                )
            return self._apply_string_expression(
                self.transform_response, response_json, response_text, context
            )

        if callable(self.transform_response):
            return self.transform_response(response_json, response_text, context)

        raise InvalidTransformResponseError(
            "Invalid transform_response type. Must be a string, function, or file path."
        )

    def _apply_string_expression(
        self,
        expression: str,
        response_json: Dict[str, Any],
        response_text: str,
        context: Dict[str, Any],
    ) -> Any:
        """
        Evaluates a string-based expression.

        Args:
            expression: The expression string to evaluate.
            response_json: Parsed JSON response.
            response_text: Raw text response.
            context: Additional response metadata.

        Returns:
            Extracted value based on the expression.

        Raises:
            StringExpressionEvaluationError: If an error occurs during evaluation.
        """
        try:
            # Support json/text/context variables
            local_vars = {
                "json": response_json,
                "text": response_text,
                "context": context,
            }
            return eval(expression, {}, local_vars)
        except Exception as e:
            raise StringExpressionEvaluationError(
                f"Error evaluating transformResponse expression: {e}"
            )

    def _evaluate_inline_function(
        self,
        function_str: str,
        response_json: Dict[str, Any],
        response_text: str,
        context: Dict[str, Any],
    ) -> Any:
        """
        Evaluates an inline function.

        Args:
            function_str: The function definition as a string.
            response_json: Parsed JSON response.
            response_text: Raw text response.
            context: Additional response metadata.

        Returns:
            The transformed response.

        Raises:
            InlineFunctionEvaluationError: If an error occurs while evaluating the function.
        """
        try:
            exec(f"transform_fn = {function_str}", {}, locals())
            return locals()["transform_fn"](response_json, response_text, context)
        except Exception as e:
            raise InlineFunctionEvaluationError(
                f"Error evaluating inline function transformResponse: {e}"
            )

    def _load_from_file(
        self,
        file_path: str,
        response_json: Dict[str, Any],
        response_text: str,
        context: Dict[str, Any],
    ) -> Any:
        """
        Loads a transformation function from a Python file.

        Args:
            file_path: The file path (e.g., "file://path/to/parser.py:functionName").
            response_json: Parsed JSON response.
            response_text: Raw text response.
            context: Additional response metadata.

        Returns:
            The transformed response.

        Raises:
            FileLoadingError: If the file cannot be loaded or the function does not exist.
        """
        file_path = file_path.replace("file://", "")

        if ":" in file_path:
            file_path, function_name = file_path.split(":")
        else:
            function_name = "parse_response"

        if not os.path.exists(file_path):
            raise FileLoadingError(f"Response parser file '{file_path}' not found.")

        try:
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            raise FileLoadingError(f"Error loading file '{file_path}': {e}")

        if not hasattr(module, function_name):
            raise FileLoadingError(
                f"Function '{function_name}' not found in '{file_path}'."
            )

        transform_function: Callable[[Dict[str, Any], str, Dict[str, Any]], Any] = (
            getattr(module, function_name)
        )
        return transform_function(response_json, response_text, context)


# Example Usage
if __name__ == "__main__":
    # Example 1: String-Based Expression
    parser1 = ResponseParser('json["message"].upper()')
    print(parser1.apply_parser({"message": "hello"}, "hello", {}))  # Output: "HELLO"

    # Example 2: Inline Lambda Function
    parser2 = ResponseParser("lambda json, text, context: json['content'].split()[0]")
    print(
        parser2.apply_parser({"content": "Hello world!"}, "Hello world!", {})
    )  # Output: "Hello"

    # Example 3: File-Based Response Transformation (Assumes `parser.py` exists with `parse_response` function)
    # parser3 = ResponseParser("file://parser.py:parse_response")
    # print(parser3.apply_parser({"data": "test"}, "test", {}))

    # Example 4: Direct Function Call
    def custom_parser(json_data, text, context):
        return {"processed": json_data.get("output", text)}

    parser4 = ResponseParser(custom_parser)
    print(parser4.apply_parser({"output": "Processed response"}, "Raw response", {}))
    # Output: {'processed': 'Processed response'}
