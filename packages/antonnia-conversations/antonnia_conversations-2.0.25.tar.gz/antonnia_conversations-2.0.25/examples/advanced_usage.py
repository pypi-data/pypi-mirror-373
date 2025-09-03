"""
Advanced usage example for the Antonnia SDK.

This example demonstrates:
1. Working with different message content types
2. Session transfers between agents  
3. Custom HTTP client configuration
4. Advanced error handling and retries
5. Pagination for large result sets
"""

import asyncio
import os
import httpx
from antonnia.conversations import Conversations
from antonnia.conversations.types import (
    MessageContentText,
    MessageContentImage,
    MessageContentAudio,
    MessageContentFile,
)
from antonnia.conversations.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    APIError
)


async def create_rich_conversation():
    """Demonstrate creating a conversation with rich content types."""
    
    api_token = os.getenv("ANTONNIA_API_TOKEN")
    if not api_token:
        print("Please set ANTONNIA_API_TOKEN environment variable")
        return
    
    # Create custom HTTP client with timeout and retries
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(timeout=60),
        limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
    )
    
    async with Conversations(
        token=api_token,
        base_url="https://api.antonnia.com",
        http_client=http_client
    ) as client:
        
        print("🎨 Creating a rich conversation with multiple content types...")
        
        # Create session
        session = await client.sessions.create(
            contact_id="premium_user_789",
            contact_name="Alice Johnson", 
            metadata={
                "tier": "premium",
                "language": "en",
                "timezone": "UTC-8"
            }
        )
        
        print(f"✅ Session created: {session.id}")
        
        # Send different types of messages
        messages = []
        
        # 1. Text message
        text_msg = await client.sessions.messages.create(
            session_id=session.id,
            content=MessageContentText(
                type="text",
                text="Hi! I'm having trouble uploading my profile picture. Here's what I see:"
            ),
            role="user"
        )
        messages.append(("Text", text_msg))
        
        # 2. Image message (screenshot of the issue)
        image_msg = await client.sessions.messages.create(
            session_id=session.id,
            content=MessageContentImage(
                type="image",
                url="https://example.com/screenshots/error_screenshot.png"
            ),
            role="user",
            provider_message_id="whatsapp_img_123"
        )
        messages.append(("Image", image_msg))
        
        # 3. Audio message (voice explanation)
        audio_msg = await client.sessions.messages.create(
            session_id=session.id,
            content=MessageContentAudio(
                type="audio",
                url="https://example.com/audio/voice_message.mp3",
                transcript="I've been trying to upload my profile picture for the past hour but it keeps failing with this error message."
            ),
            role="user",
            provider_message_id="whatsapp_audio_456"
        )
        messages.append(("Audio", audio_msg))
        
        # 4. File message (logs)
        file_msg = await client.sessions.messages.create(
            session_id=session.id,
            content=MessageContentFile(
                type="file",
                url="https://example.com/files/browser_console.log",
                mime_type="text/plain",
                name="browser_console.log"
            ),
            role="user",
            provider_message_id="whatsapp_file_789"
        )
        messages.append(("File", file_msg))
        
        print(f"📨 Created {len(messages)} messages with different content types:")
        for content_type, msg in messages:
            print(f"   - {content_type}: {msg.id}")
        
        return session


async def demonstrate_session_management():
    """Show advanced session management features."""
    
    api_token = os.getenv("ANTONNIA_API_TOKEN")
    if not api_token:
        return
    
    async with Conversations(token=api_token) as client:
        
        print("\n🔄 Demonstrating session management...")
        
        # Create a session that will need human intervention
        session = await client.sessions.create(
            contact_id="escalation_user_456",
            contact_name="Bob Smith",
            agent_id="ai_agent_123",  # Start with AI agent
            metadata={
                "complexity": "high",
                "requires_escalation": True
            }
        )
        
        print(f"✅ Created session {session.id} with AI agent")
        
        # Simulate AI trying to help but needs escalation
        await client.sessions.messages.create(
            session_id=session.id,
            content=MessageContentText(
                type="text",
                text="I need to cancel my subscription and get a refund, but your AI chatbot isn't helping."
            ),
            role="user"
        )
        
        # Transfer to human agent
        print("🚀 Transferring to human agent...")
        
        try:
            transferred_session = await client.sessions.transfer(
                session_id=session.id,
                agent_id="human_agent_456"
            )
            
            print(f"✅ Session transferred to human agent: {transferred_session.agent.name if transferred_session.agent else 'Unknown'}")
            
        except APIError as e:
            print(f"⚠️  Transfer failed: {e.message}")
        
        # Update metadata to track the escalation
        await client.sessions.update(
            session_id=session.id,
            fields={
                "metadata": {
                    "complexity": "high",
                    "requires_escalation": True,
                    "escalated_at": "2024-01-15T14:30:00Z",
                    "escalation_reason": "refund_request"
                }
            }
        )
        
        print("📝 Updated session metadata to track escalation")


async def paginate_large_results():
    """Demonstrate pagination for handling large result sets."""
    
    api_token = os.getenv("ANTONNIA_API_TOKEN")
    if not api_token:
        return
    
    async with Conversations(token=api_token) as client:
        
        print("\n📄 Demonstrating pagination...")
        
        page_size = 5
        offset = 0
        all_sessions = []
        
        while True:
            # Get a page of sessions
            sessions_page = await client.sessions.search(
                contact_id="bulk_user_123", 
                offset=offset,
                limit=page_size
            )
            
            if not sessions_page:
                break
                
            all_sessions.extend(sessions_page)
            print(f"📖 Loaded page with {len(sessions_page)} sessions (offset: {offset})")
            
            # If we got less than the page size, we're done
            if len(sessions_page) < page_size:
                break
                
            offset += page_size
        
        print(f"✅ Total sessions loaded: {len(all_sessions)}")


async def handle_rate_limiting():
    """Demonstrate proper rate limiting handling."""
    
    api_token = os.getenv("ANTONNIA_API_TOKEN") 
    if not api_token:
        return
    
    async with Conversations(token=api_token) as client:
        
        print("\n⏱️  Demonstrating rate limit handling...")
        
        max_retries = 3
        
        for i in range(5):  # Try to make several requests quickly
            
            for retry in range(max_retries):
                try:
                    # This might hit rate limits if done too quickly
                    sessions = await client.sessions.search(limit=1)
                    print(f"✅ Request {i+1} succeeded")
                    break
                    
                except RateLimitError as e:
                    if retry < max_retries - 1:
                        wait_time = e.retry_after or 1
                        print(f"⏳ Rate limited, waiting {wait_time}s before retry {retry+1}")
                        await asyncio.sleep(wait_time)
                    else:
                        print(f"❌ Request {i+1} failed after {max_retries} retries")
                        
                except APIError as e:
                    print(f"⚠️  Request {i+1} failed: {e.message}")
                    break


async def main():
    """Run all advanced examples."""
    
    print("🚀 Running advanced Antonnia SDK examples...\n")
    
    try:
        # Run each example
        session = await create_rich_conversation()
        await demonstrate_session_management()
        await paginate_large_results()
        await handle_rate_limiting()
        
        print("\n🎉 All advanced examples completed!")
        
    except AuthenticationError:
        print("❌ Authentication failed. Please check your ANTONNIA_API_TOKEN.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 