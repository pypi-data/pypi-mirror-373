import datetime
import importlib.util
from typing import Callable, Optional, Union

import requests

from dtx.core import logging
from dtx.plugins.providers.http.exceptions import (
    InvalidHttpResponseError,
    StringExpressionEvaluationError,
)

logger = logging.getLogger(__name__)


class HttpResponseValidator:
    """
    Handles validation of HTTP responses.

    Supports:
    - **Function-based validation** (`lambda response: response.status_code < 500`)
    - **String-based validation** (`"status >= 200 and status < 300"`)
    - **File-based validation** (`"file://path/to/validator.py:function_name"`)

    Usage:
    ```python
    validator = HttpResponseValidator(lambda response: response.status_code < 500)
    validator.validate(response)  # ✅ Valid
    ```
    """

    def __init__(
        self, validation_rule: Optional[Union[str, Callable[[requests.Response], bool]]]
    ):
        """
        Initializes the response validator.

        Args:
            validation_rule: Function, string, or file reference for validation.
        """
        self.validation_rule = validation_rule

        if validation_rule is None:
            logger.debug(
                "No validation rule provided. Defaulting to accept all responses."
            )
            self.validation_function = lambda response: True
        elif isinstance(validation_rule, str):
            if validation_rule.startswith("file://"):
                self.validation_function = self._load_from_file(validation_rule)
            else:
                self.validation_function = self._create_lambda(validation_rule)
        elif callable(validation_rule):
            self.validation_function = validation_rule
        else:
            raise ValueError(
                "Invalid validate_response type. Must be a string or function."
            )

    def validate(self, response: requests.Response) -> bool:
        """
        Validates the HTTP response.

        Args:
            response (requests.Response): The HTTP response object.

        Returns:
            bool: True if response is valid, raises `InvalidHttpResponseError` otherwise.
        """
        if self.validation_rule is None:
            return True  # Accept all responses if no validation rule is set

        try:
            if self.validation_function(response):
                return True
        except Exception as e:
            logger.error(f"Error in validation function: {e}")
            raise InvalidHttpResponseError(
                f"Error in response validation function: {e}"
            )

        return False

    def _create_lambda(self, expression: str) -> Callable[[requests.Response], bool]:
        """
        Converts a string-based validation rule into a lambda function.
        """
        try:
            return lambda response: eval(
                expression,
                {},
                {
                    "status": response.status_code,
                    "headers": response.headers,
                    "body": (
                        response.json()
                        if "application/json"
                        in response.headers.get("Content-Type", "").lower()
                        else {}
                    ),
                    "elapsed": response.elapsed.total_seconds()
                    if isinstance(response.elapsed, datetime.timedelta)
                    else response.elapsed,
                },
            )
        except Exception as e:
            raise StringExpressionEvaluationError(
                f"Invalid response validation expression: {e}"
            )

    def _load_from_file(self, file_path: str) -> Callable[[requests.Response], bool]:
        """
        Loads a validation function from an external Python file.

        Args:
            file_path (str): File path with optional function name (e.g., `"file://path/to/validator.py:function"`).

        Returns:
            Callable[[requests.Response], bool]: The loaded function.
        """
        file_path = file_path.replace("file://", "")

        if ":" in file_path:
            file_path, function_name = file_path.split(":")
        else:
            function_name = "validate_response"

        try:
            module_name = file_path.split("/")[-1].replace(".py", "")
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            raise ValueError(f"Error loading validation function from file: {e}")

        if not hasattr(module, function_name):
            raise ValueError(f"Function '{function_name}' not found in '{file_path}'.")

        return getattr(module, function_name)


# Example Usage
if __name__ == "__main__":
    import requests
    from requests.models import Response

    # Simulate an HTTP response
    mock_response = Response()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response._content = b'{"message": "Success"}'
    mock_response.elapsed = datetime.timedelta(seconds=1.2)  # Simulated response time

    print("Mock Response:", mock_response.status_code, mock_response.headers)

    # Example 1: Validate status code (should pass)
    validator1 = HttpResponseValidator("status == 200")
    try:
        print("Validation Passed:", validator1.validate(mock_response))
    except InvalidHttpResponseError:
        print("Validation Failed!")

    # Example 2: Validate status code (should fail)
    validator2 = HttpResponseValidator("status == 500")
    try:
        print("Validation Passed:", validator2.validate(mock_response))
    except InvalidHttpResponseError:
        print("Validation Failed!")

    # Example 3: Validate response time (should pass)
    validator3 = HttpResponseValidator("elapsed.total_seconds() < 2")
    try:
        print("Validation Passed:", validator3.validate(mock_response))
    except InvalidHttpResponseError:
        print("Validation Failed!")

    # Example 4: Validate headers (should pass)
    validator4 = HttpResponseValidator("headers['Content-Type'] == 'application/json'")
    try:
        print("Validation Passed:", validator4.validate(mock_response))
    except InvalidHttpResponseError:
        print("Validation Failed!")

    # Example 5: Validate headers (should fail)
    validator5 = HttpResponseValidator("headers['Content-Type'] == 'text/html'")
    try:
        print("Validation Passed:", validator5.validate(mock_response))
    except InvalidHttpResponseError:
        print("Validation Failed!")

    # Example 6: Validate response body (should pass)
    validator6 = HttpResponseValidator("body['message'] == 'Success'")
    try:
        print("Validation Passed:", validator6.validate(mock_response))
    except InvalidHttpResponseError:
        print("Validation Failed!")

    # Example 7: File-based validation (Assume external file `validator.py` exists)
    # validator7 = HttpResponseValidator("file://path/to/validator.py:validate_response")
    # try:
    #     print("Validation Passed:", validator7.validate(mock_response))
    # except InvalidHttpResponseError:
    #     print("Validation Failed!")
