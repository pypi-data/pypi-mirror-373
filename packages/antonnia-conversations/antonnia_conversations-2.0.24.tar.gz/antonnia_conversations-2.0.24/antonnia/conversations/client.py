"""
Main Conversations API client for the Antonnia SDK.
"""

import httpx
from typing import Optional

from .sessions import Sessions


class Conversations:
    """
    Main client for the Antonnia Conversations API v2.
    
    This client manages authentication and provides access to all API endpoints
    through organized sub-clients.
    
    Example:
        ```python
        async with Conversations(
            token="your_api_token",
            base_url="https://api.antonnia.com"
        ) as client:
            # Create a session
            session = await client.sessions.create(
                contact_id="1234567890",
                contact_name="John Doe",
                metadata={"priority": "high"}
            )
            
            # Create a message within the session
            message = await client.sessions.messages.create(
                session_id=session.id,
                content={"type": "text", "text": "Hello!"},
                role="user"
            )
        ```
    """
    
    def __init__(
        self,
        token: str,
        base_url: str = "https://services.antonnia.com/conversations/v2",
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """
        Initialize the Conversations API client.
        
        Args:
            token: Authentication token for API access
            base_url: Base URL for the API (default: "https://api.antonnia.com")
            http_client: Optional existing HTTP client to reuse
        """
        self.token = token
        self.base_url = base_url.rstrip('/')
        
        # Initialize HTTP client with common configuration
        self._http_client = http_client or httpx.AsyncClient(timeout=httpx.Timeout(timeout=300.0, connect=60.0), limits=httpx.Limits(max_connections=1000, max_keepalive_connections=100) )
        self._owns_client = http_client is None
        
        # Initialize sessions client (which includes messages as a subclient)
        self.sessions = Sessions(
            base_url=self.base_url,
            token=self.token,
            http_client=self._http_client
        )
    
    async def close(self) -> None:
        """Close the HTTP client to free up resources."""
        if self._owns_client:
            await self._http_client.aclose()
    
    async def __aenter__(self) -> "Conversations":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close() 