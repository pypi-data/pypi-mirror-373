from __future__ import annotations

import contextlib
import csv
from collections.abc import Generator, Iterable, Sequence
from email.message import Message
from pathlib import Path
from typing import TextIO

import immutables as immu

from tesseract_olap.common import is_numeric, numerify

from . import models

DELIMITER_TRANSLATE = immu.Map(
    comma=",",
    semicolon=";",
    tab="\t",
    space=" ",
)


class ColumnTypeInferrer:
    def __init__(self, iterable: Iterable[str], csv_params: dict):
        self.csv_params = csv_params
        self.headers = ""
        self.iterator = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self):
        row = next(self.iterator)
        if self.headers:
            row_items = next(csv.reader([row], **self.csv_params))
            self.types = [itype and is_numeric(item) for item, itype in zip(row_items, self.types)]
        else:
            self.headers = list(csv.reader(row))
            self.types = [True for item in self.headers]
        return row

    def cast(
        self,
        table: Iterable[Sequence[str]],
    ) -> Generator[tuple[float | str, ...], None, None]:
        iterator = iter(table)
        yield tuple(next(iterator))
        yield from (
            tuple(numerify(item) if is_num else item for item, is_num in zip(row, self.types))
            for row in iterator
        )


class CSVSchema(models.Schema):
    pass


class CSVInlineTable(models.InlineTable):
    pass


def parse_csv(
    content: Iterable[str],
    *,
    dialect: str | csv.Dialect = "",
    mimetype: str = "",
    **kwargs,
) -> list[tuple[float | str, ...]]:
    """General use function to parse a CSV string, from an external source.

    `kwargs` are the parameters to define a :class:`csv.Dialect`.
    """
    dialects = csv.list_dialects()
    if isinstance(dialect, csv.Dialect) or dialect in dialects:
        return [tuple(item) for item in csv.reader(content, dialect)]

    if mimetype:
        msg = Message()
        msg.add_header("Content-Type", mimetype)
        options = dict(msg.get_params(failobj=[], header="Content-Type")[1:])

        dialect = options.get("dialect", "")
        if dialect != "":
            return parse_csv(content, dialect=dialect)

        kwargs.update(options)

    if "delimiter" in kwargs:
        delimiter = kwargs["delimiter"]
        kwargs["delimiter"] = DELIMITER_TRANSLATE.get(delimiter, delimiter)

    content = ColumnTypeInferrer(content, kwargs)
    table = tuple(csv.reader(content, **kwargs))
    return list(content.cast(table))


def parse_csv_schema(source: str | Path | TextIO, table_name: str = "") -> CSVSchema:
    if isinstance(source, Path):
        if not table_name:
            table_name = source.name.replace(source.suffix, "")
        with source.open("r", encoding="utf8") as io:
            headers, *rows = parse_csv(io)

    elif isinstance(source, str):
        headers, *rows = parse_csv(source.splitlines())

    else:  # isinstance(a, TextIO) has runtime issues
        with contextlib.suppress(AttributeError):
            table_name = table_name if table_name else source.name
        headers, *rows = parse_csv(source.readlines())
        source.close()

    table = CSVInlineTable(
        name=table_name,
        headers=tuple(str(item) for item in headers),
        types=CSVInlineTable.infer_types(rows),
        rows=tuple(rows),
    )

    return CSVSchema(
        name="",
        default_locale="",
        shared_table_map=immu.Map([(table.name, table)]),
    )
