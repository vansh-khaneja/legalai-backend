from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.controllers.chat_controller import ChatController
from app.models.schema import IngestResponse, QueryRequest, QueryResponse, ChatResponse, AddMessageRequest, MessageResponse, ChatListResponse
from app.services.auth_service import get_current_user_email

router = APIRouter(prefix="/chat", tags=["chat"])

chat_controller = ChatController()

@router.post("/", response_model=ChatResponse)
async def create_chat(user_email: str = Depends(get_current_user_email)):
    """
    Create a new chat for the authenticated user.

    Returns the chat ID and user ID.
    """
    return chat_controller.create_chat(user_email)

@router.get("/", response_model=ChatListResponse)
async def get_chats(user_email: str = Depends(get_current_user_email)):
    """
    Get all chats for the authenticated user.

    Returns a list of chats with their IDs and creation timestamps.
    """
    return chat_controller.get_user_chats(user_email)

@router.post("/message", response_model=MessageResponse)
async def add_message(message_request: AddMessageRequest, user_email: str = Depends(get_current_user_email)):
    """
    Add a message to a chat.

    - **chat_id**: The ID of the chat
    - **role**: 'user' or 'assistant'
    - **content**: The message content
    """
    return chat_controller.add_message(message_request)

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...), 
    case_type: str = Form(...), 
    date: str = Form(...),
    user_email: str = Depends(get_current_user_email)
):
    """
    Ingest legal document into vector database
    """
    return await chat_controller.ingest(file, case_type, date)

@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    user_email: str = Depends(get_current_user_email)
):
    """
    Query the vector database and generate a response
    """
    return await chat_controller.query(request.query)
