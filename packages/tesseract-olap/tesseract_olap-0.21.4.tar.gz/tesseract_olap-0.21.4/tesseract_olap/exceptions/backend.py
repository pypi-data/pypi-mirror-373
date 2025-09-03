"""Backend exceptions module.

The errors in this module refer to problems during the retrieval of data from
the backend, but happening at the backend plugin side of the code.
These should be extended/raised from inside the Backend module.
"""

from . import BackendError


class UpstreamNotPrepared(BackendError):
    """A connection attempt was done against a backend which is unable to accept connections.

    The user must avoid race conditions and ensure connections and cursors are
    in usable state.
    """

    def __init__(
        self,
        message: str = "Attempting to use a connection that is not open.",
        *args,
    ) -> None:
        super().__init__(message, *args)


class UpstreamInternalError(BackendError):
    """The remote server returned a valid response with details about an internal server error.

    This must be caught and reported to the administrator.
    """

    def __init__(self, message: str, *args) -> None:
        super().__init__(message, *args)


class UnexpectedResponseError(BackendError):
    """The database driver can't handle a response that doesn't adjust to expectations.

    This must be caught and logged, but usually is related to a malformed query,
    so not further handling might be needed.
    """

    code: int = 400


class BackendValidationError(BackendError):
    """The schema is set to use features that the backend is not prepared to handle.

    This must be reported to the administrator, but also should stop the process
    so the user can fix the schema.
    """


class BackendLimitsException(BackendError):
    """The user intends to perform a request that exceeds the capabilities of the Backend.

    The Backend preemptively cancels the request, and must inform the user so
    the request can be reformulated.
    """

    code: int = 413
