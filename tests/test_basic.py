"""
Basic tests for the gspace library.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from gspace import GSpace
from gspace.utils.logger import get_logger, setup_logger
from gspace.utils.scopes import GoogleScopes


class TestGoogleScopes:
    """Test the GoogleScopes utility class."""

    def test_get_service_scopes_calendar(self):
        """Test getting calendar scopes."""
        scopes = GoogleScopes.get_service_scopes("calendar", "full")
        assert len(scopes) > 0
        assert GoogleScopes.CALENDAR in scopes

    def test_get_service_scopes_gmail(self):
        """Test getting Gmail scopes."""
        scopes = GoogleScopes.get_service_scopes("gmail", "readonly")
        assert len(scopes) > 0
        assert GoogleScopes.GMAIL_READONLY in scopes

    def test_get_service_scopes_invalid_service(self):
        """Test getting scopes for invalid service."""
        with pytest.raises(ValueError):
            GoogleScopes.get_service_scopes("invalid_service", "full")

    def test_get_service_scopes_invalid_access_level(self):
        """Test getting scopes for invalid access level."""
        with pytest.raises(ValueError):
            GoogleScopes.get_service_scopes("calendar", "invalid_level")

    def test_get_all_scopes(self):
        """Test getting all available scopes."""
        all_scopes = GoogleScopes.get_all_scopes()
        assert "calendar" in all_scopes
        assert "gmail" in all_scopes
        assert "drive" in all_scopes
        assert "sheets" in all_scopes
        assert "docs" in all_scopes

    def test_validate_scopes(self):
        """Test scope validation."""
        valid_scopes = [GoogleScopes.CALENDAR_READONLY, GoogleScopes.GMAIL_SEND]
        validated = GoogleScopes.validate_scopes(valid_scopes)
        assert len(validated) == 2

        # Test with invalid scope
        invalid_scopes = [GoogleScopes.CALENDAR_READONLY, "https://invalid-scope.com"]
        validated = GoogleScopes.validate_scopes(invalid_scopes)
        assert len(validated) == 1


class TestLogger:
    """Test the logging utilities."""

    def test_setup_logger(self):
        """Test logger setup."""
        logger = setup_logger("test_logger", level="DEBUG")
        assert logger.name == "test_logger"
        assert logger.level == 10  # DEBUG level

    def test_get_logger(self):
        """Test getting existing logger."""
        logger1 = setup_logger("test_logger2", level="INFO")
        logger2 = get_logger("test_logger2")
        assert logger1 is logger2


class TestGSpaceClient:
    """Test the main GSpace client."""

    @patch("gspace.client.client.AuthManager")
    def test_client_initialization(self, mock_auth_manager):
        """Test client initialization."""
        mock_auth = Mock()
        mock_auth_manager.return_value = mock_auth

        # Mock credentials file
        credentials_file = Path("test_credentials.json")

        client = GSpace(credentials_file, scopes=["calendar"])

        assert client.auth == mock_auth
        assert client.services == {}

    @patch("gspace.client.client.AuthManager")
    def test_from_oauth_classmethod(self, mock_auth_manager):
        """Test from_oauth class method."""
        mock_auth = Mock()
        mock_auth_manager.return_value = mock_auth

        credentials_file = Path("test_credentials.json")
        scopes = ["calendar", "gmail"]

        client = GSpace.from_oauth(credentials_file, scopes)

        assert client.auth == mock_auth
        assert client.services == {}

    @patch("gspace.client.client.AuthManager")
    def test_from_service_account_classmethod(self, mock_auth_manager):
        """Test from_service_account class method."""
        mock_auth = Mock()
        mock_auth_manager.return_value = mock_auth

        credentials_file = Path("test_credentials.json")
        scopes = ["drive", "sheets"]

        client = GSpace.from_service_account(credentials_file, scopes)

        assert client.auth == mock_auth
        assert client.services == {}

    @patch("gspace.client.client.AuthManager")
    def test_service_lazy_loading(self, mock_auth_manager):
        """Test that services are loaded lazily."""
        mock_auth = Mock()
        mock_auth_manager.return_value = mock_auth

        client = GSpace("test_credentials.json")

        # Services should not be loaded yet
        assert len(client.services) == 0

        # Access calendar service
        _calendar = client.calendar()
        assert "calendar" in client.services
        assert len(client.services) == 1

        # Access Gmail service
        _gmail = client.gmail()
        assert "gmail" in client.services
        assert len(client.services) == 2

    @patch("gspace.client.client.AuthManager")
    def test_get_available_services(self, mock_auth_manager):
        """Test getting available services."""
        mock_auth = Mock()
        mock_auth_manager.return_value = mock_auth

        client = GSpace("test_credentials.json")

        # Initially no services
        assert client.get_available_services() == []

        # Load some services
        client.calendar()
        client.gmail()

        services = client.get_available_services()
        assert "calendar" in services
        assert "gmail" in services
        assert len(services) == 2

    @patch("gspace.client.client.AuthManager")
    def test_close_method(self, mock_auth_manager):
        """Test client close method."""
        mock_auth = Mock()
        mock_auth_manager.return_value = mock_auth

        client = GSpace("test_credentials.json")

        # Load some services
        client.calendar()
        client.gmail()

        assert len(client.services) == 2

        # Close client
        client.close()
        assert len(client.services) == 0


if __name__ == "__main__":
    pytest.main([__file__])
