from neofin_toobox.exceptions.common_exceptions import CommonException


class CompanyNotFoundException(CommonException):
    def __init__(self, message: str):
        super().__init__(message, 404)