from __future__ import annotations

import logging
from itertools import chain

from pypika import functions as fn
from pypika.enums import Order
from pypika.queries import QueryBuilder, Table
from pypika.terms import Criterion, Field, PyformatParameter

from tesseract_olap.backend import ParamManager
from tesseract_olap.common import shorthash
from tesseract_olap.query import MembersQuery
from tesseract_olap.schema import CubeTraverser, DataType, models

from .dialect import ClickhouseJoin, ClickhouseJoinType, ClickHouseQuery

logger = logging.getLogger(__name__)


def sql_membersquery(
    query: MembersQuery,
    *,
    count: bool = False,
) -> tuple[QueryBuilder, ParamManager]:
    """Build the query which will list all the members of a Level in a dimension table.

    Depending on the filtering parameters set by the user, this list can also
    be limited by pagination, search terms, or members observed in a fact table.
    """
    if count:
        qb, meta = sql_membersquery(query)
        return ClickHouseQuery.from_(qb).select(fn.Count("*")), meta

    meta = ParamManager()

    def _convert_table(table: models.Table | models.InlineTable, alias: str | None) -> Table:
        if isinstance(table, models.Table):
            return Table(table.name, schema=table.schema, alias=alias)
        meta.set_table(table)
        return Table(table.name, alias=alias)

    locale = query.locale
    hiefi = query.hiefield

    table_fact = _convert_table(query.cube.table, "tfact")

    table_dim = (
        _convert_table(query.cube.table, "tdim")
        if hiefi.table is None
        else _convert_table(hiefi.table, "tdim")
    )

    ancestor_columns = (
        (alias, column_name)
        for depth, lvlfi in enumerate(hiefi.levels[:-1])
        for alias, column_name in (
            (f"ancestor.{depth}.key", lvlfi.level.key_column),
            (f"ancestor.{depth}.caption", lvlfi.level.get_name_column(locale)),
        )
    )
    property_columns = (
        (f"properties.{prop.name}", prop.get_key_column(locale))
        for prop in hiefi.deepest_level.properties
    )
    level_columns = (
        ("key", hiefi.deepest_level.level.key_column),
        ("caption", hiefi.deepest_level.level.get_name_column(locale)),
    )

    level_fields = tuple(
        Field(column_name, alias=alias, table=table_dim)
        for alias, column_name in chain(level_columns, ancestor_columns, property_columns)
        if column_name is not None
    )

    subquery = (
        ClickHouseQuery.from_(table_fact)
        .select(table_fact.field(hiefi.foreign_key))
        .distinct()
        .as_("tfact_distinct")
    )

    qb: QueryBuilder = (
        ClickHouseQuery.from_(table_dim)
        .select(*level_fields)
        .distinct()
        .where(table_dim.field(hiefi.primary_key).isin(subquery))
        .orderby(*level_fields, order=Order.asc)
    )

    limit, offset = query.pagination.as_tuple()
    if limit > 0:
        qb = qb.limit(limit)
    if offset > 0:
        qb = qb.offset(offset)

    if query.search is not None:
        pname = meta.set_param(f"%{query.search}%")
        param = PyformatParameter(pname)
        search_criterion = Criterion.any(
            Field(field).ilike(param)  # type: ignore
            for lvlfield in query.hiefield.levels
            for field in (
                lvlfield.level.key_column if lvlfield.level.key_type == DataType.STRING else None,
                lvlfield.level.get_name_column(locale),
            )
            if field is not None
        )
        qb = qb.where(search_criterion)

    return qb, meta


def sql_cubemembers(cube: CubeTraverser) -> tuple[QueryBuilder, ParamManager]:
    fact_table = Table(cube.table.name, alias="tfact")
    query = ClickHouseQuery._builder()
    meta = ParamManager()
    flag_join = False

    for dimension in cube.dimensions:
        for hierarchy in dimension.hierarchies:
            table = hierarchy.table
            table_alias = shorthash(f"{dimension.name}.{hierarchy.name}")
            levels = [(level, shorthash(level.name)) for level in hierarchy.levels]

            if table is None:
                gen_columns = (
                    fn.Count(fact_table.field(level.key_column), alias).distinct()
                    for level, alias in levels
                )
                tquery = (
                    ClickHouseQuery.from_(fact_table).select(*gen_columns).as_(f"sq_{table_alias}")
                )

            else:
                if isinstance(table, models.InlineTable):
                    meta.set_table(table)

                dim_table = Table(table.name, alias="tdim")

                gen_columns = (
                    fn.Count(dim_table.field(level.key_column), alias).distinct()
                    for level, alias in levels
                )
                tquery = (
                    ClickHouseQuery.from_(dim_table)
                    .select(*gen_columns)
                    .where(
                        dim_table.field(hierarchy.primary_key).isin(
                            ClickHouseQuery.from_(fact_table)
                            .select(fact_table.field(dimension.foreign_key))
                            .distinct(),
                        ),
                    )
                    .as_(f"sq_{table_alias}")
                )

            if flag_join:
                query.do_join(ClickhouseJoin(tquery, ClickhouseJoinType.paste))
            else:
                query = query.from_(tquery)
                flag_join = True

            gen_fields = (tquery.field(alias).as_(level.name) for level, alias in levels)
            query = query.select(*gen_fields)

    return query, meta
