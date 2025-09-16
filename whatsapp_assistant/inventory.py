"""Inventory management helpers for the WhatsApp assistant."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Iterable, List, Optional

from . import text_utils


@dataclass
class InventoryItem:
    """Represents one item from the rental catalog."""

    id: str
    name: str
    category: str
    quantity: int
    image_url: Optional[str] = None
    description: Optional[str] = None
    aliases: List[str] = field(default_factory=list)

    def all_keywords(self) -> List[str]:
        return [self.name, *self.aliases]


class Inventory:
    """Simple in-memory inventory loaded from a JSON file."""

    def __init__(self, items: Iterable[InventoryItem]):
        self._items = list(items)

    def items(self) -> List[InventoryItem]:
        return list(self._items)

    def find_best_match(self, query: str, min_score: float = 0.45) -> Optional[InventoryItem]:
        """Find the inventory item that best matches *query*.

        The search uses token overlap and a basic similarity ratio to attempt to
        match user input (which is usually a small phrase) with the item names or
        aliases defined in :class:`InventoryItem`.
        """

        if not query:
            return None

        normalized_query = text_utils.normalize_text(query)
        query_tokens = text_utils.tokenize(normalized_query)

        best_item: Optional[InventoryItem] = None
        best_score = 0.0

        for item in self._items:
            for keyword in item.all_keywords():
                normalized_keyword = text_utils.normalize_text(keyword)
                if not normalized_keyword:
                    continue
                keyword_tokens = set(normalized_keyword.split())
                if keyword_tokens:
                    overlap = len(keyword_tokens & query_tokens)
                    if overlap == len(keyword_tokens) and overlap > 0:
                        return item
                    if overlap == 0:
                        continue
                    weight = overlap / len(keyword_tokens)
                else:
                    weight = 1.0
                score = _similarity_score(normalized_keyword, normalized_query) * weight
                if score > best_score:
                    best_item = item
                    best_score = score

        if best_item and best_score >= min_score:
            return best_item
        return None

    def list_catalog(self) -> List[InventoryItem]:
        """Return the inventory sorted alphabetically by item name."""

        return sorted(self._items, key=lambda item: text_utils.normalize_text(item.name))

    @classmethod
    def from_file(cls, path: Path) -> "Inventory":
        with Path(path).open("r", encoding="utf-8") as fp:
            payload = json.load(fp)
        items = [
            InventoryItem(
                id=entry["id"],
                name=entry["name"],
                category=entry["category"],
                quantity=int(entry.get("quantity", 0)),
                image_url=entry.get("image_url"),
                description=entry.get("description"),
                aliases=list(entry.get("aliases", [])),
            )
            for entry in payload.get("items", [])
        ]
        return cls(items)


def _similarity_score(keyword: str, query: str) -> float:
    """Compute a similarity score between *keyword* and *query*."""

    if not keyword or not query:
        return 0.0

    try:
        from difflib import SequenceMatcher
    except ImportError:  # pragma: no cover - difflib is in the stdlib
        return 0.0

    return SequenceMatcher(None, keyword, query).ratio()
