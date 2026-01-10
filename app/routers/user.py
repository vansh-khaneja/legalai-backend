from fastapi import APIRouter, Depends
from app.controllers.user_controller import UserController
from app.models.schema import CreateUserRequest, UserResponse, PremiumCheckResponse
from app.services.auth_service import get_current_user_id

router = APIRouter(prefix="/users", tags=["users"])

user_controller = UserController()

@router.post("/", response_model=UserResponse)
async def create_user(user_request: CreateUserRequest):
    """
    Create a new user with the given email and user_id.

    - **email**: User's email address
    - **user_id**: User's custom ID (string)
    """
    return user_controller.create_user(user_request)

@router.get("/premium", response_model=PremiumCheckResponse)
async def check_premium(user_id: str = Depends(get_current_user_id)):
    """
    Check if the authenticated user has premium status.

    Returns the user's ID and premium status.
    """
    return user_controller.check_premium(user_id)
