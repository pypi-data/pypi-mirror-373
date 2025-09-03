"""
Example demonstrating survey submissions functionality.
"""

import asyncio
from antonnia.conversations import Conversations
from antonnia.conversations.types import MessageContentText


async def main():
    """
    Example of using survey submissions functionality.
    """
    async with Conversations(
        token="your_api_token",
        base_url="https://services.antonnia.com/conversations/v2"
    ) as client:
        # Create a session
        session = await client.sessions.create(
            contact_id="5531994340234",
            contact_name="John Doe",
            metadata={"priority": "high"}
        )
        
        print(f"Created session: {session.id}")
        
        # Send a message
        message = await client.sessions.messages.create(
            session_id=session.id,
            content=MessageContentText(type="text", text="Hello! How can I help you?"),
            role="user"
        )
        
        print(f"Created message: {message.id}")
        
        # If there's a survey submission available (from session finishing)
        if session.ending_survey_submission_id:
            # Get the survey submission
            survey_submission = await client.sessions.survey_submissions.get(
                session_id=session.id,
                survey_submission_id=session.ending_survey_submission_id
            )
            
            print(f"Found survey submission: {survey_submission.id}")
            print(f"Survey submission status: {survey_submission.status}")
            print(f"Survey expires at: {survey_submission.expires_at}")
            
            # If the survey is still active, trigger an automated reply
            if survey_submission.is_active:
                updated_submission = await client.sessions.survey_submissions.reply(
                    session_id=session.id,
                    survey_submission_id=survey_submission.id
                )
                
                print(f"Survey submission updated: {updated_submission.status}")
                print(f"Finished at: {updated_submission.finished_at}")
            else:
                print("Survey submission is no longer active")
        else:
            print("No survey submission found for this session")


if __name__ == "__main__":
    asyncio.run(main()) 