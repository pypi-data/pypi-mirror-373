from __future__ import annotations

from typing import TYPE_CHECKING

from . import SchemaError

if TYPE_CHECKING:
    from lxml import etree


class XMLParseError(SchemaError):
    """An error happened while trying to parse a XML Schema."""


class MalformedXML(XMLParseError):
    """An unexpected node was found."""

    def __init__(self, expected: str, actual: str | etree._Element) -> None:
        message = f"A node '{actual}' was found while attempting to parse a '{expected}'"
        super().__init__(message)


class InvalidXMLAttributeName(XMLParseError):
    """An invalid attribute was found in a node."""

    def __init__(self, node: str, node_name: str, attr: str) -> None:
        message = f"An attribute '{attr}' was found while attempting to parse {node} '{node_name}'"
        super().__init__(message)


class InvalidXMLAttributeValue(XMLParseError):
    """An invalid value was found in the attribute of a node."""

    def __init__(self, node: str, node_name: str, attr: str, value: str) -> None:
        message = (
            f"An invalid value '{value}' for the '{attr}' attribute was found while "
            f"trying to parse {node} '{node_name}'"
        )
        super().__init__(message)


class MissingXMLNode(XMLParseError):
    """A required child node is missing."""

    def __init__(self, node: str, node_name: str, child_node: str) -> None:
        message = f"A '{child_node}' child node is missing in {node} '{node_name}'"
        super().__init__(message)


class MissingXMLAttribute(XMLParseError):
    """A required attribute is not present."""

    def __init__(self, node: str, attr: str) -> None:
        message = f"A required attribute '{attr}' is missing in a '{node}' node"
        super().__init__(message)


class JSONParseError(SchemaError):
    """An error happened while trying to parse a JSON Schema."""


class MalformedJSON(JSONParseError):
    """An unexpected object was found."""

    def __init__(self, expected: str) -> None:
        message = ""
        super().__init__(message)


class MissingPropertyError(SchemaError):
    """A mandatory property couldn't be retrieved from a Shared/Usage entity combination."""

    def __init__(self, entity: str, name: str, attr: str):
        message = f"There's a missing '{attr}' attribute in {entity} '{name}'."
        super().__init__(message)


class InvalidNameError(SchemaError):
    """The name of an Entity contains invalid characters."""

    def __init__(self, cube: str, entity: str, name: str) -> None:
        message = (
            f"There's a {entity} with an invalid name '{name}' in the cube '{cube}'. "
            "Entity names can't contain the characters colon (:), dot (.), or comma (,)."
        )
        super().__init__(message)


class DuplicateKeyError(SchemaError):
    """The key of some property in the schema is shared in two nodes."""

    def __init__(self, key: str) -> None:
        message = f"Key '{key}' is duplicated"
        super().__init__(message)


class DuplicatedNameError(SchemaError):
    """The name of an Entity is duplicated across its parent cube."""

    def __init__(self, cube: str, entity_prev: str, entity: str, name: str):
        message = (
            f"In the cube '{cube}' a {entity_prev} and a {entity} share the same name '{name}'. "
            "Names of Measures, Levels and Properties must be unique across its cube."
        )
        super().__init__(message)


class EntityUsageError(SchemaError):
    """A declared Usage reference points to a non-existent shared Entity."""

    def __init__(self, entity: str, source: str) -> None:
        message = f"An usage reference for '{source}' {entity} cannot be found."
        super().__init__(message)
