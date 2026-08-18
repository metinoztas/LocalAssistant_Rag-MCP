"""
Local LLM Servisi

Görevleri:
- Foundry Manager'dan modeli almak
- Modeli yüklemek
- Chat Client oluşturmak
- Soruları modele göndermek
"""

import re
from app.config import MODEL_NAME
from app.foundry import get_manager


class LocalLLM:
    """
    Yerel dil modeli ile iletişim kurar.
    """

    def __init__(self):
        # Ortak Foundry Manager
        self.manager = get_manager()

        self.model = None
        self.chat_client = None

    def load_model(self):
        """
        Modeli indirir (gerekirse),
        belleğe yükler ve Chat Client oluşturur.
        """

        # Execution Provider'ları hazırla
        self.manager.download_and_register_eps()

        # Modeli al
        self.model = self.manager.catalog.get_model(MODEL_NAME)

        # Model indir
        self.model.download()

        # Belleğe yükle
        self.model.load()

        # Chat istemcisi oluştur
        self.chat_client = self.model.get_chat_client()

    def ask(self, prompt: str) -> str:
        """
        Modele tek bir soru gönderir.
        """

        if self.chat_client is None:
            raise RuntimeError("Model henüz yüklenmedi.")

        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.chat_client.complete_chat(messages)
        

        content = response.choices[0].message.content

        # Qwen3 modelinin <think>...</think> düşünme bloğunu temizle
        content = re.sub(r"<think>.*?</think>\s*", "", content, flags=re.DOTALL)

        return content.strip()

    