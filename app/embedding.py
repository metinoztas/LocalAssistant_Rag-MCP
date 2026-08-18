"""
Embedding Servisi

Görevleri:
- Foundry Manager'dan embedding modelini almak
- Embedding modelini yüklemek
- Metinleri vektöre dönüştürmek
"""

from app.config import EMBEDDING_MODEL
from app.foundry import get_manager


class EmbeddingService:
    """
    Metinleri embedding vektörüne dönüştürür.
    """

    def __init__(self):
        # Ortak Foundry Manager
        self.manager = get_manager()

        self.model = None
        self.client = None

    def load_model(self):
        """
        Embedding modelini indirir (gerekirse),
        belleğe yükler ve Embedding Client oluşturur.
        """

        # Embedding modelini al
        self.model = self.manager.catalog.get_model(EMBEDDING_MODEL)

        # Model indir
        self.model.download()

        # Belleğe yükle
        self.model.load()

        # Embedding istemcisi oluştur
        self.client = self.model.get_embedding_client()

    def embed(self, text: str):
        """
        Verilen metni embedding vektörüne dönüştürür.
        """

        if self.client is None:
            raise RuntimeError("Embedding modeli henüz yüklenmedi.")

        response = self.client.generate_embedding(text)

        return response.data[0].embedding