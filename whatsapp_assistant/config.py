"""Configuration helpers for the WhatsApp assistant."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AssistantConfig:
    """Configuration parameters used by the assistant."""

    inventory_path: Path
    default_media_limit: int = 3

    @classmethod
    def from_env(cls) -> "AssistantConfig":
        inventory_path = Path(os.getenv("INVENTORY_PATH", "data/inventory.json"))
        media_limit = int(os.getenv("MEDIA_LIMIT", "3"))
        return cls(inventory_path=inventory_path, default_media_limit=media_limit)
