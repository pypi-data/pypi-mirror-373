"""Minimal deprecation stubs for BeautifulSoup."""

from typing import Any, Callable, TypeVar

T = TypeVar("T")

def _deprecated(new_name: str, version: str) -> Callable[[T], T]: ...