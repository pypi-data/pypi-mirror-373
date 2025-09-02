"""Minimal type stubs for BeautifulSoup elements focusing on our usage."""

from typing import Any, Dict, List, Optional, Union

class PageElement:
    """Base class for all elements in the parse tree."""
    
    def get_text(self, separator: str = ..., strip: bool = ...) -> str: ...
    def decompose(self) -> None: ...

class NavigableString(str, PageElement):
    """A string that is part of the parse tree."""
    pass

class Tag(PageElement):
    """An HTML/XML tag with attributes and contents."""
    
    name: Optional[str]
    
    def find(
        self,
        name: Optional[Union[str, List[str]]] = ...,
        attrs: Optional[Dict[str, str]] = ...,
        id: Optional[str] = ...,
        **kwargs: str
    ) -> Optional["Tag"]: ...
    
    def find_all(
        self,
        name: Optional[Union[str, List[str]]] = ...,
        attrs: Optional[Dict[str, str]] = ...,
        class_: Optional[str] = ...,
        **kwargs: str
    ) -> List["Tag"]: ...
    
    def find_parent(
        self,
        name: Optional[Union[str, List[str]]] = ...,
        attrs: Optional[Dict[str, str]] = ...,
        **kwargs: str
    ) -> Optional["Tag"]: ...
    
    def find_next_sibling(
        self,
        name: Optional[Union[str, List[str]]] = ...,
        attrs: Optional[Dict[str, str]] = ...,
        **kwargs: str
    ) -> Optional["Tag"]: ...
    
    def get(self, key: str, default: str = ...) -> str: ...
    def get_text(self, separator: str = ..., strip: bool = ...) -> str: ...
    def replace_with(self, *args: Union[str, "PageElement"]) -> "Tag": ...
    def decompose(self) -> None: ...