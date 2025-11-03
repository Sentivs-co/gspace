class GoogleScopes:
    """
    Google API scopes for various Google Workspace services.
    """

    # Calendar scopes
    CALENDAR_READONLY = "https://www.googleapis.com/auth/calendar.readonly"
    CALENDAR_EVENTS = "https://www.googleapis.com/auth/calendar.events"
    CALENDAR = "https://www.googleapis.com/auth/calendar"

    # Gmail scopes
    GMAIL_READONLY = "https://www.googleapis.com/auth/gmail.readonly"
    GMAIL_SEND = "https://www.googleapis.com/auth/gmail.send"
    GMAIL_MODIFY = "https://www.googleapis.com/auth/gmail.modify"
    GMAIL_COMPOSE = "https://www.googleapis.com/auth/gmail.compose"
    GMAIL_FULL = "https://www.googleapis.com/auth/gmail"

    # Drive scopes
    DRIVE_READONLY = "https://www.googleapis.com/auth/drive.readonly"
    DRIVE_FILE = "https://www.googleapis.com/auth/drive.file"
    DRIVE_APPDATA = "https://www.googleapis.com/auth/drive.appdata"
    DRIVE_METADATA = "https://www.googleapis.com/auth/drive.metadata"
    DRIVE = "https://www.googleapis.com/auth/drive"

    # Sheets scopes
    SHEETS_READONLY = "https://www.googleapis.com/auth/spreadsheets.readonly"
    SHEETS = "https://www.googleapis.com/auth/spreadsheets"

    # Docs scopes
    DOCS_READONLY = "https://www.googleapis.com/auth/documents.readonly"
    DOCS = "https://www.googleapis.com/auth/documents"

    # Admin SDK scopes
    ADMIN_DIRECTORY_USER = "https://www.googleapis.com/auth/admin.directory.user"
    ADMIN_DIRECTORY_GROUP = "https://www.googleapis.com/auth/admin.directory.group"

    # People API scopes
    PEOPLE_READONLY = "https://www.googleapis.com/auth/userinfo.profile"
    PEOPLE_CONTACTS = "https://www.googleapis.com/auth/contacts"
    PEOPLE_CONTACTS_READONLY = "https://www.googleapis.com/auth/contacts.readonly"

    # Tasks scopes
    TASKS = "https://www.googleapis.com/auth/tasks"
    TASKS_READONLY = "https://www.googleapis.com/auth/tasks.readonly"

    # Keep scopes
    KEEP = "https://www.googleapis.com/auth/keep"
    KEEP_READONLY = "https://www.googleapis.com/auth/keep.readonly"

    # UserInfo API scopes
    USERINFO_EMAIL = "https://www.googleapis.com/auth/userinfo.email"
    USERINFO_PROFILE = "https://www.googleapis.com/auth/userinfo.profile"
    OPENID = "openid"

    @classmethod
    def get_service_scopes(cls, service: str, access_level: str = "full") -> list[str]:
        """
        Get scopes for a specific service and access level.

        Args:
            service: Service name (calendar, gmail, drive, sheets, docs, etc.)
            access_level: Access level (readonly, full, etc.)

        Returns:
            List of scope URLs
        """
        scope_map = {
            "calendar": {
                "readonly": [cls.CALENDAR_READONLY],
                "events": [cls.CALENDAR_EVENTS],
                "full": [cls.CALENDAR],
            },
            "gmail": {
                "readonly": [cls.GMAIL_READONLY],
                "send": [cls.GMAIL_SEND],
                "modify": [cls.GMAIL_MODIFY],
                "compose": [cls.GMAIL_COMPOSE],
                "full": [cls.GMAIL_FULL],
            },
            "drive": {
                "readonly": [cls.DRIVE_READONLY],
                "file": [cls.DRIVE_FILE],
                "appdata": [cls.DRIVE_APPDATA],
                "metadata": [cls.DRIVE_METADATA],
                "full": [cls.DRIVE],
            },
            "sheets": {"readonly": [cls.SHEETS_READONLY], "full": [cls.SHEETS]},
            "docs": {"readonly": [cls.DOCS_READONLY], "full": [cls.DOCS]},
            "admin": {
                "user": [cls.ADMIN_DIRECTORY_USER],
                "group": [cls.ADMIN_DIRECTORY_GROUP],
                "full": [cls.ADMIN_DIRECTORY_USER, cls.ADMIN_DIRECTORY_GROUP],
            },
            "people": {
                "readonly": [cls.PEOPLE_READONLY],
                "contacts": [cls.PEOPLE_CONTACTS],
                "contacts_readonly": [cls.PEOPLE_CONTACTS_READONLY],
                "full": [cls.PEOPLE_READONLY, cls.PEOPLE_CONTACTS],
            },
            "tasks": {"readonly": [cls.TASKS_READONLY], "full": [cls.TASKS]},
            "keep": {"readonly": [cls.KEEP_READONLY], "full": [cls.KEEP]},
            "userinfo": {
                "readonly": [cls.USERINFO_EMAIL, cls.USERINFO_PROFILE, cls.OPENID],
            },
        }

        if service not in scope_map:
            raise ValueError(f"Unknown service: {service}")

        if access_level not in scope_map[service]:
            raise ValueError(
                f"Unknown access level '{access_level}' for service '{service}'"
            )

        return scope_map[service][access_level]

    @classmethod
    def get_all_scopes(cls) -> dict[str, list[str]]:
        """
        Get all available scopes organized by service.

        Returns:
            Dictionary mapping service names to their available scopes
        """
        return {
            "calendar": [cls.CALENDAR_READONLY, cls.CALENDAR_EVENTS, cls.CALENDAR],
            "gmail": [
                cls.GMAIL_READONLY,
                cls.GMAIL_SEND,
                cls.GMAIL_MODIFY,
                cls.GMAIL_COMPOSE,
                cls.GMAIL_FULL,
            ],
            "drive": [
                cls.DRIVE_READONLY,
                cls.DRIVE_FILE,
                cls.DRIVE_APPDATA,
                cls.DRIVE_METADATA,
                cls.DRIVE,
            ],
            "sheets": [cls.SHEETS_READONLY, cls.SHEETS],
            "docs": [cls.DOCS_READONLY, cls.DOCS],
            "admin": [cls.ADMIN_DIRECTORY_USER, cls.ADMIN_DIRECTORY_GROUP],
            "people": [
                cls.PEOPLE_READONLY,
                cls.PEOPLE_CONTACTS,
                cls.PEOPLE_CONTACTS_READONLY,
            ],
            "tasks": [cls.TASKS_READONLY, cls.TASKS],
            "keep": [cls.KEEP_READONLY, cls.KEEP],
            "userinfo": [cls.USERINFO_EMAIL, cls.USERINFO_PROFILE, cls.OPENID],
        }

    @classmethod
    def validate_scopes(cls, scopes: list[str]) -> list[str]:
        """
        Validate and return only valid Google API scopes.

        Args:
            scopes: List of scope URLs to validate

        Returns:
            List of valid scope URLs
        """
        all_scopes = []
        for service_scopes in cls.get_all_scopes().values():
            all_scopes.extend(service_scopes)

        valid_scopes = [scope for scope in scopes if scope in all_scopes]

        if len(valid_scopes) != len(scopes):
            invalid_scopes = [scope for scope in scopes if scope not in all_scopes]
            import warnings

            warnings.warn(f"Invalid scopes found: {invalid_scopes}", stacklevel=2)

        return valid_scopes
