"""Schema Aggregators module.

Contains the different types of aggregator that can be used in the definition of
a Measure in the Schema.
"""

import dataclasses as dcls
from typing import Any, Dict, Iterable, List, Tuple, Union

from typing_extensions import TypeGuard

from .enums import AggregatorType


def _get_fields(obj: object) -> List[str]:
    """Returns a set of strings, with the names of the fields in this class."""
    return sorted(f.name for f in dcls.fields(obj)) if dcls.is_dataclass(obj) else []


class Aggregator:
    """Base class for aggregator methods.

    The instances contain parameters to compose the associated SQL query.
    Backend packages should extend these according to support, and implement
    the methods needed for conversion to string.
    """

    def __repr__(self):
        params = ", ".join(
            f"{field}={repr(getattr(self, field))}" for field in _get_fields(self)
        )
        return f"{type(self).__name__}({params})"

    def __str__(self) -> str:
        return type(self).__name__

    def __iter__(self):
        yield "type", type(self).__name__
        yield from ((field, getattr(self, field)) for field in _get_fields(self))

    def get_params(self) -> Dict[str, str]:
        """Returns a dict with the serialized params of the instance.

        Base class just returns an empty dict. More complex subclasses must
        override this method."""
        return dict((field, getattr(self, field)) for field in _get_fields(self))

    def get_columns(self) -> Iterable[Tuple[str, str]]:
        """Returns the columns needed to calculate this aggregation."""
        return set()

    @classmethod
    def new(cls, kwargs: Dict[str, Any]) -> "Aggregator":
        field_names = _get_fields(cls)
        return cls(**{k: v for k, v in kwargs.items() if k in field_names})

    @staticmethod
    def from_enum(enum: AggregatorType) -> "Aggregator":
        agg_classes = {
            AggregatorType.AVERAGE: Average,
            AggregatorType.COUNT: Count,
            AggregatorType.MAX: Max,
            AggregatorType.MEDIAN: Median,
            AggregatorType.MIN: Min,
            AggregatorType.MODE: Mode,
            AggregatorType.SUM: Sum,
            AggregatorType.BASICGROUPEDMEDIAN: BasicGroupedMedian,
            AggregatorType.CALCULATEDMOE: CalculatedMoe,
            AggregatorType.QUANTILE: Quantile,
            AggregatorType.REPLICATEWEIGHTMOE: ReplicateWeightMoe,
            AggregatorType.WEIGHTEDAVERAGE: WeightedAverage,
            AggregatorType.WEIGHTEDAVERAGEMOE: WeightedAverageMoe,
            AggregatorType.WEIGHTEDSUM: WeightedSum,
            AggregatorType.DISTINCTCOUNT: DistinctCount,
        }
        return agg_classes[enum]


class Sum(Aggregator):
    pass


class Count(Aggregator):
    pass


class Average(Aggregator):
    pass


class Max(Aggregator):
    pass


class Min(Aggregator):
    pass


class Mode(Aggregator):
    pass


class Median(Aggregator):
    pass


class DistinctCount(Aggregator):
    pass


@dcls.dataclass(frozen=True)
class Quantile(Aggregator):
    """Quantile is calculated against the measure's value column.

    `quantileExact(quantile_level)(column)`

    where quantile_level = Quantile level between 0 and 1
    """

    quantile_level: Union[str, float]


@dcls.dataclass(frozen=True)
class BasicGroupedMedian(Aggregator):
    group_aggregator: str
    group_dimension: str


@dcls.dataclass(frozen=True)
class WeightedSum(Aggregator):
    """Weighted Sum is calculated against the measure's value column.

    `sum(column * weight_column)`

    First roll-up is sum(column * weight_column) as weighted_sum_first
    Second roll-up is sum(weighted_sum_first) as weighted_sum_final
    """

    weight_column: str

    def get_columns(self):
        yield "weight", self.weight_column


@dcls.dataclass(frozen=True)
class WeightedAverage(Aggregator):
    """Weighted Average is calculated against the measure's value column.

    `sum(column * weight_column) / sum(weight_column)`
    """

    weight_column: Union[str, Tuple[str, float]]

    def get_columns(self):
        if _is_column(self.weight_column):
            yield "weight", self.weight_column


@dcls.dataclass(frozen=True)
class ReplicateWeightMoe(Aggregator):
    """Where the measure column is the primary value, and a list of secondary
    columns is provided to the MO aggregator:

    The general equation for Margin of Error is

    `cv * pow(df * (pow(sum(column) - sum(secondary_columns[0]), 2) + pow(sum(column) - sum(secondary_columns_[1]), 2) + ...), 0.5)`

    where cv = critical value, for 90% confidence interval it's 1.645
    where df = design factor / #samples
    """

    critical_value: float
    design_factor: float
    secondary_columns: List[str]

    def get_columns(self):
        return (
            (f"secondary_{index}", item)
            for index, item in enumerate(self.secondary_columns)
        )


@dcls.dataclass(frozen=True)
class CalculatedMoe(Aggregator):
    """Where the moe is already calculated for each row, and this just
    aggregates them correctly.

    `sqrt(sum(power(moe / cv, 2))) * cv`

    where cv = critical value; for 90% confidence interval it's 1.645
    """

    critical_value: Union[str, float]


@dcls.dataclass(frozen=True)
class WeightedAverageMoe(Aggregator):
    """
    Where the measure column is the primary value,
    and a list of secondary weight columns is provided to the MO aggregator:

    The general equation for Margin of Error is

    `cv * pow(df * (pow(( sum(column * primary_weight)/sum(primary_weight) ) - ( sum(column * secondary_weight_columns[0])/sum(secondary_weight_columns[0]) ), 2) + pow(( sum(column * primary_weight)/sum(primary_weight) ) - ( sum(column * secondary_weight_columns[1]/sum(secondary_weight_columns[1]) ), 2) + ...), 0.5)`

    where cv = critical value, for 90% confidence interval it's 1.645
    where df = design factor / #samples
    """

    critical_value: float
    design_factor: float
    primary_weight: str
    secondary_weight_columns: List[str]

    def get_columns(self):
        if _is_column(self.primary_weight):
            yield "primary", self.primary_weight
        yield from (
            (f"secondary_{index}", item)
            for index, item in enumerate(self.secondary_weight_columns)
        )


def _is_column(value: Any) -> TypeGuard[str]:
    try:
        return isinstance(value, str) and not float(value)
    except ValueError:
        return True
    return False
