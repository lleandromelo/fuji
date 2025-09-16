"""Assistente virtual para atendimento no WhatsApp."""

from .config import AssistantConfig
from .inventory import Inventory, InventoryItem
from .message_handler import HandlerResponse, MessageHandler

__all__ = [
    "AssistantConfig",
    "HandlerResponse",
    "Inventory",
    "InventoryItem",
    "MessageHandler",
]
