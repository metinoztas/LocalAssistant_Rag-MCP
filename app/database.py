# SQLite işlemleri

import sqlite3
import json


class Database:

    def __init__(self, db_path="database/rag.db"):
        self.db_path = db_path
        self.create_table()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def create_table(self):
        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                embedding TEXT NOT NULL,
                source TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                UNIQUE(content, source)
            )
            """)

    def add_document(
        self,
        content,
        embedding,
        source,
        chunk_index
    ):
        """
        Yeni bir doküman chunk'ını veritabanına ekler.
        """

        embedding_json = json.dumps(embedding)

        with self.connect() as connection:

            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO documents
                (
                    content,
                    embedding,
                    source,
                    chunk_index
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    content,
                    embedding_json,
                    source,
                    chunk_index
                )
            )

            return cursor.rowcount > 0

    def get_documents(self):
        documents = []

        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    content,
                    embedding,
                    source,
                    chunk_index
                FROM documents
                """
            ).fetchall()

        for row in rows:
            documents.append({
                "id": row[0],
                "content": row[1],
                "embedding": json.loads(row[2]),
                "source": row[3],
                "chunk_index": row[4]
            })

        return documents
    
    def get_sources(self):
        """
        Veritabanındaki benzersiz belge kaynaklarını döndürür.
        """

        with self.connect() as connection:
            rows = connection.execute(
                "SELECT DISTINCT source FROM documents"
            ).fetchall()

        return [row[0] for row in rows]

    def delete_by_source(self, source):
        """
        Bir kaynağa ait tüm chunk'ları siler.
        """

        with self.connect() as connection:
            connection.execute(
                "DELETE FROM documents WHERE source = ?",
                (source,)
            )