"""
Neden var?

Projedeki tüm ayarları tek yerde toplamak için.

İleride model adını değiştirmek istersek sadece burayı değiştireceğiz.

"""

from foundry_local_sdk import Configuration

APP_NAME = "local_rag_ai_assistant"

MODEL_NAME = "qwen3-4b"

EMBEDDING_MODEL = "qwen3-embedding-0.6b"

config = Configuration(
    app_name=APP_NAME
)

SEMANTIC_WEIGHT = 0.80
KEYWORD_WEIGHT = 0.20
