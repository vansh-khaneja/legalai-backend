from app.repositories.user_repository import create_user
from app.models.schema import CreateUserRequest, UserResponse

class UserController:

    def create_user(self, user_request: CreateUserRequest) -> UserResponse:
        """Create a new user with the given email."""
        user_id = create_user(user_request.email)

        if user_id:
            return UserResponse(id=user_id, email=user_request.email)
        else:
            raise ValueError(f"Failed to create or find user with email {user_request.email}")
