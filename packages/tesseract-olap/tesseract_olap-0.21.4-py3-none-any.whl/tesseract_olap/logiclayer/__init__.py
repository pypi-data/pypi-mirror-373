"""Tesseract Module for LogicLayer.

This module provides a subclass of :class:`LogicLayerModule`, which provides a
set of endpoints fully compatible with the API of Tesseract Rust.

This submodule it's dependent on the logiclayer package, but as the package it's
not declared as that, it must not be exported in the main module of the package.
The user must import it using

`from tesseract_olap.logiclayer import TesseractModule`.
"""

__all__ = (
    "DataSearchParams",
    "ResponseFormat",
    "TesseractModule",
)

from .dependencies import DataSearchParams
from .module import TesseractModule
from .response import ResponseFormat
