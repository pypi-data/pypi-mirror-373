"""Query-related internal structs module.

This module contains data-storing structs, used mainly on the query and backend
modules.
"""

import dataclasses as dcls
from collections.abc import Collection, Generator, Iterable, Mapping, Sequence
from collections.abc import Set as AbstractSet
from copy import copy
from functools import cached_property
from typing import Annotated, Any, Literal, NamedTuple, Optional, TypeVar, Union

from pydantic import BaseModel, Field, model_validator
from typing_extensions import TypeGuard

from tesseract_olap.common import Prim, shorthash
from tesseract_olap.schema import (
    AnyMeasure,
    CalculatedMeasure,
    DataType,
    DimensionTraverser,
    HierarchyTraverser,
    InlineTable,
    LevelTraverser,
    PropertyTraverser,
    Table,
)

from .enums import (
    AnyOrder,
    Comparison,
    ConditionType,
    JoinType,
    LogicOperator,
    Membership,
    NullityOperator,
    Order,
    Restriction,
    TimeScale,
)

SingleCondition = Union[
    tuple[Literal[ConditionType.AGAINST_COLUMN], Comparison, str],
    tuple[Literal[ConditionType.AGAINST_SCALAR], Comparison, float],
    tuple[Literal[ConditionType.MEMBERSHIP], Membership, Union[Sequence[str], AbstractSet[str]]],
    tuple[Literal[ConditionType.NULLITY], NullityOperator],
]
ConditionRef = TypeVar("ConditionRef", bound=Union[SingleCondition, tuple[Any, LogicOperator, Any]])
Condition = Union[SingleCondition, tuple[ConditionRef, LogicOperator, ConditionRef]]

TimeConstraint = Union[
    tuple[Literal[Restriction.COMPLETE], Optional[str]],
    tuple[Literal[Restriction.LATEST, Restriction.OLDEST], int],
    tuple[Literal[Restriction.LEADING, Restriction.TRAILING], int],
    tuple[Literal[Restriction.EXPR], Condition[Any]],
]


def is_single_condition(condition: Condition) -> TypeGuard[SingleCondition]:
    """Check if the provided Condition object is a SingleCondition."""
    return not isinstance(condition[0], tuple)


def parse_condition(value: Sequence[str]) -> Condition:
    """Parse a condition expression.

    This could be a simple comparison, membership or nullability condition, or a
    more complex combination of these with logic operators.
    """
    if isinstance(value, str):
        if ".and." in value:
            left, right = value.split(".and.", maxsplit=1)
            return parse_condition(left), LogicOperator.AND, parse_condition(right)
        if ".or." in value:
            left, right = value.split(".or.", maxsplit=1)
            return parse_condition(left), LogicOperator.OR, parse_condition(right)
        if ".xor." in value:
            left, right = value.split(".xor.", maxsplit=1)
            return parse_condition(left), LogicOperator.XOR, parse_condition(right)

        return parse_single_condition(value)

    # value inferred as non-str sequence
    if len(value) > 2 and value[1] in {"and", "or", "xor"}:
        joint = LogicOperator.from_str(value[1])
        return parse_condition(value[0]), joint, parse_condition(value[2:])

    value = value[0] if len(value) == 1 else ".".join(str(i) for i in value)
    return parse_condition(value)


def parse_single_condition(value: str) -> SingleCondition:
    """Parse a single condition expression.

    This could be a simple comparison, membership or nullability condition.
    """
    nullity_match = NullityOperator.match(value)
    if nullity_match:
        return ConditionType.NULLITY, nullity_match

    if "." in value:
        token, reference = value.split(".", maxsplit=1)

        membership_match = Membership.match(token)
        if membership_match:
            return ConditionType.MEMBERSHIP, membership_match, reference.split(".")

        comparison = Comparison.from_str(token)
        try:
            cond = ConditionType.AGAINST_SCALAR, comparison, float(reference)
        except ValueError:
            cond = ConditionType.AGAINST_COLUMN, comparison, reference
        return cond

    msg = f"Can't parse single condition {value!r}"
    raise ValueError(msg)


class CutIntent(BaseModel):
    """Filtering instructions for a qualitative value.

    Instances of this class are used to define cut parameters.
    Its values are directly inputted by the user, so should never be considered
    valid by itself.
    """

    level: str
    include_members: set[Prim]
    exclude_members: set[Prim]

    def __lt__(self, other: object) -> bool:
        """Compare two CutIntent instances by their level name."""
        if isinstance(other, type(self)):
            return self.level < other.level
        return NotImplemented

    @model_validator(mode="before")
    @classmethod
    def parse(cls, value: object):
        if isinstance(value, str):
            value = value.split(":", 1)

        if isinstance(value, Collection) and not isinstance(value, Mapping):
            if len(value) == 2:
                level, members = value
                members = members.split(",") if isinstance(members, str) else members
                value = {
                    "level": level.lstrip("~"),
                    "include_members": [] if level.startswith("~") else members,
                    "exclude_members": members if level.startswith("~") else [],
                }

            elif len(value) == 3:
                level, incl, excl = value
                value = {"level": level, "include_members": incl, "exclude_members": excl}

        if isinstance(value, Mapping):
            nullables = {None, "", ","}
            include = value.get("include") or value["include_members"]
            exclude = value.get("exclude") or value["exclude_members"]
            value = {
                "level": value["level"],
                "include_members": set(include) - nullables,
                "exclude_members": set(exclude) - nullables,
            }

        return value


class FilterIntent(BaseModel):
    """Filtering instructions for a quantitative value.

    Instances of this class are used to define filter parameters.
    Its values are directly inputted by the user, so should never be considered
    valid by itself.
    """

    field: str
    condition: Condition

    def __lt__(self, other: object) -> bool:
        """Compare two FilterIntent instances by their level name."""
        if isinstance(other, type(self)):
            return self.field < other.field
        return NotImplemented

    @model_validator(mode="before")
    @classmethod
    def parse(cls, value: object):
        if isinstance(value, str):
            value = value.split(".", 1)

        if isinstance(value, Collection) and not isinstance(value, Mapping):
            field, *condition = value

            if not isinstance(field, str):
                msg = (
                    "When parsing a tuple, the first element must be a string with "
                    f"the name of the measure to apply the filter. Found {field!r}"
                )
                raise ValueError(msg)  # noqa: TRY004

            return {"field": field, "condition": parse_condition(condition)}

        return value


class JoinOnColumns(BaseModel):
    left_on: Union[str, list[str]]
    right_on: Union[str, list[str]]


class JoinIntent(BaseModel):
    """Specifies the intent of the user to perform a Join operation between 2 datasets."""

    on: Union[str, list[str], "JoinOnColumns", None] = None
    how: JoinType = JoinType.LEFT
    suffix: Optional[str] = None
    validate_relation: Literal["m:m", "m:1", "1:m", "1:1"] = "m:m"
    join_nulls: bool = False
    coalesce: Optional[bool] = None


class PaginationIntent(BaseModel):
    """Pagination instructions."""

    limit: Annotated[int, Field(ge=0)] = 0
    offset: Annotated[int, Field(ge=0)] = 0

    @model_validator(mode="before")
    @classmethod
    def parse(cls, value: object):
        if isinstance(value, str):
            value = (0, 0) if value == "" else value.strip().split(",")

        if isinstance(value, Sequence):
            if len(value) not in (1, 2):
                msg = f"Invalid pagination value, must provide 1 or 2 integers. Found {value!r}"
                raise ValueError(msg)
            return {"limit": value[0], "offset": value[1] if len(value) == 2 else 0}

        return value

    def as_tuple(self) -> tuple[int, int]:
        """Return the contents of this filter as a tuple of (limit, offset)."""
        return self.limit, self.offset


class SortingIntent(BaseModel):
    """Sorting instructions for internal use."""

    field: str
    order: AnyOrder

    @model_validator(mode="before")
    @classmethod
    def parse(cls, value: object):
        if isinstance(value, str):
            field, order, *_ = f"{value}.asc".split(".")
            if not field:
                msg = "Sorting field must be a valid column name"
                raise ValueError(msg)
            return {"field": field, "order": Order.match(order) or Order.ASC}

        if isinstance(value, Sequence):
            field, order, *_ = [*value, "asc"]
            if not field:
                msg = "Sorting field must be a valid column name"
                raise ValueError(msg)
            return {"field": field, "order": Order.match(order) or Order.ASC}

        return value

    def as_tuple(self) -> tuple[str, AnyOrder]:
        """Return the contents of this filter as a tuple of (field, order)."""
        return self.field, self.order


class TimeRestriction(BaseModel):
    """Time-axis filtering instructions for internal use.

    Instances of this class are used to define a time restriction over the
    resulting data. It must always contain both fields.
    """

    level: Union[str, TimeScale]
    constraint: TimeConstraint

    @model_validator(mode="before")
    @classmethod
    def parse(cls, value: object):
        if isinstance(value, str):
            if "." not in value:
                msg = "Time restriction is malformed; tokens must be separated by dots"
                raise ValueError(msg)

            value = value.split(".")

        if isinstance(value, (list, tuple)):
            if not value:
                msg = "Time restriction needs to specify a time scale/level name, and a constraint over it"
                raise ValueError(msg)

            level, *constraint = value

            # normalize ['lt.2000'] or ["lt", 2000] to ["lt", 2000]
            constraint = ".".join(constraint).split(".")

            if not level:
                msg = "Time restriction needs to specify a level from a time dimension, or a valid time scale available as level in this cube."
                raise ValueError(msg)

            # Attempt to match a TimeScale, else use value as Level name
            level = TimeScale.match(level) or level

            if not constraint:
                msg = "Time restriction needs to specify a constraint applied to the provided level, which can be a relative time frame or a filtering condition"
                raise ValueError(msg)

            token = constraint[0].strip().lower()

            restriction_match = Restriction.match(token)
            if restriction_match is Restriction.COMPLETE:
                if isinstance(level, TimeScale) and level not in (
                    TimeScale.YEAR,
                    TimeScale.QUARTER,
                ):
                    msg = "Only 'Year' and 'Quarter' time scales are available for 'complete' restriction."
                    raise ValueError(msg)
                # extra params are unused at the moment, but available in case of
                constraint = (Restriction.COMPLETE, "")
            elif restriction_match in (
                Restriction.LATEST,
                Restriction.OLDEST,
                Restriction.TRAILING,
                Restriction.LEADING,
            ):
                amount = int(constraint[1] if len(constraint) > 1 else "1")
                if amount < 1:
                    msg = "The amount of periods in the Time Restriction must be at least 1"
                    raise ValueError(msg)
                constraint = (restriction_match, amount)
            else:
                constraint = (Restriction.EXPR, parse_condition(constraint))

            return {"level": level, "constraint": constraint}

        return value


class TopkIntent(BaseModel):
    """Limits the results to the K first/last elements in subsets determined by one or more levels and their associated value.

    Adds a column that indicates the position of each element in that ranking.
    """

    levels: tuple[str, ...]
    measure: str
    order: AnyOrder = Order.DESC
    amount: int = 1

    @model_validator(mode="before")
    @classmethod
    def parse(cls, value: object):
        if isinstance(value, str):
            amount, levels, measure, order, *_ = f"{value}....".split(".")
            if not levels:
                msg = "Topk 'levels' field must contain at least a valid level name from the drilldowns in your request."
                raise ValueError(msg)
            if not measure:
                msg = "Topk 'measure' field must contain a valid measure name from the measures in your request."
                raise ValueError(msg)
            return {
                "amount": amount,
                "levels": levels.split(","),
                "measure": measure,
                "order": Order.match(order) or Order.ASC,
            }

        return value


class GrowthIntent(BaseModel):
    """Calculation of growth with respect to a time parameter and a measure."""

    time_level: str
    measure: str
    method: Union[
        tuple[Literal["period"], int],
        tuple[Literal["fixed"], str],
    ] = ("period", 1)

    @model_validator(mode="before")
    @classmethod
    def parse(cls, value: object):
        if isinstance(value, str):
            time_level, measure, *params = value.split(".")
            if not time_level:
                msg = "Growth calculation requires the name of a level from a time dimension included in your request."
                raise ValueError(msg)
            if not measure:
                msg = "Growth calculation must contain a valid measure name from the measures in your request."
                raise ValueError(msg)
            if not len(params) > 1:
                msg = (
                    "Growth calculation method requires 2 parameters: "
                    "'fixed' and the member key to use as anchor value, or "
                    "'period' and an integer for how many periods to take as difference."
                )
                raise ValueError(msg)
            method = ("fixed", params[1]) if params[0] == "fixed" else ("period", int(params[1]))
            return {"time_level": time_level, "measure": measure, "method": method}

        return value


class Column(NamedTuple):
    name: str
    alias: str

    @property
    def hash(self):
        return shorthash(self.alias + self.name)


@dcls.dataclass(eq=True, frozen=True, order=False)
class HierarchyField:
    """Contains the parameters associated to a slicing operation on the data, based on a single Hierarchy from a Cube's Dimension."""

    dimension: "DimensionTraverser"
    hierarchy: "HierarchyTraverser"
    levels: tuple["LevelField", ...]

    def __copy__(self) -> "HierarchyField":
        """Create a copy of this object and its contents."""
        return HierarchyField(
            dimension=self.dimension,
            hierarchy=self.hierarchy,
            levels=tuple(copy(level) for level in self.levels),
        )

    @property
    def alias(self) -> str:
        """Returns a deterministic unique short ID for the entity."""
        return shorthash(self.dimension.name + self.hierarchy.primary_key)

    @property
    def cut_levels(self) -> Iterable["LevelField"]:
        """Yield the levels containing a cut declaration."""
        return (item for item in self.levels if item.is_cut)

    @property
    def drilldown_levels(self) -> Iterable["LevelField"]:
        """Yield the levels declared as drilldowns."""
        return (item for item in self.levels if item.is_drilldown)

    @property
    def deepest_level(self) -> "LevelField":
        """Return the deepest LevelField requested in this Hierarchy, for this query operation."""
        # TODO: check if is needed to force this to use drilldowns only
        return self.levels[-1]

    @property
    def foreign_key(self) -> str:
        """Return the column in the fact table of the Cube this Dimension belongs to, that matches the primary key of the items in the dim_table."""
        return self.dimension.foreign_key

    @property
    def has_drilldowns(self) -> bool:
        """Verify if any of the contained LevelFields is being used as a drilldown."""
        return any(self.drilldown_levels)

    @property
    def primary_key(self) -> str:
        """Return the column in the dimension table for the parent Dimension, which is used as primary key for the whole set of levels in the chosen Hierarchy."""
        return self.hierarchy.primary_key

    @property
    def table(self) -> Union[Table, InlineTable, None]:
        """Return the table to use as source for the Dimension data.

        If not set, the data is stored directly in the fact table for the Cube.
        """
        return self.hierarchy.table


@dcls.dataclass(eq=True, frozen=True, order=False, repr=False)
class LevelField:
    """Contains the parameters associated to the slice operation, specifying the columns each resulting group should provide to the output data."""

    level: "LevelTraverser"
    level_alias: Optional[str] = None
    caption: Optional["PropertyTraverser"] = None
    is_drilldown: bool = False
    members_exclude: set[str] = dcls.field(default_factory=set)
    members_include: set[str] = dcls.field(default_factory=set)
    properties: frozenset["PropertyTraverser"] = dcls.field(default_factory=frozenset)
    time_restriction: Optional[TimeRestriction] = None

    def __copy__(self):
        return LevelField(
            level=self.level,
            level_alias=self.level_alias,
            caption=self.caption,
            is_drilldown=self.is_drilldown,
            members_exclude=set(self.members_exclude),
            members_include=set(self.members_include),
            properties=frozenset(self.properties),
            time_restriction=(
                self.time_restriction.model_copy() if self.time_restriction else None
            ),
        )

    def __repr__(self):
        params = (
            f"name={self.level.name!r}",
            f"is_drilldown={self.is_drilldown!r}",
            f"alias={self.level_alias!r}",
            f"caption={self.caption!r}",
            f"properties={sorted(self.properties, key=lambda x: x.name)!r}",
            f"cut_exclude={sorted(self.members_exclude)!r}",
            f"cut_include={sorted(self.members_include)!r}",
            f"time_restriction={self.time_restriction!r}",
        )
        return f"{type(self).__name__}({', '.join(params)})"

    @property
    def alias(self) -> str:
        """Returns a deterministic unique short ID for the entity."""
        return shorthash(self.level.name + self.level.key_column)

    @property
    def is_cut(self) -> bool:
        """Checks if this level contains a cut declaration."""
        return len(self.members_exclude) + len(self.members_include) > 0

    @property
    def key_column(self) -> str:
        """Return the key_column of the level in this field."""
        return self.level.key_column

    @property
    def name(self) -> str:
        """Return the name of the Level in this field."""
        return self.level.name

    @property
    def time_scale(self) -> TimeScale:
        """If from a Time dimension, return the time scale this Level represents."""
        return TimeScale.from_str(self.level.time_scale or self.level.name)

    def id_column(self, locale: str) -> Column:
        """Return the column used as ID for the level in this field."""
        key_column = self.level.key_column
        if self.level.get_name_column(locale) is None:
            return Column(key_column, self.level.name)
        return Column(key_column, f"{self.level.name} ID")

    def iter_columns(self, locale: str) -> Generator[Column, Any, None]:
        """Yield the related columns in the database as defined by this object.

        This comprises Drilldown ID, Drilldown Caption, and Properties.
        """
        name = self.level.name
        key_column = self.level.key_column
        name_column = self.level.get_name_column(locale)
        if name_column is None:
            yield Column(key_column, name)
        else:
            yield Column(key_column, f"{name} ID")
            yield Column(name_column, name)
        for propty in self.properties:
            propty_column = propty.get_key_column(locale)
            yield Column(propty_column, propty.name)


@dcls.dataclass(eq=True, frozen=True, order=False, repr=False)
class MeasureField:
    """MeasureField dataclass.

    Contains the parameters needed to filter the data points returned by the
    query operation from the server.
    """

    measure: "AnyMeasure"
    is_measure: bool = False
    constraint: Optional[Condition] = None
    with_ranking: Optional[Literal["asc", "desc"]] = None

    def __copy__(self):
        return MeasureField(
            measure=self.measure,
            is_measure=self.is_measure,
            constraint=(
                copy(self.constraint) if isinstance(self.constraint, tuple) else self.constraint
            ),
            with_ranking=self.with_ranking,
        )

    def __repr__(self) -> str:
        params = (
            f"name={self.measure.name!r}",
            f"is_measure={self.is_measure!r}",
            f"constraint={self.constraint!r}",
            f"with_ranking={self.with_ranking!r}",
        )
        return f"{type(self).__name__}({', '.join(params)})"

    @cached_property
    def alias_name(self) -> str:
        """Return a deterministic short hash of the name of the entity."""
        return shorthash(self.measure.name)

    @cached_property
    def alias_key(self) -> str:
        """Return a deterministic hash of the key column of the entity."""
        return shorthash(
            repr(self.measure.formula)
            if isinstance(self.measure, CalculatedMeasure)
            else self.measure.key_column,
        )

    @property
    def name(self) -> str:
        """Quick method to return the measure name."""
        return self.measure.name

    @property
    def aggregator_params(self) -> dict[str, str]:
        """Quick method to retrieve the measure aggregator params."""
        return self.measure.aggregator.get_params()

    @property
    def aggregator_type(self) -> str:
        """Quick method to retrieve the measure aggregator type."""
        return str(self.measure.aggregator)

    def get_source(self):
        # TODO add locale compatibility
        """Quick method to obtain the source information of the measure."""
        return self.measure.annotations.get("source")

    @property
    def datatype(self):
        return DataType.FLOAT64
