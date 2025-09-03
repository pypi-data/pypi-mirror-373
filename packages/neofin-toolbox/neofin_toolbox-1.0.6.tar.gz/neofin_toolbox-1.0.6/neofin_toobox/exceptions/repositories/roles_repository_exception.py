from neofin_toobox.exceptions.common_exceptions import CommonException


class RolesRepositoryException(CommonException):
    """Exceção personalizada para erros do UserRepository"""
    pass


class RolesNotFoundException(CommonException):
    """Exceção para quando usuário não é encontrado"""
    pass