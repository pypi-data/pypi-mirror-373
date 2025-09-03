"""Conversation service implementation."""

from typing import List

from ..models.conversation import Conversation, ConversationDetails
from ..utils import ApiRequestHandler


class ConversationService:
    """Service for managing user conversations."""

    def __init__(self, api_domain: str, token: str, verify_ssl: bool = True):
        """Initialize the conversation service.

        Args:
            api_domain: Base URL for the API
            token: Authentication token
            verify_ssl: Whether to verify SSL certificates
        """
        self._api = ApiRequestHandler(api_domain, token, verify_ssl)

    def list(self) -> List[Conversation]:
        """Get list of all conversations for the current user.

        Returns:
            List of all conversations for the current user.
        """
        return self._api.get("/v1/conversations", List[Conversation])

    def list_by_assistant_id(self, assistant_id: str) -> List[Conversation]:
        """Get list of all conversations for the current user that include the specified assistant.

        Args:
            assistant_id: Assistant ID

        Returns:
            List of conversations for the specified assistant.
        """
        return [
            conv
            for conv in self._api.get("/v1/conversations", List[Conversation])
            if assistant_id in conv.assistant_ids
        ]

    def get_conversation(self, conversation_id: str) -> ConversationDetails:
        """Get details for a specific conversation by its ID.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation details
        """
        return self._api.get(
            f"/v1/conversations/{conversation_id}",
            ConversationDetails,
        )

    def delete(self, conversation_id: str) -> dict:
        """Delete a specific conversation by its ID.

        Args:
            conversation_id: Conversation ID to delete

        Returns:
            Deletion confirmation
        """
        return self._api.delete(
            f"/v1/conversations/{conversation_id}",
            dict,
        )
