#!/usr/bin/env python3
"""
Advanced Features Example - Demonstrates the new GSpace features.
"""

import asyncio
import json
from datetime import datetime, timedelta

from gspace import (
    APIRateLimiter,
    BatchRequestManager,
    EncryptedTokenBackend,
    GSpace,
    RateLimitConfig,
    RetryConfig,
    RetryStrategy,
    TokenManager,
    WebhookEventType,
    WebhookHandler,
)


def example_async_operations():
    """Example of async operations with GSpace."""
    print("🚀 Async Operations Example")
    print("=" * 50)

    async def async_workflow():
        # Initialize client
        client = GSpace("path/to/credentials.json")

        # Use async methods for concurrent operations
        calendar_service = await client.calendar_async()
        gmail_service = await client.gmail_async()
        drive_service = await client.drive_async()

        # Perform concurrent operations
        tasks = [
            calendar_service.list_events("primary", max_results=10),
            gmail_service.list_messages(max_results=5),
            drive_service.list_files(max_results=10),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        print(
            f"Calendar events: {len(results[0]) if not isinstance(results[0], Exception) else 'Error'}"
        )
        print(
            f"Gmail messages: {len(results[1]) if not isinstance(results[1], Exception) else 'Error'}"
        )
        print(
            f"Drive files: {len(results[2]) if not isinstance(results[2], Exception) else 'Error'}"
        )

        await client.close_async()

    # Run async workflow
    asyncio.run(async_workflow())


def example_webhook_handler():
    """Example of webhook handling for real-time notifications."""
    print("\n🔔 Webhook Handler Example")
    print("=" * 50)

    # Initialize webhook handler
    handler = WebhookHandler(verification_token="your_verification_token")

    # Register event handlers
    def handle_calendar_event(event):
        print(f"📅 Calendar event: {event.event_type.value}")
        print(f"   Resource: {event.resource_id}")
        print(f"   Time: {event.timestamp}")

    def handle_gmail_event(event):
        print(f"📧 Gmail event: {event.event_type.value}")
        print(f"   Resource: {event.resource_id}")
        print(f"   Time: {event.timestamp}")

    def handle_drive_event(event):
        print(f"📁 Drive event: {event.event_type.value}")
        print(f"   Resource: {event.resource_id}")
        print(f"   Time: {event.timestamp}")

    # Register handlers for different event types
    handler.register_handler(
        WebhookEventType.CALENDAR_EVENT_CREATED, handle_calendar_event
    )
    handler.register_handler(
        WebhookEventType.CALENDAR_EVENT_UPDATED, handle_calendar_event
    )
    handler.register_handler(WebhookEventType.GMAIL_MESSAGE_ADDED, handle_gmail_event)
    handler.register_handler(WebhookEventType.DRIVE_FILE_CREATED, handle_drive_event)

    # Fallback handler for unhandled events
    def fallback_handler(event):
        print(
            f"⚠️  Unhandled event: {event.event_type.value if event.event_type else 'Unknown'}"
        )

    handler.register_fallback_handler(fallback_handler)

    # Example webhook payload
    sample_webhook = {
        "event_type": "calendar.event.created",
        "resource_id": "event_123",
        "resource_uri": "https://www.googleapis.com/calendar/v3/events/event_123",
        "timestamp": datetime.now().isoformat(),
        "payload": {"summary": "Team Meeting"},
        "user_id": "user@example.com",
    }

    # Process webhook
    response = handler.handle_webhook(
        json.dumps(sample_webhook), {"X-Goog-Signature": "sample_signature"}
    )

    print(f"Webhook processed: {response}")
    print(f"Supported events: {handler.get_supported_events()}")


def example_batch_requests():
    """Example of batch requests for bulk operations."""
    print("\n📦 Batch Requests Example")
    print("=" * 50)

    # Initialize batch manager
    batch_manager = BatchRequestManager(max_batch_size=50)

    # Add multiple requests to the batch
    for i in range(10):
        batch_manager.add_get_request(
            request_id=f"calendar_event_{i}",
            url=f"/calendar/v3/events/event_{i}",
            headers={"Authorization": "Bearer token"},
        )

    for i in range(5):
        batch_manager.add_post_request(
            request_id=f"create_event_{i}",
            url="/calendar/v3/events",
            body={
                "summary": f"Event {i}",
                "start": {"dateTime": "2024-01-15T10:00:00Z"},
            },
            headers={"Authorization": "Bearer token"},
        )

    print(f"Batch contains {batch_manager.get_request_count()} requests")
    print(f"Remaining capacity: {batch_manager.get_remaining_capacity()}")

    # Create batch payload (for demonstration)
    try:
        payload = batch_manager.create_batch_payload()
        print(f"Batch payload created (length: {len(payload)} characters)")
    except Exception as e:
        print(f"Error creating batch payload: {e}")

    # Note: Actual execution requires a Google API service instance
    print("Note: Execute batch requires Google API service instance")


def example_rate_limiting_and_retry():
    """Example of rate limiting and retry logic."""
    print("\n⏱️  Rate Limiting & Retry Example")
    print("=" * 50)

    # Configure rate limiting
    rate_limit_config = RateLimitConfig(
        requests_per_second=5,  # 5 requests per second
        burst_limit=10,  # Allow burst of 10 requests
        window_size=1.0,  # 1 second window
    )

    # Configure retry logic
    retry_config = RetryConfig(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        jitter=True,
    )

    # Create combined rate limiter and retry handler
    api_limiter = APIRateLimiter(rate_limit_config, retry_config)

    # Example function that makes API calls
    def make_api_call(endpoint: str):
        print(f"Making API call to: {endpoint}")
        # Simulate API call
        import random

        if random.random() < 0.3:  # 30% chance of failure
            raise Exception("API call failed")
        return f"Success: {endpoint}"

    # Execute with rate limiting and retry
    try:
        result1 = api_limiter.execute(make_api_call, "/calendar/v3/events")
        print(f"Result 1: {result1}")

        result2 = api_limiter.execute(make_api_call, "/gmail/v1/messages")
        print(f"Result 2: {result2}")

        result3 = api_limiter.execute(make_api_call, "/drive/v3/files")
        print(f"Result 3: {result3}")

    except Exception as e:
        print(f"All retries exhausted: {e}")

    # Get statistics
    stats = api_limiter.get_stats()
    print(f"\nRate limiter stats: {json.dumps(stats, indent=2, default=str)}")


def example_token_management():
    """Example of OAuth2 token management."""
    print("\n🔐 Token Management Example")
    print("=" * 50)

    # Initialize token manager with encrypted storage
    token_manager = TokenManager(
        backend=EncryptedTokenBackend(password="your_secret_password"),
        auto_refresh=True,
    )

    # Save tokens for a user
    user_id = "user@example.com"
    success = token_manager.save_tokens(
        user_id=user_id,
        access_token="access_token_123",
        refresh_token="refresh_token_456",
        expires_at=datetime.utcnow() + timedelta(hours=1),
        additional_data={"scope": "calendar gmail drive"},
    )

    print(f"Tokens saved: {success}")

    # Load tokens
    tokens = token_manager.load_tokens(user_id)
    if tokens:
        print(f"Tokens loaded for {user_id}")
        print(f"Access token: {tokens['access_token'][:20]}...")
        print(f"Expires at: {tokens['expires_at']}")

    # Check token validity
    is_valid = token_manager.is_token_valid(user_id)
    print(f"Token valid: {is_valid}")

    # Get token information
    token_info = token_manager.get_token_info(user_id)
    if token_info:
        print(f"Token info: {json.dumps(token_info, indent=2, default=str)}")

    # List all users
    users = token_manager.list_users()
    print(f"Users with tokens: {users}")

    # Cleanup expired tokens
    cleaned_count = token_manager.cleanup_expired_tokens()
    print(f"Cleaned up {cleaned_count} expired token sets")


def example_cli_usage():
    """Example of CLI usage."""
    print("\n💻 CLI Usage Example")
    print("=" * 50)

    print("The GSpace CLI provides easy access to common operations:")
    print()
    print("List calendars:")
    print("  gspace --credentials creds.json calendars")
    print()
    print("List recent emails:")
    print("  gspace --credentials creds.json emails --max-results 10")
    print()
    print("Download a file:")
    print("  gspace --credentials creds.json download FILE_ID output.txt")
    print()
    print("Create calendar event:")
    print(
        "  gspace --credentials creds.json create-event 'Meeting' '2024-01-15T10:00:00' '2024-01-15T11:00:00'"
    )
    print()
    print("Send email:")
    print(
        "  gspace --credentials creds.json send-email user@example.com 'Subject' 'Email body'"
    )


def main():
    """Run all examples."""
    print("🌟 GSpace Advanced Features Examples")
    print("=" * 60)

    try:
        # Run examples
        example_async_operations()
        example_webhook_handler()
        example_batch_requests()
        example_rate_limiting_and_retry()
        example_token_management()
        example_cli_usage()

        print("\n✅ All examples completed successfully!")
        print("\n📚 For more information, check the documentation and examples.")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Note: Some examples require valid credentials and API access.")


if __name__ == "__main__":
    main()
