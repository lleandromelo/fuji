"""Rule-based intent detection for Portuguese WhatsApp messages."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from . import text_utils


class IntentType(Enum):
    GREETING = auto()
    HELP = auto()
    INVENTORY_QUERY = auto()
    STOCK_QUERY = auto()
    IMAGE_REQUEST = auto()
    CATALOG_REQUEST = auto()
    THANKS = auto()
    GOODBYE = auto()
    UNKNOWN = auto()


@dataclass
class Intent:
    type: IntentType
    confidence: float = 0.0


_GREETING_KEYWORDS = {"ola", "bom dia", "boa tarde", "boa noite", "oi"}
_HELP_KEYWORDS = {"ajuda", "como funciona", "o que voce faz", "menu"}
_STOCK_KEYWORDS = {"quantas", "qtd", "estoque", "quantidade"}
_AVAILABILITY_KEYWORDS = {"tem", "disponivel", "disponibilidade", "possui", "aluga"}
_IMAGE_KEYWORDS = {"foto", "imagem", "imagens", "catalogo", "catálogo", "acervo", "portifolio", "portfolio"}
_THANKS_KEYWORDS = {"obrigado", "obrigada", "valeu"}
_GOODBYE_KEYWORDS = {"ate mais", "tchau", "ate logo"}


def detect_intent(message: str) -> Intent:
    """Detect the intent behind a WhatsApp message."""

    normalized = text_utils.normalize_text(message)
    if not normalized:
        return Intent(IntentType.UNKNOWN, confidence=0.0)

    tokens = text_utils.tokenize(normalized)

    if text_utils.contains_any(normalized, _GREETING_KEYWORDS):
        return Intent(IntentType.GREETING, confidence=0.95)

    if text_utils.contains_any(normalized, _THANKS_KEYWORDS):
        return Intent(IntentType.THANKS, confidence=0.9)

    if text_utils.contains_any(normalized, _GOODBYE_KEYWORDS):
        return Intent(IntentType.GOODBYE, confidence=0.9)

    if text_utils.contains_any(normalized, _HELP_KEYWORDS):
        return Intent(IntentType.HELP, confidence=0.8)

    if text_utils.contains_any(normalized, _IMAGE_KEYWORDS):
        # the user usually expects both text and images
        return Intent(IntentType.IMAGE_REQUEST, confidence=0.85)

    if text_utils.contains_any(normalized, _STOCK_KEYWORDS):
        return Intent(IntentType.STOCK_QUERY, confidence=0.8)

    if text_utils.contains_any(normalized, _AVAILABILITY_KEYWORDS):
        return Intent(IntentType.INVENTORY_QUERY, confidence=0.7)

    if len(tokens) <= 2:
        # likely a short product name, treat as inventory lookup
        return Intent(IntentType.INVENTORY_QUERY, confidence=0.55)

    return Intent(IntentType.UNKNOWN, confidence=0.1)
