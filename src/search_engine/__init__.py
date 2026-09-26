"""A small search engine implemented from scratch in Python."""

from .document import Document
from .engine import SearchEngine
from .ranking import SearchResult

__all__ = ["Document", "SearchEngine", "SearchResult"]
