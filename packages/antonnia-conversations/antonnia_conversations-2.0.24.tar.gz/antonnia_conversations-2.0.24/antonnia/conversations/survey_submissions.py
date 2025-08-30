"""
Survey submissions client for managing survey submissions.
"""

import httpx
from typing import Optional

from .types import SurveySubmission
from .exceptions import create_error_from_response


class SurveySubmissions:
    """
    Survey submissions client for managing survey submissions within sessions.
    
    Provides methods for retrieving and managing survey submissions.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """
        Initialize the SurveySubmissions client.
        
        Args:
            base_url: Base URL for the API
            token: Authentication token
            http_client: Optional shared HTTP client instance
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.api_url = self.base_url
        self._client = http_client or httpx.AsyncClient(timeout=60.0)
        self._owns_client = http_client is None
    
    def _get_headers(self, content_type: Optional[str] = None) -> dict[str, str]:
        """Get headers with authentication and optional content type."""
        headers = {"Authorization": f"Bearer {self.token}"}
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    async def get(self, session_id: str, survey_submission_id: str) -> SurveySubmission:
        """
        Get a survey submission by ID within a session.
        
        Args:
            session_id: ID of the session containing the survey submission
            survey_submission_id: ID of the survey submission to retrieve
            
        Returns:
            SurveySubmission object
            
        Raises:
            AuthenticationError: If authentication fails
            NotFoundError: If survey submission is not found
            APIError: For other API errors
        """
        response = await self._client.get(
            url=f"{self.api_url}/sessions/{session_id}/surveys/{survey_submission_id}",
            headers=self._get_headers(),
        )
        
        if not response.is_success:
            error_data = response.json() if response.content else {}
            raise create_error_from_response(response.status_code, error_data)
        
        return SurveySubmission(**response.json())

    async def reply(self, session_id: str, survey_submission_id: str) -> SurveySubmission:
        """
        Trigger automatic reply for a survey submission.
        
        Args:
            session_id: ID of the session containing the survey submission
            survey_submission_id: ID of the survey submission to process
            
        Returns:
            Updated SurveySubmission object
            
        Raises:
            AuthenticationError: If authentication fails
            NotFoundError: If survey submission is not found
            ValidationError: If survey submission is not active
            APIError: For other API errors
        """
        response = await self._client.post(
            url=f"{self.api_url}/sessions/{session_id}/surveys/{survey_submission_id}/reply",
            headers=self._get_headers(),
        )
        
        if not response.is_success:
            error_data = response.json() if response.content else {}
            raise create_error_from_response(response.status_code, error_data)
        
        return SurveySubmission(**response.json())

    async def close(self) -> None:
        """Close the HTTP client to free up resources."""
        if self._owns_client:
            await self._client.aclose() 