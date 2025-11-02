from pathlib import Path

from ..auth.auth import AuthManager
from ..calender.calender import Calendar
from ..docs.docs import Docs
from ..drive.drive import Drive
from ..gmail.gmail import Gmail
from ..sheets.sheets import Sheets
from ..utils.logger import get_logger


class GSpace:
    """
    Main GSpace client for Google Workspace APIs.
    Provides unified access to Calendar, Gmail, Drive, Sheets, and Docs services.
    """

    def __init__(
        self,
        credentials: str | Path,
        auth_type: str = "OAuth2",
        scopes: list[str] | None = None,
    ):
        """
        Initialize GSpace client.

        Args:
            credentials: Path to credentials file (JSON)
            scopes: List of Google API scopes
            auth_type: service_account or OAuth2
        """
        self.logger = get_logger("gspace.client")
        self.logger.info("Initializing GSpace client")
        self.auth_type = auth_type
        self._validate_auth_type()
        self.auth = AuthManager(credentials, scopes, self.auth_type)
        self.services = {}

        self.logger.info("GSpace client initialized successfully")

    def _validate_auth_type(self):
        if self.auth_type not in ["service_account", "OAuth2"]:
            raise ValueError(f"Unsupported Authentication type {self.auth_type}")

    @classmethod
    def from_oauth(cls, credentials_file: str | Path, scopes: list[str]):
        """
        Create GSpace client from OAuth2 credentials.

        Args:
            credentials_file: Path to OAuth2 client credentials file
            scopes: List of Google API scopes

        Returns:
            GSpace client instance
        """
        return cls(credentials_file, scopes, auth_type="OAuth2")

    @classmethod
    def from_service_account(cls, service_account_file: str | Path, scopes: list[str]):
        """
        Create GSpace client from service account credentials.

        Args:
            service_account_file: Path to service account credentials file
            scopes: List of Google API scopes

        Returns:
            GSpace client instance
        """
        return cls(service_account_file, scopes, auth_type="service_account")

    def calendar(self) -> Calendar:
        """
        Get Calendar service instance.

        Returns:
            Calendar service instance
        """
        if "calendar" not in self.services:
            self.logger.debug("Initializing Calendar service")
            self.services["calendar"] = Calendar(self.auth)
        return self.services["calendar"]

    def gmail(self) -> Gmail:
        """
        Get Gmail service instance.

        Returns:
            Gmail service instance
        """
        if "gmail" not in self.services:
            self.logger.debug("Initializing Gmail service")
            self.services["gmail"] = Gmail(self.auth)
        return self.services["gmail"]

    def drive(self) -> Drive:
        """
        Get Drive service instance.

        Returns:
            Drive service instance
        """
        if "drive" not in self.services:
            self.logger.debug("Initializing Drive service")
            self.services["drive"] = Drive(self.auth)
        return self.services["drive"]

    def sheets(self) -> Sheets:
        """
        Get Sheets service instance.

        Returns:
            Sheets service instance
        """
        if "sheets" not in self.services:
            self.logger.debug("Initializing Sheets service")
            self.services["sheets"] = Sheets(self.auth)
        return self.services["sheets"]

    def docs(self) -> Docs:
        """
        Get Docs service instance.

        Returns:
            Docs service instance
        """
        if "docs" not in self.services:
            self.logger.debug("Initializing Docs service")
            self.services["docs"] = Docs(self.auth)
        return self.services["docs"]

    def is_authenticated(self) -> bool:
        """
        Check if the client is properly authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        return self.auth.is_authenticated()

    def get_user_info(self) -> dict:
        """
        Get information about the authenticated user.

        Returns:
            User information dictionary
        """
        return self.auth.get_user_info()

    def get_available_services(self) -> list[str]:
        """
        Get list of available services.

        Returns:
            List of service names
        """
        return list(self.services.keys())

    def close(self):
        """Close all service connections and cleanup resources."""
        self.logger.info("Closing GSpace client")
        self.services.clear()
        self.logger.info("GSpace client closed")

    # Async methods for concurrent operations
    async def calendar_async(self) -> "Calendar":
        """
        Get Calendar service instance asynchronously.

        Returns:
            Calendar service instance
        """
        if "calendar" not in self.services:
            self.logger.debug("Initializing Calendar service")
            self.services["calendar"] = Calendar(self.auth)
        return self.services["calendar"]

    async def gmail_async(self) -> "Gmail":
        """
        Get Gmail service instance asynchronously.

        Returns:
            Gmail service instance
        """
        if "gmail" not in self.services:
            self.logger.debug("Initializing Gmail service")
            self.services["gmail"] = Gmail(self.auth)
        return self.services["gmail"]

    async def drive_async(self) -> "Drive":
        """
        Get Drive service instance asynchronously.

        Returns:
            Drive service instance
        """
        if "drive" not in self.services:
            self.logger.debug("Initializing Drive service")
            self.services["drive"] = Drive(self.auth)
        return self.services["drive"]

    async def sheets_async(self) -> "Sheets":
        """
        Get Sheets service instance asynchronously.

        Returns:
            Sheets service instance
        """
        if "sheets" not in self.services:
            self.logger.debug("Initializing Sheets service")
            self.services["sheets"] = Sheets(self.auth)
        return self.services["sheets"]

    async def docs_async(self) -> "Docs":
        """
        Get Docs service instance asynchronously.

        Returns:
            Docs service instance
        """
        if "docs" not in self.services:
            self.logger.debug("Initializing Docs service")
            self.services["docs"] = Docs(self.auth)
        return self.services["docs"]

    async def is_authenticated_async(self) -> bool:
        """
        Check if the client is properly authenticated asynchronously.

        Returns:
            True if authenticated, False otherwise
        """
        return self.auth.is_authenticated()

    async def get_user_info_async(self) -> dict:
        """
        Get information about the authenticated user asynchronously.

        Returns:
            User information dictionary
        """
        return self.auth.get_user_info()

    async def close_async(self):
        """Close all service connections and cleanup resources asynchronously."""
        self.logger.info("Closing GSpace client")
        self.services.clear()
        self.logger.info("GSpace client closed")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_async()
