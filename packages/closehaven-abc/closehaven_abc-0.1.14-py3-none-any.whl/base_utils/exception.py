import jwt


class ImproperConfigurationError(Exception):
    status_code = 500

    def __init__(self, message: str, status_code=status_code) -> None:
        super().__init__(message)
        self.status_code = status_code


class EntityNotFoundError(Exception):
    status_code = 404

    def __init__(self, message: str, status_code=status_code) -> None:
        super().__init__(message)
        self.status_code = status_code


class DataAlreadyExist(Exception):
    status_code = 409

    def __init__(self, message: str, status_code=status_code) -> None:
        super().__init__(message)
        self.status_code = status_code


class BadRequestError(Exception):
    status_code = 400

    def __init__(self, message: str, status_code=status_code) -> None:
        super().__init__(message)
        self.status_code = status_code


class UnauthorizedError(Exception):
    status_code = 401

    def __init__(self, message: str, status_code=status_code) -> None:
        super().__init__(message)
        self.status_code = status_code


class ExpiredTokenError(jwt.exceptions.ExpiredSignatureError):
    status_code = 401

    def __init__(self, message: str, status_code=status_code) -> None:
        super().__init__(message)
        self.status_code = status_code
