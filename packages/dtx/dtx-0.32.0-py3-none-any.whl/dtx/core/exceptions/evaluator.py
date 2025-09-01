from .base import FeatureNotImplementedError


class BaseEvaluatorException(Exception):
    pass


class EvaluatorNotAvailable(FeatureNotImplementedError):
    pass


class EvaluatorRuntimeException(BaseEvaluatorException):
    pass
