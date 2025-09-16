from pathlib import Path
import unittest

from whatsapp_assistant.config import AssistantConfig
from whatsapp_assistant.inventory import Inventory
from whatsapp_assistant.message_handler import MessageHandler


class MessageHandlerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        inventory_path = Path("data/inventory.json")
        inventory = Inventory.from_file(inventory_path)
        config = AssistantConfig(inventory_path=inventory_path, default_media_limit=2)
        cls.handler = MessageHandler(inventory, config=config)

    def test_availability_response_for_known_item(self):
        response = self.handler.handle("Vocês têm a cadeira Tiffany branca disponível?")
        self.assertIn("Cadeira Tiffany Branca", response.text)
        self.assertIn("120", response.text)
        self.assertTrue(response.media_urls)

    def test_stock_response_for_known_item(self):
        response = self.handler.handle("Quantas cadeiras Dior vocês têm no estoque?")
        self.assertIn("60", response.text)
        self.assertTrue(response.media_urls)

    def test_catalog_request_returns_media(self):
        response = self.handler.handle("Pode enviar fotos do acervo?")
        self.assertTrue(response.media_urls)
        self.assertLessEqual(len(response.media_urls), 2)

    def test_unknown_item_returns_fallback(self):
        response = self.handler.handle("Vocês possuem cadeira fantasma roxa?")
        self.assertIn("Não encontrei esse item", response.text)
        self.assertFalse(response.media_urls)


if __name__ == "__main__":
    unittest.main()
