class AuthenticationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class TargetMissingError(Exception):
    pass


class CommandError(Exception):
    def __init__(self, err_type: str, message: str) -> None:
        self.err_type = err_type
        self.message = message
        super().__init__(message)


class DaemonError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
