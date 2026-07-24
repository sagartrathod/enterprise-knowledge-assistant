from __future__ import annotations


class AppException(Exception):
    """
    Base application exception.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error: str = "Application Error",
        details=None,
    ):

        self.message = message
        self.status_code = status_code
        self.error = error
        self.details = details

        super().__init__(message)


class DatabaseException(AppException):

    def __init__(
        self,
        message: str = "Database operation failed.",
    ):
        super().__init__(
            message=message,
            status_code=500,
            error="Database Error",
        )


class DocumentNotFoundException(AppException):

    def __init__(self):
        super().__init__(
            message="Document not found.",
            status_code=404,
            error="Document Not Found",
        )


class EmbeddingException(AppException):

    def __init__(
        self,
        message="Embedding generation failed.",
    ):
        super().__init__(
            message=message,
            status_code=500,
            error="Embedding Error",
        )


class RetrievalException(AppException):

    def __init__(
        self,
        message="Document retrieval failed.",
    ):
        super().__init__(
            message=message,
            status_code=500,
            error="Retrieval Error",
        )


class LLMException(AppException):

    def __init__(
        self,
        message="LLM generation failed.",
    ):
        super().__init__(
            message=message,
            status_code=500,
            error="LLM Error",
        )