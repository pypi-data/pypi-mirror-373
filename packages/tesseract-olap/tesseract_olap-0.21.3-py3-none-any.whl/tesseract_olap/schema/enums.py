from __future__ import annotations

from collections.abc import Sequence
from enum import Enum
from typing import Any, Callable

import polars as pl

from tesseract_olap.common import FALSEY_STRINGS


class SchemaEnum(Enum):
    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"

    def __str__(self) -> str:
        return self.value


class AggregatorType(SchemaEnum):
    """Possible aggregation operations to perform on the data to return a measure."""

    SUM = "sum"
    COUNT = "count"
    AVERAGE = "avg"
    MAX = "max"
    MIN = "min"
    MODE = "mode"
    BASICGROUPEDMEDIAN = "basic_grouped_median"
    WEIGHTEDSUM = "weighted_sum"
    WEIGHTEDAVERAGE = "weighted_avg"
    REPLICATEWEIGHTMOE = "replicate_weight_moe"
    CALCULATEDMOE = "moe"
    WEIGHTEDAVERAGEMOE = "weighted_average_moe"
    MEDIAN = "median"
    QUANTILE = "quantile"
    DISTINCTCOUNT = "distinct_count"

    @classmethod
    def from_str(cls, value: str | None) -> AggregatorType:
        """Return the matching AggregatorType from a string value."""
        return cls(value.lower()) if value else cls.SUM


class DimensionType(SchemaEnum):
    """Kind of data a dimension is storing."""

    STANDARD = "standard"
    TIME = "time"
    GEO = "geo"

    @classmethod
    def from_str(cls, value: str | None) -> DimensionType:
        """Return the matching DimensionType from a string value."""
        return cls(value.lower()) if value else cls.STANDARD


class DataType(SchemaEnum):
    """Types of the data the user can expect to find in the associated column."""

    BOOLEAN = "bool"
    DATE = "date"
    TIME = "time"
    DATETIME = "dttm"
    TIMESTAMP = "stmp"
    FLOAT32 = "f32"
    FLOAT64 = "f64"
    INT8 = "i8"
    INT16 = "i16"
    INT32 = "i32"
    INT64 = "i64"
    INT128 = "i128"
    UINT8 = "u8"
    UINT16 = "u16"
    UINT32 = "u32"
    UINT64 = "u64"
    UINT128 = "u128"
    STRING = "str"

    def get_caster(self) -> Callable[[str], int | float | bool | str]:
        """Return a function to parse a string value into the correct type."""
        pldt = self.to_polars()
        if pldt.is_integer():
            return int
        if pldt.is_float():
            return float
        if self is DataType.BOOLEAN:
            return lambda value: value not in FALSEY_STRINGS
        return str

    def to_polars(self) -> type[pl.DataType]:
        """Return the matching polars.DataType from a tesseract_olap.DataType."""
        return _POLARS_DATATYPES[self]

    @classmethod
    def from_str(cls, value: str | None) -> DataType:
        """Return the matching DataType from a string value."""
        return cls(value.lower()) if value else cls.INT64

    @classmethod
    def from_polars(cls, value: pl.DataType) -> DataType:
        """Return a tesseract_olap.DataType from a polars.DataType."""
        return _POLARS_DATATYPES_REVERSE[type(value)]

    @classmethod
    def from_values(cls, values: Sequence[Any]) -> DataType:
        """Return a DataType able to store all the provided values."""
        types = {type(value) for value in values}

        if len(types) == 1 and bool in types:
            return DataType.BOOLEAN

        if float in types:
            return DataType.FLOAT64

        if int in types:
            return cls.from_int_values(values)

        return DataType.STRING

    @classmethod
    def from_int_values(cls, values: Sequence[int]) -> DataType:
        """Return the minimal DataType that allows to store the provided integer."""
        mini = min(values)
        maxi = max(values)

        if mini < 0:
            if mini < -(2**63) or maxi > 2**63 - 1:
                return cls.INT128
            if mini < -(2**31) or maxi > 2**31 - 1:
                return cls.INT64
            if mini < -(2**15) or maxi > 2**15 - 1:
                return cls.INT32
            if mini < -128 or maxi > 127:
                return cls.INT16
            return cls.INT8

        if maxi > 2**64 - 1:
            return cls.UINT128
        if maxi > 2**32 - 1:
            return cls.UINT64
        if maxi > 65535:
            return cls.UINT32
        if maxi > 255:
            return cls.UINT16
        return cls.UINT8


_POLARS_DATATYPES: dict[DataType, type[pl.DataType]] = {
    DataType.BOOLEAN: pl.Boolean,
    DataType.DATE: pl.Date,
    DataType.TIME: pl.Time,
    DataType.DATETIME: pl.Datetime,
    DataType.TIMESTAMP: pl.UInt64,
    DataType.FLOAT32: pl.Float32,
    DataType.FLOAT64: pl.Float64,
    DataType.INT8: pl.Int8,
    DataType.INT16: pl.Int16,
    DataType.INT32: pl.Int32,
    DataType.INT64: pl.Int64,
    DataType.INT128: pl.Int64,
    DataType.UINT8: pl.UInt8,
    DataType.UINT16: pl.UInt16,
    DataType.UINT32: pl.UInt32,
    DataType.UINT64: pl.UInt64,
    DataType.UINT128: pl.UInt64,
    DataType.STRING: pl.String,
}

_POLARS_DATATYPES_REVERSE = {value: key for key, value in _POLARS_DATATYPES.items()}
