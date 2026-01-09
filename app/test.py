from repositories.vector_repository import VectorRepository
from services.embedding_service import EmbeddingService
es = EmbeddingService()

vr = VectorRepository()

text = "I love Electonic"
embedding = es.get_text_embedding(text)

vr.ingest_vector(embedding, text, "contract", "file_123", "2024-10-01")

