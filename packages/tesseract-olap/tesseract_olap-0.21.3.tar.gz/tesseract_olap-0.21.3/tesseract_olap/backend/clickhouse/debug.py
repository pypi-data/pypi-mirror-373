from tesseract_olap.backend import ParamManager
from tesseract_olap.schema import InlineTable

from .dialect import ClickhouseDataType


def inlinetable_to_sql(table: InlineTable):
    definition = ", ".join(
        f"{name} {ClickhouseDataType.from_datatype(dtype)}"
        for name, dtype in zip(table.headers, table.types)
    )
    values = ", ".join(str(row) for row in table.rows)
    return f"SELECT * FROM VALUES('{definition}', {values})"


def debug_single_query(sql: str, meta: ParamManager) -> dict[str, str]:
    return {
        "tables": "\n".join(
            f"{table.name} AS {inlinetable_to_sql(table)}" for table in meta.tables
        ),
        "query": sql,
        "params": "\n".join(f"{key!r}: {value!r}" for key, value in meta.params.items()),
    }
