import hashlib
import hmac
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from gspace.utils.logger import get_logger


class WebhookEventType(Enum):
    """Types of webhook events."""

    CALENDAR_EVENT_CREATED = "calendar.event.created"
    CALENDAR_EVENT_UPDATED = "calendar.event.updated"
    CALENDAR_EVENT_DELETED = "calendar.event.deleted"
    GMAIL_MESSAGE_ADDED = "gmail.message.added"
    GMAIL_MESSAGE_DELETED = "gmail.message.deleted"
    DRIVE_FILE_CREATED = "drive.file.created"
    DRIVE_FILE_UPDATED = "drive.file.updated"
    DRIVE_FILE_DELETED = "drive.file.deleted"
    SHEETS_SPREADSHEET_UPDATED = "sheets.spreadsheet.updated"
    DOCS_DOCUMENT_UPDATED = "docs.document.updated"


@dataclass
class WebhookEvent:
    """Represents a webhook event."""

    event_type: WebhookEventType
    resource_id: str
    resource_uri: str
    timestamp: datetime
    payload: dict[str, Any]
    user_id: str | None = None
    domain: str | None = None


class WebhookHandler:
    """
    Handles Google Workspace webhook notifications.
    Supports verification, parsing, and event routing.
    """

    def __init__(self, verification_token: str | None = None):
        """
        Initialize the webhook handler.

        Args:
            verification_token: Token for webhook verification
        """
        self.logger = get_logger("gspace.webhooks")
        self.verification_token = verification_token
        self.event_handlers: dict[WebhookEventType, list[Callable]] = {}
        self.fallback_handler: Callable | None = None

        self.logger.info("WebhookHandler initialized")

    def register_handler(
        self, event_type: WebhookEventType, handler: Callable[[WebhookEvent], None]
    ):
        """
        Register an event handler for a specific event type.

        Args:
            event_type: Type of event to handle
            handler: Function to call when event occurs
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []

        self.event_handlers[event_type].append(handler)
        self.logger.info(f"Registered handler for {event_type.value}")

    def register_fallback_handler(self, handler: Callable[[WebhookEvent], None]):
        """
        Register a fallback handler for unhandled events.

        Args:
            handler: Function to call for unhandled events
        """
        self.fallback_handler = handler
        self.logger.info("Registered fallback handler")

    def verify_webhook(
        self, request_body: bytes, signature: str, algorithm: str = "sha256"
    ) -> bool:
        """
        Verify webhook signature for security.

        Args:
            request_body: Raw request body
            signature: Signature header value
            algorithm: Hashing algorithm used

        Returns:
            True if signature is valid, False otherwise
        """
        if not self.verification_token:
            self.logger.warning("No verification token set, skipping verification")
            return True

        try:
            if algorithm.lower() == "sha256":
                expected_signature = hmac.new(
                    self.verification_token.encode("utf-8"),
                    request_body,
                    hashlib.sha256,
                ).hexdigest()
            else:
                self.logger.error(f"Unsupported algorithm: {algorithm}")
                return False

            return hmac.compare_digest(expected_signature, signature)

        except Exception as e:
            self.logger.error(f"Error verifying webhook signature: {e}")
            return False

    def parse_webhook(
        self, request_body: str, headers: dict[str, str]
    ) -> WebhookEvent | None:
        """
        Parse webhook request into a WebhookEvent object.

        Args:
            request_body: JSON string of the webhook payload
            headers: HTTP headers from the request

        Returns:
            Parsed WebhookEvent or None if parsing fails
        """
        try:
            data = json.loads(request_body)

            # Extract event information
            event_type_str = data.get("event_type", "")
            resource_id = data.get("resource_id", "")
            resource_uri = data.get("resource_uri", "")
            timestamp_str = data.get("timestamp", "")
            payload = data.get("payload", {})
            user_id = data.get("user_id")
            domain = data.get("domain")

            # Parse timestamp
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            except ValueError:
                timestamp = datetime.utcnow()

            # Map event type string to enum
            try:
                event_type = WebhookEventType(event_type_str)
            except ValueError:
                self.logger.warning(f"Unknown event type: {event_type_str}")
                event_type = None

            event = WebhookEvent(
                event_type=event_type,
                resource_id=resource_id,
                resource_uri=resource_uri,
                timestamp=timestamp,
                payload=payload,
                user_id=user_id,
                domain=domain,
            )

            self.logger.info(
                f"Parsed webhook event: {event_type_str} for resource {resource_id}"
            )
            return event

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse webhook JSON: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing webhook: {e}")
            return None

    def handle_webhook(
        self, request_body: str, headers: dict[str, str]
    ) -> dict[str, Any]:
        """
        Handle incoming webhook request.

        Args:
            request_body: JSON string of the webhook payload
            headers: HTTP headers from the request

        Returns:
            Response dictionary
        """
        try:
            # Verify webhook if signature is provided
            signature = headers.get("X-Goog-Signature", "")
            if signature and not self.verify_webhook(
                request_body.encode("utf-8"), signature
            ):
                self.logger.warning("Webhook signature verification failed")
                return {"error": "Invalid signature", "status": 401}

            # Parse webhook
            event = self.parse_webhook(request_body, headers)
            if not event:
                return {"error": "Failed to parse webhook", "status": 400}

            # Route to appropriate handlers
            if event.event_type and event.event_type in self.event_handlers:
                for handler in self.event_handlers[event.event_type]:
                    try:
                        handler(event)
                    except Exception as e:
                        self.logger.error(f"Error in event handler: {e}")
            elif self.fallback_handler:
                try:
                    self.fallback_handler(event)
                except Exception as e:
                    self.logger.error(f"Error in fallback handler: {e}")
            else:
                self.logger.info(
                    f"No handler registered for event type: {event.event_type}"
                )

            return {"status": "success", "event_processed": True}

        except Exception as e:
            self.logger.error(f"Error handling webhook: {e}")
            return {"error": str(e), "status": 500}

    def create_subscription_payload(
        self,
        topic_name: str,
        push_endpoint: str,
        custom_attributes: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Create payload for setting up webhook subscriptions.

        Args:
            topic_name: Google Cloud Pub/Sub topic name
            push_endpoint: URL endpoint to receive webhooks
            custom_attributes: Additional attributes for the subscription

        Returns:
            Subscription configuration payload
        """
        payload = {
            "topic": f"projects/_/topics/{topic_name}",
            "pushConfig": {
                "pushEndpoint": push_endpoint,
                "attributes": custom_attributes or {},
            },
        }

        return payload

    def get_supported_events(self) -> list[str]:
        """
        Get list of supported event types.

        Returns:
            List of event type strings
        """
        return [event.value for event in WebhookEventType]

    def get_handler_count(self, event_type: WebhookEventType) -> int:
        """
        Get number of handlers registered for an event type.

        Args:
            event_type: Type of event

        Returns:
            Number of registered handlers
        """
        return len(self.event_handlers.get(event_type, []))

    def clear_handlers(self, event_type: WebhookEventType | None = None):
        """
        Clear event handlers.

        Args:
            event_type: Specific event type to clear, or None to clear all
        """
        if event_type:
            if event_type in self.event_handlers:
                del self.event_handlers[event_type]
                self.logger.info(f"Cleared handlers for {event_type.value}")
        else:
            self.event_handlers.clear()
            self.logger.info("Cleared all event handlers")
