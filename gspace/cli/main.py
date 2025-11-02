#!/usr/bin/env python3
"""
GSpace CLI - Command-line interface for Google Workspace operations.
"""

import argparse
import sys

from gspace.client import GSpace
from gspace.utils.logger import get_logger


class GSpaceCLI:
    """Command-line interface for GSpace."""

    def __init__(self):
        self.logger = get_logger("gspace.cli")
        self.client: GSpace | None = None

    def setup_client(
        self,
        credentials: str,
        scopes: list[str] | None = None,
        auth_type: str = "OAuth2",
    ) -> None:
        """Initialize the GSpace client."""
        try:
            self.client = GSpace(credentials, scopes, auth_type)
            self.logger.info("GSpace client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize client: {e}")
            sys.exit(1)

    def list_calendars(self) -> None:
        """List all available calendars."""
        if not self.client:
            print("Client not initialized")
            return

        try:
            calendar_service = self.client.calendar()
            calendars = calendar_service.list_calendars()

            print("\n📅 Available Calendars:")
            print("-" * 50)
            for cal in calendars:
                print(f"• {cal.get('summary', 'No name')} ({cal.get('id', 'No ID')})")
                if cal.get("description"):
                    print(f"  Description: {cal['description']}")
                print()

        except Exception as e:
            print(f"Error listing calendars: {e}")

    def list_events(self, calendar_id: str = "primary", max_results: int = 10) -> None:
        """List calendar events."""
        if not self.client:
            print("Client not initialized")
            return

        try:
            calendar_service = self.client.calendar()
            events = calendar_service.list_events(calendar_id, max_results=max_results)

            print(f"\n📅 Events in {calendar_id}:")
            print("-" * 50)
            for event in events:
                start = event.get("start", {}).get(
                    "dateTime", event.get("start", {}).get("date", "No start time")
                )
                print(f"• {event.get('summary', 'No title')}")
                print(f"  Start: {start}")
                if event.get("description"):
                    print(f"  Description: {event['description']}")
                print()

        except Exception as e:
            print(f"Error listing events: {e}")

    def list_emails(self, max_results: int = 10) -> None:
        """List recent emails."""
        if not self.client:
            print("Client not initialized")
            return

        try:
            gmail_service = self.client.gmail()
            messages = gmail_service.list_messages(max_results=max_results)

            print("\n📧 Recent Emails:")
            print("-" * 50)
            for msg in messages:
                headers = msg.get("payload", {}).get("headers", [])
                subject = next(
                    (h["value"] for h in headers if h["name"] == "Subject"),
                    "No subject",
                )
                sender = next(
                    (h["value"] for h in headers if h["name"] == "From"),
                    "Unknown sender",
                )
                date = next(
                    (h["value"] for h in headers if h["name"] == "Date"), "No date"
                )

                print(f"• {subject}")
                print(f"  From: {sender}")
                print(f"  Date: {date}")
                print()

        except Exception as e:
            print(f"Error listing emails: {e}")

    def list_files(self, max_results: int = 10) -> None:
        """List Drive files."""
        if not self.client:
            print("Client not initialized")
            return

        try:
            drive_service = self.client.drive()
            files = drive_service.list_files(max_results=max_results)

            print("\n📁 Drive Files:")
            print("-" * 50)
            for file in files:
                print(f"• {file.get('name', 'No name')}")
                print(f"  ID: {file.get('id', 'No ID')}")
                print(f"  Type: {file.get('mimeType', 'Unknown type')}")
                print(f"  Size: {file.get('size', 'Unknown size')} bytes")
                print()

        except Exception as e:
            print(f"Error listing files: {e}")

    def download_file(self, file_id: str, output_path: str) -> None:
        """Download a file from Drive."""
        if not self.client:
            print("Client not initialized")
            return

        try:
            drive_service = self.client.drive()
            drive_service.download_file(file_id, output_path)
            print(f"✅ File downloaded successfully to {output_path}")

        except Exception as e:
            print(f"Error downloading file: {e}")

    def upload_file(self, file_path: str, parent_folder_id: str | None = None) -> None:
        """Upload a file to Drive."""
        if not self.client:
            print("Client not initialized")
            return

        try:
            drive_service = self.client.drive()
            file_id = drive_service.upload_file(file_path, parent_folder_id)
            print(f"✅ File uploaded successfully with ID: {file_id}")

        except Exception as e:
            print(f"Error uploading file: {e}")

    def create_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        description: str | None = None,
        calendar_id: str = "primary",
    ) -> None:
        """Create a calendar event."""
        if not self.client:
            print("Client not initialized")
            return

        try:
            calendar_service = self.client.calendar()
            event_id = calendar_service.create_event(
                summary=summary,
                start_time=start_time,
                end_time=end_time,
                description=description,
                calendar_id=calendar_id,
            )
            print(f"✅ Event created successfully with ID: {event_id}")

        except Exception as e:
            print(f"Error creating event: {e}")

    def send_email(self, to: str, subject: str, body: str) -> None:
        """Send an email."""
        if not self.client:
            print("Client not initialized")
            return

        try:
            gmail_service = self.client.gmail()
            message_id = gmail_service.send_email(to, subject, body)
            print(f"✅ Email sent successfully with ID: {message_id}")

        except Exception as e:
            print(f"Error sending email: {e}")

    def get_user_info(self) -> None:
        """Display user information."""
        if not self.client:
            print("Client not initialized")
            return

        try:
            user_info = self.client.get_user_info()

            print("\n👤 User Information:")
            print("-" * 50)
            for key, value in user_info.items():
                print(f"• {key.title()}: {value}")
            print()

        except Exception as e:
            print(f"Error getting user info: {e}")

    def run(self, args) -> None:
        """Run the CLI with the given arguments."""
        # Setup client
        self.setup_client(args.credentials, args.scopes, args.auth_type)

        # Execute command
        if args.command == "calendars":
            self.list_calendars()
        elif args.command == "events":
            self.list_events(args.calendar_id, args.max_results)
        elif args.command == "emails":
            self.list_emails(args.max_results)
        elif args.command == "files":
            self.list_files(args.max_results)
        elif args.command == "download":
            self.download_file(args.file_id, args.output_path)
        elif args.command == "upload":
            self.upload_file(args.file_path, args.parent_folder_id)
        elif args.command == "create-event":
            self.create_event(
                args.summary,
                args.start_time,
                args.end_time,
                args.description,
                args.calendar_id,
            )
        elif args.command == "send-email":
            self.send_email(args.to, args.subject, args.body)
        elif args.command == "user-info":
            self.get_user_info()
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GSpace CLI - Command-line interface for Google Workspace operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gspace calendars                    # List all calendars
  gspace events --max-results 20     # List 20 calendar events
  gspace emails --max-results 5      # List 5 recent emails
  gspace files --max-results 15      # List 15 Drive files
  gspace download FILE_ID output.txt # Download a file
  gspace upload document.pdf         # Upload a file
  gspace create-event "Meeting" "2024-01-15T10:00:00" "2024-01-15T11:00:00"
  gspace send-email user@example.com "Subject" "Email body"
  gspace user-info                   # Show user information
        """,
    )

    # Global options
    parser.add_argument(
        "--credentials", "-c", required=True, help="Path to credentials file (JSON)"
    )
    parser.add_argument(
        "--scopes",
        "-s",
        nargs="+",
        help="Google API scopes (e.g., calendar gmail drive)",
    )
    parser.add_argument(
        "--auth_type",
        required=True,
        help="Authentication type (service_account or OAuth2 )",
    )
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Calendars command
    subparsers.add_parser("calendars", help="List all calendars")

    # Events command
    events_parser = subparsers.add_parser("events", help="List calendar events")
    events_parser.add_argument(
        "--calendar-id", default="primary", help="Calendar ID (default: primary)"
    )
    events_parser.add_argument(
        "--max-results", type=int, default=10, help="Maximum number of events"
    )

    # Emails command
    emails_parser = subparsers.add_parser("emails", help="List recent emails")
    emails_parser.add_argument(
        "--max-results", type=int, default=10, help="Maximum number of emails"
    )

    # Files command
    files_parser = subparsers.add_parser("files", help="List Drive files")
    files_parser.add_argument(
        "--max-results", type=int, default=10, help="Maximum number of files"
    )

    # Download command
    download_parser = subparsers.add_parser(
        "download", help="Download a file from Drive"
    )
    download_parser.add_argument("file_id", help="File ID to download")
    download_parser.add_argument("output_path", help="Output file path")

    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload a file to Drive")
    upload_parser.add_argument("file_path", help="Local file path to upload")
    upload_parser.add_argument("--parent-folder-id", help="Parent folder ID (optional)")

    # Create event command
    create_event_parser = subparsers.add_parser(
        "create-event", help="Create a calendar event"
    )
    create_event_parser.add_argument("summary", help="Event summary/title")
    create_event_parser.add_argument("start_time", help="Start time (ISO format)")
    create_event_parser.add_argument("end_time", help="End time (ISO format)")
    create_event_parser.add_argument("--description", help="Event description")
    create_event_parser.add_argument(
        "--calendar-id", default="primary", help="Calendar ID"
    )

    # Send email command
    send_email_parser = subparsers.add_parser("send-email", help="Send an email")
    send_email_parser.add_argument("to", help="Recipient email address")
    send_email_parser.add_argument("subject", help="Email subject")
    send_email_parser.add_argument("body", help="Email body")

    # User info command
    subparsers.add_parser("user-info", help="Show user information")

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Run CLI
    cli = GSpaceCLI()
    cli.run(args)


if __name__ == "__main__":
    main()
