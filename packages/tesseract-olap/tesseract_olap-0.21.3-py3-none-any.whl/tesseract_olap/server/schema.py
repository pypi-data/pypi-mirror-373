import logging
from itertools import chain
from pathlib import Path
from typing import TextIO, Union

import httpx

from tesseract_olap.exceptions.server import UnknownSchemaError
from tesseract_olap.schema import (
    Schema,
    parse_csv_schema,
    parse_json_schema,
    parse_xml_schema,
)

logger = logging.getLogger(__name__)


def setup_schema(source: Union[str, Path, TextIO]) -> "Schema":
    """Generate a new Schema instance from a string source.

    The source can be a path to a local file, an URL to an external schema file,
    or the text content of a schema file to be parsed.
    Raises a :class:`ValueError` instance if the source can't be recognized as
    either of these.
    """
    # if argument is string...
    if isinstance(source, str):
        source = source.strip()

        # Check if argument is a URL and fetch the file
        if source.startswith(("http:", "https:", "ftp:")):
            return _parse_source_url(source)

        # Try to parse string as raw contents
        result = _parse_source_raw_string(source)
        if result is not None:
            return result

        # Assume source is a filesystem path
        # Transform it and let next block handle it
        source = Path(source)

    # if argument is a pathlib.Path, open it and parse contents
    if isinstance(source, Path):
        source = source.resolve()

        if not source.exists():
            msg = f"Path {source} does not exist"
            raise FileNotFoundError(msg)

        if source.is_file():
            return _parse_path_file(source)

        if source.is_dir():
            logger.debug("Looking for schemas in local directory: %s", source)
            schemas = (
                _parse_path_file(item)
                for item in chain(source.glob("**/*.csv"), source.glob("**/*.xml"))
                if item.is_file()
            )
            return Schema.join(*schemas)

    msg = f"Schema source can't be recognized as URL, file or raw string: {source}"
    raise UnknownSchemaError(msg)


def _parse_source_url(source: str) -> "Schema":
    """Attempt to fetch a remote URL and parse its contents as a Schema."""
    response = httpx.get(source)
    if response.is_error:
        msg = f"Problem retrieving remote schema file '{source}': Error {response.status_code}"
        raise FileNotFoundError(msg)

    path = response.url.path
    ctype = response.headers["Content-Type"].lower()
    text = response.text.strip()

    if path.endswith(".xml") or ctype == "text/xml" or text.startswith(("<Schema ", "<?xml ")):
        logger.debug("Parsing XML schema from URL: %s", source)
        return parse_xml_schema(text)

    if path.endswith(".json") or ctype == "application/json" or text.startswith(('{"', "[{")):
        logger.debug("Parsing JSON schema from URL: %s", source)
        return parse_json_schema(text)

    if path.endswith(".csv") or ctype in ("text/csv", "application/vnd.ms-excel"):
        logger.debug("Parsing CSV table from URL: %s", source)
        _, _, table_name = path.rpartition("/")
        table_name = table_name.replace(".csv", "")
        return parse_csv_schema(text, table_name)

    msg = f"Linked source couldn't be parsed: {source}"
    raise UnknownSchemaError(msg)


def _parse_source_raw_string(source: str) -> Union["Schema", None]:
    """Attempt to parse the contents of the provided string as a Schema."""
    # Check if argument is a raw XML string
    if source.startswith(("<Schema ", "<?xml ")):
        logger.debug("Parsing XML schema from string")
        return parse_xml_schema(source)

    # Check if argument is a raw JSON string
    if source.startswith(('{"', "[{")):
        logger.debug("Parsing JSON schema from string")
        return parse_json_schema(source)

    # A raw CSV here doesn't provide a valid Schema, so bypass
    return None


def _parse_path_file(item: Path) -> "Schema":
    """Attempt parsing the contents of a reference to a local file as a Schema."""
    if item.suffix == ".xml":
        logger.debug("Parsing XML schema from file contents: %s", item)
        return parse_xml_schema(item)

    if item.suffix == ".json":
        logger.debug("Parsing JSON schema from file contents: %s", item)
        return parse_json_schema(item)

    if item.suffix == ".csv":
        logger.debug("Parsing CSV table from file contents: %s", item)
        return parse_csv_schema(item)

    result = _parse_source_raw_string(item.read_text())
    if result is not None:
        return result

    msg = f"File contents couldn't be parsed: {item}"
    raise UnknownSchemaError(msg)
