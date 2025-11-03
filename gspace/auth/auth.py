import json
from pathlib import Path

from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from gspace.utils.logger import get_logger
from gspace.utils.scopes import GoogleScopes


class AuthManager:
    """
    Manages authentication for Google Workspace APIs.
    Supports both OAuth2 and Service Account authentication.
    """

    def __init__(
        self,
        credentials: str | Path,
        scopes: list[str] | None = None,
        auth_type: str | None = None,
    ):
        """
        Initialize the AuthManager.

        Args:
            credentials: Path to credentials file (JSON)
            scopes: List of Google API scopes
        """
        self.logger = get_logger("gspace.auth")
        self.credentials_path = Path(credentials)
        self.scopes = scopes or []
        self.credentials = None

        self.logger.info(
            f"Initializing AuthManager with credentials: {self.credentials_path}"
        )
        self._load_credentials(auth_type)

    def _load_credentials(self, auth_type) -> None:
        """Load and validate credentials from file."""
        try:
            if not self.credentials_path.exists():
                raise FileNotFoundError(
                    f"Credentials file not found: {self.credentials_path}"
                )

            if self.credentials_path.suffix.lower() != ".json":
                raise ValueError(
                    f"Credentials file must be JSON format: {self.credentials_path}"
                )

            # Read and parse credentials file
            with open(self.credentials_path) as f:
                cred_data = json.load(f)

            # Determine credential type and load accordingly
            # service account
            if auth_type == "service_account":
                self.logger.info("Loading service account credentials")
                self.credentials = self._load_service_account(cred_data)
            # OAuth2
            elif auth_type == "OAuth2":
                self.logger.info("Loading OAuth2 client credentials")
                self.credentials = self._load_oauth2(cred_data)
            else:
                raise ValueError(f"Unsupported Autentication type {auth_type}")

            self.logger.info("Credentials loaded successfully")

        except Exception as e:
            self.logger.error(f"Failed to load credentials: {e}")
            raise

    def _load_service_account(self, cred_data: dict):
        """Load service account credentials."""
        try:
            scopes = self._map_scopes(self.scopes)
            self.logger.debug(f"Using scopes: {scopes}")

            credentials = service_account.Credentials.from_service_account_info(
                cred_data, scopes=scopes
            )

            # Refresh if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())

            return credentials

        except Exception as e:
            self.logger.error(f"Failed to load service account credentials: {e}")
            raise GoogleAuthError(f"Service account authentication failed: {e}") from e

    def _load_oauth2(self, cred_data: dict):
        """Load OAuth2 credentials."""
        try:
            scopes = self._map_scopes(self.scopes)
            self.logger.debug(f"Using scopes: {scopes}")

            flow = InstalledAppFlow.from_client_config(cred_data, scopes=scopes)

            # Run local server for OAuth2 flow
            self.logger.info(
                "Starting OAuth2 flow - check your browser for authorization"
            )
            credentials = flow.run_local_server(
                port=8080, redirect_uri_trailing_slash=True
            )

            self.logger.info("OAuth2 authentication completed successfully")
            return credentials

        except Exception as e:
            self.logger.error(f"Failed to load OAuth2 credentials: {e}")
            raise GoogleAuthError(f"OAuth2 authentication failed: {e}") from e

    def _map_scopes(self, scopes: list[str]) -> list[str]:
        """
        Map service names to full Google API scope URLs.

        Args:
            scopes: List of service names or scope URLs

        Returns:
            List of full scope URLs
        """
        if not scopes:
            # Default to basic scopes if none specified
            return [
                GoogleScopes.CALENDAR_READONLY,
                GoogleScopes.GMAIL_READONLY,
                GoogleScopes.DRIVE_READONLY,
                GoogleScopes.USERINFO_EMAIL,
                GoogleScopes.USERINFO_PROFILE,
                GoogleScopes.OPENID,
            ]

        mapped_scopes = []
        for scope in scopes:
            if scope.startswith("https://"):
                # Already a full scope URL
                mapped_scopes.append(scope)
            else:
                # Map service name to default scope
                try:
                    service_scopes = GoogleScopes.get_service_scopes(scope, "readonly")
                    mapped_scopes.extend(service_scopes)
                except ValueError:
                    self.logger.warning(f"Unknown scope: {scope}, skipping")

        # Remove duplicates and validate
        unique_scopes = list(set(mapped_scopes))
        valid_scopes = GoogleScopes.validate_scopes(unique_scopes)

        self.logger.debug(f"Mapped scopes: {valid_scopes}")
        return valid_scopes

    def build_service(self, api_name: str, api_version: str = "v1"):
        """
        Build a Google API service client.

        Args:
            api_name: Name of the Google API (e.g., 'calendar', 'gmail')
            api_version: API version (default: 'v1')

        Returns:
            Google API service client
        """
        try:
            self.logger.info(f"Building service for {api_name} v{api_version}")

            if not self.credentials:
                raise GoogleAuthError("No credentials available")

            # Check if credentials are expired and refresh if needed
            if self.credentials.expired and hasattr(self.credentials, "refresh_token"):
                self.logger.debug("Refreshing expired credentials")
                self.credentials.refresh(Request())

            service = build(api_name, api_version, credentials=self.credentials)
            self.logger.info(f"Successfully built {api_name} service")

            return service

        except HttpError as e:
            self.logger.error(f"HTTP error building {api_name} service: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to build {api_name} service: {e}")
            raise

    def is_authenticated(self) -> str:
        """
        Check if the credentials are authenticated.

        Returns:
            "authenticated" if authenticated, "invalid credentials" otherwises
        """
        status = self.credentials.valid if self.credentials else False
        if status:
            return "authenticated"
        else:
            return "invalid credentials"

    def get_user_info(self) -> dict:
        """
        Get information about the authenticated user.

        Returns:
            User information dictionary
        """
        oauth2 = build("oauth2", "v2", credentials=self.credentials)
        user_info = oauth2.userinfo().get().execute()
        del oauth2
        return user_info
