# Dokümanları okuyacak

import re
from pathlib import Path

from app.document_loader import load_document
from app.text_cleaner import clean_text


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 1
):
    """
    Metni paragraf tabanlı olarak chunk'lara ayırır.

    - Paragrafları mümkün olduğunca korur.
    - chunk_size aşılınca yeni chunk oluşturur.
    - overlap kadar paragraf sonraki chunk'a aktarılır.
    """

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]

    chunks = []

    current_chunk = []
    current_length = 0

    for paragraph in paragraphs:

        paragraph_length = len(paragraph) + 2

        if (
            current_chunk
            and current_length + paragraph_length > chunk_size
        ):

            chunks.append(
                "\n\n".join(current_chunk)
            )

            current_chunk = current_chunk[-overlap:]

            current_length = sum(
                len(item) + 2
                for item in current_chunk
            )

        current_chunk.append(paragraph)
        current_length += paragraph_length

    if current_chunk:
        chunks.append(
            "\n\n".join(current_chunk)
        )

    return chunks


def ingest_text(
    text,
    database,
    embedding_service,
    source="Manual Text",
    chunk_size=500
):
    """
    Verilen metni chunk'lara ayırır ve veritabanına kaydeder.
    """

    text = clean_text(text)

    chunks = chunk_text(
        text,
        chunk_size
    )

    added_count = 0

    for chunk_index, chunk in enumerate(chunks):

        embedding = embedding_service.embed(chunk)

        added = database.add_document(
            content=chunk,
            embedding=embedding,
            source=source,
            chunk_index=chunk_index
        )

        if added:
            added_count += 1

    return added_count


def ingest_directory(
    directory_path,
    database,
    embedding_service
):
    """
    Desteklenen tüm dokümanları okuyup veritabanına ekler.
    """

    added_chunks = 0

    directory = Path(directory_path)

    for file in directory.iterdir():

        if not file.is_file():
            continue

        try:

            text = load_document(file)

            added_chunks += ingest_text(
                text=text,
                database=database,
                embedding_service=embedding_service,
                source=file.name
            )

        except ValueError:
            # Desteklenmeyen dosya türü
            continue

    return added_chunks


def ingest_document(
    file_path,
    database,
    embedding_service
):
    """
    Tek bir dokümanı okuyup chunk'lara ayırarak veritabanına kaydeder.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    text = load_document(path)

    return ingest_text(
        text=text,
        database=database,
        embedding_service=embedding_service,
        source=path.name
    )