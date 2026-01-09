from fastapi import APIRouter, UploadFile, File, Form, Depends
from controllers.chat_controller import ChatController
from models.schema import IngestResponse, QueryRequest, QueryResponse
from services.auth_service import get_current_user_email

router = APIRouter(prefix="/chat", tags=["chat"])

chat_controller = ChatController()

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
