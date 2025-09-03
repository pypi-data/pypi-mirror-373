from base_utils.exception import BadRequestError, EntityNotFoundError, UnauthorizedError


def convert_error_type(error_type: str) -> Exception:
    exception_mapping = {
        "ExpiredSignatureError": UnauthorizedError,
        "InvalidTokenError": UnauthorizedError,
        "BadRequestError": BadRequestError,
        "EntityNotFoundError": EntityNotFoundError,
        "UnauthorizedError": UnauthorizedError,
        "ZeroDivisionError": ZeroDivisionError,
    }
    return exception_mapping.get(error_type, Exception)
