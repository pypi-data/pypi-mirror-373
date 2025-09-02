from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from typing_extensions import Self

from . import traverse
from .enums import DataType, DimensionType
from .models import Annotations


@dataclass(eq=False, frozen=True, order=False)
class TesseractSchema:
    name: str
    locales: list[str]
    default_locale: str
    annotations: Annotations
    cubes: list["TesseractCube"]

    @classmethod
    def from_entity(
        cls,
        entity: traverse.SchemaTraverser,
        roles: Iterable[str] = [],
        locale: Optional[str] = None,
        show_all: bool = False,
    ) -> Self:
        """Generate a dataclass-schema object describing this entity."""
        default_locale = entity.schema.default_locale
        locale = default_locale if locale is None else locale
        return cls(
            name=entity.schema.name,
            locales=sorted(entity.get_locale_available()),
            default_locale=default_locale,
            cubes=[
                TesseractCube.from_entity(item, locale, show_all=show_all)
                for item in entity.cube_map.values()
                if item.visible and item.is_authorized(roles)
            ],
            annotations=dict(entity.schema.annotations),
        )


@dataclass(eq=False, frozen=True, order=False)
class TesseractCube:
    name: str
    caption: str
    annotations: Annotations
    dimensions: list["TesseractDimension"]
    measures: list["TesseractMeasure"]

    @classmethod
    @lru_cache(maxsize=256)
    def from_entity(cls, entity: traverse.CubeTraverser, locale: str, show_all: bool = False) -> Self:
        """Generate a dataclass-schema object describing this entity."""
        return cls(
            name=entity.name,
            caption=entity.get_caption(locale),
            dimensions=[
                TesseractDimension.from_entity(item, locale, show_all=show_all)
                for item in entity.dimensions
                if show_all or item.visible
            ],
            measures=[
                TesseractMeasure.from_entity(item, locale, show_all=show_all)
                for item in entity.measures
                if show_all or item.visible
            ],
            annotations=dict(entity.annotations),
        )


@dataclass(eq=False, frozen=True, order=False)
class TesseractMeasure:
    name: str
    caption: str
    aggregator: str
    annotations: Annotations
    attached: list["TesseractMeasure"]

    @classmethod
    def from_entity(cls, entity: traverse.AnyMeasure, locale: str, show_all: bool = False) -> Self:
        """Generate a dataclass-schema object describing this entity."""
        return cls(
            name=entity.name,
            caption=entity.get_caption(locale),
            aggregator=str(entity.aggregator),
            annotations=dict(entity.annotations),
            attached=[
                cls.from_entity(item, locale, show_all=show_all)
                for item in entity.submeasures.values()
                if show_all or item.visible
            ],
        )


@dataclass(eq=False, frozen=True, order=False)
class TesseractDimension:
    name: str
    caption: str
    type: DimensionType
    annotations: Annotations
    hierarchies: list["TesseractHierarchy"]
    default_hierarchy: str

    @classmethod
    def from_entity(cls, entity: traverse.DimensionTraverser, locale: str, show_all: bool = False) -> Self:
        """Generate a dataclass-schema object describing this entity."""
        return cls(
            name=entity.name,
            caption=entity.get_caption(locale),
            type=entity.dim_type,
            annotations=dict(entity.annotations),
            hierarchies=[
                TesseractHierarchy.from_entity(item, locale, show_all=show_all)
                for item in entity.hierarchies
                if show_all or item.visible
            ],
            default_hierarchy=entity._entity.default_hierarchy,
        )


@dataclass(eq=False, frozen=True, order=False)
class TesseractHierarchy:
    name: str
    caption: str
    annotations: Annotations
    levels: list["TesseractLevel"]

    @classmethod
    def from_entity(cls, entity: traverse.HierarchyTraverser, locale: str, show_all: bool = False) -> Self:
        """Generate a dataclass-schema object describing this entity."""
        return cls(
            name=entity.name,
            caption=entity.get_caption(locale),
            annotations=dict(entity.annotations),
            levels=[
                TesseractLevel.from_entity(item, locale) for item in entity.levels if show_all or item.visible
            ],
        )


@dataclass(eq=False, frozen=True, order=False)
class TesseractLevel:
    name: str
    caption: str
    depth: int
    count: int
    annotations: Annotations
    properties: list["TesseractProperty"]

    @classmethod
    def from_entity(cls, entity: traverse.LevelTraverser, locale: str) -> Self:
        """Generate a dataclass-schema object describing this entity."""
        return cls(
            name=entity.name,
            caption=entity.get_caption(locale),
            depth=entity.depth,
            count=entity.count,
            annotations=dict(entity.annotations),
            properties=[
                TesseractProperty.from_entity(item, locale)
                for item in entity.properties
                if item.visible
            ],
        )


@dataclass(eq=False, frozen=True, order=False)
class TesseractProperty:
    name: str
    caption: str
    type: DataType
    annotations: Annotations

    @classmethod
    def from_entity(cls, entity: traverse.PropertyTraverser, locale: str) -> Self:
        """Generate a dataclass-schema object describing this entity."""
        return cls(
            name=entity.name,
            caption=entity.get_caption(locale),
            type=entity.key_type,
            annotations=dict(entity.annotations),
        )
