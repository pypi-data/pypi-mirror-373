import json
from typing import Dict, Optional, Tuple, Union

from dtx.plugins.providers.http.exceptions import (
    HttpRequestParsingError,
    InvalidHttpMethodError,
    InvalidHttpRequestFormatError,
    InvalidJsonBodyError,
    MissingHostHeaderError,
)
from dtx.plugins.providers.http.utils.headers import HeaderUtils


class RawHttpRequestParser:
    """
    Parses raw HTTP requests, handling:
    - JSON requests (`application/json`)
    - Form-encoded requests (`application/x-www-form-urlencoded`) (returns raw string)
    - Multipart form-data requests (`multipart/form-data`) (returns raw string)

    Usage:
    ```
    raw_request = b"POST /v1/completions HTTP/1.1\r\nHost: api.example.com\r\nContent-Type: application/json\r\n\r\n{\"prompt\": \"Hello\"}"

    parser = RawHttpRequestParser()
    method, url, headers, body = parser.parse(raw_request, use_https=True)
    ```
    """

    def parse(
        self, raw_request: Union[bytes, str], use_https: bool = True
    ) -> Tuple[str, str, Dict[str, str], Optional[Union[str, Dict]]]:
        """
        Parses the raw HTTP request.

        Args:
            raw_request (bytes | str): The raw HTTP request data.
            use_https (bool): Whether to use HTTPS (`True`) or HTTP (`False`) in the URL.

        Returns:
            Tuple:
                - method (str): HTTP method (e.g., "POST", "GET").
                - url (str): Full request URL (e.g., "https://api.example.com/v1/completions").
                - headers (dict): Parsed headers as a case-sensitive dictionary.
                - body (dict | str | None): JSON-parsed body (if present) or raw string.

        Raises:
            InvalidHttpRequestFormatError: If the raw request is empty.
            InvalidHttpRequestFormatError: If the request format is incorrect.
            InvalidHttpMethodError: If an invalid HTTP method is used.
            MissingHostHeaderError: If the Host header is missing.
            InvalidJsonBodyError: If the body contains invalid JSON.
        """
        if not raw_request:
            raise InvalidHttpRequestFormatError("The raw HTTP request is empty.")

        # Decode bytes to string if necessary
        if isinstance(raw_request, bytes):
            raw_request = raw_request.decode("utf-8").strip()
        else:
            raw_request = raw_request.strip()

        # Normalize line endings
        raw_request = raw_request.replace("\r\n", "\n")

        # Split request into headers and body
        parts = raw_request.split("\n\n", 1)
        headers_section = parts[0]
        body_section = parts[1] if len(parts) > 1 else ""

        # Extract request line (ensure it's valid)
        header_lines = headers_section.split("\n")
        if not header_lines or len(header_lines[0].split()) < 3:
            raise InvalidHttpRequestFormatError(
                "Invalid or missing request line in HTTP request."
            )

        request_line_parts = header_lines[0].split()
        method, path, http_version = request_line_parts[:3]
        method = method.upper()

        # Validate method (only if request format is valid)
        if method not in {"GET", "POST", "PUT", "DELETE", "PATCH"}:
            raise InvalidHttpMethodError(f"Invalid HTTP method: {method}")

        # Parse headers while maintaining case sensitivity
        headers_dict = {}
        for line in header_lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                headers_dict[key.strip()] = value.strip()  # Preserve original key case

        # Wrap headers with HeaderUtils for case-insensitive lookup
        headers = HeaderUtils(headers_dict)

        # Extract Host header for constructing full URL
        host = headers.get("Host")
        if not host:
            raise MissingHostHeaderError("Missing 'Host' header in raw HTTP request.")

        scheme = "https://" if use_https else "http://"
        full_url = f"{scheme}{host}{path}"

        # Parse body
        body = None
        if body_section:
            if headers.is_json():  # Use HeaderUtils method for JSON check
                try:
                    body = json.loads(body_section)
                except json.JSONDecodeError:
                    raise InvalidJsonBodyError(
                        "Invalid JSON body format in raw HTTP request."
                    )
            else:
                body = body_section  # Keep raw string for non-JSON content

        return method, full_url, headers_dict, body


# Example Usage
if __name__ == "__main__":
    raw_request = b"""
POST /v1/completions HTTP/1.1
Host: api.example.com
Content-Type: application/json

{"prompt": "Hello, world!", "max_tokens": 100}
    """

    parser = RawHttpRequestParser()
    try:
        method, url, headers, body = parser.parse(raw_request, use_https=True)

        print("Method:", method)  # "POST"
        print("URL:", url)  # "https://api.example.com/v1/completions"
        print("Headers:", headers)  # Dictionary with case-sensitive keys
        print("Content-Type:", headers.get("Content-Type"))  # "application/json"
        print("Is JSON Content-Type:", HeaderUtils(headers).is_json())  # True
        print("Body:", body)  # {'prompt': 'Hello, world!', 'max_tokens': 100}

    except HttpRequestParsingError as e:
        print(f"Error parsing request: {e}")
