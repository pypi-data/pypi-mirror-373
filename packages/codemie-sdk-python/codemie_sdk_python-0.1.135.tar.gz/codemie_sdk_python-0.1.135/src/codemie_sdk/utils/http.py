"""HTTP utilities for CodeMie SDK."""

import os
from typing import TypeVar, Type, Optional, Any, Union, Dict, List, get_origin, get_args
from pydantic import BaseModel
import requests
import logging
from functools import wraps

T = TypeVar("T", bound=Union[BaseModel, List[BaseModel], dict])

logger = logging.getLogger(__name__)


def log_request(func):
    """Decorator to log request details"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        method = kwargs.get("method", args[0] if args else None)
        endpoint = kwargs.get("endpoint", args[1] if len(args) > 1 else None)
        logger.debug(f"Making {method} request to {self._base_url}{endpoint}")

        try:
            result = func(self, *args, **kwargs)
            logger.info(f"Successfully processed {method} request to {endpoint}")
            return result
        except Exception as e:
            logger.error(f"Error during {method} request to {endpoint}: {str(e)}")
            raise

    return wrapper


class ApiRequestHandler:
    """Handles HTTP requests with consistent error handling and response parsing."""

    def __init__(self, base_url: str, token: str, verify_ssl: bool = True):
        """Initialize the API request handler.

        Args:
            base_url: Base URL for the API
            token: Authentication token
            verify_ssl: Whether to verify SSL certificates
        """
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._verify_ssl = verify_ssl

    def _get_headers(self, exclude_content_type: bool = False) -> dict:
        """Gets request headers with auth token.

        Args:
            exclude_content_type: Whether to exclude Content-Type header (for multipart requests)
        """
        headers = {}
        if not exclude_content_type:
            headers["Content-Type"] = "application/json"

        headers["Authorization"] = (
            f"Bearer {self._token}"
            if os.getenv("ENV", "").lower() != "local"
            else "dev-codemie-user"
        )
        return headers

    def _parse_response(
        self,
        response: requests.Response,
        response_model: Type[T],
        wrap_response: bool = True,
    ) -> T:
        """Parse response data into model, handling both single models and lists.

        Args:
            response: Response from requests
            response_model: Type to parse into (can be a single model or List[model])
            wrap_response: Whether response is wrapped in 'data' field

        Returns:
            Parsed response object or list of objects
        """
        try:
            response_data = response.json()
            logger.debug(f"Received response with status {response.status_code}")
            logger.debug(f"Response datasource_type: {type(response_data)}")

            # Handle data wrapper for dict responses only
            if wrap_response and isinstance(response_data, dict):
                response_data = response_data.get("data", response_data)

            # If response_model is dict, return raw data
            if response_model is dict:
                return response_data

            # Handle List types
            origin = get_origin(response_model)
            if origin is list:
                # Get the model class from List[Model]
                model_class = get_args(response_model)[0]
                if not isinstance(response_data, list):
                    response_data = [response_data]
                return [model_class.model_validate(item) for item in response_data]
            else:
                # Handle single model
                return response_model.model_validate(response_data)

        except ValueError as e:
            logger.error(f"Failed to parse response: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {str(e)}")
            raise

    @log_request
    def get(
        self,
        endpoint: str,
        response_model: Type[T],
        params: Optional[Dict[str, Any]] = None,
        wrap_response: bool = True,
    ) -> T:
        """Makes a GET request and parses the response.

        Args:
            endpoint: API endpoint path
            response_model: Pydantic model class or List[Model] for response
            params: Query parameters
            wrap_response: Whether response is wrapped in 'data' field

        Returns:
            Parsed response object or list of objects
        """
        if params:
            logger.debug(f"Request params: {params}")
        response = requests.get(
            url=f"{self._base_url}{endpoint}",
            headers=self._get_headers(),
            params=params,
            verify=self._verify_ssl,
        )
        response.raise_for_status()

        return self._parse_response(response, response_model, wrap_response)

    @log_request
    def post(
        self,
        endpoint: str,
        response_model: Type[T],
        json_data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        wrap_response: bool = True,
    ) -> Union[T, requests.Response]:
        """Makes a POST request and parses the response.

        Args:
            endpoint: API endpoint path
            response_model: Pydantic model class or List[Model] for response
            json_data: JSON request body
            stream: Whether to return streaming response
            wrap_response: Whether response is wrapped in 'data' field

        Returns:
            Parsed response object/list or streaming response
        """
        if json_data:
            logger.debug(f"Request body: {json_data}")

        response = requests.post(
            url=f"{self._base_url}{endpoint}",
            headers=self._get_headers(),
            json=json_data,
            verify=self._verify_ssl,
            stream=stream,
        )
        response.raise_for_status()

        if stream:
            return response

        return self._parse_response(response, response_model, wrap_response)

    @log_request
    def post_multipart(
        self,
        endpoint: str,
        response_model: Type[T],
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[List] = None,
        wrap_response: bool = True,
    ) -> T:
        """Makes a POST multipart/form-data request and parses the response.

        Args:
            endpoint: API endpoint path
            response_model: Pydantic model class or List[Model] for response
            params: Url parameters
            data: Data to be sent as multipart/form-data
            files: List of file tuples for upload
            wrap_response: Whether response is wrapped in 'data' field

        Returns:
            Parsed response object or list of objects
        """

        response = requests.post(
            url=f"{self._base_url}{endpoint}",
            headers=self._get_headers(
                exclude_content_type=True
            ),  # Let requests set multipart content-type
            params=params,
            data=data,
            files=files,
            verify=self._verify_ssl,
        )
        response.raise_for_status()

        return self._parse_response(response, response_model, wrap_response)

    @log_request
    def put(
        self,
        endpoint: str,
        response_model: Type[T],
        json_data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        wrap_response: bool = True,
    ) -> T:
        """Makes a PUT request and parses the response.

        Args:
            endpoint: API endpoint path
            response_model: Pydantic model class or List[Model] for response
            json_data: JSON request body
            params: Query parameters
            wrap_response: Whether response is wrapped in 'data' field

        Returns:
            Parsed response object or list of objects
        """
        logger.debug(f"Request body: {json_data}")
        response = requests.put(
            url=f"{self._base_url}{endpoint}",
            headers=self._get_headers(),
            json=json_data,
            params=params,
            verify=self._verify_ssl,
        )
        response.raise_for_status()
        return self._parse_response(response, response_model, wrap_response)

    @log_request
    def delete(
        self, endpoint: str, response_model: Type[T], wrap_response: bool = True
    ) -> T:
        """Makes a DELETE request and parses the response.

        Args:
            endpoint: API endpoint path
            response_model: Pydantic model class or List[Model] for response
            wrap_response: Whether response is wrapped in 'data' field

        Returns:
            Parsed response object or list of objects
        """
        response = requests.delete(
            url=f"{self._base_url}{endpoint}",
            headers=self._get_headers(),
            verify=self._verify_ssl,
        )
        response.raise_for_status()

        return self._parse_response(response, response_model, wrap_response)
