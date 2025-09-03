from neofin_toobox.exceptions.common_exceptions import CommonException


class UserRepositoryException(CommonException):
    """Exceção personalizada para erros do UserRepository"""
    pass


class UserNotFoundException(CommonException):
    """Exceção para quando usuário não é encontrado"""
    def __init__(self, message: str):
        super().__init__(message, status_code=403)