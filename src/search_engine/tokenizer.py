import re
from collections.abc import Iterable

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")
_DEFAULT_STOP_WORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "by", "for",
        "from", "in", "is", "it", "of", "on", "or", "that", "the",
        "this", "to", "was", "were", "with",
    }
)


class Tokenizer:
    """Normalize text into searchable terms."""

    def __init__(self, stop_words: Iterable[str] = _DEFAULT_STOP_WORDS) -> None:
        self._stop_words = frozenset(word.casefold() for word in stop_words)

    def tokenize(self, text: str) -> list[str]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        tokens = (match.group(0).casefold() for match in _TOKEN_PATTERN.finditer(text))
        return [token for token in tokens if token not in self._stop_words]

    def normalize_query(self, query: str) -> list[str]:
        return self.tokenize(query)
