import enum
from typing import Literal, Union

from strenum import StrEnum

AnyOrder = Union[Literal["asc", "desc"], "Order"]


class ConditionType(enum.Enum):
    """Defines available kind of condition to apply over a column."""

    AGAINST_COLUMN = enum.auto()
    AGAINST_SCALAR = enum.auto()
    MEMBERSHIP = enum.auto()
    NULLITY = enum.auto()


class ParseableStrEnum(StrEnum):
    def __repr__(self):
        return f"{type(self).__name__}.{self.name}"

    def __str__(self):
        return self.value

    @classmethod
    def from_str(cls, string: str):
        value = string.strip().lower()
        if not value:
            msg = f"Can't parse {cls.__name__} from empty string"
            raise ValueError(msg)
        value = EXTRA_VALUE_MAPPINGS.get((cls, value), value)
        return cls(value)

    @classmethod
    def match(cls, string: str):
        try:
            return cls.from_str(string)
        except ValueError:
            return None


class Comparison(ParseableStrEnum):
    """Defines the available comparison operations."""

    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    EQ = "eq"
    NEQ = "neq"


class JoinType(ParseableStrEnum):
    """Defines the different types of join operations available to the user."""

    INNER = "inner"
    LEFT = "left"
    RIGHT = "right"
    FULL = "full"
    SEMI = "semi"
    ANTI = "anti"
    CROSS = "cross"


class LogicOperator(ParseableStrEnum):
    """Defines logical operations between conditional predicates."""

    AND = "and"
    OR = "or"
    XOR = "xor"


class Membership(ParseableStrEnum):
    """Specifies the membership relation of a value to a set."""

    IN = "in"
    NIN = "nin"


class NullityOperator(ParseableStrEnum):
    """Evaluates if a value is or not is NULL."""

    ISNULL = "isnull"
    ISNOTNULL = "isnotnull"


class Order(ParseableStrEnum):
    """Defines a direction to use in a sorting operation."""

    ASC = "asc"
    DESC = "desc"


class TimeScale(ParseableStrEnum):
    """Specifies a scale of detail in time."""

    YEAR = "year"
    QUARTER = "quarter"
    MONTH = "month"
    WEEK = "week"
    DAY = "day"


class Restriction(ParseableStrEnum):
    COMPLETE = "complete"
    LATEST = "latest"
    OLDEST = "oldest"
    TRAILING = "trailing"
    LEADING = "leading"
    EXPR = "expr"


EXTRA_VALUE_MAPPINGS: dict[tuple[type[ParseableStrEnum], str], str] = {
    (Comparison, "!="): Comparison.NEQ,
    (Comparison, "<"): Comparison.LT,
    (Comparison, "<="): Comparison.LTE,
    (Comparison, "<>"): Comparison.NEQ,
    (Comparison, "="): Comparison.EQ,
    (Comparison, "=="): Comparison.EQ,
    (Comparison, ">"): Comparison.GT,
    (Comparison, ">="): Comparison.GTE,
    (LogicOperator, "&"): LogicOperator.AND,
    (LogicOperator, "^"): LogicOperator.XOR,
    (LogicOperator, "|"): LogicOperator.OR,
    (Membership, "notin"): Membership.NIN,
    (Restriction, "earliest"): Restriction.OLDEST,
    (Restriction, "last"): Restriction.LATEST,
}
