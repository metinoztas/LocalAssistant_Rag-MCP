"""
Retrieval Module

Görevleri:
- Sorgu embedding'ini oluşturmak
- Doküman benzerlik skorlarını hesaplamak
- Sonuçları filtrelemek
- Sonuçları sıralamak
- En alakalı dokümanları döndürmek
"""

from math import sqrt
from app.config import SEMANTIC_WEIGHT, KEYWORD_WEIGHT
from app.text_cleaner import keyword_score


def cosine_similarity(vector1, vector2):
    """
    İki embedding arasındaki cosine similarity değerini hesaplar.
    """

    if len(vector1) != len(vector2):
        raise ValueError(
            "Embedding boyutları uyuşmuyor."
        )

    dot_product = sum(
        a * b
        for a, b in zip(vector1, vector2)
    )

    norm1 = sqrt(sum(x * x for x in vector1))
    norm2 = sqrt(sum(x * x for x in vector2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def calculate_similarity_scores(
    query,
    query_embedding,
    documents
):
    """
    Her doküman için cosine similarity skorunu hesaplar.
    """

    results = []

    for document in documents:

        semantic_score = cosine_similarity(
            query_embedding,
            document["embedding"]
        )

        lexical_score = keyword_score(
            query,
            document["content"]
        )

        final_score = (
            semantic_score * SEMANTIC_WEIGHT
            +
            lexical_score * KEYWORD_WEIGHT
        )

        results.append({
            "id": document["id"],
            "content": document["content"],
            "source": document["source"],
            "chunk_index": document["chunk_index"],
            "semantic_score": semantic_score,
            "keyword_score": lexical_score,
            "score": final_score
        })

    return results


def filter_results(
    results,
    threshold=None
):
    """
    Threshold verilmişse düşük skorlu sonuçları eler.
    """

    if threshold is None:
        return results

    return [
        result
        for result in results
        if result["score"] >= threshold
    ]


def sort_results(results):
    """
    Sonuçları benzerlik skoruna göre sıralar.
    """

    return sorted(
        results,
        key=lambda item: item["score"],
        reverse=True
    )


def retrieve(
    query,
    database,
    embedding_service,
    k=3,
    threshold=None
):
    """
    Veritabanındaki en alakalı dokümanları döndürür.
    """

    documents = database.get_documents()

    if not documents:
        return []

    query_embedding = embedding_service.embed(query)

    results = calculate_similarity_scores(
        query,
        query_embedding,
        documents
    )

    results = filter_results(
        results,
        threshold
    )

    results = sort_results(results)

    return results[:k]


def retrieve_best_match(
    query,
    database,
    embedding_service,
    threshold=None
):
    """
    En yüksek skorlu tek sonucu döndürür.
    """

    results = retrieve(
        query=query,
        database=database,
        embedding_service=embedding_service,
        k=1,
        threshold=threshold
    )

    if not results:
        return None

    return results[0]


