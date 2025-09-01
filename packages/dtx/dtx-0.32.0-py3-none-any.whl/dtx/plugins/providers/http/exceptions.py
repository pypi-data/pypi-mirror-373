class BaseHttpProviderException(Exception):
    pass


class HttpResponseParserError(BaseHttpProviderException):
    """Base exception for response parsing errors."""

    pass


class InvalidTransformResponseError(HttpResponseParserError):
    """Raised when the transform_response is of an invalid type."""

    pass


class StringExpressionEvaluationError(HttpResponseParserError):
    """Raised when there is an error evaluating a string expression."""

    pass


class InlineFunctionEvaluationError(HttpResponseParserError):
    """Raised when there is an error evaluating an inline function."""

    pass


class FileLoadingError(HttpResponseParserError):
    """Raised when a file-based transformation cannot be loaded."""

    pass


class HttpRequestParsingError(BaseHttpProviderException):
    """Base exception for HTTP request parsing errors."""

    pass


class EmptyHttpRequestSendFailedError(HttpRequestParsingError):
    """Raised when an empty HTTP request is provided."""

    pass


class InvalidHttpRequestFormatError(HttpRequestParsingError):
    """Raised when the HTTP request format is invalid."""

    pass


class InvalidHttpMethodError(HttpRequestParsingError):
    """Raised when an invalid HTTP method is encountered."""

    pass


class MissingHostHeaderError(HttpRequestParsingError):
    """Raised when the Host header is missing in the HTTP request."""

    pass


class InvalidJsonBodyError(HttpRequestParsingError):
    """Raised when the body contains invalid JSON format."""

    pass


class HttpRequestSendFailedError(BaseHttpProviderException):
    """Base class for all HTTP request errors."""

    pass


class RateLimitExceededError(HttpRequestSendFailedError):
    """Raised when the request is rate-limited (HTTP 429)."""

    pass


class ServerError(HttpRequestSendFailedError):
    """Raised for 5xx server errors."""

    pass


class HttpRequestFailedError(HttpRequestSendFailedError):
    """Raised when an HTTP request fails for other reasons."""

    pass


class HttpResponseValidationError(BaseHttpProviderException):
    """Base class for all HTTP request errors."""

    pass


class InvalidHttpResponseError(HttpResponseValidationError):
    """Raised when an HTTP response status code fails validation."""

    def __init__(self, status_code, message="Invalid response status code"):
        super().__init__(f"{message}: {status_code}")
        self.status_code = status_code
