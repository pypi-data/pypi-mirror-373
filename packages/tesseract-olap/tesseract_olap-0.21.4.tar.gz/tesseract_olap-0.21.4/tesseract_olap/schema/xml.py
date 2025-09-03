"""XML Schema parsing module.

Defines subclasses for the core Entity classes, parsed from an XML document.
"""

import logging
from ast import literal_eval as eval_tuple
from collections import OrderedDict
from collections.abc import Generator, Iterable
from pathlib import Path
from typing import Optional, TextIO, TypeVar, Union

import immutables as immu
from lxml import etree

from tesseract_olap.common import TRUTHY_STRINGS, T, is_numeric, numerify
from tesseract_olap.exceptions.schema import (
    DuplicateKeyError,
    InvalidXMLAttributeValue,
    MissingXMLAttribute,
    MissingXMLNode,
)

from . import models
from .aggregators import Aggregator
from .csv import parse_csv
from .enums import AggregatorType, DataType, DimensionType

logger = logging.getLogger(__name__)

XMLEntity = Union[
    "XMLSharedDimension",
    "XMLHierarchy",
    "XMLLevel",
    "XMLProperty",
    "XMLInlineTable",
    "XMLCube",
    "XMLDimensionUsage",
    "XMLHierarchyUsage",
    "XMLLevelUsage",
    "XMLPropertyUsage",
    "XMLPrivateDimension",
    "XMLMeasure",
    "XMLCalculatedMeasure",
]

AnyXMLDimension = TypeVar(
    "AnyXMLDimension",
    bound=Union["XMLSharedDimension", "XMLPrivateDimension"],
)
AnyXMLEntity = TypeVar("AnyXMLEntity", bound=XMLEntity)

FKEY_TIME_FORMATS = ("YYYYMMDD", "YYYYMM", "YYYYQ", "YYYYQQ", "YYYY-Q", "YYYY-QQ", "YYYY")


class XMLSchema(models.Schema):
    tag = "Schema"

    @classmethod
    def parse(cls, node: etree._Element, index: int = 0):
        """Parse a <Schema> XML node."""
        name = _get_attr(node, "name")
        logger.debug("Parsing node <%s name='%s' />", cls.tag, name)

        return cls(
            name=name,
            cube_map=OrderedDict(
                _raise_if_duplicate(_yield_children_nodes(node, XMLCube)),
            ),
            shared_dimension_map=immu.Map(
                _raise_if_duplicate(_yield_children_nodes(node, XMLSharedDimension)),
            ),
            shared_table_map=immu.Map(
                _raise_if_duplicate(_yield_children_nodes(node, XMLInlineTable)),
            ),
            default_locale=node.get("default_locale", "xx"),
            annotations=immu.Map(_yield_annotations(node)),
        )


class XMLAccessControl(models.AccessControl):
    tag = "Access"

    @classmethod
    def parse(cls, node: etree._Element):
        """Parse all <Access> XML node that are directly under this node."""
        return cls(
            public=_get_boolean(node, "public", True),
            rules=immu.Map(
                _raise_if_duplicate(
                    (role, _get_attr(item, "rule") == "allow")
                    for item in node.iterchildren(cls.tag)
                    for role in _get_attr(item, "roles").split(",")
                ),
            ),
        )


class XMLCube(models.Cube):
    tag = "Cube"

    @classmethod
    def parse(cls, node: etree._Element, index: int):
        """Parse a <Cube> XML node."""
        name = _get_attr(node, "name")
        logger.debug("Parsing node <%s name='%s' />", cls.tag, name)

        table = _find_table_ref(node)
        if table is None:
            raise MissingXMLNode(node.tag, name, "Table")

        dimension_map = OrderedDict(
            _raise_if_duplicate(
                _yield_children_nodes(node, XMLPrivateDimension, XMLDimensionUsage),
            ),
        )
        if len(dimension_map) == 0:
            raise MissingXMLNode(node.tag, name, "Dimension")

        measure_map = OrderedDict(
            _raise_if_duplicate(
                _yield_children_nodes(node, XMLMeasure, XMLCalculatedMeasure),
            ),
        )
        if len(measure_map) == 0:
            raise MissingXMLNode(node.tag, name, "Measure")

        return cls(
            name=name,
            captions=immu.Map(
                _raise_if_duplicate(_yield_locale_pairs(node, "caption")),
            ),
            acl=XMLAccessControl.parse(node),
            dimension_map=dimension_map,
            measure_map=measure_map,
            table=table,
            annotations=immu.Map(_yield_annotations(node)),
            subset_table=_get_boolean(node, "subset_table", False),
            visible=_get_boolean(node, "visible", True),
        )


class XMLDimensionUsage(models.DimensionUsage):
    tag = "DimensionUsage"

    @classmethod
    def parse(cls, node: etree._Element, index: int):
        """Parse a <DimensionUsage> XML node."""
        name = _get_attr(node, "name")
        logger.debug("Parsing node <%s name='%s' />", cls.tag, name)

        time_format = node.get("fkey_time")
        if time_format not in (*FKEY_TIME_FORMATS, None):
            raise InvalidXMLAttributeValue(node.tag, name, "fkey_time", time_format)

        return cls(
            name=name,
            source=_get_attr(node, "source"),
            foreign_key=_get_attr(node, "foreign_key"),
            annotations=immu.Map(_yield_annotations(node)),
            captions=immu.Map(
                _raise_if_duplicate(_yield_locale_pairs(node, "caption")),
            ),
            fkey_time_format=time_format,
            hierarchy_map=OrderedDict(
                _raise_if_duplicate(
                    _yield_children_nodes(node, XMLHierarchyUsage, attr="source"),
                ),
            ),
            visible=_get_boolean(node, "visible", True),
        )


class XMLHierarchyUsage(models.HierarchyUsage):
    tag = "HierarchyUsage"

    @classmethod
    def parse(cls, node: etree._Element, index: int):
        """Parse a <HierarchyUsage> XML node."""
        name = _get_attr(node, "name")
        logger.debug("Parsing node <%s name='%s' />", cls.tag, name)

        return cls(
            name=name,
            source=_get_attr(node, "source"),
            annotations=immu.Map(_yield_annotations(node)),
            captions=immu.Map(
                _raise_if_duplicate(_yield_locale_pairs(node, "caption")),
            ),
            level_map=OrderedDict(
                _raise_if_duplicate(
                    _yield_children_nodes(node, XMLLevelUsage, attr="source"),
                ),
            ),
            visible=_get_boolean(node, "visible", True),
        )


class XMLLevelUsage(models.LevelUsage):
    tag = "LevelUsage"

    @classmethod
    def parse(cls, node: etree._Element, index: int):
        """Parse a <LevelUsage> XML node."""
        name = _get_attr(node, "name")
        logger.debug("Parsing node <%s name='%s' />", cls.tag, name)

        return cls(
            name=name,
            source=_get_attr(node, "source"),
            annotations=immu.Map(_yield_annotations(node)),
            captions=immu.Map(
                _raise_if_duplicate(_yield_locale_pairs(node, "caption")),
            ),
            property_map=OrderedDict(
                _raise_if_duplicate(
                    _yield_children_nodes(node, XMLPropertyUsage, attr="source"),
                ),
            ),
            visible=_get_boolean(node, "visible", True),
        )


class XMLPropertyUsage(models.PropertyUsage):
    tag = "PropertyUsage"

    @classmethod
    def parse(cls, node: etree._Element, index: int):
        """Parse a <PropertyUsage> XML node."""
        name = _get_attr(node, "name")
        logger.debug("Parsing node <%s name='%s' />", cls.tag, name)

        return cls(
            name=name,
            source=_get_attr(node, "source"),
            annotations=immu.Map(_yield_annotations(node)),
            captions=immu.Map(
                _raise_if_duplicate(_yield_locale_pairs(node, "caption")),
            ),
            visible=_get_boolean(node, "visible", True),
        )


class XMLTable(models.Table):
    tag = "Table"

    @classmethod
    def parse(cls, node: etree._Element, index: int):
        """Parse a <Table> XML node."""
        name = _get_attr(node, "name")
        logger.debug("Parsing node <%s name='%s' />", cls.tag, name)

        return cls(
            name=name,
            schema=node.get("schema"),
            primary_key=node.get("primary_key", "id"),
        )


class XMLInlineTable(models.InlineTable):
    tag = "InlineTable"

    @classmethod
    def parse(cls, node: etree._Element, index: int):
        """Parse a <InlineTable> XML node."""
        name = _get_attr(node, "name")
        logger.debug("Parsing node <%s name='%s' />", cls.tag, name)

        node_format = _get_attr(node, "format")

        if node_format == "csv":
            node_format = "text/csv"

        if node_format == "tuples":
            headers, rows = cls.parse_tuples(node)
        elif node_format.startswith("text/csv"):
            content = [] if node.text is None else node.text.strip().splitlines()
            headers, *rows = parse_csv(content, mimetype=node_format)
            headers = tuple(str(item) for item in headers)
        else:
            raise InvalidXMLAttributeValue(node.tag, name, "format", node_format)

        return cls(
            name=name,
            headers=headers,
            types=cls.infer_types(rows),
            rows=tuple(rows),
        )

    @staticmethod
    def parse_tuples(
        node: etree._Element,
    ) -> tuple[tuple[str, ...], list[tuple[Union[str, float], ...]]]:
        """Parse the child nodes from an InlineTable with `tuples` format."""
        try:
            # try parsing literal tuples with ast.eval()
            children: list[tuple[Union[str, float], ...]] = [
                eval_tuple(line)
                for line in (item.text for item in node.iterchildren("Row"))
                if line
            ]
        except SyntaxError:
            # Python `tuples` looks similar to CSV, so let's try with it
            row_iter = (
                line[1:-1] if line.startswith("(") and line.endswith(")") else line
                for line in (item.text for item in node.iterchildren("Row"))
                if line is not None
            )
            children = parse_csv(row_iter, skipinitialspace=True)
        # at least 2 rows must be present: a header list and a data row
        if len(children) < 2:
            raise MissingXMLNode(node.tag, _get_attr(node, "name"), "Row")
        headers = tuple(str(item) for item in children[0])
        return headers, children[1:]


class XMLDimension(models.Dimension):
    tag = "Dimension"

    @classmethod
    def parse(cls, node: etree._Element, index: int):
        """Parse a <Dimension> XML node."""
        name = _get_attr(node, "name")
        logger.debug("Parsing node <%s name='%s' />", cls.tag, name)

        dim_type = DimensionType.from_str(node.get("type"))

        hierarchy_map = OrderedDict(
            _raise_if_duplicate(_yield_children_nodes(node, XMLHierarchy)),
        )

        default_hierarchy = node.get("default_hierarchy")
        if default_hierarchy not in hierarchy_map:
            default_hierarchy = next(iter(hierarchy_map.keys()))

        time_format = node.get("fkey_time") if dim_type is DimensionType.TIME else None
        if time_format not in (*FKEY_TIME_FORMATS, None):
            raise InvalidXMLAttributeValue(node.tag, name, "fkey_time", time_format)

        return cls(
            name=name,
            captions=immu.Map(
                _raise_if_duplicate(_yield_locale_pairs(node, "caption")),
            ),
            default_hierarchy=default_hierarchy,
            dim_type=dim_type,
            foreign_key=node.get("foreign_key"),
            fkey_time_format=time_format,
            hierarchy_map=hierarchy_map,
            annotations=immu.Map(_yield_annotations(node)),
            visible=_get_boolean(node, "visible", True),
        )


class XMLSharedDimension(XMLDimension):
    tag = "SharedDimension"


class XMLPrivateDimension(XMLDimension):
    @classmethod
    def parse(cls, node: etree._Element, index: int):
        """Parse a Private <Dimension> XML node."""
        dimension = super().parse(node, index)

        # foreign keys are required in Private Dimensions
        if dimension.foreign_key is None:
            raise MissingXMLAttribute(node.tag, "foreign_key")

        return dimension


class XMLHierarchy(models.Hierarchy):
    tag = "Hierarchy"

    @classmethod
    def parse(cls, node: etree._Element, index: int):
        """Parse a <Hierarchy> XML node."""
        name = _get_attr(node, "name")
        logger.debug("Parsing node <%s name='%s' />", cls.tag, name)

        level_map = OrderedDict(
            _raise_if_duplicate(_yield_children_nodes(node, XMLLevel)),
        )
        if len(level_map) == 0:
            raise MissingXMLNode(node.tag, name, "Level")

        default_pk = ""
        for item in level_map.values():
            default_pk = item.key_column

        return cls(
            name=name,
            primary_key=node.get("primary_key", default_pk),
            captions=immu.Map(
                _raise_if_duplicate(_yield_locale_pairs(node, "caption")),
            ),
            table=_find_table_ref(node),
            level_map=level_map,
            default_member=cls._parse_default_member(node),
            annotations=immu.Map(_yield_annotations(node)),
            visible=_get_boolean(node, "visible", True),
        )

    @staticmethod
    def _parse_default_member(node: etree._Element):
        items: list[str] = node.get("default_member", "").split(".", maxsplit=1)
        return (items[0], items[1]) if len(items) == 2 else None


class XMLLevel(models.Level):
    tag = "Level"

    @classmethod
    def parse(cls, node: etree._Element, index: int):
        """Parse a <Level> XML node."""
        name = _get_attr(node, "name")
        logger.debug("Parsing node <%s name='%s' />", cls.tag, name)

        key_type = node.get("key_type")

        return cls(
            name=name,
            depth=index + 1,
            count=0,
            key_column=_get_attr(node, "key_column"),
            key_type=DataType.from_str(key_type),
            captions=immu.Map(
                _raise_if_duplicate(_yield_locale_pairs(node, "caption")),
            ),
            name_column_map=immu.Map(
                _raise_if_duplicate(_yield_locale_pairs(node, "name_column")),
            ),
            property_map=OrderedDict(
                _raise_if_duplicate(_yield_children_nodes(node, XMLProperty)),
            ),
            time_scale=node.get("time_scale"),
            annotations=immu.Map(_yield_annotations(node)),
            visible=_get_boolean(node, "visible", True),
        )


class XMLProperty(models.Property):
    tag = "Property"

    @classmethod
    def parse(cls, node: etree._Element, index: int):
        """Parse a <Property> XML node."""
        name = _get_attr(node, "name")
        logger.debug("Parsing node <%s name='%s' />", cls.tag, name)

        key_type = node.get("key_type")

        keycol_map = immu.Map(
            _raise_if_duplicate(_yield_locale_pairs(node, "key_column")),
        )
        if len(keycol_map) == 0:
            raise MissingXMLAttribute(node.tag, "key_column")

        return cls(
            name=name,
            annotations=immu.Map(_yield_annotations(node)),
            captions=immu.Map(
                _raise_if_duplicate(_yield_locale_pairs(node, "caption")),
            ),
            key_column_map=keycol_map,
            key_type=DataType.from_str(key_type),
            visible=_get_boolean(node, "visible", True),
        )


class XMLMeasure(models.Measure):
    tag = "Measure"

    @classmethod
    def parse(cls, node: etree._Element, index: int):
        """Parse a <Measure> XML node."""
        name = _get_attr(node, "name")
        logger.debug("Parsing node <%s name='%s' />", cls.tag, name)

        return cls(
            name=name,
            key_column=_get_attr(node, "key_column"),
            aggregator=cls._get_aggregator(node),
            annotations=immu.Map(_yield_annotations(node)),
            captions=immu.Map(
                _raise_if_duplicate(_yield_locale_pairs(node, "caption")),
            ),
            submeasures=immu.Map(
                _raise_if_duplicate(_yield_children_nodes(node, cls, XMLCalculatedMeasure)),
            ),
            visible=_get_boolean(node, "visible", True),
        )

    @staticmethod
    def _get_aggregator(mea_node: etree._Element) -> Aggregator:
        """Parse the Aggregator parameter from the XML tree.

        Raises:
        :class:`MissingXMLAttribute` --
            If the node doesn't have an `aggregator` attribute or an
            `<Agregation>` child node.

        :class:`InvalidXMLAttributeValue` --
            If the aggregator defined for this node has an unexpected value.

        """
        agg_node = mea_node.find("Aggregation")

        # if there's an <Aggregation> node, get its `type`
        # else get the `<Measure>`'s `aggregator` attribute
        node, attr = (mea_node, "aggregator") if agg_node is None else (agg_node, "type")
        value = _get_attr(node, attr)

        try:
            agg_type = AggregatorType(value)
        except ValueError:
            node_name = _get_attr(mea_node, "name")
            raise InvalidXMLAttributeValue(node.tag, node_name, attr, value) from None
        else:
            agg_cls = Aggregator.from_enum(agg_type)
            agg_args = {
                str(k).replace("-", "_"): numerify(v) if is_numeric(v) else str(v)
                for k, v in node.attrib.items()
            }
            return agg_cls.new(agg_args)


class XMLCalculatedMeasure(models.CalculatedMeasure):
    tag = "CalculatedMeasure"

    @classmethod
    def parse(cls, node: etree._Element, index: int):
        """Parse a <CalculatedMeasure> XML node."""
        name = _get_attr(node, "name")
        logger.debug("Parsing node <%s name='%s' />", cls.tag, name)

        # if there's an <Formula> node, get its child text
        # else get the `<Measure>`'s `formula` attribute
        frml_node = node.find("Formula")
        formula = _get_attr(node, "formula") if frml_node is None else frml_node.text

        if not formula:
            raise InvalidXMLAttributeValue(cls.tag, name, "formula", str(formula))

        return cls(
            name=name,
            formula=cls._parse_formula(formula),
            annotations=immu.Map(_yield_annotations(node)),
            captions=immu.Map(
                _raise_if_duplicate(_yield_locale_pairs(node, "caption")),
            ),
            visible=_get_boolean(node, "visible", True),
        )


def _find_table_ref(node: etree._Element):
    gen_tables = (item for item in node.iterchildren("InlineTable", "Table", "TableUsage"))
    table_node = next(gen_tables, None)

    if table_node is None:
        return None
    if table_node.tag == "InlineTable":
        return XMLInlineTable.parse(table_node, 0)
    if table_node.tag == "Table":
        return XMLTable.parse(table_node, 0)
    if table_node.tag == "TableUsage":
        return _get_attr(table_node, "source")

    raise MissingXMLNode(node.tag, _get_attr(node, "name"), "Table")


def _get_attr(node: etree._Element, attr: str) -> str:
    """Retrieve an attribute from a node.

    If the attribute is not present, raises :class:`MissingXMLAttribute`.
    """
    try:
        value = node.attrib[attr]
    except KeyError as exc:
        raise MissingXMLAttribute(node.tag, attr) from exc
    else:
        return str(value)


def _get_boolean(node: etree._Element, attr: str, default: bool) -> bool:
    value = node.get(attr)
    return default if value is None else (value.lower() in TRUTHY_STRINGS)


def _raise_if_duplicate(
    generator: Iterable[tuple[str, T]],
    exc_cls: type[DuplicateKeyError] = DuplicateKeyError,
):
    seen_keys = set()
    for key, value in generator:
        if key in seen_keys:
            raise exc_cls(key)
        seen_keys.add(key)
        yield key, value


def _yield_annotations(node: etree._Element) -> Iterable[tuple[str, Optional[str]]]:
    """Yield a pair of (name, value) for each Annotation in the node."""
    return _raise_if_duplicate(
        (_get_attr(item, "name"), item.text) for item in node.iterchildren("Annotation")
    )


def _yield_children_nodes(
    node: etree._Element,
    *children: type[AnyXMLEntity],
    attr: str = "name",
) -> Generator[tuple[str, AnyXMLEntity], None, None]:
    tags = (item.tag for item in children)
    parsers = {item.tag: item.parse for item in children}
    for index, item in enumerate(node.iterchildren(*tags)):
        reducer = parsers[item.tag]
        yield _get_attr(item, attr), reducer(item, index)


def _yield_locale_pairs(
    node: etree._Element,
    attribute: str,
) -> Generator[tuple[str, str], None, None]:
    attr_value = node.get(attribute)
    if attr_value is not None:
        yield ("xx", attr_value)

    for child_node in node.iterchildren("LocalizedAttr"):
        child_attr = _get_attr(child_node, "attr")
        if child_attr != attribute:
            continue

        child_value = child_node.get("value", child_node.text)
        if child_value is not None:
            yield (_get_attr(child_node, "locale"), child_value)


def parse_xml_schema(source: Union[str, Path, TextIO]) -> XMLSchema:
    """Attempt to parse an object into a XMLSchema.

    This function accepts:
    - A raw XML :class:`str`
    - A local path (as a :class:`pathlib.Path`) to a XML file
    - A not-binary read-only :class:`TextIO` instance for a file-like object
    """
    parser = etree.XMLParser(
        encoding="utf-8",
        remove_blank_text=True,
        remove_comments=True,
    )

    # if argument is str, is assumed to be a raw XML string
    if isinstance(source, str):
        root = etree.fromstring(source, parser)
        return XMLSchema.parse(root)

    # if argument is pathlib.Path or TextIO, open it and parse contents
    tree = etree.parse(source, parser)
    root = tree.getroot()
    return XMLSchema.parse(root)
