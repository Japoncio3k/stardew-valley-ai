import json
from typing import Any, Dict

from fastembed import TextEmbedding
from qdrant_client import http

from data_ingestion.data.qdrant_datasource import QdrantDatasource

COLLECTION_NAME = "stardew"
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"

embedding_model = TextEmbedding(model_name=EMBEDDING_MODEL)


def get_embedding_model_size() -> int:
    return embedding_model.get_embedding_size(model_name=EMBEDDING_MODEL)


def create_embedding_text(chunk: Dict[str, Any]) -> str:
    """Creates a combined text string for embedding from an enriched chunk."""
    return f"""
    {chunk.get("summary", "")}\n
    {chunk.get("keywords", "")}\n
    {chunk.get("source", "")}\n
    {chunk.get("hypothetical_questions", "")}\n
    {chunk.get("table_summary", "") if chunk.get("is_table", False) else chunk.get("content")}
    """


def ingest_file(file_path: str, next_id: int, qdrant_ds: QdrantDatasource) -> int:
    """Ingests a single enriched chunks file into Qdrant. Returns the updated next_id."""
    with open(file_path, "r", encoding="utf-8") as fp:
        try:
            data = json.load(fp)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {file_path}: {e}")
            return next_id

    points_to_upsert = []
    texts_to_embed = []
    for chunk in data["items"]:
        texts_to_embed.append(create_embedding_text(chunk))
        points_to_upsert.append(
            http.models.PointStruct(
                id=next_id,
                payload=chunk,
                vector=[],
            )
        )
        next_id += 1

    print(f"Prepared {len(points_to_upsert)} points for upsert.")

    if len(points_to_upsert) == 0:
        print("No points to upsert, skipping file.")
        return next_id

    print("Generating embeddings...")
    embeddings = list(embedding_model.embed(texts_to_embed, batch_size=32))

    print("Upserting into Qdrant...")
    for i, embedding in enumerate(embeddings):
        points_to_upsert[i].vector = embedding.tolist()

    qdrant_ds.upsert_points(COLLECTION_NAME, points_to_upsert)

    print("Upsert complete!")

    collection_info = qdrant_ds.get_collection_info(COLLECTION_NAME)
    print(f"Points in collection: {collection_info.points_count}\n")

    return next_id
