"""Minimal type stubs for BeautifulSoup focusing on our usage."""

from typing import Any, Dict, List, Optional, Union

from ._warnings import (
    AttributeResemblesVariableWarning,
    GuessedAtParserWarning,
    MarkupResemblesLocatorWarning,
    UnusualUsageWarning,
    XMLParsedAsHTMLWarning,
)
from .element import NavigableString, PageElement, Tag

__all__ = [
    "BeautifulSoup",
    "Tag",
    "NavigableString",
    "PageElement",
    "AttributeResemblesVariableWarning",
    "GuessedAtParserWarning", 
    "MarkupResemblesLocatorWarning",
    "UnusualUsageWarning",
    "XMLParsedAsHTMLWarning",
]

class BeautifulSoup(Tag):
    """A BeautifulSoup object representing a parsed HTML/XML document."""
    
    def __init__(
        self,
        markup: Union[str, bytes] = ...,
        features: Optional[Union[str, List[str]]] = ...,
        **kwargs: Any
    ) -> None: ...