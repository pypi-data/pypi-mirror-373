"""LLM service implementation."""

from typing import List

from ..models.llm import LLMModel
from ..utils.http import ApiRequestHandler


class LLMService:
    """Service for managing LLM models."""

    def __init__(self, api_domain: str, token: str, verify_ssl: bool = True):
        """Initialize the LLM models service.

        Args:
            api_domain: Base URL for the CodeMie API
            token: Authentication token
            verify_ssl: Whether to verify SSL certificates. Default: True
        """
        self._api = ApiRequestHandler(api_domain, token, verify_ssl)

    def list(self) -> List[LLMModel]:
        """Get list of available LLM models.

        Returns:
            List of LLM models
        """
        return self._api.get("/v1/llm_models", List[LLMModel], wrap_response=False)

    def list_embeddings(self) -> List[LLMModel]:
        """Get list of available embeddings models.

        Returns:
            List of embeddings models
        """
        return self._api.get(
            "/v1/embeddings_models", List[LLMModel], wrap_response=False
        )
