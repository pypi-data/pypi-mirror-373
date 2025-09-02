"""Requests module.

Contains structs to build a :class:`DataRequest` instance: an object to describe
the parameters needed for the query using only entity names and relationships.
"""

import hashlib
from collections.abc import Collection, Generator, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Optional, Union

from pydantic import (
    BaseModel,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)
from typing_extensions import Literal, Protocol, TypedDict

from tesseract_olap.common import FALSEY_STRINGS, TRUTHY_STRINGS, Array, stringify
from tesseract_olap.query import AnyOrder

from .models import (
    Condition,
    CutIntent,
    FilterIntent,
    GrowthIntent,
    JoinIntent,
    PaginationIntent,
    SortingIntent,
    TimeRestriction,
    TopkIntent,
)

Parseable = Union[str, Collection[str]]
AnyRequest = Union["DataRequest", "MembersRequest"]


class RequestWithRoles(Protocol):
    """Defines an interface of commons between DataRequest and MembersRequest."""

    cube: str
    roles: set[str]


class DataRequestOptionalParams(TypedDict, total=False):
    """Defines the optional parameters in the DataRequestParams interface.

    Is a separate class is due to the implementation of the
    [Totality](https://www.python.org/dev/peps/pep-0589/#totality) in the
    :class:`TypedDict` class.

    This will give a better hint to the type checker when the user makes use of
    this interface.
    """

    aliases: Union[Parseable, Mapping[str, str]]
    captions: Parseable
    cuts: Union[Parseable, Mapping[str, Collection[str]]]
    cuts_exclude: Union[Parseable, Mapping[str, Collection[str]]]
    cuts_include: Union[Parseable, Mapping[str, Collection[str]]]
    filters: Union[Parseable, Mapping[str, Condition]]
    growth: str
    locale: str
    pagination: Union[str, tuple[int, int]]
    parents: Union[Parseable, bool]
    properties: Parseable
    ranking: Union[Parseable, bool, Mapping[str, AnyOrder]]
    roles: Parseable
    sorting: Union[Parseable, tuple[str, AnyOrder]]
    sparse: bool
    time: str
    top: str


class DataRequestParams(DataRequestOptionalParams, total=True):
    """DataRequestParams interface.

    Determines the expected params in a :class:`dict`, to use when creating a
    new :class:`DataRequest` object via the :func:`DataRequest.new` class method.
    """

    drilldowns: Parseable
    measures: Parseable


class DataRequest(BaseModel):
    """Represents the intent for a Data Query made by the user.

    All its properties are defined by strings of the names of the components
    from the schema.
    None of these parameters are verified during construction, so it's possible
    for the query to be invalid; a subclass of :class:`backend.exceptions.BackendError`
    will be raised in that case.
    The only purpose of this structure is containing and passing over the query
    intent to the internals.

    During a request, a :class:`Query` instance is constructed with objects from
    a schema, using parameters from this instance.
    """

    cube: str
    drilldowns: set[str]
    measures: set[str]
    aliases: dict[str, str] = field(default_factory=dict)
    captions: set[str] = field(default_factory=set)
    cuts: dict[str, CutIntent] = field(default_factory=dict)
    filters: dict[str, FilterIntent] = field(default_factory=dict)
    locale: Optional[str] = None
    options: dict[str, bool] = field(default_factory=dict)
    pagination: PaginationIntent = field(default_factory=PaginationIntent)
    parents: Union[bool, set[str]] = False
    properties: set[str] = field(default_factory=set)
    ranking: Union[bool, dict[str, Literal["asc", "desc"]]] = False
    roles: set[str] = field(default_factory=set)
    sorting: Optional[SortingIntent] = None
    sparse: bool = True
    time_restriction: Optional[TimeRestriction] = None
    topk: Optional[TopkIntent] = None
    growth: Optional[GrowthIntent] = None

    def __eq__(self, value: object) -> bool:
        return isinstance(value, DataRequest) and hash(self) == hash(value)

    def __hash__(self) -> int:
        return hash((repr(self), *sorted(self.roles)))

    def __repr__(self) -> str:
        params = (
            f"cube={self.cube!r}",
            f"locale={self.locale!r}",
            f"drilldowns={stringify(self.drilldowns)}",
            f"aliases={self.aliases!r}",
            f"captions={stringify(self.captions)}",
            f"properties={stringify(self.properties)}",
            f"cuts={stringify(list(self.cuts.values()))}",
            f"time={self.time_restriction!r}",
            f"topk={self.topk!r}",
            f"measures={stringify(self.measures)}",
            f"filters={stringify(list(self.filters.values()))}",
            f"ranking={stringify(self.ranking)}",
            f"pagination={self.pagination!r}",
            f"parents={stringify(self.parents)}",
            f"sorting={self.sorting!r}",
            f"sparse={self.sparse!r}",
            f"growth={self.growth!r}",
        )
        return f"{type(self).__name__}({', '.join(params)})"

    def key(self) -> str:
        """Generate a hash to differentiate the parameters that influence the resulting data.

        This hash can be used to compare requests, and as cache key for the resulting data.
        It doesn't consider roles on purpose, as the roles define the access to the dataset
        instead of its contents. This also means a comparison operation between requests must
        compare roles separately.
        """
        return hashlib.md5(repr(self).encode("utf-8"), usedforsecurity=False).hexdigest()

    @field_validator("drilldowns", "measures", mode="before")
    @classmethod
    def split_str_list_mandatory(cls, value: object, info: ValidationInfo):
        """Parse a list of strings, where is mandatory to have at lease one valid value."""
        if isinstance(value, str):
            items = {item for item in value.split(",") if item}
            if not items:
                msg = f"Field {info.field_name} requires at least a value."
                raise ValueError(msg)
            return items
        return value

    @field_validator("captions", "properties", "roles", mode="before")
    @classmethod
    def split_str_list(cls, value: object):
        """Parse a list of strings, separated by comma."""
        if isinstance(value, str):
            return {item for item in value.split(",") if item}
        return value

    @field_validator("aliases", mode="before")
    @classmethod
    def parse_aliases(cls, value: object):
        """Parse a map of aliases from a string."""
        if isinstance(value, str):
            value = value.split(";")

        if isinstance(value, Mapping):
            return dict(value)

        if isinstance(value, Collection):
            gen_alias_pairs = (token.split(":", 1) for token in value if ":" in token)
            return dict(_validate_alias_pairs(gen_alias_pairs))

        return value

    @field_validator("cuts", mode="before")
    @classmethod
    def parse_cuts(cls, value: object):
        """Parse a list of cuts in string form, into CutIntents.

        The input can be a single cut, a list of single cuts, or a string containing
        multiple single cuts separated by semicolon (;).
        If provided a dict, it will be assumed as {"level": "member,member"}, where
        level can have a leading tilde (~) to indicate the list of members as exclusion
        instead of inclusion mode.
        """
        if isinstance(value, str):
            value = value.split(";")

        if isinstance(value, Mapping):
            levels = {name.lstrip("~") for name in value if isinstance(name, str)}
            value = [(level, value.get(level, []), value.get(f"~{level}", [])) for level in levels]

        if isinstance(value, Collection):
            gen_cuts = (CutIntent.model_validate(item) for item in value)
            return {item.level: item for item in gen_cuts}

        return value

    @field_validator("filters", mode="before")
    @classmethod
    def parse_filters(cls, value: object):
        """Parse a list of filters in string form, into FilterIntents.

        The input can be a single filter, a list of single filters, or a string
        containing multiple single filters separated by comma (,).
        If provided a dict, it will be assumed as {"field": condition}, where
        the condition can be in string form ("gt.1000.and.lt.2000") or in tuple
        form (("gt", 1000), "and", ("lt", 2000)).
        """
        if isinstance(value, str):
            value = value.split(",")

        if isinstance(value, Mapping):
            value = list(value.items())

        if isinstance(value, Collection):
            gen_filters = (FilterIntent.model_validate(item) for item in value)
            return {item.field: item for item in gen_filters}

        return value

    @field_validator("parents", mode="before")
    @classmethod
    def parse_parents(cls, value: object):
        """Parse parents values into compliance.

        This method can parse a single boolean from string, or a list of strings
        separated by comma (,).
        """
        if isinstance(value, str):
            if value.lower() in FALSEY_STRINGS:
                return False
            if value.lower() in TRUTHY_STRINGS:
                return True
            return {item.strip() for item in value.split(",")}

        if isinstance(value, Sequence):
            return set(value)

        return value

    @field_validator("ranking", mode="before")
    @classmethod
    def parse_ranking(cls, value: object):
        """Parse ranking values into compliance.

        This method can parse a single boolean string, or a list of strings
        separated by comma, each with an optional minus sign as prefix.
        """
        if isinstance(value, str):
            if value.lower() in FALSEY_STRINGS:
                return False
            if value.lower() in TRUTHY_STRINGS:
                return True
            return {
                item.lstrip("-"): "desc" if item.startswith("-") else "asc"
                for item in value.split(",")
            }
        return value

    @classmethod
    def new(cls, cube: str, params: DataRequestParams):
        """Create a new :class:`DataRequest` instance from a set of parameters defined in a dict.

        This should be the preferred method by final users, as it doesn't
        require the use of internal dataclasses and the setup of internal
        structures and unique conditions.
        """
        param_map = {
            "cube": cube,
            "drilldowns": params.get("drilldowns"),
            "measures": params.get("measures"),
            "aliases": params.get("aliases"),
            "captions": params.get("captions"),
            "cuts": [
                *_consolidate_cuts(params.get("cuts", {})),
                *_consolidate_cuts(params.get("cuts_include", {})),
                *_consolidate_cuts(params.get("cuts_exclude", {}), exclude=True),
            ],
            "filters": params.get("filters"),
            "locale": params.get("locale"),
            "options": params.get("options"),
            "pagination": params.get("pagination"),
            "parents": params.get("parents"),
            "properties": params.get("properties"),
            "ranking": params.get("ranking"),
            "roles": params.get("roles"),
            "sorting": params.get("sorting"),
            "sparse": params.get("sparse"),
            "time_restriction": params.get("time"),
            "topk": params.get("top"),
            "growth": params.get("growth"),
        }
        clean_params = {
            key: value for key, value in param_map.items() if value is not None and value != ""
        }

        return cls.model_validate(clean_params)


class DataMultiRequest(BaseModel):
    requests: list[DataRequest]
    joins: list[JoinIntent] = Field(default_factory=list)
    pagination: PaginationIntent = Field(default_factory=PaginationIntent)

    @model_validator(mode="before")
    @classmethod
    def parse_request(cls, value: object):
        if isinstance(value, dict):
            requests = value.get("queries") or value.get("requests", [])
            if not isinstance(requests, Sequence):
                msg = "Invalid 'requests' parameter: it must be a list of dictionaries containing the request parameters of the queries to be merged."
                raise ValueError(msg)

            request_count = len(requests)
            if not request_count > 1:
                msg = "At least 2 DataRequest objects are required to perform a join operation."
                raise ValueError(msg)

            joins = value.get("joins", [])
            if not isinstance(joins, Sequence):
                msg = "Invalid 'joins' parameter. It must be a list of dictionaries with the parameters to use."
                raise ValueError(msg)

            if not joins:
                joins = [{}] * (request_count - 1)
            elif len(joins) == 1:
                joins = list(joins) * (request_count - 1)
            elif len(joins) == request_count - 1:
                pass
            else:
                msg = f"Invalid 'joins' parameter. It must be a list of objects with the parameters to use; this list must contain 1 object (if you intend to apply the same parameters to all queries), {request_count - 1} objects (one per each step of this join operation), or left empty/unset to let the server attempt to guess the parameters."
                raise ValueError(msg)

            return {
                "requests": requests,
                "joins": joins,
                "pagination": value.get("pagination", "0,0"),
            }
        return value


class MembersRequestOptionalParams(TypedDict, total=False):
    """Defines the optional parameters in the MembersRequestParams interface.

    Is a separate class is due to the implementation of the
    [Totality](https://www.python.org/dev/peps/pep-0589/#totality) in the
    :class:`TypedDict` class.

    This will give a better hint to the type checker when the user makes use of
    this interface.
    """

    children: bool
    locale: str
    pagination: Union[str, tuple[int, int]]
    parents: bool
    properties: Collection[str]
    roles: Array[str]
    search: str


class MembersRequestParams(MembersRequestOptionalParams, total=True):
    """MembersRequestParams interface.

    Determines the expected params in a :class:`dict`, to use when creating a
    new :class:`MembersRequest` object via the :func:`MembersRequest.new` class
    method.
    """

    level: str


@dataclass(eq=False, order=False)
class MembersRequest:
    """Represents the intent for a Level Metadata Query made by the user.

    Parameters are constructed with primitives that describe the entities being
    requested.

    It is suggested to use the :func:`MembersRequest.new` method to create a new
    instance of this class, instead of calling a new instance directly.
    """

    cube: str
    level: str
    children: bool = False
    locale: Optional[str] = None
    pagination: PaginationIntent = field(default_factory=PaginationIntent)
    parents: bool = False
    properties: Collection[str] = field(default_factory=set)
    roles: set[str] = field(default_factory=set)
    search: Optional[str] = None

    @classmethod
    def new(cls, cube: str, request: MembersRequestParams):
        """Create a new :class:`MembersRequest` instance from a set of parameters defined in a dict.

        This should be the preferred method by final users, as it doesn't
        require the use of internal dataclasses and the setup of internal
        structures and unique conditions.
        """
        item = request.get("roles", [])
        roles = set(item) if isinstance(item, (list, tuple)) else item

        return cls(
            cube=cube,
            level=request["level"],
            children=request.get("children", False),
            locale=request.get("locale"),
            pagination=PaginationIntent.model_validate(request.get("pagination", "0")),
            parents=request.get("parents", False),
            properties=request.get("properties", []),
            roles=roles,
            search=request.get("search"),
        )


def _consolidate_cuts(
    cuts: Union[Parseable, Mapping[str, Collection[str]]] = {},
    *,
    exclude: bool = False,
):
    if isinstance(cuts, str):
        return cuts.split(";")
    if isinstance(cuts, Mapping):
        if exclude:
            return [(f"~{level}", members) for level, members in cuts.items()]
        return list(cuts.items())
    return cuts


def _validate_alias_pairs(
    generator: Iterable[list[str]],
) -> Generator[tuple[str, str], None, None]:
    seen_keys = set()
    for name, alias in generator:
        clean_name, clean_alias = name.strip(), alias.strip()
        if not clean_name:
            msg = f"Empty level name in alias pair: '{name}:{alias}'"
            raise ValueError(msg)
        if not clean_alias:
            msg = f"Empty level alias in alias pair: '{name}:{alias}'"
            raise ValueError(msg)
        if clean_name in seen_keys:
            msg = f"Request contains two aliases for the same level: '{clean_name}'"
            raise ValueError(msg)
        seen_keys.add(clean_name)
        yield clean_name, clean_alias
