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


def clean_response(text: str) -> str:
    """
    Model yanıtından düşünme etiketlerini ve
    istenmeyen formatlama kalıntılarını temizler.
    """

    # 1) Tamamlanmış <think>...</think> bloklarını temizle
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    # 2) Kapanmamış <think> etiketini ve sonrasını temizle
    text = re.sub(r"<think>.*", "", text, flags=re.DOTALL)

    # 3) Tek başına kalan </think> etiketini temizle
    text = re.sub(r"</think>", "", text)

    # 4) Diğer olası model iç etiketlerini temizle
    text = re.sub(r"<\|.*?\|>", "", text)

    return text.strip()


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

    def ask(self, prompt: str, system_message: str = None) -> str:
        """
        Modele bir soru gönderir.

        system_message: Modele tutarlı davranış kazandıran
                        sistem talimatı (opsiyonel).
        """

        if self.chat_client is None:
            raise RuntimeError("Model henüz yüklenmedi.")

        messages = []

        # System mesajı varsa ekle
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })

        # Kullanıcı mesajını ekle
        messages.append({
            "role": "user",
            "content": prompt
        })

        response = self.chat_client.complete_chat(messages)

        content = response.choices[0].message.content

        # Yanıtı temizle
        content = clean_response(content)

        return content

    