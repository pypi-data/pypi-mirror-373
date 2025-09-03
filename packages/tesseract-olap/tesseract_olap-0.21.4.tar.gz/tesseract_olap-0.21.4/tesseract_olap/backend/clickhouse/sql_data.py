"""SQL generation for DataQuery module."""

from __future__ import annotations

import logging
from itertools import chain
from typing import TYPE_CHECKING, Any, Union

import immutables as immu
from pypika import analytics as an
from pypika.enums import Order
from pypika.functions import Count
from pypika.queries import AliasedQuery, QueryBuilder, Selectable, Table
from pypika.terms import Criterion, EmptyCriterion, Field, Term

from tesseract_olap.backend import ParamManager
from tesseract_olap.exceptions.query import InvalidEntityName, InvalidParameter
from tesseract_olap.query import (
    DataQuery,
    HierarchyField,
    LevelField,
    Restriction,
    TimeConstraint,
)
from tesseract_olap.schema import models as sch

from .dialect import ClickHouseQuery, LagInFrame
from .sql_common import _filter_criterion, _get_aggregate, _transf_formula
from .time import (
    find_timerestriction,
    make_date_column,
    qb_timerel_yyyy,
    qb_timerel_yyyymm,
    qb_timerel_yyyymmdd,
    timerel_complete_criterion,
)

if TYPE_CHECKING:
    from collections.abc import Generator

SchemaTable = Union[sch.Table, sch.InlineTable]

logger = logging.getLogger(__name__)


def _find_measure_column_by_name(query: DataQuery, name: str) -> str:
    """Return the transient column alias for the measure of the provided name."""
    for msrfi in query.fields_quantitative:
        column_name = f"ag_{msrfi.alias_name}"
        if name == msrfi.name:
            return column_name
        if msrfi.with_ranking and name == f"{msrfi.name} Ranking":
            return f"{column_name}_rk"
        # TopK is calculated in Clickhouse when query asks TopK but not Growth
        if query.topk and not query.growth and name == f"Top {msrfi.name}":
            return "topk"

    raise InvalidEntityName("Measure", name)  # noqa: EM101


def _find_level_column_by_name(query: DataQuery, name: str) -> str:
    """Return the transient column alias for the level of the provided name."""
    for hiefi in query.fields_qualitative:
        for lvlfi in hiefi.levels:
            if lvlfi.name == name:
                return f"lv_{lvlfi.id_column(query.locale).hash}"

    raise InvalidEntityName("Level", name)  # noqa: EM101


def sql_dataquery(query: DataQuery, *, count: bool = False) -> tuple[QueryBuilder, ParamManager]:
    """Convert a DataQuery into a SQL string under Clickhouse dialect, and its parameters."""
    # Manages parameters for safe SQL execution
    meta = ParamManager(query)

    def _convert_table(table: SchemaTable, alias: str | None) -> Table:
        """Convert schema-defined tables into query tables for SQL generation."""
        if isinstance(table, sch.Table):
            return Table(table.name, schema=table.schema, alias=alias)
        return Table(table.name, alias=alias)

    def _get_table(table: SchemaTable | None, *, alias: str | None = None) -> Table:
        """Return a specified table, or the default fact table if not defined."""
        return table_fact if table is None else _convert_table(table, alias)

    table_fact = _convert_table(query.cube.table, "tfact")

    # TABLE FROM
    # Reduces the amount of rows to aggregate by applying cuts as criterions.

    tfrom = AliasedQuery("qb_from")
    qb_from = (
        ClickHouseQuery.from_(table_fact)
        .select(*_tfrom_select(query, table_fact))
        .where(_tfrom_where(query, table_fact))
    )

    # TABLE TIME
    # Apply the time restriction criterion to the tfrom set, if defined.

    ttime = tfrom
    qb_time = qb_from

    time_restriction = find_timerestriction(query)
    if time_restriction:
        # If the restriction is 'complete', we need to parse the foreign key
        # into a new column of datatype Date
        if time_restriction[2][0] is Restriction.COMPLETE:
            field_date = make_date_column(time_restriction[0], query, qb_from)
            if field_date is not None:
                qb_from = qb_from.select(field_date)

        restr_table = _get_table(time_restriction[0].table)
        ttime = AliasedQuery("qb_time")
        qb_time = _ttime_timerestriction(
            query,
            tfrom,
            restr_table,
            time_restriction,
        )

    # TABLE JOIN
    # Extends the rows with the keys used for grouping in the aggregation step.
    # At this point we also need the columns that formulas require to resolve
    # calculated measures.

    tjoin = AliasedQuery("qb_join")
    qb_join = ClickHouseQuery.from_(ttime).select(
        *_tjoin_select_measures(query, ttime),
        *_tjoin_select_levels(query, ttime),
    )

    for table, criterion in _tjoin_leftjoin(query, ttime):
        qb_join = qb_join.left_join(table).on(criterion)

    # TABLE GROUP
    # Performs the aggregation step, executes derived measures, and applies filters
    # over the results.

    tgroup = AliasedQuery("qb_group")
    qb_group = (
        ClickHouseQuery.from_(tjoin)
        .select(*_tgroup_select(query, tjoin))
        .groupby(*_tgroup_groupby(query, tjoin))
        .having(_tgroup_having(query))
    )

    # TABLE CALC
    # If requested, adds calculations to TopK and Growth.

    qb_group = _tcalc_topk(query, qb_group)
    # qb_group = _tcalc_growth(query, qb_group)

    # ENRICH QUERY
    # Filters out unnecessary columns, adds category labels, and renames
    # everything to its final labels. Also applies sorting and pagination.

    if count:
        qb = ClickHouseQuery.from_(tgroup).select(Count("*"))

    else:
        if query.sparse:
            qb = ClickHouseQuery.from_(tgroup).select(*_trich_select(query, tgroup))
            for table, criterion in _trich_leftjoin(query, tgroup):
                qb = qb.left_join(table).on(criterion)

        else:
            qb = (
                _trich_crossjoins(query, tgroup)
                .select(*_trich_select(query, tgroup))
                .set_setting("aggregate_functions_null_for_empty", "1")
            )

        # resolve criteria for sorting according to all parameters
        for field, order in _trich_sorting(query):
            qb = qb.orderby(field, order=order)

        # apply pagination parameters if values are higher than zero
        limit, offset = query.pagination.as_tuple()
        if limit > 0:
            qb = qb.limit(limit)
        if offset > 0:
            qb = qb.offset(offset)

    # adds WITHs for context
    qb = qb.with_(qb_from, tfrom.name)
    if qb_time is not qb_from:
        qb = qb.with_(qb_time, ttime.name)
    qb = qb.with_(qb_join, tjoin.name)
    qb = qb.with_(qb_group, tgroup.name)

    qb = qb.set_setting("use_query_cache", "true")

    return qb, meta


def _trich_crossjoins(query: DataQuery, tgroup: AliasedQuery) -> QueryBuilder:
    qb = None
    on_criterion = EmptyCriterion()

    for hiefi in query.fields_qualitative:
        drilldown_levels = list(hiefi.drilldown_levels)

        # if hierarchy table comes from fact table, skip cross join
        if hiefi.table is None or not drilldown_levels:
            continue

        tdim = Table(hiefi.table.name)
        drilldown_fields = [
            tdim.field(column.name)
            for lvlfi in drilldown_levels
            for column in lvlfi.iter_columns(query.locale)
        ]

        # apply cuts to crossjoined tables
        cut_criterion = EmptyCriterion()
        for lvlfi in hiefi.cut_levels:
            caster = lvlfi.level.key_type.get_caster()
            members_include = sorted(caster(mem) for mem in lvlfi.members_include)
            members_exclude = sorted(caster(mem) for mem in lvlfi.members_exclude)

            key_column = tdim.field(lvlfi.key_column)
            if members_include:
                cut_criterion &= key_column.isin(members_include)
            if members_exclude:
                cut_criterion &= key_column.notin(members_exclude)

        tdimsub = (
            ClickHouseQuery.from_(tdim)
            .select(*drilldown_fields)
            .distinct()
            .where(cut_criterion)
            .as_(f"tdim_{hiefi.alias}")
        )
        qb = ClickHouseQuery.from_(tdimsub) if qb is None else qb.cross_join(tdimsub).cross()

        key_column = drilldown_levels[-1].id_column(query.locale)
        on_criterion &= tgroup.field(f"lv_{key_column.hash}") == tdimsub.field(key_column.name)

    if qb is None:
        return ClickHouseQuery.from_(tgroup)

    return qb.left_join(tgroup).on(on_criterion)


def _tfrom_select(query: DataQuery, tfact: Selectable) -> Generator[Field, Any, None]:
    """Yield the fields from the fact table that will be used later in the queries."""
    locale = query.locale

    # get the fields from the fact table which contain the values
    # to aggregate and filter; ensure to not duplicate key_column
    yield from (
        tfact.field(key_column).as_(f"ms_{key_hash}")
        for key_column, key_hash in {
            (msrfi.measure.key_column, msrfi.alias_key)
            for msrfi in query.fields_quantitative
            if isinstance(msrfi.measure, sch.Measure)
        }
    )
    # also select the associated columns needed as parameters
    # for the advanced aggregation functions
    yield from (
        tfact.field(column).as_(f"msp_{msrfi.alias_key}_{alias}")
        for msrfi in query.fields_quantitative
        for alias, column in msrfi.measure.aggregator.get_columns()
    )

    # get the columns related to levels in the fact table
    for hiefi in query.fields_qualitative:
        if hiefi.table is None:
            # all relevant columns are in fact table
            yield from (
                tfact.field(column.name).as_(f"lv_{column.hash}")
                for lvlfi in hiefi.levels
                # levels used as cuts are not needed in select fields
                # time_restriction's are needed in a different subquery
                if lvlfi.is_drilldown or lvlfi.time_restriction
                for column in lvlfi.iter_columns(locale)
            )
        else:
            # only foreign key is available
            yield tfact.field(hiefi.foreign_key).as_(f"fk_{hiefi.alias}")


def _tfrom_where(query: DataQuery, tfact: Selectable) -> Criterion:
    """Return a set of conditions intended to be applied on the fact table.

    The objective is to reduce the initial set of data, before joins and aggregations.
    """
    criterion = EmptyCriterion()

    for hiefi in query.fields_qualitative:
        tdim = (
            tfact if hiefi.table is None else Table(hiefi.table.name, alias=f"tdim_{hiefi.alias}")
        )

        # this will unify complex criterions in case we need to use a subquery
        criterion_tdim = EmptyCriterion()

        for lvlfi in hiefi.levels:
            # check if the level has a cut directive, skip if not
            if not lvlfi.is_cut:
                continue

            caster = lvlfi.level.key_type.get_caster()
            members_include = sorted(caster(mem) for mem in lvlfi.members_include)
            members_exclude = sorted(caster(mem) for mem in lvlfi.members_exclude)

            # if target is fact table, apply criterion directly
            if hiefi.table is None or lvlfi.key_column == hiefi.primary_key:
                key_column = (
                    tfact.field(hiefi.foreign_key)
                    if lvlfi.key_column == hiefi.primary_key
                    else tfact.field(lvlfi.key_column)
                )

                if members_include:
                    criterion &= key_column.isin(members_include)
                if members_exclude:
                    criterion &= key_column.notin(members_exclude)

            # if target is dimension table, get relevant primary keys with subquery
            else:
                key_column = tdim.field(lvlfi.key_column)

                if members_include:
                    criterion_tdim &= key_column.isin(members_include)
                if members_exclude:
                    criterion_tdim &= key_column.notin(members_exclude)

        # if we need to use a subset of the fact table, the same struct applies;
        # an EmptyCriterion is ignored and it uses all primary keys available
        if not isinstance(criterion_tdim, EmptyCriterion) or (
            hiefi.table is not None and query.cube.subset_table
        ):
            field_pkey = tdim.field(hiefi.primary_key)
            # assumption: primarykey in dimension table is unique, doesn't need DISTINCT
            criterion &= tfact.field(hiefi.foreign_key).isin(
                ClickHouseQuery.from_(tdim).select(field_pkey).where(criterion_tdim),
            )

    return criterion


def _tjoin_select_measures(query: DataQuery, tfrom: Selectable) -> Generator[Field, Any, None]:
    """Generate the measure fields used to select columns in the joining query."""
    # get the fields from the fact table which contain the values
    # to aggregate and filter; ensure to not duplicate key_column
    yield from (
        tfrom.field(key_column).as_(key_column)
        for key_column in {
            f"ms_{msrfi.alias_key}"
            for msrfi in query.fields_quantitative
            if isinstance(msrfi.measure, sch.Measure)
        }
    )
    # also select the associated columns needed as parameters
    # for the advanced aggregation functions
    yield from (
        tfrom.field(f"msp_{msrfi.alias_key}_{alias}")
        for msrfi in query.fields_quantitative
        for alias, _ in msrfi.measure.aggregator.get_columns()
    )


def _tjoin_select_levels(query: DataQuery, tfrom: Selectable) -> Generator[Field, Any, None]:
    """Generate the level fields used to select columns in the joining query."""
    calcmsr_dependencies = query.formula_dependencies
    locale = query.locale

    # from levels, we need the deepest Level ID meant for aggregation, and
    # related columns used in CalculatedMeasures if applicable
    for hiefi in query.fields_qualitative:
        if hiefi.table is None:
            # all needed columns must be inherited from tfrom
            yield from (
                tfrom.field(f"lv_{column.hash}").as_(f"lv_{column.hash}")
                for lvlfi in hiefi.drilldown_levels
                for column in lvlfi.iter_columns(locale)
            )
        else:
            # needed columns must come from join operation
            tdim = Table(hiefi.table.name, alias=f"tdim_{hiefi.alias}")
            for lvlfi in hiefi.drilldown_levels:
                column_gen = lvlfi.iter_columns(locale)
                # always yield ID column
                column = next(column_gen)  # should not raise StopIteration
                if column.name == hiefi.primary_key:
                    yield tfrom.field(f"fk_{hiefi.alias}").as_(f"lv_{column.hash}")
                else:
                    yield tdim.field(column.name).as_(f"lv_{column.hash}")
                # yield other columns needed for CalculatedMeasures
                yield from (
                    tdim.field(column.name).as_(f"lv_{column.hash}")
                    for column in column_gen
                    if column.alias in calcmsr_dependencies
                )


def _tjoin_leftjoin(
    query: DataQuery,
    tfrom: Selectable,
) -> Generator[tuple[Table, Criterion], Any, None]:
    """Generate the LEFT JOIN parameters needed for the SELECT columns in this stage."""
    calcmsr_dependencies = query.formula_dependencies
    locale = query.locale

    for hiefi in query.fields_qualitative:
        if hiefi.table is None:
            continue

        # We need a LEFT JOIN if the primary_key is not the only ID column requested
        # or if there are declared calculated measures that need to be inherited
        if {lvlfi.key_column for lvlfi in hiefi.drilldown_levels} - {
            hiefi.primary_key,
        } or calcmsr_dependencies.intersection(
            column.alias
            for lvlfi in hiefi.drilldown_levels
            for column in lvlfi.iter_columns(locale)
        ):
            tdim = Table(hiefi.table.name, alias=f"tdim_{hiefi.alias}")
            yield (
                tdim,
                tfrom.field(f"fk_{hiefi.alias}") == tdim.field(hiefi.primary_key),
            )


def _ttime_timerestriction(
    query: DataQuery,
    tfrom: Selectable,
    tdim: Table,
    timerestr: tuple[HierarchyField, LevelField, TimeConstraint],
) -> QueryBuilder:
    """Generate the query to filter the tfrom query against a relative timeframe."""
    # target:
    #   build a query FROM AliasedQuery(tfrom) that keeps only rows related to relevant time
    # need:
    #   criteria that can be applied on non-extended fact table that does this subquery
    #   for this needs to return the set of primary keys that globes the subset of time
    # assumption:
    #   primary keys always are the most fine-grained unit of time available; criteria
    #   is always more general, so set of primary keys is always subset of user request

    hiefi, lvlfi, constraint = timerestr

    field_fkey = tfrom.field(f"fk_{hiefi.alias}")
    restr_column = lvlfi.id_column(query.locale)

    fields_tfrom = (tfrom.field(field.alias or "") for field in _tfrom_select(query, tfrom))

    # time_format is None if the dimension is not DimensionType.TIME, that's guaranteed here
    time_format = hiefi.dimension.fkey_time_format or ""  # the `or ""` is unreachable

    def get_field(_: str) -> Field:
        msg = "Comparisons against other columns aren't available for Time Restrictions"
        raise InvalidParameter("time", msg)

    if constraint[0] == Restriction.COMPLETE:
        criterion = timerel_complete_criterion(tfrom, hiefi, lvlfi)
        return ClickHouseQuery.from_(tfrom).select(*fields_tfrom).where(criterion)

    if constraint[0] == Restriction.LEADING or constraint[0] == Restriction.TRAILING:
        criterion = EmptyCriterion()

        if time_format == "YYYYMMDD":
            criterion = qb_timerel_yyyymmdd(query, tfrom, hiefi, lvlfi, constraint)
        elif time_format == "YYYYMM":
            criterion = qb_timerel_yyyymm(query, tfrom, hiefi, lvlfi, constraint)
        elif time_format == "YYYY":
            criterion = qb_timerel_yyyy(query, tfrom, hiefi, lvlfi, constraint)

        return ClickHouseQuery.from_(tfrom).select(*fields_tfrom).where(criterion)

    if hiefi.table is None or hiefi.primary_key == lvlfi.key_column:
        field_restr = tfrom.field(f"lv_{restr_column.hash}") if hiefi.table is None else field_fkey

        # qbA will be the query that resolves the subset of values that match the filter
        qb_a = ClickHouseQuery.from_(tfrom).select(field_restr).distinct()

        if constraint[0] is Restriction.EXPR:
            criterion = _filter_criterion(field_restr, constraint[1], get_field)
            qb_a = qb_a.where(criterion)

        else:  # Restriction.OLDEST, Restriction.LATEST
            order = Order.asc if constraint[0] == Restriction.OLDEST else Order.desc
            qb_a = qb_a.orderby(field_restr, order=order).limit(constraint[1])

        # qbB will get the subset of data that matches the time filter
        qb_b = ClickHouseQuery.from_(tfrom).select(*fields_tfrom).where(field_restr.isin(qb_a))

        return qb_b

    # This branch is more complicated; a translation from the dim table is needed

    field_restr = tdim.field(restr_column.name)
    field_pkey = tdim.field(hiefi.primary_key)

    # First we need the set of foreign keys in tfrom to filter the possible values in tdim
    qb_a = ClickHouseQuery.from_(tfrom).select(field_fkey).distinct()

    # From tdim, we select the column of the level the user wants to filter on, and get
    # its possible values filtered by the foreign keys obtained on the previous step
    qb_b = ClickHouseQuery.from_(tdim).select(field_restr).distinct().where(field_pkey.isin(qb_a))

    # We resolve and apply the user filter to this subset and get the values of the user column
    if constraint[0] is Restriction.EXPR:
        criterion = _filter_criterion(field_restr, constraint[1], get_field)
        qb_b = qb_b.having(criterion)

    else:  # Restriction.OLDEST, Restriction.LATEST
        order = Order.asc if constraint[0] == Restriction.OLDEST else Order.desc
        qb_b = qb_b.orderby(field_restr, order=order).limit(constraint[1])

    # Then we select the primary keys where the user column is in the set of the last step
    # We need to do this separatedly because we need the DISTINCT to apply to the user column
    qb_c = ClickHouseQuery.from_(tdim).select(field_pkey).where(field_restr.isin(qb_b))

    # And finally we filter tfrom using that set of primary keys against the foreign keys
    qb_d = ClickHouseQuery.from_(tfrom).select(*fields_tfrom).where(field_fkey.isin(qb_c))

    return qb_d


def _tgroup_select(query: DataQuery, tcore: Selectable) -> Generator[Term, Any, None]:
    """Yield the fields used to select columns on the grouping query."""
    locale = query.locale

    yield from _tgroup_groupby(query, tcore)

    # Enables CalculatedMeasures to use Level ID, Label, and Property
    level_columns = (
        (column.alias, tcore.field(f"lv_{column.hash}").as_(f"lv_{column.hash}"))
        for hiefi in query.fields_qualitative
        for lvlfi in hiefi.levels
        for column in lvlfi.iter_columns(locale)
    )
    measure_columns = (
        (msrfi.name, Field(f"ag_{msrfi.alias_name}")) for msrfi in query.fields_quantitative
    )
    columns = immu.Map(chain(level_columns, measure_columns))

    def _translate_col(column: str) -> Field:
        """Translate column names to fields in the grouping query."""
        return columns.get(column) or Field(column)

    for msrfi in query.fields_quantitative:
        measure = msrfi.measure
        alias = f"ag_{msrfi.alias_name}"

        if isinstance(measure, sch.Measure):
            yield _get_aggregate(tcore, measure).as_(alias)

        else:  # isinstance(measure, sch.CalculatedMeasure):
            yield _transf_formula(measure.formula, _translate_col).as_(alias)

        # Creates Ranking columns using window functions
        if msrfi.with_ranking:
            yield an.Rank(alias=f"{alias}_rk").orderby(
                Field(alias),
                order=Order.asc if msrfi.with_ranking == "asc" else Order.desc,
            )


def _tgroup_groupby(query: DataQuery, tcore: Selectable) -> Generator[Field, Any, None]:
    """Yield the fields used as categories to group by on the grouping query."""
    calcmsr_dependencies = query.formula_dependencies
    locale = query.locale

    for hiefi in query.fields_qualitative:
        if hiefi.table is None:
            yield from (
                tcore.field(f"lv_{column.hash}")
                for lvlfi in hiefi.drilldown_levels
                for column in lvlfi.iter_columns(locale)
            )
        else:
            for lvlfi in hiefi.drilldown_levels:
                column_gen = lvlfi.iter_columns(locale)
                column = next(column_gen)
                yield tcore.field(f"lv_{column.hash}")
                yield from (
                    tcore.field(f"lv_{column.hash}")
                    for column in column_gen
                    if column.alias in calcmsr_dependencies
                )


def _tgroup_having(query: DataQuery) -> Criterion:
    """Return the criterion to filter the results of the aggregation query."""
    criterion = EmptyCriterion()

    def get_field(name: str) -> Field:
        column = _find_measure_column_by_name(query, name)
        return Field(column)

    for msrfi in query.fields_quantitative:
        if msrfi.constraint:
            field = Field(f"ag_{msrfi.alias_name}")
            criterion &= _filter_criterion(field, msrfi.constraint, get_field)

    return criterion


def _trich_select(query: DataQuery, tgroup: Selectable) -> Generator[Term, Any, None]:
    """Return the final columns to select on the enriching query.

    When the query is in disabled sparse mode, as all values from the cross join
    table are matched with some values from the aggregation table, all level
    values _must_ come from the cross join table.
    """
    calcmsr_dependencies = query.formula_dependencies
    locale = query.locale

    for hiefi in query.fields_qualitative:
        if hiefi.table is None:
            # All related columns were inherited on each intermediate query
            yield from (
                tgroup.field(f"lv_{column.hash}").as_(column.alias)
                for lvlfi in hiefi.drilldown_levels
                for column in lvlfi.iter_columns(locale)
            )
        else:
            # Needed columns must come from join operation
            tdim = Table(hiefi.table.name, alias=f"tdim_{hiefi.alias}")
            for lvlfi in hiefi.drilldown_levels:
                column_gen = lvlfi.iter_columns(locale)
                if query.sparse:
                    column = next(column_gen)  # take 'Level ID' from tgroup
                    yield tgroup.field(f"lv_{column.hash}").as_(column.alias)

                    for column in column_gen:  # take the rest from tdim
                        if column.alias in calcmsr_dependencies:
                            yield tgroup.field(f"lv_{column.hash}").as_(column.alias)
                        else:
                            yield tdim.field(column.name).as_(column.alias)
                else:
                    for column in column_gen:
                        yield tdim.field(column.name).as_(column.alias)

    for msrfi in query.fields_quantitative:
        column_name = f"ag_{msrfi.alias_name}"

        if msrfi.is_measure:
            yield tgroup.field(column_name).as_(msrfi.name)

        if msrfi.with_ranking:
            yield tgroup.field(f"{column_name}_rk").as_(f"{msrfi.name} Ranking")

    if query.topk and not query.growth:
        yield tgroup.field("topk").as_(f"Top {query.topk.measure}")

    # if query.growth:
    #     yield tgroup.field("growth_value").as_(f"{query.growth.measure} Growth Value")
    #     yield tgroup.field("growth").as_(f"{query.growth.measure} Growth")


def _trich_leftjoin(
    query: DataQuery,
    tgroup: Selectable,
) -> Generator[tuple[QueryBuilder, Criterion], Any, None]:
    """Yield the LEFT JOIN parameters needed for the enriching query.

    Returns a tuple containing (selectable to join with, criterion to join on).
    """
    locale = query.locale

    for hiefi in query.fields_qualitative:
        lvlfi_columns = [
            column_list
            for column_list in (
                list(lvlfi.iter_columns(locale)) for lvlfi in hiefi.drilldown_levels
            )
            if len(column_list) > 1  # skip if only 'Level ID', as is taken from tgroup
        ]
        columns = [column for column_list in lvlfi_columns for column in column_list]
        # All needed columns from the fact table are inherited
        # Avoid LEFT JOIN if only ID column is involved
        if not hiefi.table or len(columns) < 2:  # noqa: PLR2004
            continue

        tdim = Table(hiefi.table.name)
        fields = (tdim.field(column.name) for column in columns)
        tdimsub = ClickHouseQuery.from_(tdim).select(*fields).distinct().as_(f"tdim_{hiefi.alias}")
        key_column = next(reversed(lvlfi_columns))[0]

        yield (
            tdimsub,
            tgroup.field(f"lv_{key_column.hash}") == tdimsub.field(key_column.name),
        )


def _tcalc_growth(query: DataQuery, tprev: QueryBuilder) -> QueryBuilder:
    """If defined, wraps the previous query into a new to calculate Growth."""
    if query.growth is None:
        return tprev

    msg = "We can't implement growth on the database until we have enabled sparse=False"
    raise NotImplementedError(msg)

    measure_column = _find_measure_column_by_name(query, query.growth.measure)
    growth_measure = tprev.field(measure_column)

    level_column = _find_level_column_by_name(query, query.growth.time_level)
    growth_time = tprev.field(level_column)

    growth_method = query.growth.method

    if growth_method[0] == "period":
        amount = growth_method[1]
        return ClickHouseQuery.from_(tprev).select(
            tprev.star,
            LagInFrame(growth_measure, amount, growth_measure, unbounded=True)
            .orderby(growth_time, order=Order.asc)
            .as_("growth_lag"),
            (growth_measure - Field("growth_lag")).as_("growth_value"),
            (Field("growth_value") / Field("growth_lag")).as_("growth"),
        )

    if growth_method[0] == "fixed":
        pivot = growth_method[1]
        raise NotImplementedError
        return ClickHouseQuery.from_(tprev).select()

    msg = "Invalid growth_method parameter"
    raise ValueError(msg)  # unreachable


def _tcalc_topk(query: DataQuery, tprev: QueryBuilder) -> QueryBuilder:
    """If defined, wraps the previous query into a new to calculate TopK.

    Build the query which will perform the grouping by drilldown members,
    and then the aggregation over the resulting groups.
    """
    # Do not calculate topK on clickhouse if growth is requested
    if query.growth:
        return tprev

    if query.topk is None:
        return tprev

    locale = query.locale

    # Get the list of fields to create the windows
    drilldown_map = {
        lvlfi.name: lvlfi.id_column(locale)
        for hiefi in query.fields_qualitative
        for lvlfi in hiefi.drilldown_levels
    }
    try:
        topk_levels = [
            tprev.field(f"lv_{column.hash}")
            for column in [drilldown_map[level] for level in query.topk.levels]
        ]
    except KeyError as exc:
        raise InvalidEntityName("Level", exc.args[0]) from None  # noqa: EM101

    # Get the field used to rank values within the windows
    try:
        value_column = _find_measure_column_by_name(query, query.topk.measure)
        topk_value = tprev.field(value_column)
    except InvalidEntityName:
        value_column = drilldown_map.get(query.topk.measure)
        if value_column is None:
            raise
        topk_value = tprev.field(f"lv_{value_column.hash}")

    topk_order = Order.asc if query.topk.order == "asc" else Order.desc

    return (
        ClickHouseQuery.from_(tprev)
        .select(
            tprev.star,
            an.RowNumber().over(*topk_levels).orderby(topk_value, order=topk_order).as_("topk"),
        )
        .qualify(Field("topk") <= query.topk.amount)
    )


def _trich_sorting(query: DataQuery) -> Generator[tuple[Field, Order], Any, None]:
    """Resolve the sorting directions for the main query."""
    locale = query.locale

    level_map = {
        lvlfi.level.name: column.alias
        for hiefi in query.fields_qualitative
        for lvlfi in hiefi.drilldown_levels
        for column in [lvlfi.id_column(locale)]
    }
    property_set = {
        propty.name
        for hiefi in query.fields_qualitative
        for lvlfi in hiefi.drilldown_levels
        for propty in lvlfi.properties
    }

    if query.sorting:
        sort_field, sort_order = query.sorting.as_tuple()
        order = Order.asc if sort_order == "asc" else Order.desc

        # find matching measure to sort_field
        gen_measures = (
            msrfi.measure for msrfi in query.fields_quantitative if sort_field == msrfi.name
        )
        measure = next(gen_measures, None)
        if measure:
            yield Field(measure.name), order

        # find matching level to sort_field
        elif sort_field in level_map:
            yield Field(level_map[sort_field]), order

        # find matching property to sort_field
        elif sort_field in property_set:
            yield Field(sort_field), order

    elif query.topk and not query.growth:
        yield from (
            (Field(level_map[level]), Order.asc)
            for level in query.topk.levels
            if level in level_map
        )
        if query.topk.amount > 1:
            yield Field(f"Top {query.topk.measure}"), Order.asc

    else:
        yield from (
            (Field(lvlfi.id_column(locale).alias), Order.asc)
            for hiefi in query.fields_qualitative
            if (not query.topk or hiefi.deepest_level.name in query.topk.levels)
            for lvlfi in hiefi.drilldown_levels
        )
