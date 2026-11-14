import unicodedata
from collections.abc import Iterable

_DEFAULT_STOP_WORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "by", "for",
        "from", "in", "is", "it", "of", "on", "or", "that", "the",
        "this", "to", "was", "were", "with",
    }
)


def _is_token_char(char: str) -> bool:
    # Letters, numbers, and combining marks (marks keep scripts such as
    # Bengali intact, where vowel signs combine with consonants).
    return unicodedata.category(char)[0] in "LNM"


def _split_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    for index, char in enumerate(text):
        if _is_token_char(char):
            current.append(char)
        elif (
            char == "'"
            and current
            and index + 1 < len(text)
            and _is_token_char(text[index + 1])
        ):
            current.append(char)
        elif current:
            tokens.append("".join(current))
            current = []
    if current:
        tokens.append("".join(current))
    return tokens


class Tokenizer:
    """Normalize text into searchable terms."""

    def __init__(self, stop_words: Iterable[str] = _DEFAULT_STOP_WORDS) -> None:
        self._stop_words = frozenset(word.casefold() for word in stop_words)

    def tokenize(self, text: str) -> list[str]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        tokens = (token.casefold() for token in _split_tokens(text))
        return [token for token in tokens if token not in self._stop_words]

    def normalize_query(self, query: str) -> list[str]:
        return self.tokenize(query)
