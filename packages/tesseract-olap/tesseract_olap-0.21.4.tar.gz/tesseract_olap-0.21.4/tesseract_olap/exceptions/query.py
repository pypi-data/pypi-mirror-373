"""Query exceptions module.

The errors in this module refer to problems during the retrieval of data from
the backend, but happening at the core side of the code.
"""

from __future__ import annotations

from collections.abc import Collection, Iterable

from . import QueryError


class InvalidQuery(QueryError):  # noqa: N818
    """General error for when a query is misconstructed.

    Can be raised before or after a request is made against a data server.
    """


class InvalidParameter(InvalidQuery):
    """A parameter in the query is incorrectly set before any data validation happens.

    This includes parameters with the wrong type.
    As this is entirely an user issue, should be informed to the user, but not
    necessarily to the administrator.
    """

    def __init__(self, param: str, detail: str | None) -> None:
        """Initialize an instance of the error."""
        msg = f"Query parameter '{param}' set incorrectly"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)


class InvalidEntityName(InvalidQuery):
    """A query asks for an object missing in the schema."""

    def __init__(self, node: str, name: str) -> None:
        """Initialize an instance of the error."""
        super().__init__(
            f"Failed attempt to get a {node} object with name {name!r}: Entity doesn't exist",
        )


class TimeDimensionUnavailable(InvalidQuery):
    """The requested Cube doesn't contain a "time" Dimension type.

    On an information level this should be informed to the user, and in a debug
    level should be reported to the administrator to check if there's a issue
    with the schema.
    """

    def __init__(self, cube_name: str) -> None:
        """Initialize an instance of the error."""
        super().__init__(
            f"Cube {cube_name!r} doesn't contain a declared time dimension.",
        )


class TimeScaleUnavailable(InvalidQuery):
    """The requested time scale is not available in any level of the selected dimension."""

    def __init__(self, cube_name: str, scale: str) -> None:
        """Initialize an instance of the error."""
        super().__init__(
            f"Time scale {scale!r} is not available among dimensions in cube {cube_name!r}",
        )


class InvalidFormat(InvalidQuery):
    """A format used to retrieve data is not supported by the upstream server.

    Should be raised before the query is executed against the upstream server.
    """

    def __init__(self, extension: str) -> None:
        """Initialize an instance of the error."""
        super().__init__(f"Format '{extension}' is not supported by the server.")


class MissingMeasures(InvalidQuery):
    """A feature intends to use a measure that is not being requested in the query.

    Should be raised before the query is executed against the upstream server.
    """

    def __init__(self, feature: str, measures: Collection[str]) -> None:
        """Initialize an instance of the error."""
        super().__init__(
            f"Requesting {feature} for measures not in the request: {', '.join(measures)}",
        )


class NotAuthorized(InvalidQuery):
    """Provided roles don't match the roles needed to access some of the requested resources.

    Should be raised before the query is executed against the upstream server.
    """

    code = 403

    def __init__(self, resource: str, roles: Iterable[str]) -> None:
        """Initialize an instance of the error."""
        super().__init__(
            f"Requested resource {resource!r} is not allowed for the roles "
            f"provided by credentials: '{', '.join(roles)}'",
        )
        self.resource = resource
        self.roles = roles
