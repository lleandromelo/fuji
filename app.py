"""Flask application that exposes a webhook for WhatsApp (Twilio) messages."""

from __future__ import annotations

import logging
from pathlib import Path

from flask import Flask, abort, request
try:
    from twilio.twiml.messaging_response import MessagingResponse
except ModuleNotFoundError as exc:  # pragma: no cover - dependency provided by the deploy environment
    raise SystemExit(
        "O pacote 'twilio' é necessário para executar o webhook. Instale as dependências listadas em requirements.txt"
    ) from exc

from whatsapp_assistant.config import AssistantConfig
from whatsapp_assistant.inventory import Inventory
from whatsapp_assistant.message_handler import MessageHandler

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

_config = AssistantConfig.from_env()
if not Path(_config.inventory_path).exists():
    raise SystemExit(
        f"Arquivo de inventário '{_config.inventory_path}' não encontrado. Atualize a variável INVENTORY_PATH ou crie data/inventory.json."
    )

_inventory = Inventory.from_file(_config.inventory_path)
_handler = MessageHandler(_inventory, config=_config)


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


@app.post("/webhook")
def whatsapp_webhook():
    """Entry point used pelo webhook do WhatsApp via Twilio."""

    incoming_message = request.form.get("Body", "")
    if incoming_message is None:
        abort(400, "Mensagem inválida")

    response = MessagingResponse()
    handler_response = _handler.handle(incoming_message)
    message = response.message(handler_response.text)
    for media_url in handler_response.media_urls:
        message.media(media_url)

    logging.info("Respondendo mensagem: %s", handler_response.text)
    return str(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
