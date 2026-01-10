from app.repositories.user_repository import create_user, is_user_premium
from app.models.schema import CreateUserRequest, UserResponse, PremiumCheckResponse

class UserController:

    def create_user(self, user_request: CreateUserRequest) -> UserResponse:
        """Create a new user with the given email and user_id."""
        user_id = create_user(user_request.email, user_request.user_id)

        if user_id:
            return UserResponse(id=user_id, email=user_request.email)
        else:
            raise ValueError(f"Failed to create or find user with email {user_request.email}")

    def check_premium(self, user_id: str) -> PremiumCheckResponse:
        """Check if a user has premium status."""
        is_premium = is_user_premium(user_id)
        return PremiumCheckResponse(user_id=user_id, is_premium=is_premium)
