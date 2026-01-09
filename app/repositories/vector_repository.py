from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import uuid

class VectorRepository:
    def __init__(self):
        load_dotenv()
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            check_compatibility=False
        )
        self.collection_name = os.getenv("QDRANT_CLUSTER_NAME")
        self.vector_dimension = int(os.getenv("VECTOR_DIMENSION", "1536"))
        self._ensure_collection()

    def _ensure_collection(self):
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_dimension, distance=Distance.COSINE)
            )

    def retrieve_top_k(self, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
    # Use qdrant.query_points with query as direct vector (list of floats)
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,        # just pass the list of floats
            with_payload=True,            # get payload back
            limit=top_k
        )

        output = []
        for pt in results.points:
            output.append({
                "score": pt.score,
                "text": pt.payload.get("text"),
                "case_types": pt.payload.get("case_types"),
                "file_id": pt.payload.get("file_id"),
                "date": pt.payload.get("date"),
                "pdf_url": pt.payload.get("pdf_url")
            })
        return output

    def add(self, embeddings: List[List[float]], texts: List[str], case_type: str, file_id: str, date: str, pdf_url: str):
        # Ingest multiple vectors with payloads into Qdrant
        points = []
        for i, (embedding, text) in enumerate(zip(embeddings, texts)):
            point = PointStruct(
                id=str(uuid.uuid4()),  # Use UUID for unique ID
                vector=embedding,
                payload={
                    "text": text,
                    "case_types": case_type,
                    "file_id": file_id,
                    "date": date,
                    "pdf_url": pdf_url
                }
            )
            points.append(point)
        self.client.upsert(collection_name=self.collection_name, points=points)
