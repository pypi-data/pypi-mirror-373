class FeatureNotImplementedError(ValueError):
    pass


class MethodNotImplementedError(FeatureNotImplementedError):
    pass


class ModuleNotFoundError(FeatureNotImplementedError):
    pass


class EntityNotFound(ValueError):
    pass


class ModelNotFoundError(ModuleNotFoundError):
    pass
