class BaseAgentException(Exception):
    pass


class RemoteConnectionError(BaseAgentException):
    """
    Raised when remote endpoints return connection error
    """

    pass


class RemoteResponseError(BaseAgentException):
    """
    Raised when remote endpoints return error as response
    """

    pass


class UnknownAgentException(BaseAgentException):
    pass


class ExecutionRuntimeError(BaseAgentException):
    """
    Raised when remote endpoints return connection error
    """

    pass
