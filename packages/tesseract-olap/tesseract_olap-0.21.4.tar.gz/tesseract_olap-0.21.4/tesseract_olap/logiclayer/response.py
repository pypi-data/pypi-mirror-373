from __future__ import annotations

import logging
from collections.abc import Generator, Mapping
from dataclasses import dataclass
from io import BytesIO
from typing import Any

import orjson
import polars as pl
from fastapi import HTTPException
from fastapi.responses import PlainTextResponse, Response, StreamingResponse
from strenum import StrEnum
from typing_extensions import Self

from tesseract_olap.backend import Result
from tesseract_olap.common import AnyDict
from tesseract_olap.query import DataMultiQuery, DataQuery, MembersQuery
from tesseract_olap.schema import Annotations, DataType, TesseractProperty

logger = logging.getLogger(__name__)


class ResponseFormat(StrEnum):
    """Define the extensions available to the user and how to response to them."""

    csv = "csv"
    csvbom = "csvbom"
    excel = "xlsx"
    jsonarrays = "jsonarrays"
    jsonrecords = "jsonrecords"
    parquet = "parquet"
    tsv = "tsv"
    tsvbom = "tsvbom"

    def get_mimetype(self) -> str:
        """Return the matching mimetype for the current enum value."""
        return MIMETYPES[self]


MIMETYPES = {
    ResponseFormat.csv: "text/csv",
    ResponseFormat.csvbom: "text/csv",
    ResponseFormat.excel: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ResponseFormat.jsonarrays: "application/json",
    ResponseFormat.jsonrecords: "application/json",
    ResponseFormat.parquet: "application/vnd.apache.parquet",
    ResponseFormat.tsv: "text/tab-separated-values",
    ResponseFormat.tsvbom: "text/tab-separated-values",
}


@dataclass(eq=False, order=False)
class MembersResponseModel:
    """Describes a level, its properties, and its associated members in the backend."""

    name: str
    caption: str
    depth: int
    annotations: Annotations
    properties: list[TesseractProperty]
    dtypes: Mapping[str, DataType]
    members: list[AnyDict]

    @classmethod
    def from_result(cls, query: MembersQuery, result: Result[list[AnyDict]]) -> Self:
        locale = query.locale
        lvlfi = query.hiefield.deepest_level
        level = lvlfi.level

        return cls(
            name=level.name,
            caption=level.get_caption(locale),
            depth=level.depth,
            annotations=dict(level.annotations),
            properties=[TesseractProperty.from_entity(item, locale) for item in level.properties],
            dtypes=result.columns,
            members=[nest_dict(row) for row in result.data]
            if len(query.hiefield.levels) > 1 or lvlfi.properties
            else result.data,
        )


def data_response(
    query: DataQuery | DataMultiQuery,
    result: Result[pl.DataFrame],
    extension: ResponseFormat,
) -> Response:
    """Generate a Response object containing the result of the provided query."""
    df = result.data
    columns = tuple(df.columns)

    headers = {
        "X-Tesseract-Cache": result.cache.get("status", "MISS"),
        "X-Tesseract-Columns": ",".join(columns),
        "X-Tesseract-QueryRows": str(df.height),
        "X-Tesseract-TotalRows": str(result.page["total"]),
    }
    kwargs: AnyDict = {"headers": headers, "media_type": extension.get_mimetype()}

    if extension in (ResponseFormat.csv, ResponseFormat.csvbom):
        with_bom = extension is ResponseFormat.csvbom
        content = df.write_csv(separator=",", include_bom=with_bom, include_header=True)
        headers["Content-Disposition"] = f'attachment; filename="{query.filename}.{extension}"'
        return PlainTextResponse(content, **kwargs)

    if extension in (ResponseFormat.tsv, ResponseFormat.tsvbom):
        with_bom = extension is ResponseFormat.tsvbom
        content = df.write_csv(separator="\t", include_bom=with_bom, include_header=True)
        headers["Content-Disposition"] = f'attachment; filename="{query.filename}.{extension}"'
        return PlainTextResponse(content, **kwargs)

    if extension is ResponseFormat.jsonarrays:
        streamer = _stream_jsonarrays(result, annotations=query.get_annotations())
        return StreamingResponse(streamer, **kwargs)

    if extension is ResponseFormat.jsonrecords:
        streamer = _stream_jsonrecords(result, annotations=query.get_annotations())
        return StreamingResponse(streamer, **kwargs)

    if extension is ResponseFormat.excel:
        content = BytesIO()
        df.write_excel(content)
        headers["Content-Disposition"] = f'attachment; filename="{query.filename}.{extension}"'
        return PlainTextResponse(content.getbuffer(), **kwargs)

    if extension is ResponseFormat.parquet:
        content = BytesIO()
        df.write_parquet(content)
        headers["Content-Disposition"] = f'attachment; filename="{query.filename}.{extension}"'
        return PlainTextResponse(content.getbuffer(), **kwargs)

    raise HTTPException(406, f"Requested format is not supported: {extension}")


def nest_dict(flat_dict: dict[str, Any]) -> dict[str, Any]:
    """Convert a flat dictionary with dot-notation keys into a nested dictionary or list structure.

    This function transforms keys with dot-separated components into nested objects.
    Numeric indices create lists, while string keys create nested dictionaries.

    Args:
        input_dict (dict): A dictionary with potentially nested keys using dot notation

    Returns:
        dict: A nested dictionary with hierarchical structure based on input keys

    Example:
        >>> flatten_nested_dict({"key": 101, "ancestor.0.key": 1})
        {"key": 101, "ancestor": [{"key": 1}]}

    """
    nested_dict = {}

    for key, value in flat_dict.items():
        key_parts = key.split(".")  # Split the key by periods

        # Traverse or create the nested structure
        current = nested_dict
        for part in key_parts[:-1]:
            # Check if the part is a number (array index)
            if part.isdigit():
                # Ensure the parent is a list
                if not isinstance(current, list):
                    current = nested_dict[key_parts[0]] = []

                index = int(part)
                while len(current) <= index:
                    current.append({})  # Extend list if needed

                # Move to the specific list item
                current = current[index]

            else:
                if part not in current:
                    current[part] = {}  # Create nested dict if not exists
                current = current[part]

        # Set the final value, assuming it never ends with digit
        current[key_parts[-1]] = value

    return nested_dict


def _stream_jsonarrays(
    result: Result[pl.DataFrame],
    *,
    annotations: AnyDict,
    chunk_size: int = 100000,
) -> Generator[bytes]:
    """Return a JSON Records representation of the data through a Generator."""
    data = result.data
    yield b'{"annotations":%b,"page":%b,"columns":%b,"data":[' % (
        orjson.dumps(annotations),
        orjson.dumps(result.page),
        orjson.dumps(data.columns),
    )
    for index in range(0, data.height + 1, chunk_size):
        data_chunk = data.slice(index, chunk_size).to_dict(as_series=False)
        # we have the indivitual columns, transform in individual rows
        trasposed = list(zip(*(data_chunk[key] for key in data.columns)))
        comma = b"," if index + chunk_size < data.height else b""
        # remove JSON array brackets and add comma if needed
        yield orjson.dumps(trasposed)[1:-1] + comma
    yield b"]}"


def _stream_jsonrecords(
    result: Result[pl.DataFrame],
    *,
    annotations: dict[str, Any],
    chunk_size: int = 100000,
) -> Generator[bytes]:
    """Return a JSON Records representation of the data through a Generator."""
    data = result.data
    yield b'{"annotations":%b,"page":%b,"columns":%b,"data":[' % (
        orjson.dumps(annotations),
        orjson.dumps(result.page),
        orjson.dumps(data.columns),
    )
    for index in range(0, data.height + 1, chunk_size):
        data_chunk = data.slice(index, chunk_size).to_dicts()
        # JSON is picky with trailing commas, use them only if not finished
        comma = b"," if index + chunk_size < data.height else b""
        # remove JSON array brackets and add comma
        yield orjson.dumps(data_chunk)[1:-1] + comma
    yield b"]}"
