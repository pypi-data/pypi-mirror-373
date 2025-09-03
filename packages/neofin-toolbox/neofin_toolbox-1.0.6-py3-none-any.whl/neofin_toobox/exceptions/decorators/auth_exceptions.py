from neofin_toobox.exceptions.common_exceptions import CommonException

class AuthException(CommonException):
    """Exceção personalizada para erros de autenticação/autorização"""
    pass


class PermissionException(CommonException):
    def __init__(self, message: str):
        super().__init__(message, status_code=403)

class AuthenticationException(CommonException):
    def __init__(self, message: str):
        super().__init__(message, status_code=403)

class MissingUserException(CommonException):
    def __init__(self, message: str):
        super().__init__(message, status_code=403)

class MissingRoleException(CommonException):
    def __init__(self, message: str):
        super().__init__(message, status_code=403)