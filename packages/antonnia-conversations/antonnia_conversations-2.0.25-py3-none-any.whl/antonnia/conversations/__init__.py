"""
Antonnia Conversations Python SDK

A Python client library for the Antonnia Conversations API v2.

Example:
    ```python
    import asyncio
    from antonnia.conversations import Conversations
    from antonnia.conversations.types import MessageContentText
    
    async def main():
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
            
            # Create a message
            message = await client.sessions.messages.create(
                session_id=session.id,
                content=MessageContentText(type="text", text="Hello!"),
                role="user"
            )
            
            # Get a survey submission
            survey_submission = await client.sessions.survey_submissions.get(
                session_id=session.id,
                survey_submission_id="subm_123"
            )
            
            print(f"Created session: {session.id}")
            print(f"Created message: {message.id}")
    
    asyncio.run(main())
    ```
"""

from .client import Conversations

__version__ = "2.0.25"
__author__ = "Antonnia"
__email__ = "support@antonnia.com"

__all__ = [
    "Conversations",
] 