from fastapi import APIRouter, Depends
from app.controllers.user_controller import UserController
from app.models.schema import CreateUserRequest, UserResponse, PremiumCheckResponse
from app.services.auth_service import get_current_user_email

router = APIRouter(prefix="/users", tags=["users"])

user_controller = UserController()

@router.post("/", response_model=UserResponse)
async def create_user(user_request: CreateUserRequest):
    """
    Create a new user with the given email.

    - **email**: User's email address
    """
    return user_controller.create_user(user_request)

@router.get("/premium", response_model=PremiumCheckResponse)
async def check_premium(user_email: str = Depends(get_current_user_email)):
    """
    Check if the authenticated user has premium status.

    Returns the user's email and premium status.
    """
    return user_controller.check_premium(user_email)
