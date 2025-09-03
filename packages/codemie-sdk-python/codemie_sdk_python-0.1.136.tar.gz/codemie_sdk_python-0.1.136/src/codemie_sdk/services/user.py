"""User service implementation."""

from ..models.user import User, UserData
from ..utils.http import ApiRequestHandler


class UserService:
    """Service for managing user profile and preferences."""

    def __init__(self, api_domain: str, token: str, verify_ssl: bool = True):
        """Initialize the User service.

        Args:
            api_domain: Base URL for the CodeMie API
            token: Authentication token
            verify_ssl: Whether to verify SSL certificates. Default: True
        """
        self._api = ApiRequestHandler(api_domain, token, verify_ssl)

    def about_me(self) -> User:
        """Get current user profile.

        Returns:
            User profile information
        """
        return self._api.get("/v1/user", User, wrap_response=False)

    def get_data(self) -> UserData:
        """Get user data and preferences.

        Returns:
            User data and preferences
        """
        return self._api.get("/v1/user/data", UserData, wrap_response=False)
