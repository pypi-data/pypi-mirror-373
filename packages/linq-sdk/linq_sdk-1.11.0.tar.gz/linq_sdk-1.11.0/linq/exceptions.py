from .auth.server import AuthErrorMessage


class APIError(Exception):
    pass


class AuthError(Exception):
    message: AuthErrorMessage

    def __init__(self, message: AuthErrorMessage):
        self.message = message


class HubRestartCommandResponseNotFound(APIError):
    pass


class DuplicateWorkflowName(Exception):
    pass
