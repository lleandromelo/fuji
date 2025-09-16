"""Utility helpers for normalizing and working with natural language text."""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable, Set


_WHITESPACE_RE = re.compile(r"\s+")
_NON_WORD_RE = re.compile(r"[^a-z0-9]+")


def normalize_text(text: str) -> str:
    """Normalize user provided text for easier comparison.

    The function removes accents, converts to lower case and collapses
    punctuation so that simple keyword checks become more reliable when dealing
    with Portuguese sentences.
    """

    if not text:
        return ""
    value = unicodedata.normalize("NFD", text.lower())
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = _NON_WORD_RE.sub(" ", value)
    value = _WHITESPACE_RE.sub(" ", value)
    return value.strip()


def tokenize(text: str) -> Set[str]:
    """Return a set of tokens extracted from *text* after normalization."""

    normalized = normalize_text(text)
    if not normalized:
        return set()
    return set(normalized.split())


def contains_any(text: str, keywords: Iterable[str]) -> bool:
    """Return ``True`` if *text* contains any of the *keywords*.

    Both the input *text* and the provided *keywords* are normalized before the
    search happens.
    """

    normalized_text = normalize_text(text)
    if not normalized_text:
        return False
    for keyword in keywords:
        if not keyword:
            continue
        if normalize_text(keyword) in normalized_text:
            return True
    return False


def best_keyword_match(text: str, candidates: Iterable[str]) -> str | None:
    """Return the candidate that best matches *text* using a simple heuristic."""

    normalized_text = normalize_text(text)
    if not normalized_text:
        return None

    best_match: tuple[str, float] | None = None
    for candidate in candidates:
        normalized_candidate = normalize_text(candidate)
        if not normalized_candidate:
            continue
        score = _similarity_score(normalized_candidate, normalized_text)
        if score is None:
            continue
        if best_match is None or score > best_match[1]:
            best_match = (candidate, score)
    return best_match[0] if best_match else None


def _similarity_score(left: str, right: str) -> float | None:
    """Compute a very small similarity score based on token overlap."""

    if not left or not right:
        return None
    left_tokens = left.split()
    right_tokens = right.split()

    overlap = len(set(left_tokens) & set(right_tokens))
    if overlap:
        return overlap / max(len(set(left_tokens)), 1)

    # fall back to sequence ratio for strings that do not share tokens
    try:
        from difflib import SequenceMatcher
    except ImportError:  # pragma: no cover - difflib is in the stdlib
        return None
    return SequenceMatcher(None, left, right).ratio()
