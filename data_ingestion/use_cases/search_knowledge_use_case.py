from typing import Any

from fastembed import TextEmbedding
from sentence_transformers import CrossEncoder

from data_ingestion.data.qdrant_datasource import QdrantDatasource

COLLECTION_NAME = "stardew"

embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
cross_encoder_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def search_knowledge(
    query: str,
    qdrant_ds: QdrantDatasource,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Searches the knowledge base using vector similarity and cross-encoder reranking."""
    query_embedding = list(embedding_model.embed([query]))[0]

    search_results = qdrant_ds.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=20,
    )

    rerank_pairs: list[list[str]] = []
    for point in search_results.points:
        if point.payload:
            rerank_pairs.append([query, point.payload.get("content")])  # type: ignore
    scores = cross_encoder_model.predict(rerank_pairs)

    for i, score in enumerate(scores):
        search_results.points[i].score = score

    reranked_results = sorted(search_results.points, key=lambda x: x.score, reverse=True)
    print("  - Re-ranked the results using Cross-Encoder.")

    final_results = []
    for result in reranked_results[:top_k]:
        if result.payload:
            final_results.append(
                {
                    "source": result.payload.get("source"),
                    "content": result.payload.get("content"),
                    "summary": result.payload.get("summary"),
                    "rerank_score": float(result.score),
                }
            )

    return final_results
