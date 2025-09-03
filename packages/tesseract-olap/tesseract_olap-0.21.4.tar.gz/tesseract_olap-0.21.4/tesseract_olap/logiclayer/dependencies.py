from collections.abc import Iterable, Sequence
from typing import Annotated, Optional, TypedDict

from fastapi import Depends, Header, Query, Request
from logiclayer import AuthToken, AuthTokenType
from pydantic import with_config

from tesseract_olap.query import (
    DataRequest,
    DataRequestParams,
    MembersRequest,
    MembersRequestParams,
)

DESCRIPTION_ALIASES = """Custom names for measures or dimensions in the response"""

DESCRIPTION_PAGINATION = """Controls how many results to return and from which position to start.

Format: A single number (limit) or two numbers separated by comma (limit,offset)
- limit: Maximum number of items to return
- offset: Starting position (0-based index) in the full result set

Examples: "10" returns first 10 items, "10,20" returns 10 items starting from position 20"""

DESCRIPTION_SORTING = """Controls the order of results by measures or properties.

Format: field or field.order
- field: Name of the measure or property to sort by
- order: "asc" (ascending) or "desc" (descending), defaults to "asc" if not specified

The system first looks for a measure with this name, then for a property.
Examples: "Population", "Population.desc", "Country.asc" """

DESCRIPTION_TIME = """Filter data by time periods using various restriction types.

Format: level.constraint
- level: Time dimension level name as defined in the cube (e.g., "Year", "Month") or time scale ("year", "quarter", "month", "day")
- constraint: Time restriction type with parameters

Constraint types (periods are defined by the time dimension level):
- `complete`: Return all available time periods (only for "year" and "quarter" scales)
- `latest.N`: Return the N most recent records, regardless of time continuity (e.g., "latest.5" for last 5 records)
- `oldest.N`: Return the N earliest records, regardless of time continuity (e.g., "oldest.3" for first 3 records)
- `trailing.N`: Return the records available in the last N periods (e.g., "trailing.12" for records within the last 12 periods)
- `leading.N`: Return the records available in the first N periods (e.g., "leading.3" for records within the first 3 periods)
- expr.condition: Custom time filtering using comparison operators (e.g., "gt.2020", "gte.2020.and.lt.2022")

Examples: `Year.latest.5` (last 5 years), `Month.trailing.12` (last 12 months), `Quarter.complete` (all quarters)"""

DESCRIPTION_TOP = """Return only the top/bottom results grouped by specified levels.

Format: amount.level[,level...].measure.order
- amount: Number of top/bottom results to return (integer > 0)
- level[,level...]: One or more levels to group by (comma-separated)
- measure: The measure to rank by
- order: "desc" for top results, "asc" for bottom results

Examples: `10.Country.Population.desc` (top 10 countries by population) or `5.State,City.Sales.asc` (bottom 5 state-city combinations by sales)

This groups the data by the specified levels, then returns only the top or bottom results based on the measure value."""

DESCRIPTION_GROWTH = """Calculate growth rates for measures over time.

Format: time_level.measure.params
- time_level: The time dimension level (e.g., "Year", "Month", "Quarter")
- measure: The measure to calculate growth for
- params: Either `fixed.member_id` (compare to specific time period) or `period.amount` (compare consecutive periods)

Examples: `Year.Population.fixed.2020` (growth compared to 2020) or `Month.Sales.period.1` (month-over-month growth)

This adds period difference and growth percentage columns showing the change in measure values over time."""

DESCRIPTION_EXCLUDE = """Specifies which dimension members to exclude from the results.

Format: LevelName:member1,member2;LevelName2:member3,member4
- LevelName: The name of the dimension level
- member1,member2: Comma-separated list of member IDs to exclude

Examples: `Country:XX,YY` or `Year:2020;Country:XX,YY`"""

DESCRIPTION_INCLUDE = """Specifies which dimension members to include in the results.

Format: LevelName:member1,member2;LevelName2:member3,member4
- LevelName: The name of the dimension level
- member1,member2: Comma-separated list of member IDs to include

Examples: `Country:US,CA,MX` or `Year:2020,2021;Country:US,CA`

For backward compatibility, you can also use the level name directly as a parameter:
`&Country=US,CA,MX` is equivalent to `&include=Country:US,CA,MX`.
This is not recommended though, as it may cause confusion."""

DESCRIPTION_FILTERS = """Apply filters to measure values in the results.

Format: measure.operator.value or measure.operator1.value1.logic.operator2.value2
- measure: Name of the measure to filter
- operator: gt (greater than), gte (greater than or equal), eq (equal), neq (not equal), lt (less than), lte (less than or equal)
- value: Numeric value to compare against
- logic: "and", "or", "xor" (when combining two conditions)

Examples: `Population.gt.1000000` or `Sales.gte.1000.and.lt.5000`"""

DESCRIPTION_PARENTS = """Include parent level information for drilldown dimensions

Options:
- "true" or "1": Include parents for all drilldowns
- "false" or "0": Exclude all parents (default)
- "Level1,Level2": Include parents only for specified levels

Examples: "true", "Country,State" """

DESCRIPTION_PROPERTIES = """Additional properties to include for each dimension member"""

DESCRIPTION_RANKING = """Add ranking numbers to measures in the results.

Options:
- "true" or "1": Add rankings for all measures
- "false" or "0": No rankings (default)
- "Measure1,Measure2": Add rankings only for specified measures

Use "-" prefix for descending order: "-Population" ranks Population in descending order.
Equal values get the same rank, with gaps for ties."""

DESCRIPTION_SPARSE = """Control whether to return only rows with data or all possible combinations.

- true (default): Return only rows that have at least one non-null measure value
- false: Return all possible dimension combinations, even with null values

Warning: Setting to false may return very large datasets, specially when many drilldowns are used."""


class DataSearchParamsRequired(TypedDict, total=True):
    cube: Annotated[str, Query(description="The name of the cube to work with.")]
    drilldowns: Annotated[
        Sequence[str],
        Query(description="A list of the level names to slice the bulk of the aggregated data."),
    ]
    measures: Annotated[
        Sequence[str],
        Query(description="A list of the measure names to retrieve from the aggregated data."),
    ]


@with_config(str_strip_whitespace=True)
class DataSearchParams(DataSearchParamsRequired, total=False):
    locale: Annotated[
        Optional[str],
        Query(description="The code of the language for the content in the response."),
    ]
    limit: Annotated[str, Query(description=DESCRIPTION_PAGINATION)]
    sort: Annotated[str, Query(description=DESCRIPTION_SORTING)]
    time: Annotated[str, Query(description=DESCRIPTION_TIME)]
    top: Annotated[str, Query(description=DESCRIPTION_TOP)]
    growth: Annotated[str, Query(description=DESCRIPTION_GROWTH)]
    sparse: Annotated[str, Query(description=DESCRIPTION_SPARSE)]
    aliases: Annotated[Sequence[str], Query(description=DESCRIPTION_ALIASES)]
    parents: Annotated[Sequence[str], Query(description=DESCRIPTION_PARENTS)]
    properties: Annotated[Sequence[str], Query(description=DESCRIPTION_PROPERTIES)]
    ranking: Annotated[Sequence[str], Query(description=DESCRIPTION_RANKING)]
    exclude: Annotated[Sequence[str], Query(description=DESCRIPTION_EXCLUDE)]
    include: Annotated[Sequence[str], Query(description=DESCRIPTION_INCLUDE)]
    filters: Annotated[Sequence[str], Query(description=DESCRIPTION_FILTERS)]


def auth_token(
    header_auth: Annotated[Optional[str], Header(alias="authorization")] = None,
    header_jwt: Annotated[Optional[str], Header(alias="x-tesseract-jwt")] = None,
    query_token: Annotated[Optional[str], Query(alias="token")] = None,
):
    if header_jwt:
        return AuthToken(AuthTokenType.JWTOKEN, header_jwt)
    if query_token:
        return AuthToken(AuthTokenType.SEARCHPARAM, query_token)
    if header_auth:
        if header_auth.startswith("Bearer "):
            return AuthToken(AuthTokenType.JWTOKEN, header_auth[7:])
        if header_auth.startswith("Basic "):
            return AuthToken(AuthTokenType.BASIC, header_auth[6:])
        if header_auth.startswith("Digest "):
            return AuthToken(AuthTokenType.DIGEST, header_auth[7:])

    return None


def query_cuts_include(
    request: Request,
    include: Annotated[str, Query(description=DESCRIPTION_INCLUDE)] = "",
):
    """FastAPI Dependency to parse including cut parameters.

    It also parses all URL Search Params whose key is capitalized, as cut definitions.
    Values are members' IDs, separated by commas.
    """
    result = {
        key: value.split(",") for key, value in request.query_params.items() if key[0].isupper()
    }
    return {**result, **query_cuts_exclude(include)}


def query_cuts_exclude(
    exclude: Annotated[str, Query(description=DESCRIPTION_EXCLUDE)] = "",
):
    """FastAPI Dependency to parse excluding cut parameters."""
    return {
        key: value.split(",")
        for key, value in (item.split(":")[:2] for item in exclude.split(";") if item != "")
    }


def query_filters(
    filters: Annotated[list[str], Query(description=DESCRIPTION_FILTERS)] = [],
) -> list[str]:
    """FastAPI Dependency to parse filter parameters."""
    return [item for token in filters for item in token.split(",") if item != ""]


def dataquery_params(
    cube_name: Annotated[
        str,
        Query(alias="cube", description="The name of the cube to work with."),
    ],
    drilldowns: Annotated[
        str,
        Query(description="A list of the level names to slice the bulk of the aggregated data."),
    ],
    measures: Annotated[
        str,
        Query(description="A list of the measure names to retrieve from the aggregated data."),
    ],
    aliases: Annotated[Optional[str], Query(description=DESCRIPTION_ALIASES)] = None,
    cuts_exclude: dict[str, list[str]] = Depends(query_cuts_exclude),
    cuts_include: dict[str, list[str]] = Depends(query_cuts_include),
    filters: list[str] = Depends(query_filters),
    locale: Optional[str] = None,
    pagination: Annotated[str, Query(alias="limit", description=DESCRIPTION_PAGINATION)] = "0",
    parents: Annotated[str, Query(description=DESCRIPTION_PARENTS)] = "",
    properties: Annotated[Optional[str], Query(description=DESCRIPTION_PROPERTIES)] = None,
    ranking: Annotated[str, Query(description=DESCRIPTION_RANKING)] = "",
    sorting: Annotated[str, Query(alias="sort", description=DESCRIPTION_SORTING)] = "",
    sparse: Annotated[bool, Query(description=DESCRIPTION_SPARSE)] = True,
    time: Annotated[Optional[str], Query(description=DESCRIPTION_TIME)] = None,
    top: Annotated[Optional[str], Query(description=DESCRIPTION_TOP)] = None,
    growth: Annotated[Optional[str], Query(description=DESCRIPTION_GROWTH)] = None,
):
    """FastAPI Dependency to parse parameters into a DataRequest object."""
    params: DataRequestParams = {
        "drilldowns": [item.strip() for item in drilldowns.split(",")],
        "measures": [item.strip() for item in measures.split(",")],
        "cuts_exclude": cuts_exclude,
        "cuts_include": cuts_include,
        "filters": filters,
        "pagination": pagination,
        "parents": parents,
        "ranking": ranking,
        "sorting": sorting,
        "sparse": sparse,
    }

    if locale is not None:
        params["locale"] = locale

    if properties is not None:
        params["properties"] = properties.split(",")

    if time is not None:
        params["time"] = time

    if top is not None:
        params["top"] = top

    if growth is not None:
        params["growth"] = growth

    if aliases is not None:
        params["aliases"] = aliases

    return DataRequest.new(cube_name, params)


def membersquery_params(
    cube_name: Annotated[
        str,
        Query(alias="cube", description="The name of the cube to work with."),
    ],
    level: Annotated[str, Query(description="The name of the level to get the members from.")],
    locale: Annotated[
        Optional[str],
        Query(description="The locale to get the members labels in."),
    ] = None,
    pagination: Annotated[
        str,
        Query(alias="limit", description=DESCRIPTION_PAGINATION),
    ] = "0",
    parents: bool = False,
    properties: Annotated[
        list[str],
        Query(description="The Properties to get for each of the members in the selected level."),
    ] = [],
    search: str = "",
):
    """FastAPI Dependency to parse parameters into a MembersRequest object."""
    params: MembersRequestParams = {
        "level": level,
        "pagination": pagination,
        "parents": parents,
        "properties": {item for item in split_list(properties) if item},
    }

    if locale is not None:
        params["locale"] = locale

    if search != "":
        params["search"] = search

    return MembersRequest.new(cube_name, params)


def split_list(items: list[str], tokensep: str = ",") -> Iterable[str]:
    """Split the items in a list of strings, and filter empty strings."""
    return (token.strip() for item in items for token in item.split(tokensep))
