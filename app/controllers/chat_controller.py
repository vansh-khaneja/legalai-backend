from fastapi import UploadFile
from app.services.rag_service import RagService
from app.services.embedding_service import EmbeddingService
from app.services.chat_service import ChatService
from app.services.cloudinary_service import CloudinaryService
from app.repositories.vector_repository import VectorRepository
from app.repositories.user_repository import get_user_by_email, create_user
from app.repositories.chat_repository import create_chat, get_user_chats
from app.repositories.message_repository import add_message, get_chat_messages
from app.models.schema import ChatResponse, AddMessageRequest, MessageResponse, ChatListResponse, ChatMessagesResponse
import uuid
import os

class ChatController:

    def __init__(self):
        self.vector_repo = VectorRepository()
        self.embedding_service = EmbeddingService()
        self.rag_service = RagService()
        self.chat_service = ChatService()
        self.cloudinary_service = CloudinaryService()

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

    def get_chat_messages(self, chat_id: str, user_email: str, limit: int = None, offset: int = None) -> ChatMessagesResponse:
        """Get messages for a specific chat with pagination."""
        # First verify the user owns this chat
        user = get_user_by_email(user_email)
        if not user:
            raise ValueError(f"User with email {user_email} not found")

        # Get all chats for this user to verify ownership
        user_chats = get_user_chats(user["id"])
        chat_ids = [chat["id"] for chat in user_chats]

        if chat_id not in chat_ids:
            raise ValueError(f"Chat {chat_id} not found or doesn't belong to user {user_email}")

        # Get messages for this chat with pagination
        messages = get_chat_messages(chat_id, limit, offset)

        return ChatMessagesResponse(chat_id=chat_id, messages=messages)

    async def ingest(self, file: UploadFile, case_type: str, date: str):
        # Generate a stable file_id and use it as the filename
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1]
        filename = f"{file_id}{ext}"

        # Upload to Cloudinary
        upload_response = self.cloudinary_service.upload_file_stream(file.file, filename, folder="legal-documents")
        pdf_url = upload_response["url"]
        
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
        
        # Temporary hardcoded dummy results
        # results = [
        #     {
        #         "score": 0.89,
        #         "text": "According to Section 420 of the Indian Penal Code, cheating and dishonestly inducing delivery of property is punishable with imprisonment up to 7 years and fine.",
        #         "case_types": "Criminal Law - Fraud",
        #         "file_id": "dummy-file-001",
        #         "date": "2024-01-15",
        #         "pdf_url": "#"
        #     },
        #     {
        #         "score": 0.76,
        #         "text": "The Supreme Court in landmark judgment held that the burden of proof lies on the prosecution to establish guilt beyond reasonable doubt.",
        #         "case_types": "Criminal Procedure",
        #         "file_id": "dummy-file-002",
        #         "date": "2023-11-20",
        #         "pdf_url": "#"
        #     },
        #     {
        #         "score": 0.65,
        #         "text": "Under Article 21 of the Constitution, right to life includes right to live with dignity and all aspects that make life meaningful.",
        #         "case_types": "Constitutional Law",
        #         "file_id": "dummy-file-003",
        #         "date": "2024-02-10",
        #         "pdf_url": "#"
        #     }
        # ]
        
        # Build context from results
        context = "\n".join([result["text"] for result in results])
        # context = ""
        
        # Generate response
        response = self.chat_service.generate_response(query, context)
        
        return {"response": response, "sources": results}
        
