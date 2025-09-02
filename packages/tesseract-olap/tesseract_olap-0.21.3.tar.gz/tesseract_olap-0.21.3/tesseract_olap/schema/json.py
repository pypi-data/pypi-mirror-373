import json
from functools import lru_cache
from pathlib import Path
from typing import Callable, Dict, TextIO, Union

from tesseract_olap.common import T

from . import models


class JSONSchema(models.Schema):
    @classmethod
    def parse(cls, root: dict):
        raise NotImplementedError("Parsing for JSONSchema is not yet available.")

        cubes_mapper = _mapper_factory("cubes", "name", JSONCube.parse)
        dimensions_mapper = _mapper_factory("dimensions", "name", JSONDimension.parse)
        tables_mapper = _mapper_factory("inline_tables", "name", JSONInlineTable.parse)

        return cls(
            name=root["name"],
            annotations=root.get("annotations", {}),
            cubes=cubes_mapper(root),
            shared_dimensions=dimensions_mapper(root),
            shared_tables=tables_mapper(root),
            default_role=root.get("default_role"),
            default_locale=root.get("default_locale", "xx"),
        )


class JSONCube(models.Cube):
    @classmethod
    def parse(cls, root: dict):
        raise NotImplementedError()


class JSONDimension(models.Dimension):
    @classmethod
    def parse(cls, root: dict):
        raise NotImplementedError()


class JSONInlineTable(models.InlineTable):
    @classmethod
    def parse(cls, root: dict):
        raise NotImplementedError()


@lru_cache(10)
def _mapper_factory(
    parent_obj: str,
    property_name: str,
    reducer: Callable[[dict], T],
) -> Callable[[dict], Dict[str, T]]:
    """ """

    def mapper_func(root: dict) -> Dict[str, T]:
        return {item[property_name]: reducer(item) for item in root.get(parent_obj, [])}

    return mapper_func


def parse_json_schema(source: Union[str, Path, TextIO]) -> JSONSchema:
    """Attempts to parse an object into a JSONSchema.

    This function accepts:
    - A raw JSON :class:`str`
    - A local path (as a :class:`pathlib.Path`) to a JSON file
    - A not-binary read-only :class:`TextIO` instance for a file-like object
    """
    contents: Union[str, bytes]

    # if argument is pathlib.Path, resolve its contents
    if isinstance(source, Path):
        contents = source.read_bytes()

    # if argument is str, parse its contents directly
    elif isinstance(source, str):
        contents = source

    # if argument is a file-like, attempt to read it
    else:
        contents = source.read()
        source.close()

    root = json.loads(contents)
    return JSONSchema.parse(root)
