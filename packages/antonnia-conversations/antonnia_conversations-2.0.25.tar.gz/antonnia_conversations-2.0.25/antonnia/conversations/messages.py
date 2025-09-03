"""
Messages client for managing conversation messages.
"""

import httpx
from typing import Dict, List, Optional

from .types import Message, MessageContent, MessageRole
from .exceptions import create_error_from_response


class Messages:
    """
    Messages client for managing conversation messages.
    
    Provides methods for creating, retrieving, updating, and searching messages within sessions.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """
        Initialize the Messages client.
        
        Args:
            base_url: Base URL for the API
            token: Authentication token
            http_client: Optional shared HTTP client instance
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.api_url = self.base_url
        self._client = http_client or httpx.AsyncClient(timeout=httpx.Timeout(timeout=600.0, connect=5.0), limits=httpx.Limits(max_connections=1000, max_keepalive_connections=100))
        self._owns_client = http_client is None

    def _get_headers(self, content_type: Optional[str] = None) -> Dict[str, str]:
        """Get headers with authentication and optional content type."""
        headers = {"Authorization": f"Bearer {self.token}"}
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    async def create(
        self,
        session_id: str,
        content: MessageContent,
        role: MessageRole = "user",
        provider_message_id: Optional[str] = None,
        replied_provider_message_id: Optional[str] = None,
    ) -> Message:
        """
        Create a new message in a session.
        
        Args:
            session_id: ID of the session to add the message to
            content: Message content (text, image, audio, etc.)
            role: Role of the message sender (user, assistant)
            provider_message_id: Optional external system message ID
            replied_provider_message_id: Optional ID of message being replied to
            
        Returns:
            Created message object
            
        Raises:
            AuthenticationError: If authentication fails
            NotFoundError: If session is not found
            ValidationError: If request validation fails
            APIError: For other API errors
        """
        # Convert content to dict if it's a Pydantic model
        if hasattr(content, 'model_dump'):
            content_dict = content.model_dump()
        else:
            content_dict = content
        
        payload = {
            "content": content_dict,
            "role": role,
        }
        
        if provider_message_id is not None:
            payload["provider_message_id"] = provider_message_id
        if replied_provider_message_id is not None:
            payload["replied_provider_message_id"] = replied_provider_message_id
        
        response = await self._client.post(
            url=f"{self.api_url}/sessions/{session_id}/messages",
            json=payload,
            headers=self._get_headers("application/json"),
        )
        
        if not response.is_success:
            error_data = response.json() if response.content else {}
            raise create_error_from_response(response.status_code, error_data)
        
        return Message(**response.json())

    async def get(
        self,
        session_id: str,
        message_id: str,
    ) -> Optional[Message]:
        """
        Get a specific message by ID.
        
        Args:
            session_id: ID of the session containing the message
            message_id: ID of the message to retrieve
            
        Returns:
            Message object or None if not found
            
        Raises:
            AuthenticationError: If authentication fails
            NotFoundError: If session or message is not found
            APIError: For other API errors
        """
        response = await self._client.get(
            url=f"{self.api_url}/sessions/{session_id}/messages/{message_id}",
            headers=self._get_headers(),
        )
        
        if not response.is_success:
            error_data = response.json() if response.content else {}
            raise create_error_from_response(response.status_code, error_data)
        
        response_data = response.json()
        return Message(**response_data) if response_data else None

    async def update(
        self,
        session_id: str,
        message_id: str,
        provider_message_id: Optional[str] = None,
        replied_provider_message_id: Optional[str] = None,
    ) -> Message:
        """
        Update message metadata (provider IDs only).
        
        Args:
            session_id: ID of the session containing the message
            message_id: ID of the message to update
            provider_message_id: New provider message ID
            replied_provider_message_id: New replied provider message ID
            
        Returns:
            Updated message object
            
        Raises:
            AuthenticationError: If authentication fails
            NotFoundError: If session or message is not found
            ValidationError: If request validation fails
            APIError: For other API errors
        """
        payload = {}
        if provider_message_id is not None:
            payload["provider_message_id"] = provider_message_id
        if replied_provider_message_id is not None:
            payload["replied_provider_message_id"] = replied_provider_message_id
        
        response = await self._client.patch(
            url=f"{self.api_url}/sessions/{session_id}/messages/{message_id}",
            json=payload,
            headers=self._get_headers("application/json"),
        )
        
        if not response.is_success:
            error_data = response.json() if response.content else {}
            raise create_error_from_response(response.status_code, error_data)
        
        return Message(**response.json())

    async def search(
        self,
        session_id: Optional[str] = None,
        provider_message_id: Optional[str] = None,
        replied_provider_message_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Message]:
        """
        Search for messages with optional filters.
        
        Args:
            session_id: Filter by session ID
            provider_message_id: Filter by provider message ID
            replied_provider_message_id: Filter by replied provider message ID
            offset: Number of results to skip (for pagination)
            limit: Maximum number of results to return
            
        Returns:
            List of message objects
            
        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If request validation fails
            APIError: For other API errors
        """
        payload = {}
        if session_id is not None:
            payload["session_id"] = session_id
        if provider_message_id is not None:
            payload["provider_message_id"] = provider_message_id
        if replied_provider_message_id is not None:
            payload["replied_provider_message_id"] = replied_provider_message_id
        if offset is not None:
            payload["offset"] = offset
        if limit is not None:
            payload["limit"] = limit
        
        response = await self._client.post(
            url=f"{self.api_url}/sessions/{session_id}/messages/search" if session_id else f"{self.api_url}/messages/search",
            json=payload,
            headers=self._get_headers("application/json"),
        )
        
        if not response.is_success:
            error_data = response.json() if response.content else {}
            raise create_error_from_response(response.status_code, error_data)
        
        return [Message(**message) for message in response.json()]

    async def close(self) -> None:
        """Close the HTTP client if owned by this instance."""
        if self._owns_client:
            await self._client.aclose() 