"""Minimal type stubs for sphobjinv - only what we actually use."""

from collections.abc import Sequence
from typing import Any, overload

class DataObjStr:
    """Sphinx inventory object data."""
    name: str
    domain: str
    role: str
    priority: str
    uri: str
    dispname: str

class Inventory:
    """Sphinx inventory containing project info and objects."""
    project: str
    version: str
    objects: Sequence[DataObjStr]
    
    def __init__(
        self, 
        *, 
        url: str | None = None,
        fname_zlib: str | None = None,
        **kwargs: Any
    ) -> None: ...
    
    @overload
    def suggest(
        self, 
        term: str, 
        *, 
        thresh: int = 75
    ) -> list[str]: ...
    
    @overload
    def suggest(
        self, 
        term: str, 
        *, 
        thresh: int = 75,
        with_score: bool
    ) -> list[str] | list[tuple[str, int]]: ...
    
    def suggest(
        self, 
        term: str, 
        *, 
        thresh: int = 75,
        with_score: bool = False
    ) -> list[str] | list[tuple[str, int]]:
        """Return fuzzy match suggestions, optionally with scores."""
        ...