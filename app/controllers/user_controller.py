from app.repositories.user_repository import create_user, is_user_premium
from app.models.schema import CreateUserRequest, UserResponse, PremiumCheckResponse

class UserController:

    def create_user(self, user_request: CreateUserRequest) -> UserResponse:
        """Create a new user with the given email."""
        user_id = create_user(user_request.email)

        if user_id:
            return UserResponse(id=user_id, email=user_request.email)
        else:
            raise ValueError(f"Failed to create or find user with email {user_request.email}")

    def check_premium(self, email: str) -> PremiumCheckResponse:
        """Check if a user has premium status."""
        is_premium = is_user_premium(email)
        return PremiumCheckResponse(email=email, is_premium=is_premium)
