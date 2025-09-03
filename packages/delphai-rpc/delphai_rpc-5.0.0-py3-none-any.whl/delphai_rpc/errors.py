class RpcError(Exception):
    pass


class RetryableError(RpcError):
    pass


class UnknownError(RpcError):
    pass


class UnhandledError(RpcError):
    pass


class BadMessageError(RpcError):
    pass


class UnknownServiceError(RpcError):
    pass


class UnknownMethodError(RpcError):
    pass


class ExecutionError(RpcError):
    pass


class ExecutionTimeoutLimitError(RpcError):
    pass


class RetryableExecutionError(RetryableError):
    pass
