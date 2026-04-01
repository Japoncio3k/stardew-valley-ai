import os

from fastembed.common.types import NumpyArray
from qdrant_client import QdrantClient, http
from qdrant_client.http.models import CollectionInfo, PointStruct, QueryResponse


class QdrantDatasource:
    def __init__(self) -> None:
        self.client = QdrantClient(
            url=os.environ.get("QDRANT_URL"),
            api_key=os.environ.get("QDRANT_API_KEY"),
        )

    def ensure_collection(self, collection_name: str, vector_size: int) -> None:
        try:
            self.client.get_collection(collection_name=collection_name)
            self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=http.models.VectorParams(
                    size=vector_size,
                    distance=http.models.Distance.COSINE,
                ),
            )
        except Exception as _:  # collection doesnt exist
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=http.models.VectorParams(
                    size=vector_size,
                    distance=http.models.Distance.COSINE,
                ),
            )

    def upsert_points(self, collection_name: str, points: list[PointStruct]) -> None:
        self.client.upsert(
            collection_name=collection_name,
            points=points,
            wait=True,
        )

    def search(self, collection_name: str, query_vector: NumpyArray, limit: int = 20) -> QueryResponse:
        return self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True,
        )

    def get_collection_info(self, collection_name: str) -> CollectionInfo:
        return self.client.get_collection(collection_name=collection_name)
