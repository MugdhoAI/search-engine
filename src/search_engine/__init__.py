"""A small search engine implemented from scratch in Python."""

from .engine import SearchEngine
from .document import Document
from .ranking import SearchResult

__all__ = ["Document", "SearchEngine", "SearchResult"]
