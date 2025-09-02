from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from pypika.dialects import ClickHouseQuery as OriginalClickhouseQuery
from pypika.dialects import ClickHouseQueryBuilder as OriginalClickhouseQueryBuilder
from pypika.enums import Dialects
from pypika.queries import Join
from pypika.terms import (
    AggregateFunction,
    AnalyticFunction,
    EmptyCriterion,
    Function,
    Term,
    ValueWrapper,
)
from pypika.utils import builder
from typing_extensions import Self

from tesseract_olap.schema import DataType

if TYPE_CHECKING:
    from pypika.queries import Selectable


class ClickHouseQuery(OriginalClickhouseQuery):
    @classmethod
    def _builder(cls, **kwargs) -> ClickHouseQueryBuilder:
        return ClickHouseQueryBuilder(
            dialect=Dialects.CLICKHOUSE,
            wrap_set_operation_queries=False,
            as_keyword=True,
            **kwargs,
        )

    @classmethod
    def from_(cls, table: Selectable | str, **kwargs) -> ClickHouseQueryBuilder:
        return cls._builder(**kwargs).from_(table)


class ClickHouseQueryBuilder(OriginalClickhouseQueryBuilder):
    QUERY_CLS = ClickHouseQuery

    def __init__(
        self,
        dialect: Dialects | None = None,
        wrap_set_operation_queries: bool = True,
        wrapper_cls: type[ValueWrapper] = ...,
        immutable: bool = True,
        as_keyword: bool = False,
    ):
        super().__init__(dialect, wrap_set_operation_queries, wrapper_cls, immutable, as_keyword)
        self._qualifies = None
        self._for_update = False  # taken over by SETTINGS keyword
        self._settings = {}

    def __copy__(self) -> ClickHouseQueryBuilder:
        newone: ClickHouseQueryBuilder = super().__copy__()  # type: ignore
        newone._qualifies = self._qualifies
        newone._settings = {**self._settings}
        return newone

    @builder
    def qualify(self, criterion: Term | EmptyCriterion) -> None:
        if isinstance(criterion, EmptyCriterion):
            return

        self._qualifies = True
        if self._havings:
            self._havings &= criterion
        else:
            self._havings = EmptyCriterion() & criterion

    @builder
    def set_setting(self, key: str, value: str) -> None:
        self._for_update = True
        self._settings[key] = value

    def _having_sql(self, quote_char: str | None = None, **kwargs) -> str:
        if self._qualifies:
            return f" QUALIFY {self._havings.get_sql(quote_char=quote_char, **kwargs)}"
        return super()._having_sql(quote_char, **kwargs)

    def _for_update_sql(self, **kwargs) -> str:
        if not self._settings:
            return ""
        return " SETTINGS " + ", ".join(f"{key}={value}" for key, value in self._settings.items())


class ClickhouseDataType(Enum):
    """Lists the types of the data the user can expect to find in the associated column."""

    BOOLEAN = "Bool"
    DATE = "Date32"
    DATETIME = "DateTime64"
    TIMESTAMP = "UInt32"
    FLOAT32 = "Float32"
    FLOAT64 = "Float64"
    INT8 = "Int8"
    INT16 = "Int16"
    INT32 = "Int32"
    INT64 = "Int64"
    INT128 = "Int128"
    UINT8 = "UInt8"
    UINT16 = "UInt16"
    UINT32 = "UInt32"  # noqa: PIE796
    UINT64 = "UInt64"
    UINT128 = "UInt128"
    STRING = "String"

    def __repr__(self) -> str:
        return f"ClickhouseDataType.{self.name}"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_datatype(cls, mt: DataType) -> ClickhouseDataType:
        """Transform a MemberType enum value into a ClickhouseDataType."""
        return cls[mt.name]

    def to_datatype(self) -> DataType:
        """Transform a ClickhouseDataType enum value into a MemberType."""
        return DataType[self.name]


class ClickhouseJoin(Join):
    def __init__(self, item: Term, how: ClickhouseJoinType) -> None:
        self.item = item
        self.how = how


class ClickhouseJoinType(Enum):
    inner = ""
    left = "LEFT"
    right = "RIGHT"
    outer = "FULL OUTER"
    left_outer = "LEFT OUTER"
    right_outer = "RIGHT OUTER"
    full_outer = "FULL OUTER"  # noqa: PIE796
    cross = "CROSS"
    asof = "ASOF"
    paste = "PASTE"


class ArrayElement(Function):
    def __init__(
        self,
        array: str | Term,
        n: int | Term,
        alias: str | None = None,
    ) -> None:
        super().__init__("arrayElement", array, n, alias=alias)


class Power(Function):
    def __init__(
        self,
        base: int | Term,
        exp: int | Term,
        alias: str | None = None,
    ):
        super().__init__("pow", base, exp, alias=alias)


class ToYYYYMMDD(Function):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("toYYYYMMDD", *args, **kwargs)


class AverageWeighted(AggregateFunction):
    def __init__(
        self,
        value_field: str | Term,
        weight_field: str | Term,
        alias: str | None = None,
    ):
        super().__init__("avgWeighted", value_field, weight_field, alias=alias)


class TopK(AggregateFunction):
    def __init__(
        self,
        amount: int,
        field: str | Term,
        alias: str | None = None,
    ):
        super().__init__(f"topK({amount:d})", field, alias=alias)


class Median(AggregateFunction):
    def __init__(
        self,
        field: str | Term,
        alias: str | None = None,
    ):
        super().__init__("median", field, alias=alias)


class Quantile(AggregateFunction):
    def __init__(
        self,
        quantile_level: float,
        field: str | Term,
        alias: str | None = None,
    ):
        if quantile_level <= 0 or quantile_level >= 1:
            msg = "The quantile_level parameter is not in the range ]0, 1["
            raise ValueError(msg)

        super().__init__(f"quantileExact({quantile_level:f})", field, alias=alias)


class DistinctCount(AggregateFunction):
    def __init__(
        self,
        field: str | Term,
        alias: str | None = None,
    ):
        super().__init__("uniqExact", field, alias=alias)


class LagInFrame(AnalyticFunction):
    def __init__(self, *args, unbounded: bool = False, **kwargs) -> None:
        super().__init__("lagInFrame", *args, **kwargs)
        self._unbounded = unbounded

    def get_partition_sql(self, **kwargs) -> str:
        partition_sql = super().get_partition_sql(**kwargs)

        if self._unbounded:
            partition_sql += " ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING"

        return partition_sql
