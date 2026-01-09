from app.repositories.user_repository import create_user
from app.models.schema import CreateUserRequest, UserResponse

class UserController:

    def create_user(self, user_request: CreateUserRequest) -> UserResponse:
        """Create a new user with the given email."""
        user_id = create_user(user_request.email)

        if user_id is None:
            # User might already exist, let's try to get their info
            # For now, we'll return a basic response
            return UserResponse(id=0, email=user_request.email, created_at=None)

        return UserResponse(id=user_id, email=user_request.email)
