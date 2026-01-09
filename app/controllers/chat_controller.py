from fastapi import UploadFile
from app.services.rag_service import RagService
from app.services.embedding_service import EmbeddingService
from app.services.chat_service import ChatService
from app.services.s3_service import S3Service
from app.repositories.vector_repository import VectorRepository
from app.repositories.user_repository import get_user_by_email, create_user
from app.repositories.chat_repository import create_chat, get_user_chats
from app.repositories.message_repository import add_message
from app.models.schema import ChatResponse, AddMessageRequest, MessageResponse, ChatListResponse
import uuid
import os

class ChatController:

    def __init__(self):
        self.vector_repo = VectorRepository()
        self.embedding_service = EmbeddingService()
        self.rag_service = RagService()
        self.chat_service = ChatService()
        self.s3_service = S3Service()

    def create_chat(self, user_email: str) -> ChatResponse:
        """Create a new chat for the user with the given email."""
        # Get user by email, create if doesn't exist
        user = get_user_by_email(user_email)
        if not user:
            # User doesn't exist, create them
            user_id = create_user(user_email)
            if not user_id:
                raise ValueError(f"Failed to create user with email {user_email}")
            user = {"id": user_id, "email": user_email}

        # Create new chat for this user
        chat_id = create_chat(user["id"])
        if not chat_id:
            raise ValueError(f"Failed to create chat for user {user_email}")

        return ChatResponse(id=chat_id, user_id=user["id"])

    def add_message(self, message_request: AddMessageRequest) -> MessageResponse:
        """Add a message to a chat."""
        # Validate role
        if message_request.role not in ['user', 'assistant']:
            raise ValueError(f"Invalid role: {message_request.role}. Must be 'user' or 'assistant'")

        # Add message to database
        add_message(message_request.chat_id, message_request.role, message_request.content)

        return MessageResponse(
            chat_id=message_request.chat_id,
            role=message_request.role,
            content=message_request.content
        )

    def get_user_chats(self, user_email: str) -> ChatListResponse:
        """Get all chats for a user."""
        # Get user by email
        user = get_user_by_email(user_email)
        if not user:
            raise ValueError(f"User with email {user_email} not found")

        # Get all chats for this user
        chats = get_user_chats(user["id"])

        return ChatListResponse(chats=chats)

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
