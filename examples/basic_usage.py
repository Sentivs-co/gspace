#!/usr/bin/env python3
"""
Basic usage examples for the gspace library.
This file demonstrates how to use various Google Workspace services.
"""

import os
from datetime import datetime, timedelta

from gspace import GSpace
from gspace.utils.scopes import GoogleScopes


def main():
    """Main function demonstrating gspace usage."""

    # Path to your credentials file
    credentials_file = "path/to/your/credentials.json"

    # Check if credentials file exists
    if not os.path.exists(credentials_file):
        print(f"Credentials file not found: {credentials_file}")
        print("Please update the credentials_file path in this example")
        return

    # Initialize GSpace client with OAuth2 credentials
    # You can also use GSpace.from_service_account() for service accounts
    try:
        gspace = GSpace.from_oauth(
            credentials_file=credentials_file,
            scopes=[
                "calendar",  # Calendar access
                "gmail",  # Gmail access
                "drive",  # Drive access
                "sheets",  # Sheets access
                "docs",  # Docs access
            ],
        )

        print("✅ GSpace client initialized successfully!")
        print(f"🔐 Authentication status: {gspace.is_authenticated()}")

        # Get user information
        user_info = gspace.get_user_info()
        print(f"👤 User: {user_info.get('name', 'Unknown')}")
        print(f"📧 Email: {user_info.get('email', 'Unknown')}")

        # Example 1: Calendar Operations
        calendar_examples(gspace)

        # Example 2: Gmail Operations
        gmail_examples(gspace)

        # Example 3: Drive Operations
        drive_examples(gspace)

        # Example 4: Sheets Operations
        sheets_examples(gspace)

        # Example 5: Docs Operations
        docs_examples(gspace)

        # Close the client
        gspace.close()
        print("\n✅ Examples completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")


def calendar_examples(gspace):
    """Demonstrate Calendar service operations."""
    print("\n📅 === CALENDAR EXAMPLES ===")

    try:
        calendar = gspace.calendar()

        # List calendars
        calendars = calendar.list_calendars()
        print(f"📋 Found {len(calendars)} calendars:")
        for cal in calendars[:3]:  # Show first 3
            print(f"   - {cal.get('summary', 'Unknown')} ({cal.get('id', 'No ID')})")

        # Create a test event
        start_time = datetime.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)

        event = calendar.create_event(
            summary="GSpace Test Event",
            start_time=start_time,
            end_time=end_time,
            description="This is a test event created by gspace library",
            location="Virtual Meeting",
        )
        print(f"✅ Created event: {event.get('summary')} (ID: {event.get('id')})")

        # List upcoming events
        events = calendar.list_events(
            time_min=datetime.now(),
            time_max=datetime.now() + timedelta(days=7),
            max_results=5,
        )
        print(f"📅 Found {len(events)} upcoming events")

        # Clean up - delete the test event
        calendar.delete_event(event.get("id"))
        print("🗑️  Deleted test event")

    except Exception as e:
        print(f"❌ Calendar error: {e}")


def gmail_examples(gspace):
    """Demonstrate Gmail service operations."""
    print("\n📧 === GMAIL EXAMPLES ===")

    try:
        gmail = gspace.gmail()

        # Get Gmail profile
        profile = gmail.get_profile()
        print(f"📧 Gmail profile: {profile.get('emailAddress', 'Unknown')}")

        # List recent messages
        messages = gmail.list_messages(max_results=5)
        print(f"📨 Found {len(messages)} recent messages")

        # List labels
        labels = gmail.list_labels()
        print(f"🏷️  Found {len(labels)} labels")

        # Note: We won't actually send emails in this example to avoid spam
        print("💡 Email sending is available via gmail.send_email() method")

    except Exception as e:
        print(f"❌ Gmail error: {e}")


def drive_examples(gspace):
    """Demonstrate Drive service operations."""
    print("\n💾 === DRIVE EXAMPLES ===")

    try:
        drive = gspace.drive()

        # List files
        files = drive.list_files(page_size=10)
        print(f"📁 Found {len(files)} files in Drive:")
        for file in files[:3]:  # Show first 3
            print(
                f"   - {file.get('name', 'Unknown')} ({file.get('mimeType', 'Unknown type')})"
            )

        # Create a test folder
        folder = drive.create_folder(
            name="GSpace Test Folder",
            description="Test folder created by gspace library",
        )
        print(f"📁 Created folder: {folder.get('name')} (ID: {folder.get('id')})")

        # Clean up - delete the test folder
        drive.delete_file(folder.get("id"))
        print("🗑️  Deleted test folder")

    except Exception as e:
        print(f"❌ Drive error: {e}")


def sheets_examples(gspace):
    """Demonstrate Sheets service operations."""
    print("\n📊 === SHEETS EXAMPLES ===")

    try:
        sheets = gspace.sheets()

        # Create a test spreadsheet
        spreadsheet = sheets.create_spreadsheet(title="GSpace Test Spreadsheet")
        print(
            f"📊 Created spreadsheet: {spreadsheet.get('properties', {}).get('title')}"
        )

        spreadsheet_id = spreadsheet.get("spreadsheetId")

        # Add some data
        test_data = [
            ["Name", "Age", "City"],
            ["John Doe", 30, "New York"],
            ["Jane Smith", 25, "Los Angeles"],
            ["Bob Johnson", 35, "Chicago"],
        ]

        result = sheets.update_values(
            spreadsheet_id=spreadsheet_id, range_name="Sheet1!A1:D4", values=test_data
        )
        print(
            f"✅ Added data to spreadsheet: {result.get('updatedCells', 0)} cells updated"
        )

        # Read the data back
        values = sheets.get_values(
            spreadsheet_id=spreadsheet_id, range_name="Sheet1!A1:D4"
        )
        print(f"📖 Read data from spreadsheet: {len(values.get('values', []))} rows")

        # Clean up - delete the test spreadsheet
        # Note: This would require additional permissions in a real scenario
        print("💡 Test spreadsheet created successfully")
        print(f"🔗 View it at: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

    except Exception as e:
        print(f"❌ Sheets error: {e}")


def docs_examples(gspace):
    """Demonstrate Docs service operations."""
    print("\n📝 === DOCS EXAMPLES ===")

    try:
        docs = gspace.docs()

        # Create a test document
        document = docs.create_document(title="GSpace Test Document")
        print(f"📝 Created document: {document.get('title')}")

        document_id = document.get("documentId")

        # Add some text
        docs.insert_text(
            document_id=document_id,
            location=1,
            text="Hello from GSpace! This is a test document created by the gspace library.",
        )
        print("✅ Added text to document")

        # Clean up - delete the test document
        # Note: This would require additional permissions in a real scenario
        print("💡 Test document created successfully")
        print(f"🔗 View it at: https://docs.google.com/document/d/{document_id}")

    except Exception as e:
        print(f"❌ Docs error: {e}")


def advanced_examples(gspace):
    """Demonstrate advanced features."""
    print("\n🚀 === ADVANCED EXAMPLES ===")

    try:
        # Show available services
        services = gspace.get_available_services()
        print(f"🔧 Available services: {', '.join(services)}")

        # Show scope information
        print("\n📋 Available scopes:")
        all_scopes = GoogleScopes.get_all_scopes()
        for service, scopes in all_scopes.items():
            print(f"   {service}: {len(scopes)} scopes available")

        # Example of getting specific scopes
        calendar_scopes = GoogleScopes.get_service_scopes("calendar", "full")
        print(f"\n📅 Calendar full access scopes: {len(calendar_scopes)}")

    except Exception as e:
        print(f"❌ Advanced examples error: {e}")


if __name__ == "__main__":
    main()
