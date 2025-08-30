"""
Antonnia Namespace Packages Demo

This example demonstrates how multiple Antonnia service packages work together
under the same namespace. 

Note: This example assumes multiple packages are installed:
- pip install antonnia-conversations
- pip install antonnia-orchestrator  
- pip install antonnia-auth

For now, only antonnia-conversations is implemented.
"""

import asyncio
import os


async def conversations_only_example():
    """Example using only the conversations package."""
    print("🗣️  Conversations-only example:")
    
    try:
        from antonnia.conversations import Conversations
        from antonnia.conversations.types import MessageContentText, Session
        from antonnia.conversations.exceptions import AuthenticationError
        
        print("✅ Successfully imported from antonnia.conversations")
        print(f"   Conversations: {Conversations}")
        print(f"   MessageContentText: {MessageContentText}")
        print(f"   Session: {Session}")
        
        # Example usage (would require real API token)
        # async with Conversations(token="your_token") as client:
        #     session = await client.sessions.create(
        #         contact_id="demo_user",
        #         contact_name="Demo User"
        #     )
        #     print(f"Created session: {session.id}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")


async def multi_service_example():
    """Example showing how multiple services would work together."""
    print("\n🚀 Multi-service integration example:")
    
    # Try importing from conversations (implemented)
    try:
        from antonnia.conversations import Conversations
        from antonnia.conversations.types import Session, MessageContentText
        print("✅ Conversations package available")
    except ImportError:
        print("❌ Conversations package not available")
        return
    
    # Try importing from orchestrator (not yet implemented)
    try:
        from antonnia.orchestrator import Orchestrator  # type: ignore
        from antonnia.orchestrator.types import Thread, Run  # type: ignore
        print("✅ Orchestrator package available")
        orchestrator_available = True
    except ImportError:
        print("⚠️  Orchestrator package not available (would be: antonnia-orchestrator)")
        orchestrator_available = False
    
    # Try importing from auth (not yet implemented)
    try:
        from antonnia.auth import Auth  # type: ignore
        from antonnia.auth.types import User, Token  # type: ignore
        print("✅ Auth package available")
        auth_available = True
    except ImportError:
        print("⚠️  Auth package not available (would be: antonnia-auth)")
        auth_available = False
    
    # Show how they would work together
    print("\n📝 How they would integrate:")
    print("""
    # Each service provides its own client and types
    conversations = Conversations(token="conv_token")
    orchestrator = Orchestrator(token="orch_token")  # When available
    auth = Auth(token="auth_token")                   # When available
    
    # Services work together seamlessly
    user = await auth.users.get("user_123")
    session = await conversations.sessions.create(
        contact_id=user.id,
        contact_name=user.name
    )
    thread = await orchestrator.threads.create(
        user_id=user.id,
        metadata={"session_id": session.id}
    )
    """)


async def demonstrate_namespace_isolation():
    """Show how each service has its own isolated types and exceptions."""
    print("\n🔒 Namespace isolation example:")
    
    from antonnia.conversations.types import Message as ConversationsMessage
    from antonnia.conversations.exceptions import APIError as ConversationsAPIError
    
    print("✅ Each service has isolated types:")
    print(f"   antonnia.conversations.types.Message: {ConversationsMessage}")
    print(f"   antonnia.conversations.exceptions.APIError: {ConversationsAPIError}")
    
    print("\n💡 Benefits:")
    print("   - No naming conflicts between services")
    print("   - Each service can evolve independently") 
    print("   - Type safety maintained across services")
    print("   - Clear separation of concerns")
    
    print("\n📦 When other services are added, you'd have:")
    print("   - antonnia.orchestrator.types.Message (different from conversations)")
    print("   - antonnia.auth.types.User")
    print("   - antonnia.contacts.types.Contact")
    print("   - etc.")


async def show_installation_patterns():
    """Demonstrate different installation patterns."""
    print("\n📥 Installation Patterns:")
    
    patterns = [
        {
            "name": "Conversations Only",
            "install": "pip install antonnia-conversations",
            "imports": [
                "from antonnia.conversations import Conversations",
                "from antonnia.conversations.types import Message, Session",
                "from antonnia.conversations.exceptions import APIError"
            ]
        },
        {
            "name": "Multiple Services",
            "install": "pip install antonnia-conversations antonnia-orchestrator",
            "imports": [
                "from antonnia.conversations import Conversations",
                "from antonnia.orchestrator import Orchestrator",
                "# Different types, no conflicts:",
                "from antonnia.conversations.types import Message as ConvMessage",
                "from antonnia.orchestrator.types import Message as OrchMessage"
            ]
        },
        {
            "name": "Full Suite",
            "install": "pip install antonnia-conversations antonnia-orchestrator antonnia-auth",
            "imports": [
                "from antonnia.conversations import Conversations",
                "from antonnia.orchestrator import Orchestrator", 
                "from antonnia.auth import Auth",
                "# All services work together seamlessly"
            ]
        }
    ]
    
    for pattern in patterns:
        print(f"\n🔧 {pattern['name']}:")
        print(f"   Install: {pattern['install']}")
        print("   Usage:")
        for imp in pattern['imports']:
            print(f"     {imp}")


async def main():
    """Run all namespace package demonstrations."""
    print("🌟 Antonnia Namespace Packages Demo")
    print("=" * 50)
    
    await conversations_only_example()
    await multi_service_example()
    await demonstrate_namespace_isolation()
    await show_installation_patterns()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\n💡 Next steps:")
    print("   1. Implement antonnia-orchestrator following the same pattern")
    print("   2. Implement antonnia-auth following the same pattern")
    print("   3. Users can install only what they need")
    print("   4. All services work together under antonnia.* namespace")


if __name__ == "__main__":
    asyncio.run(main()) 