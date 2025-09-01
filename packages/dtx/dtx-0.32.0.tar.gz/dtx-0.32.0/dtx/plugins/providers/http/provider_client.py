import json
import time
from typing import Any, Dict, Optional, Type

import requests

from dtx.core import logging
from dtx_models.providers.http import (
    HttpProvider,
    RawHttpProviderConfig,
    StructuredHttpProviderConfig,
)
from dtx.plugins.providers.http.exceptions import (
    HttpRequestFailedError,
    HttpResponseValidationError,
)
from dtx.plugins.providers.http.parsers.raw_http import RawHttpRequestParser
from dtx.plugins.providers.http.transformers.request import RequestTransformer
from dtx.plugins.providers.http.transformers.response import ResponseParser
from dtx.plugins.providers.http.validators.response import HttpResponseValidator

# Configure logging
logger = logging.getLogger(__name__)


class HttpRequestSender:
    """
    Handles HTTP requests with retry logic for rate-limiting and transient errors.
    """

    def __init__(self, session: Optional[requests.Session] = None):
        """Initializes the HTTP request sender."""
        self.session = session or requests.Session()

    def send_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        body: Optional[Any],
        max_retries: int,
    ) -> requests.Response:
        """Sends an HTTP request with retry logic."""
        retries = 0

        # --- sanitize header values ---
        headers = {str(k): str(v) for k, v in (headers or {}).items()}
        # Let requests compute Content-Length (avoid mismatches)
        headers.pop("Content-Length", None)
        headers.pop("content-length", None)

        while retries <= max_retries:
            try:
                logger.debug(f"Sending request: {method} {url} (Attempt {retries + 1})")
                response = self.session.request(method, url, json=body, headers=headers)
                print(response)
                if response.status_code == 429:
                    wait_time = 2**retries
                    logger.warning(f"Rate limited (429). Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    retries += 1
                    continue

                if 500 <= response.status_code < 600:
                    wait_time = 2**retries
                    logger.warning(
                        f"Server error ({response.status_code}). Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    retries += 1
                    continue

                return response

            except (requests.RequestException, requests.ConnectionError) as e:
                logger.error(
                    f"Request failed: {e}. Retrying {retries + 1}/{max_retries}..."
                )
                time.sleep(2**retries)
                retries += 1

        logger.critical(f"Max retries exceeded for {url}")
        raise HttpRequestFailedError(f"Max retries exceeded for {url}")


class HttpProviderClient:
    """
    Stateless HTTP client that sends requests based on a given HttpProvider.
    """

    def __init__(self, request_sender: Optional[Type["HttpRequestSender"]] = None):
        """Initializes the HTTP client."""
        self.request_sender = request_sender or HttpRequestSender()

    def generate(self, provider: HttpProvider, vars: Dict[str, Any]) -> Any:
        """
        Generates and sends an HTTP request using the provided provider.

        Args:
            provider (HttpProvider): The HTTP provider configuration.
            vars (dict): Variables to replace in the request.

        Returns:
            The processed response based on transform_response.
        """
        config = provider.config

        request_transformer = RequestTransformer(
            getattr(config, "transform_request", None), vars=vars
        )
        response_parser = ResponseParser(getattr(config, "transform_response", None))
        response_validator = HttpResponseValidator(
            getattr(config, "validate_response", None)
        )

        if isinstance(config, StructuredHttpProviderConfig):
            return self._handle_structured_request(
                config, vars, request_transformer, response_parser, response_validator
            )
        elif isinstance(config, RawHttpProviderConfig):
            return self._handle_raw_request(
                config, vars, request_transformer, response_parser, response_validator
            )
        else:
            raise ValueError("Unsupported provider configuration type.")

    def _handle_structured_request(
        self,
        config: StructuredHttpProviderConfig,
        vars: Dict[str, Any],
        request_transformer: RequestTransformer,
        response_parser: ResponseParser,
        response_validator: HttpResponseValidator,
    ) -> Any:
        """Handles a structured HTTP request."""
        url = request_transformer.apply_transform_str(config.url)
        method = config.method.value
        headers = request_transformer.apply_transform_dict_str(config.headers or {})
        body = self._transform_body(config.body, vars, request_transformer)

        max_retries = getattr(config, "max_retries", 0)

        # print(method, url, headers, body, max_retries)
        response = self.request_sender.send_request(
            method, url, headers, body, max_retries
        )
        return self._process_response(response, response_parser, response_validator)

    def _handle_raw_request(
        self,
        config: RawHttpProviderConfig,
        vars: Dict[str, Any],
        request_transformer: RequestTransformer,
        response_parser: ResponseParser,
        response_validator: HttpResponseValidator,
    ) -> Any:
        """Handles a raw HTTP request using RawHttpRequestParser."""
        parser = RawHttpRequestParser()

        method, raw_url, headers_dict, body = parser.parse(
            config.raw_request, use_https=config.use_https
        )

        url = request_transformer.apply_transform_str(raw_url)
        headers = request_transformer.apply_transform_dict_str(headers_dict or {})
        body = self._transform_body(body, vars, request_transformer)

        max_retries = getattr(config, "max_retries", 4)
        # print(method, url, headers, body, max_retries)
        response = self.request_sender.send_request(
            method, url, headers, body, max_retries
        )
        return self._process_response(response, response_parser, response_validator)

    def _transform_body(
        self, body: Any, variables: Dict[str, Any], transformer: RequestTransformer
    ) -> Any:
        """Transforms the request body if applicable."""
        if isinstance(body, dict):
            return transformer.apply_transform_dict_any(body)
        elif isinstance(body, str):
            return transformer.apply_transform_str(body)
        return body

    def _process_response(
        self,
        response: requests.Response,
        parser: ResponseParser,
        validator: HttpResponseValidator,
    ) -> Any:
        """Processes and transforms the response after validation."""
        if not validator.validate(response):
            raise HttpResponseValidationError(
                "HTTP Response Validation Error as per validation expression"
            )

        try:
            response_json = response.json()
        except json.JSONDecodeError:
            response_json = None

        context = {
            "status": response.status_code,
            "headers": dict(response.headers),
        }

        return parser.apply_parser(response_json, response.text, context)


# Example Usage
if __name__ == "__main__":
    raw_request = """
    POST /evaluate/prompt/ HTTP/1.1
    Host: localhost:8000
    Content-Type: application/json
    Authorization: Bearer my_token

    {
    "texts": [
        "{{prompt}}"
    ]
    }
    """

    provider = HttpProvider(
        id="http",
        config=RawHttpProviderConfig(
            raw_request=raw_request,
            use_https=False,
            max_retries=3,
            validate_response="status == 200",
            transform_response="{'Jailbreak': json['results'][0]['chunk_results'][0]['JAILBREAK'], 'Injection': json['results'][0]['chunk_results'][0]['INJECTION']}",
        ),
    )

    client = HttpProviderClient()
    vars = {"prompt": "Hello, world!"}
    response = client.generate(provider, vars)

    print(response)
