"""Minimal type annotations for BeautifulSoup."""

from typing import Any, Dict, List, Union

# Basic type aliases that BeautifulSoup uses
_Encoding = str
_Encodings = List[str]
_IncomingMarkup = Union[str, bytes]
_InsertableElement = Union[str, "PageElement"]
_RawAttributeValue = Union[str, List[str]]
_RawAttributeValues = Dict[str, _RawAttributeValue]
_RawMarkup = Union[str, bytes]

# Import the classes we need
from .element import PageElement