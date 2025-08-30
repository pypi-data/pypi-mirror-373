"""
Basic usage example for the Antonnia Conversations SDK.

This example demonstrates how to:
1. Create a conversation session
2. Send messages 
3. Search for sessions and messages
4. Handle errors properly
"""

import asyncio
import os
from antonnia.conversations import Conversations
from antonnia.conversations.types import MessageContentText
from antonnia.conversations.exceptions import (
    AuthenticationError,
    NotFoundError,
    APIError
)


async def main():
    # Get API token from environment variable
    api_token = os.getenv("ANTONNIA_API_TOKEN")
    if not api_token:
        print("Please set ANTONNIA_API_TOKEN environment variable")
        return
    
    # Initialize the client
    async with Conversations(
        token=api_token,
        base_url="https://api.antonnia.com"  # Update with your API URL
    ) as client:
        
        try:
            print("🚀 Creating a new conversation session...")
            
            # Create a new session
            session = await client.sessions.create(
                contact_id="user_12345",
                contact_name="John Doe",
                metadata={
                    "source": "website",
                    "priority": "normal",
                    "department": "support"
                }
            )
            
            print(f"✅ Session created: {session.id}")
            print(f"   Status: {session.status}")
            print(f"   Contact: {session.contact_id}")
            
            # Send a message from the user
            print("\n💬 Sending a message...")
            
            message = await client.sessions.messages.create(
                session_id=session.id,
                content=MessageContentText(
                    type="text", 
                    text="Hello! I need help with my account billing."
                ),
                role="user"
            )
            
            print(f"✅ Message sent: {message.id}")
            print(f"   Content: {message.content.text if message.content.type == 'text' else str(message.content.type)}")
            print(f"   Role: {message.role}")
            
            # Trigger an AI response (if you have AI agents configured)
            print("\n🤖 Triggering AI response...")
            
            try:
                updated_session = await client.sessions.reply(
                    session_id=session.id,
                    debounce_time=1000  # Wait 1 second before processing
                )
                print(f"✅ AI response triggered for session: {updated_session.id}")
            except APIError as e:
                print(f"⚠️  Could not trigger AI response: {e.message}")
                print("   This might be because no AI agent is configured for this session")
            
            # Search for messages in the session
            print("\n🔍 Searching for messages...")
            
            messages = await client.sessions.messages.search(
                session_id=session.id,
                limit=10
            )
            
            print(f"✅ Found {len(messages)} messages:")
            for i, msg in enumerate(messages, 1):
                # Handle different content types
                if msg.content.type == "text":
                    content_preview = msg.content.text[:50] + "..." if len(msg.content.text) > 50 else msg.content.text
                else:
                    content_preview = f"[{msg.content.type}]" # TODO: Handle other content types
                print(f"   {i}. [{msg.role}] {content_preview}")
            
            # Update session metadata
            print("\n📝 Updating session metadata...")
            
            updated_session = await client.sessions.update(
                session_id=session.id,
                metadata={
                    "source": "website",
                    "priority": "high",  # Escalated!
                    "department": "support",
                    "last_updated": "2024-01-15T10:30:00Z"
                }
            )
            
            print(f"✅ Session metadata updated")
            print(f"   New priority: {updated_session.metadata.get('priority')}")
            
            # Search for sessions by contact
            print("\n🔍 Searching for sessions by contact...")
            
            contact_sessions = await client.sessions.search(
                contact_id="user_12345",
                limit=5
            )
            
            print(f"✅ Found {len(contact_sessions)} sessions for contact:")
            for i, sess in enumerate(contact_sessions, 1):
                print(f"   {i}. {sess.id} - Status: {sess.status}")
            
            # Demonstrate error handling
            print("\n🚨 Demonstrating error handling...")
            
            try:
                # Try to get a non-existent session
                await client.sessions.get("invalid_session_id")
            except NotFoundError:
                print("✅ Correctly caught NotFoundError for invalid session ID")
            
            print("\n🎉 Example completed successfully!")
            
        except AuthenticationError:
            print("❌ Authentication failed. Please check your API token.")
        except APIError as e:
            print(f"❌ API Error: {e.message} (Status: {e.status_code})")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 