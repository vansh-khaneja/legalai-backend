from fastapi import APIRouter
from app.controllers.user_controller import UserController
from app.models.schema import CreateUserRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])

user_controller = UserController()

@router.post("/", response_model=UserResponse)
async def create_user(user_request: CreateUserRequest):
    """
    Create a new user with the given email.

    - **email**: User's email address
    """
    return user_controller.create_user(user_request)
