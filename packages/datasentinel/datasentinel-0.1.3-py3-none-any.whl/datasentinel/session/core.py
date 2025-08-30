from datasentinel.core import DataSentinelError


class DataSentinelSessionError(DataSentinelError):
    pass


class SessionAlreadyExistsError(DataSentinelSessionError):
    pass


class SessionNotSpecifiedError(DataSentinelSessionError):
    pass
