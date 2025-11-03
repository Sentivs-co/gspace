<p align="center">
  <img
    alt="Gspace Logo"
    src="https://repository-images.githubusercontent.com/1087982749/64312ac5-7332-4e2f-b8f4-e59f1e039656"
    width="250"
    style="border-radius: 20px;"
  />
</p>

# gspace 🚀

*A comprehensive Python SDK for Google Workspace APIs (Calendar, Gmail, Drive, Docs, Sheets, and more).*

[![PyPI version](https://img.shields.io/pypi/v/gspace.svg)](https://pypi.org/project/gspace/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

---

## 🌟 Overview

`gspace` is a unified Python client library for **Google Workspace APIs**, making it simple to interact with Google Calendar, Gmail, Drive, Docs, Sheets, and other services from a single, well-designed interface.

Instead of juggling multiple SDKs, authentication flows, and scattered scopes, `gspace` provides:

- ✅ **Single Authentication** - OAuth2 or Service Account credentials
- ✅ **Consistent API Wrappers** - Unified interface across all Google services
- ✅ **Comprehensive Logging** - Built-in logging with configurable levels
- ✅ **Helper Methods** - Common tasks simplified (send email, create event, upload file, etc.)
- ✅ **Type Hints** - Full Python type annotations for better development experience
- ✅ **Error Handling** - Robust error handling with detailed logging
- ✅ **Extensible Design** - Easy to add new Google Workspace APIs

---

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install gspace
```

### From Source

```bash
git https://github.com/Sentivs-co/gspace
poetry install
```

---

## 🚀 Quick Start

### 1. Set Up Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the APIs you need:
   - Google Calendar API
   - Gmail API
   - Google Drive API
   - Google Sheets API
   - Google Docs API
4. Create credentials (OAuth2 or Service Account)

### 2. Basic Usage

```python
from gspace import gspace
from datetime import datetime, timedelta

# Initialize with OAuth2 credentials
gspace = gspace.from_oauth(
    credentials_file="path/to/credentials.json",
    scopes=["calendar", "gmail", "drive"]
)

# Use Calendar service
calendar = gspace.calendar()
event = calendar.create_event(
    summary="Team Meeting",
    start_time=datetime.now() + timedelta(hours=1),
    end_time=datetime.now() + timedelta(hours=2),
    description="Weekly team sync"
)

# Use Gmail service
gmail = gspace.gmail()
gmail.send_simple_email(
    to="team@company.com",
    subject="Meeting Reminder",
    body="Don't forget our team meeting in 1 hour!"
)

# Use Drive service
drive = gspace.drive()
files = drive.list_files(page_size=10)
```

---

## 🔧 Features

### 📅 Calendar Service
- Create, read, update, delete events
- Manage multiple calendars
- Handle attendees and reminders
- Free/busy time queries
- Recurring events support

### 📧 Gmail Service
- Send emails (simple and with attachments)
- Read and search messages
- Manage labels and filters
- Handle drafts and threads
- Profile information

### 💾 Drive Service
- Upload and download files
- Create folders and organize content
- Share files and manage permissions
- Search and filter files
- Handle different file types

### 📊 Sheets Service
- Create and manage spreadsheets
- Read and write cell data
- Format cells and ranges
- Manage sheets and tabs
- Batch operations

### 📝 Docs Service
- Create and edit documents
- Insert text, tables, and images
- Apply formatting and styles
- Handle comments and revisions
- Batch updates

---

## 📚 API Reference

### Core Client

#### `gspace(credentials, scopes =None, auth_type = service_account or OAuth2 )`
Main client class for accessing Google Workspace services.

**Parameters:**
- `credentials` (str|Path): Path to credentials JSON file
- `scopes` (List[str], optional): List of Google API scopes

**Methods:**
- `calendar()` → Calendar service
- `gmail()` → Gmail service
- `drive()` → Drive service
- `sheets()` → Sheets service
- `docs()` → Docs service
- `close()` → None

#### Factory Methods

```python
# OAuth2 authentication
gspace = gspace.from_oauth(credentials_file, scopes)

# Service Account authentication
gspace = gspace.from_service_account(service_account_file, scopes)
```

### Authentication

The library supports two authentication methods:

1. **OAuth2** - For user applications
2. **Service Account** - For server-to-server applications

### Scopes

Use the `GoogleScopes` utility class to manage API scopes:

```python
from gspace.utils.scopes import GoogleScopes

# Get scopes for a specific service
calendar_scopes = GoogleScopes.get_service_scopes("calendar", "full")
gmail_scopes = GoogleScopes.get_service_scopes("gmail", "readonly")

# Get all available scopes
all_scopes = GoogleScopes.get_all_scopes()
```

---

## 📖 Examples

### Calendar Management

```python
# Create an event
event = calendar.create_event(
    summary="Project Review",
    start_time=datetime.now() + timedelta(days=1, hours=10),
    end_time=datetime.now() + timedelta(days=1, hours=11),
    description="Monthly project status review",
    location="Conference Room A",
    attendees=["team@company.com", "manager@company.com"]
)

# List upcoming events
events = calendar.list_events(
    time_min=datetime.now(),
    time_max=datetime.now() + timedelta(days=7),
    max_results=20
)

# Get free/busy information
free_busy = calendar.get_free_busy(
    time_min=datetime.now(),
    time_max=datetime.now() + timedelta(days=1),
    items=[{"id": "primary"}]
)
```

### Email Operations

```python
# Send simple email
gmail.send_simple_email(
    to="recipient@example.com",
    subject="Important Update",
    body="Please review the attached document."
)

# Send email with attachments
gmail.send_email(
    to=["user1@example.com", "user2@example.com"],
    subject="Project Documents",
    body="Please find the project documents attached.",
    attachments=["/path/to/doc1.pdf", "/path/to/doc2.docx"],
    cc="manager@example.com"
)

# Search for emails
messages = gmail.search_messages(
    query="from:important@company.com subject:urgent",
    max_results=50
)
```

### File Management

```python
# Upload a file
file = drive.upload_file(
    file_path="/path/to/document.pdf",
    name="Important Document",
    description="Project proposal document"
)

# Create a folder
folder = drive.create_folder(
    name="Project Files",
    description="All project-related documents"
)

# Share a file
drive.share_file(
    file_id=file.get('id'),
    email="collaborator@company.com",
    role="writer"
)

# Search for files
files = drive.search_files(
    query="name contains 'report' and modifiedTime > '2024-01-01'"
)
```

### Spreadsheet Operations

```python
# Create a new spreadsheet
spreadsheet = sheets.create_spreadsheet(
    title="Monthly Report",
    sheets=[{
        'properties': {
            'title': 'Data',
            'gridProperties': {
                'rowCount': 1000,
                'columnCount': 26
            }
        }
    }]
)

# Add data to cells
sheets.update_values(
    spreadsheet_id=spreadsheet.get('spreadsheetId'),
    range_name="Data!A1:D5",
    values=[
        ["Name", "Department", "Salary", "Start Date"],
        ["John Doe", "Engineering", 75000, "2023-01-15"],
        ["Jane Smith", "Marketing", 65000, "2023-03-20"],
        ["Bob Johnson", "Sales", 70000, "2023-02-10"]
    ]
)

# Format cells
sheets.format_cells(
    spreadsheet_id=spreadsheet.get('spreadsheetId'),
    range_name="Data!A1:D1",
    format_properties={
        'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8},
        'textFormat': {'bold': True}
    }
)
```

### Document Creation

```python
# Create a new document
document = docs.create_document(title="Project Proposal")

# Add content
docs.insert_text(
    document_id=document.get('documentId'),
    location=1,
    text="Executive Summary\n\nThis document outlines our proposed solution..."
)

# Insert a table
docs.insert_table(
    document_id=document.get('documentId'),
    location=100,
    rows=3,
    columns=4
)

# Apply formatting
docs.update_text_style(
    document_id=document.get('documentId'),
    start_index=1,
    end_index=20,
    bold=True,
    font_size=16
)
```
---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `pytest tests/`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Google for providing excellent APIs
- The Python community for amazing tools and libraries
- Contributors and users of this library

---

## 📞 Support

- 📧 **Email**: [dev@sentivs.com](mailto:dev@sentivs.com)
- 🐛 **Issues**: [GitHub Issues](https://github.com/Sentivs-co/gspace/issues)
- 📖 **Documentation**: [Docs](https://gspace.sentivs.com/)
- 💬 **Discussions**: [Chat](https://github.com/Sentivs-co/gspace/discussions)
