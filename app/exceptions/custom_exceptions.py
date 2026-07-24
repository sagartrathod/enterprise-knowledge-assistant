# app/exceptions/custom_exceptions.py

from __future__ import annotations


class AppException(Exception):
    """
    Base application exception.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
    ) -> None:

        self.message = message
        self.status_code = status_code

        super().__init__(message)


class BadRequestException(AppException):

    def __init__(
        self,
        message: str = "Bad Request",
    ) -> None:

        super().__init__(
            message=message,
            status_code=400,
        )


class UnauthorizedException(AppException):

    def __init__(
        self,
        message: str = "Unauthorized",
    ) -> None:

        super().__init__(
            message=message,
            status_code=401,
        )


class ForbiddenException(AppException):

    def __init__(
        self,
        message: str = "Forbidden",
    ) -> None:

        super().__init__(
            message=message,
            status_code=403,
        )


class NotFoundException(AppException):

    def __init__(
        self,
        message: str = "Resource not found",
    ) -> None:

        super().__init__(
            message=message,
            status_code=404,
        )


class ConflictException(AppException):

    def __init__(
        self,
        message: str = "Conflict",
    ) -> None:

        super().__init__(
            message=message,
            status_code=409,
        )


class DatabaseException(AppException):

    def __init__(
        self,
        message: str = "Database Error",
    ) -> None:

        super().__init__(
            message=message,
            status_code=500,
        )


class ValidationException(AppException):

    def __init__(
        self,
        message: str = "Validation Error",
    ) -> None:

        super().__init__(
            message=message,
            status_code=422,
        )

class ContextException(AppException):
    def __init__(
        self,
        message: str,
        details: dict | None = None,
    ):
        super().__init__(
            status_code=500,
            message=message,
            details=details,
        )

class EmbeddingException(AppException):
    """
    Raised when embedding generation fails.
    """

    def __init__(
        self,
        message: str = "Embedding generation failed.",
        details: dict | None = None,
    ):
        super().__init__(
            status_code=500,
            message=message,
            details=details,
        )