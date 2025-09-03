"""
Sessions client for managing conversation sessions.
"""

import json
import httpx
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from .types import Session, SessionStatus, SessionUpdateFields, SessionSchedule, SessionScheduleStatus, ScheduledMessageConfig, ScheduledNodeConfig
from .messages import Messages
from .survey_submissions import SurveySubmissions
from .exceptions import create_error_from_response




class Sessions:
    """
    Sessions client for managing conversation sessions and their messages.
    
    Provides methods for creating, retrieving, updating, and managing conversation sessions.
    Also includes subclients for messages and survey submissions.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """
        Initialize the Sessions client.
        
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
        
        # Initialize messages subclient
        self.messages = Messages(
            base_url=self.base_url,
            token=self.token,
            http_client=self._client
        )
        
        # Initialize survey submissions subclient
        self.survey_submissions = SurveySubmissions(
            base_url=self.base_url,
            token=self.token,
            http_client=self._client
        )
    
    def _get_headers(self, content_type: Optional[str] = None) -> Dict[str, str]:
        """Get headers with authentication and optional content type."""
        headers = {"Authorization": f"Bearer {self.token}"}
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    async def create(
        self,
        contact_id: str,
        contact_name: str,
        agent_id: Optional[str] = None,
        status: SessionStatus = "open",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """
        Create a new conversation session.
        
        Args:
            contact_id: Unique identifier for the contact
            contact_name: Display name for the contact
            agent_id: Optional agent to assign to the session
            status: Initial status of the session (default: "open")
            metadata: Optional metadata dictionary
            
        Returns:
            Created session object
            
        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If request validation fails
            APIError: For other API errors
        """
        payload: Dict[str, Any] = {
            "contact_id": contact_id,
            "contact_name": contact_name,
            "status": status,
        }
        
        if agent_id is not None:
            payload["agent_id"] = agent_id
        if metadata is not None:
            payload["metadata"] = metadata
        
        response = await self._client.post(
            url=f"{self.api_url}/sessions",
            json=payload,
            headers=self._get_headers("application/json"),
        )
        
        if not response.is_success:
            error_data = response.json() if response.content else {}
            raise create_error_from_response(response.status_code, error_data)
        
        return Session(**response.json())

    async def get(self, session_id: str) -> Session:
        """
        Get a session by ID.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            Session object
            
        Raises:
            AuthenticationError: If authentication fails
            NotFoundError: If session is not found
            APIError: For other API errors
        """
        response = await self._client.get(
            url=f"{self.api_url}/sessions/{session_id}",
            headers=self._get_headers(),
        )
        
        if not response.is_success:
            error_data = response.json() if response.content else {}
            raise create_error_from_response(response.status_code, error_data)
        
        return Session(**response.json())

    async def update(
        self,
        session_id: str,
        fields: Optional[SessionUpdateFields] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """
        Update session fields.
        
        Args:
            session_id: ID of the session to update
            fields: Session fields to update (metadata, status, agent_id, etc.)
            metadata: [DEPRECATED] New metadata to set - use fields instead
            
        Returns:
            Updated session object
            
        Raises:
            AuthenticationError: If authentication fails
            NotFoundError: If session is not found
            ValidationError: If request validation fails
            APIError: For other API errors
        """
        if fields is not None:
            payload = {"fields": fields}
        elif metadata is not None:
            # Backward compatibility
            payload = {"fields": {"metadata": metadata}}
        else:
            raise ValueError("Either 'fields' or 'metadata' must be provided")
        
        response = await self._client.patch(
            url=f"{self.api_url}/sessions/{session_id}",
            json=payload,
            headers=self._get_headers("application/json"),
        )
        
        if not response.is_success:
            error_data = response.json() if response.content else {}
            raise create_error_from_response(response.status_code, error_data)
        
        return Session(**response.json())

    async def transfer(self, session_id: str, agent_id: Optional[str] = None) -> Session:
        """
        Transfer a session to another agent.
        
        Args:
            session_id: ID of the session to transfer
            agent_id: ID of the agent to transfer to
            
        Returns:
            Updated session object
            
        Raises:
            AuthenticationError: If authentication fails
            NotFoundError: If session is not found
            ValidationError: If request validation fails
            APIError: For other API errors
        """
        payload = {"agent_id": agent_id}
        
        response = await self._client.post(
            url=f"{self.api_url}/sessions/{session_id}/transfer",
            json=payload,
            headers=self._get_headers("application/json"),
        )
        
        if not response.is_success:
            error_data = response.json() if response.content else {}
            raise create_error_from_response(response.status_code, error_data)
        
        return Session(**response.json())

    async def finish(
        self,
        session_id: str,
        ending_survey_id: Optional[str] = None,
    ) -> Session:
        """
        Finish a conversation session.
        
        Args:
            session_id: ID of the session to finish
            ending_survey_id: Optional survey ID to associate with session ending
            
        Returns:
            Finished session object
            
        Raises:
            AuthenticationError: If authentication fails
            NotFoundError: If session is not found
            ValidationError: If request validation fails
            APIError: For other API errors
        """
        payload = {}
        if ending_survey_id is not None:
            payload["ending_survey_id"] = ending_survey_id
        
        response = await self._client.post(
            url=f"{self.api_url}/sessions/{session_id}/finish",
            json=payload,
            headers=self._get_headers("application/json"),
        )
        
        if not response.is_success:
            error_data = response.json() if response.content else {}
            raise create_error_from_response(response.status_code, error_data)
        
        return Session(**response.json())

    async def reply(
        self,
        session_id: str,
        debounce_time: int = 12,
    ) -> Session:
        """
        Trigger an automatic agent reply for the session.
        
        Args:
            session_id: ID of the session to reply to
            debounce_time: Time in seconds to wait before processing
            
        Returns:
            Session object
            
        Raises:
            AuthenticationError: If authentication fails
            NotFoundError: If session is not found
            ValidationError: If request validation fails (e.g., session not open)
            APIError: For other API errors
        """
        payload = {"debounce_time": debounce_time}
        
        response = await self._client.post(
            url=f"{self.api_url}/sessions/{session_id}/reply",
            json=payload,
            headers=self._get_headers("application/json"),
        )
        
        if not response.is_success:
            error_data = response.json() if response.content else {}
            raise create_error_from_response(response.status_code, error_data)
        
        return Session(**response.json())

    async def search(
        self,
        contact_id: Optional[str] = None,
        status: Optional[SessionStatus] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Session]:
        """
        Search for sessions with optional filters.
        
        Args:
            contact_id: Filter by contact ID
            status: Filter by session status
            offset: Number of results to skip (for pagination)
            limit: Maximum number of results to return
            
        Returns:
            List of session objects
            
        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If request validation fails
            APIError: For other API errors
        """
        payload = {}
        if contact_id is not None:
            payload["contact_id"] = contact_id
        if status is not None:
            payload["status"] = status
        if offset is not None:
            payload["offset"] = offset
        if limit is not None:
            payload["limit"] = limit
        
        response = await self._client.post(
            url=f"{self.api_url}/sessions/search",
            json=payload,
            headers=self._get_headers("application/json"),
        )
        
        if not response.is_success:
            error_data = {}
            if response.content:
                try:
                    error_data = response.json()
                except (ValueError, json.JSONDecodeError):
                    error_data = {"error": f"Invalid JSON response: {response.text}"}
            raise create_error_from_response(response.status_code, error_data)
        
        return [Session(**session) for session in response.json()]


    async def schedule(
        self,
        session_id: str,
        scheduled_for: datetime,
        config: Union[ScheduledMessageConfig, ScheduledNodeConfig],
    ) -> SessionSchedule:

        payload: Dict[str, Any] = {
            "scheduled_for": scheduled_for.isoformat(),
            "config": config.model_dump(),
        }

        response = await self._client.post(
            url=f"{self.api_url}/sessions/{session_id}/schedule",
            json=payload,
            headers=self._get_headers("application/json"),
        )
        
        if not response.is_success:
            error_data = response.json() if response.content else {}
            raise create_error_from_response(response.status_code, error_data)
        
        return SessionSchedule(**response.json())

    async def close(self) -> None:
        """Close the HTTP client if owned by this instance."""
        if self._owns_client:
            await self._client.aclose() 