from fastapi import UploadFile
from services.rag_service import RagService
from services.embedding_service import EmbeddingService
from services.chat_service import ChatService
from services.cloudinary_service import CloudinaryService
from repositories.vector_repository import VectorRepository
import uuid

class ChatController:

    def __init__(self):
        self.vector_repo = VectorRepository()
        self.embedding_service = EmbeddingService()
        self.rag_service = RagService()
        self.chat_service = ChatService()
        self.cloudinary_service = CloudinaryService()

    async def ingest(self, file: UploadFile, case_type: str, date: str):
        # Upload PDF to Cloudinary
        cloudinary_response = self.cloudinary_service.upload_file_stream(file.file, file.filename)
        pdf_url = cloudinary_response["secure_url"]
        
        # Reset file pointer for text extraction
        await file.seek(0)
        
        text = self.rag_service.pdf_to_text(file.file)
        chunks = self.rag_service.chunk_text(text)

        embeddings = self.embedding_service.embed(chunks)

        file_id = str(uuid.uuid4())

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
