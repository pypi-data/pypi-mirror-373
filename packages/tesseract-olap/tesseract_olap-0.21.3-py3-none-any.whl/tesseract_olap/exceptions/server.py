from . import ServerError


class UnknownBackendError(ServerError):
    """This error occurs when the user attempts to initialize the Server with
    a connection string that doesn't match any known compatible Backend.

    The user must be informed to ensure they're using a compatible database.
    """

    def __init__(self, connection_str: str) -> None:
        super().__init__(
            f"Couldn't find a matching Backend for connection string: {connection_str}"
        )


class UnknownSchemaError(ServerError):
    """This error occurs when the user attempts to point the location of the
    Schema to a file in an unknown format.

    The user must be informed that by default, only XML and JSON files are
    allowed.
    """
