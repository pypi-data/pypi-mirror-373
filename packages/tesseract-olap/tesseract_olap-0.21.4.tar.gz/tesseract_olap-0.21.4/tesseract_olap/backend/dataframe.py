import hashlib
from datetime import datetime, timezone
from typing import Literal, Optional, TypedDict, Union

import polars as pl
from dateutil.relativedelta import relativedelta

from tesseract_olap.exceptions.query import InvalidQuery
from tesseract_olap.query import (
    AnyQuery,
    DataQuery,
    JoinIntent,
    JoinOnColumns,
    PaginationIntent,
)
from tesseract_olap.query.enums import TimeScale
from tesseract_olap.query.models import LevelField
from tesseract_olap.schema import DataType, DimensionType

from .models import Result


def is_integer_dtype(dtype: pl.DataType) -> bool:
    return dtype in (
        pl.Int8,
        pl.Int16,
        pl.Int32,
        pl.Int64,
        pl.UInt8,
        pl.UInt16,
        pl.UInt32,
        pl.UInt64,
    )


def generate_lag_column(
    lvlfi: LevelField,
    series: pl.Series,
    delta: int,
) -> pl.Expr:
    """Generate a pl.Expr for a lag of delta periods.

    The returned expression represents the same series used as reference,
    but with each value lagged by delta units.
    """
    time_scale = lvlfi.time_scale

    if time_scale is TimeScale.YEAR:
        # assumes integer column
        return pl.col(series.name) - delta

    if time_scale is TimeScale.QUARTER:
        template = quarter_template(str(series[0]))
        return pl.col(series.name).map_elements(
            lambda x: int(template.format(*shift_quarter(str(x), delta))) if is_integer_dtype(series.dtype) else template.format(*shift_quarter(str(x), delta)),
            return_dtype=series.dtype,
        )
    if time_scale is TimeScale.MONTH:
        # assumes integer format YYYYMM
        return pl.col(series.name).map_elements(
            lambda x: calc_month_delta(str(x), delta),
            return_dtype=series.dtype,
        )
    # TODO: TimeScale.WEEK
    if time_scale is TimeScale.DAY:
        # assumes integer format YYYYMMDD
        return pl.col(series.name).map_elements(
            lambda x: calc_day_delta(str(x), delta),
            return_dtype=series.dtype,
        )

    raise ValueError(f"Invalid time_id format: {series[0]}")


def parse_quarter(value: str) -> tuple[int, int]:
    return int(value[0:4]), int(value[4:].replace("-", "").replace("Q", ""))


def quarter_template(value: str) -> str:
    year, quarter = parse_quarter(value)
    pre, _, post = value.rpartition(str(quarter))
    return "{}".join([pre.replace(str(year), "{}", 1), post])


def shift_quarter(time_id: str, amount: int) -> tuple[int, int]:
    year, quarter = parse_quarter(time_id)
    # transform time column to datetime format
    curr_date = datetime(year, (quarter - 1) * 3 + 1, 1, tzinfo=timezone.utc)
    prev_date = curr_date - relativedelta(months=3 * amount)
    # get the quartile to which each month belongs
    prev_quarter = (prev_date.month - 1) // 3 + 1
    return prev_date.year, prev_quarter


def calc_month_delta(time_id: str, amount: int):
    # transform time column to datetime format
    current_date = datetime.strptime(f"{time_id[0:4]}-{time_id[4:6]}", "%Y-%m")
    prev_date = current_date - relativedelta(months=amount)
    return int(prev_date.strftime("%Y%m"))


def calc_day_delta(time_id: str, amount: int):
    # Parse the time_id into a datetime instance
    date = datetime.strptime(time_id, "%Y%m%d")
    # Subtract the delta_days
    new_date = date - relativedelta(days=amount)
    # Return the new date in 'YYYYMMDD' format
    return int(new_date.strftime("%Y%m%d"))


def growth_calculation(query: AnyQuery, df: pl.DataFrame) -> pl.DataFrame:
    # Return df unchanged if Growth does not apply
    if df.is_empty() or not isinstance(query, DataQuery) or query.growth is None:
        return df

    # define parameters
    time_name = query.growth.time_level
    measure = query.growth.measure
    method = query.growth.method

    try:
        hiefi, lvlfi = next(
            (hiefi, lvlfi)
            for hiefi in query.fields_qualitative
            if hiefi.dimension.dim_type is DimensionType.TIME
            for lvlfi in hiefi.drilldown_levels
            if lvlfi.name == time_name
        )
    except StopIteration:
        msg = f"Time level '{time_name}' is required as a drilldown for its own growth calculation"
        raise InvalidQuery(msg) from None

    time_id = (
        lvlfi.name if lvlfi.level.get_name_column(query.locale) is None else f"{lvlfi.name} ID"
    )
    topk = f"Top {query.topk.measure}" if query.topk else None

    # include different measures
    cols_measure = {
        measure.name
        for msrfi in query.fields_quantitative
        for measure in msrfi.measure.and_submeasures()
    }
    cols_timelevels = {
        column.alias
        for lvlfi in hiefi.drilldown_levels
        for column in lvlfi.iter_columns(query.locale)
    }
    cols_drill_without_time_measure = set(df.columns) - ({topk, *cols_measure, *cols_timelevels})

    if method[0] == "period":
        amount = method[1]

        expr_prev_period = generate_lag_column(lvlfi, df[time_id], amount)
        df_current = df.with_columns(expr_prev_period.alias("time_prev"))

        df = df_current.join(
            # filter the time_prev column string if it exists
            df.select([*cols_drill_without_time_measure, time_id, measure]).rename(
                {time_id: "time_prev", measure: "previous_measure"},
            ),
            on=[*cols_drill_without_time_measure, "time_prev"],
            how="left",
        )

        expr_prev_measure = pl.col("previous_measure").cast(pl.Float64)
        # calculate the absolute change
        col_growth_value = pl.col(measure).cast(pl.Float64) - expr_prev_measure
        # calculate the percentage change
        col_growth = col_growth_value / expr_prev_measure

    else:
        type_caster = lvlfi.level.key_type.get_caster()
        member_key = type_caster(method[1])

        if len(cols_drill_without_time_measure) == 0:
            # create a "dummy" column in case there are no columns for the join
            df = df.with_columns([pl.lit(1).alias("dummy")])
            cols_drill_without_time_measure.add("dummy")

        # first, we get the values ​​at fixed time per group
        df_fixed = (
            df.filter(pl.col(time_id) == member_key)
            .select([*cols_drill_without_time_measure, measure])
            .rename({measure: "previous_measure"})
        )

        # join the fixed values ​​to the original df
        df = df.join(df_fixed, on=list(cols_drill_without_time_measure), how="left")

        # calculate the absolute change with a conditional
        col_growth_value = (
            pl.when(pl.col(time_id) < member_key)
            .then(pl.col("previous_measure").cast(pl.Float64) - pl.col(measure).cast(pl.Float64))
            .otherwise(
                pl.col(measure).cast(pl.Float64) - pl.col("previous_measure").cast(pl.Float64),
            )
        )

        # calculate the percentage change with a conditional
        col_growth = (
            pl.when(pl.col(time_id) < member_key)
            .then(col_growth_value / pl.col(measure).cast(pl.Float64))
            .otherwise(col_growth_value / pl.col("previous_measure").cast(pl.Float64))
        )

    df = df.with_columns(
        col_growth_value.alias(f"{measure} Growth Value"),
        col_growth.alias(f"{measure} Growth"),
    )

    # remove temporary column 'previous measure' and 'dummy'
    columns_to_drop = ["previous_measure", "time_prev", "dummy"]
    existing_columns = [col for col in columns_to_drop if col in df.columns]
    df = df.drop(existing_columns)

    return df


def topk_calculation(query: AnyQuery, df: pl.DataFrame) -> pl.DataFrame:
    if df.is_empty() or not isinstance(query, DataQuery) or query.topk is None:
        return df

    # Calculate topK on dataframe if growth is requested
    if not query.growth:
        return df

    topk_measure = query.topk.measure
    topk_levels = query.topk.levels
    topk_colname = f"Top {topk_measure}"
    topk_desc = query.topk.order == "desc"

    return (
        df.with_columns(
            pl.col(topk_measure)
            .rank(method="dense", descending=topk_desc)
            .over(topk_levels)
            .alias(topk_colname),
        )
        .filter(pl.col(topk_colname) <= query.topk.amount)
        .sort((*topk_levels, topk_measure), descending=topk_desc)
    )


class JoinParameters(TypedDict, total=False):
    on: Union[str, list[str]]
    left_on: Union[str, list[str]]
    right_on: Union[str, list[str]]
    coalesce: Optional[bool]
    nulls_equal: bool
    suffix: str
    validate: Literal["m:m", "m:1", "1:m", "1:1"]


class JoinStep:
    data: pl.DataFrame
    keys: list[str]
    statuses: list[str]

    def __init__(
        self,
        data: pl.DataFrame,
        *,
        keys: list[str],
        statuses: list[str],
    ):
        self.data = data
        self.keys = keys
        self.statuses = statuses

    def join_with(self, result: Result[pl.DataFrame], join: JoinIntent):
        params: JoinParameters = {
            "suffix": join.suffix or "_",
            "validate": join.validate_relation,
            "nulls_equal": join.join_nulls,
            "coalesce": join.coalesce,
        }

        if isinstance(join.on, (str, list)):
            params.update(on=join.on)
        elif isinstance(join.on, JoinOnColumns):
            params.update(left_on=join.on.left_on, right_on=join.on.right_on)

        return JoinStep(
            self.data.join(result.data, how=join.how.value, **params),
            keys=[*self.keys, result.cache["key"]],
            statuses=[*self.statuses, result.cache["status"]],
        )

    def get_result(self, pagi: PaginationIntent):
        df = self.data

        cache_key = "/".join(self.keys).encode("utf-8")
        return Result(
            data=df.slice(pagi.offset, pagi.limit or None),
            columns={
                k: DataType.from_polars(v) for k, v in dict(zip(df.columns, df.dtypes)).items()
            },
            cache={
                "key": hashlib.md5(cache_key, usedforsecurity=False).hexdigest(),
                "status": ",".join(self.statuses),
            },
            page={"limit": pagi.limit, "offset": pagi.offset, "total": df.height},
        )

    @classmethod
    def new(cls, result: Result[pl.DataFrame]):
        return cls(
            result.data,
            keys=[result.cache["key"]],
            statuses=[result.cache["status"]],
        )


def rename_columns(query: DataQuery, df: pl.DataFrame) -> pl.DataFrame:
    alias_label = {
        lvlfi.level.name: lvlfi.level_alias
        for hiefi in query.fields_qualitative
        for lvlfi in hiefi.drilldown_levels
        if lvlfi.level_alias is not None
    }
    alias_id = {
        f"{key} ID": f"{value} ID"
        for key, value in alias_label.items()
        if f"{key} ID" in df.columns
    }
    return df.rename({**alias_label, **alias_id})
