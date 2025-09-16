"""Core logic that builds responses for WhatsApp messages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .config import AssistantConfig
from .intent_detection import IntentType, detect_intent
from .inventory import Inventory, InventoryItem


@dataclass
class HandlerResponse:
    text: str
    media_urls: List[str]


class MessageHandler:
    """Create WhatsApp friendly responses based on user input."""

    def __init__(self, inventory: Inventory, config: Optional[AssistantConfig] = None):
        self.inventory = inventory
        self.config = config or AssistantConfig.from_env()

    def handle(self, message: str) -> HandlerResponse:
        if not message or not message.strip():
            return HandlerResponse(
                "Não consegui entender sua mensagem. Pode repetir informando o item ou dúvida?",
                [],
            )

        intent = detect_intent(message)
        matched_item = self.inventory.find_best_match(message)

        if intent.type == IntentType.GREETING:
            return HandlerResponse(
                "Olá! Eu sou o assistente virtual da Fuji Locações. Posso ajudar com disponibilidade, valores e fotos do acervo.",
                [],
            )

        if intent.type == IntentType.HELP:
            return HandlerResponse(
                "Você pode perguntar, por exemplo: 'Tem cadeira Tiffany?', 'Quantas mesas bistrô vocês têm?' ou 'Pode enviar fotos do acervo?'.",
                [],
            )

        if intent.type == IntentType.THANKS:
            return HandlerResponse("Por nada! Qualquer outra dúvida é só chamar. 😊", [])

        if intent.type == IntentType.GOODBYE:
            return HandlerResponse("Até mais! Ficamos à disposição para o seu evento.", [])

        if intent.type == IntentType.IMAGE_REQUEST or intent.type == IntentType.CATALOG_REQUEST:
            return self._build_catalog_response(include_media=True)

        if intent.type == IntentType.STOCK_QUERY:
            if matched_item:
                return self._build_stock_response(matched_item)
            return self._fallback_unknown_item()

        if intent.type == IntentType.INVENTORY_QUERY:
            if matched_item:
                return self._build_availability_response(matched_item)
            return self._fallback_unknown_item()

        # Unknown intent but we managed to match an item: return a generic summary
        if matched_item:
            return self._build_availability_response(matched_item)

        return self._fallback_unknown_item()

    # Internal helpers -------------------------------------------------

    def _build_catalog_response(self, include_media: bool) -> HandlerResponse:
        items = self.inventory.list_catalog()
        if not items:
            return HandlerResponse(
                "Ainda não há itens cadastrados no acervo. Por favor, cadastre produtos no arquivo data/inventory.json.",
                [],
            )

        limit = max(1, self.config.default_media_limit)
        preview_items = items[:limit]

        lines = ["Confira algumas opções disponíveis na Fuji Locações:"]
        for item in preview_items:
            lines.append(f"- {item.name} ({item.quantity} no estoque)")
        lines.append("Para consultar um item específico é só me enviar o nome dele.")

        media_urls: List[str] = []
        if include_media:
            for item in items:
                if item.image_url:
                    media_urls.append(item.image_url)
                if len(media_urls) >= limit:
                    break

        return HandlerResponse("\n".join(lines), media_urls)

    def _build_availability_response(self, item: InventoryItem) -> HandlerResponse:
        if item.quantity > 0:
            text = (
                f"Sim, temos {item.quantity} unidades da {item.name} disponíveis para locação."
            )
        else:
            text = (
                f"No momento a {item.name} está com o estoque zerado, mas podemos verificar disponibilidade futura para você."
            )

        if item.description:
            text += f" {item.description.strip()}"

        text += " Precisa reservar ou saber sobre entrega?"

        media_urls = [item.image_url] if item.image_url else []
        return HandlerResponse(text, media_urls)

    def _build_stock_response(self, item: InventoryItem) -> HandlerResponse:
        text = (
            f"Atualmente temos {item.quantity} unidades da {item.name} registradas no estoque."
        )
        if item.quantity == 0:
            text += " Podemos verificar reposição ou sugerir alternativas do acervo."
        else:
            text += " Posso separar algumas para o seu evento?"
        media_urls = [item.image_url] if item.image_url else []
        return HandlerResponse(text, media_urls)

    def _fallback_unknown_item(self) -> HandlerResponse:
        return HandlerResponse(
            "Não encontrei esse item no nosso acervo. Você pode pedir o catálogo digitando 'catálogo' ou enviar o nome completo do produto que procura.",
            [],
        )
