__all__ = (
    "BackendError",
    "QueryError",
    "SchemaError",
    "ServerError",
    "TesseractError",
)


class TesseractError(Exception):
    """Base class for exceptions in `tesseract_olap` module."""

    code: int = 500
    message: str

    def __init__(self, message: str, *args) -> None:
        super().__init__(message, *args)
        self.message = message


class BackendError(TesseractError):
    """Base class for exceptions in `tesseract_olap.backend` module."""


class QueryError(TesseractError):
    """Base class for exceptions in `tesseract_olap.query` module."""

    code: int = 400


class SchemaError(TesseractError):
    """Base class for exceptions in `tesseract_olap.schema` module."""


class ServerError(TesseractError):
    """Base class for exceptions in `tesseract_olap.server` module."""
