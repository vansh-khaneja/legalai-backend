from fastapi import UploadFile
from app.services.rag_service import RagService
from app.services.embedding_service import EmbeddingService
from app.services.chat_service import ChatService
from app.services.s3_service import S3Service
from app.repositories.vector_repository import VectorRepository
import uuid
import os

class ChatController:

    def __init__(self):
        self.vector_repo = VectorRepository()
        self.embedding_service = EmbeddingService()
        self.rag_service = RagService()
        self.chat_service = ChatService()
        self.s3_service = S3Service()

    async def ingest(self, file: UploadFile, case_type: str, date: str):
        # Generate a stable file_id and use it as the S3 object name
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1]
        s3_filename = f"{file_id}{ext}"

        # Upload to storage using file_id-based name
        s3_response = self.s3_service.upload_file_stream(file.file, s3_filename)
        pdf_url = s3_response["url"]
        
        # Reset file pointer for text extraction
        await file.seek(0)
        
        text = self.rag_service.pdf_to_text(file.file)
        chunks = self.rag_service.chunk_text(text)

        embeddings = self.embedding_service.embed(chunks)

        self.vector_repo.add(
            embeddings=embeddings,
            texts=chunks,
            case_type=case_type,
            file_id=file_id,
            date=date,
            pdf_url=pdf_url
        )

        return {"message": "Document ingested successfully", "chunks": len(chunks), "pdf_url": pdf_url}

    async def query(self, query: str):
        # Embed the query
        query_embedding = self.embedding_service.get_text_embedding(query)
        
        # Retrieve top k results
        results = self.vector_repo.retrieve_top_k(query_embedding, top_k=5)
        
        # Build context from results
        context = "\n".join([result["text"] for result in results])
        
        # Generate response
        response = self.chat_service.generate_response(query, context)
        
        return {"response": response, "sources": results}
