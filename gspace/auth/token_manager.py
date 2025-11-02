import base64
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from gspace.utils.logger import get_logger


class TokenStorageBackend:
    """Abstract base class for token storage backends."""

    def save_tokens(self, user_id: str, tokens: dict[str, Any]) -> bool:
        """Save tokens for a user."""
        raise NotImplementedError

    def load_tokens(self, user_id: str) -> dict[str, Any] | None:
        """Load tokens for a user."""
        raise NotImplementedError

    def delete_tokens(self, user_id: str) -> bool:
        """Delete tokens for a user."""
        raise NotImplementedError

    def list_users(self) -> list:
        """List all users with stored tokens."""
        raise NotImplementedError


class FileTokenBackend(TokenStorageBackend):
    """File-based token storage backend."""

    def __init__(self, storage_dir: str = ".gspaces_tokens"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.logger = get_logger("gspace.token_manager.file")

    def save_tokens(self, user_id: str, tokens: dict[str, Any]) -> bool:
        """Save tokens to a file."""
        try:
            file_path = self.storage_dir / f"{user_id}.json"
            with open(file_path, "w") as f:
                json.dump(tokens, f, indent=2)
            self.logger.info(f"Tokens saved for user {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save tokens for user {user_id}: {e}")
            return False

    def load_tokens(self, user_id: str) -> dict[str, Any] | None:
        """Load tokens from a file."""
        try:
            file_path = self.storage_dir / f"{user_id}.json"
            if not file_path.exists():
                return None

            with open(file_path) as f:
                tokens = json.load(f)
            self.logger.info(f"Tokens loaded for user {user_id}")
            return tokens
        except Exception as e:
            self.logger.error(f"Failed to load tokens for user {user_id}: {e}")
            return None

    def delete_tokens(self, user_id: str) -> bool:
        """Delete tokens file for a user."""
        try:
            file_path = self.storage_dir / f"{user_id}.json"
            if file_path.exists():
                file_path.unlink()
                self.logger.info(f"Tokens deleted for user {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete tokens for user {user_id}: {e}")
            return False

    def list_users(self) -> list:
        """List all users with stored tokens."""
        try:
            users = []
            for file_path in self.storage_dir.glob("*.json"):
                user_id = file_path.stem
                users.append(user_id)
            return users
        except Exception as e:
            self.logger.error(f"Failed to list users: {e}")
            return []


class EncryptedTokenBackend(TokenStorageBackend):
    """Encrypted file-based token storage backend."""

    def __init__(
        self,
        storage_dir: str = ".gspaces_tokens_encrypted",
        password: str | None = None,
    ):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.password = password or self._get_default_password()
        self.logger = get_logger("gspace.token_manager.encrypted")

        # Generate encryption key from password
        self.fernet = self._generate_fernet()

    def _get_default_password(self) -> str:
        """Get default password from environment or generate one."""
        password = os.getenv("GSPACES_TOKEN_PASSWORD")
        if not password:
            # Generate a default password based on machine info
            machine_id = os.getenv("MACHINE_ID", "default")
            password = f"gspaces_{machine_id}_{hashlib.md5(machine_id.encode()).hexdigest()[:8]}"
        return password

    def _generate_fernet(self) -> Fernet:
        """Generate Fernet encryption key from password."""
        salt = b"gspaces_salt_2024"  # Fixed salt for consistency
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
        return Fernet(key)

    def save_tokens(self, user_id: str, tokens: dict[str, Any]) -> bool:
        """Save encrypted tokens to a file."""
        try:
            file_path = self.storage_dir / f"{user_id}.enc"
            encrypted_data = self.fernet.encrypt(json.dumps(tokens).encode())

            with open(file_path, "wb") as f:
                f.write(encrypted_data)

            self.logger.info(f"Encrypted tokens saved for user {user_id}")
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to save encrypted tokens for user {user_id}: {e}"
            )
            return False

    def load_tokens(self, user_id: str) -> dict[str, Any] | None:
        """Load and decrypt tokens from a file."""
        try:
            file_path = self.storage_dir / f"{user_id}.enc"
            if not file_path.exists():
                return None

            with open(file_path, "rb") as f:
                encrypted_data = f.read()

            decrypted_data = self.fernet.decrypt(encrypted_data)
            tokens = json.loads(decrypted_data.decode())

            self.logger.info(f"Encrypted tokens loaded for user {user_id}")
            return tokens
        except Exception as e:
            self.logger.error(
                f"Failed to load encrypted tokens for user {user_id}: {e}"
            )
            return None

    def delete_tokens(self, user_id: str) -> bool:
        """Delete encrypted tokens file for a user."""
        try:
            file_path = self.storage_dir / f"{user_id}.enc"
            if file_path.exists():
                file_path.unlink()
                self.logger.info(f"Encrypted tokens deleted for user {user_id}")
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to delete encrypted tokens for user {user_id}: {e}"
            )
            return False

    def list_users(self) -> list:
        """List all users with stored encrypted tokens."""
        try:
            users = []
            for file_path in self.storage_dir.glob("*.enc"):
                user_id = file_path.stem
                users.append(user_id)
            return users
        except Exception as e:
            self.logger.error(f"Failed to list users: {e}")
            return []


class TokenManager:
    """
    Manages OAuth2 tokens with automatic refresh and secure storage.
    Supports multiple storage backends and encryption.
    """

    def __init__(
        self, backend: TokenStorageBackend | None = None, auto_refresh: bool = True
    ):
        """
        Initialize the token manager.

        Args:
            backend: Token storage backend (defaults to encrypted file storage)
            auto_refresh: Whether to automatically refresh expired tokens
        """
        self.logger = get_logger("gspace.token_manager")
        self.backend = backend or EncryptedTokenBackend()
        self.auto_refresh = auto_refresh

        self.logger.info("TokenManager initialized")

    def save_tokens(
        self,
        user_id: str,
        access_token: str,
        refresh_token: str,
        expires_at: datetime | None = None,
        additional_data: dict[str, Any] | None = None,
    ) -> bool:
        """
        Save OAuth2 tokens for a user.

        Args:
            user_id: Unique user identifier
            access_token: OAuth2 access token
            refresh_token: OAuth2 refresh token
            expires_at: Token expiration time
            additional_data: Additional token data

        Returns:
            True if successful, False otherwise
        """
        try:
            tokens = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at.isoformat() if expires_at else None,
                "created_at": datetime.utcnow().isoformat(),
                "additional_data": additional_data or {},
            }

            success = self.backend.save_tokens(user_id, tokens)
            if success:
                self.logger.info(f"Tokens saved successfully for user {user_id}")
            return success

        except Exception as e:
            self.logger.error(f"Failed to save tokens for user {user_id}: {e}")
            return False

    def load_tokens(self, user_id: str) -> dict[str, Any] | None:
        """
        Load OAuth2 tokens for a user.

        Args:
            user_id: Unique user identifier

        Returns:
            Token data dictionary or None if not found
        """
        try:
            tokens = self.backend.load_tokens(user_id)
            if tokens:
                self.logger.info(f"Tokens loaded successfully for user {user_id}")
            return tokens
        except Exception as e:
            self.logger.error(f"Failed to load tokens for user {user_id}: {e}")
            return None

    def get_valid_access_token(self, user_id: str) -> str | None:
        """
        Get a valid access token, refreshing if necessary.

        Args:
            user_id: Unique user identifier

        Returns:
            Valid access token or None if unavailable
        """
        try:
            tokens = self.load_tokens(user_id)
            if not tokens:
                return None

            access_token = tokens.get("access_token")
            expires_at_str = tokens.get("expires_at")

            if not access_token:
                return None

            # Check if token is expired
            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str)
                if datetime.utcnow() >= expires_at:
                    if self.auto_refresh:
                        self.logger.info(
                            f"Access token expired for user {user_id}, attempting refresh"
                        )
                        return self._refresh_tokens(user_id)
                    else:
                        self.logger.warning(f"Access token expired for user {user_id}")
                        return None

            return access_token

        except Exception as e:
            self.logger.error(
                f"Failed to get valid access token for user {user_id}: {e}"
            )
            return None

    def _refresh_tokens(self, user_id: str) -> str | None:
        """
        Refresh OAuth2 tokens for a user.

        Args:
            user_id: Unique user identifier

        Returns:
            New access token or None if refresh failed
        """
        try:
            tokens = self.load_tokens(user_id)
            if not tokens:
                return None

            refresh_token = tokens.get("refresh_token")
            if not refresh_token:
                self.logger.error(f"No refresh token available for user {user_id}")
                return None

            # This would typically call the OAuth2 refresh endpoint
            # For now, we'll just log that refresh is needed
            self.logger.info(
                f"Refresh needed for user {user_id} - implement OAuth2 refresh logic"
            )

            # TODO: Implement actual OAuth2 refresh logic
            # new_tokens = self._perform_oauth2_refresh(refresh_token)
            # if new_tokens:
            #     self.save_tokens(user_id, **new_tokens)
            #     return new_tokens["access_token"]

            return None

        except Exception as e:
            self.logger.error(f"Failed to refresh tokens for user {user_id}: {e}")
            return None

    def revoke_tokens(self, user_id: str) -> bool:
        """
        Revoke and delete OAuth2 tokens for a user.

        Args:
            user_id: Unique user identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            # TODO: Implement actual OAuth2 revocation logic
            # tokens = self.load_tokens(user_id)
            # if tokens and tokens.get("access_token"):
            #     self._perform_oauth2_revocation(tokens["access_token"])

            # Delete stored tokens
            success = self.backend.delete_tokens(user_id)
            if success:
                self.logger.info(f"Tokens revoked and deleted for user {user_id}")
            return success

        except Exception as e:
            self.logger.error(f"Failed to revoke tokens for user {user_id}: {e}")
            return False

    def list_users(self) -> list:
        """
        List all users with stored tokens.

        Returns:
            List of user IDs
        """
        try:
            users = self.backend.list_users()
            self.logger.info(f"Found {len(users)} users with stored tokens")
            return users
        except Exception as e:
            self.logger.error(f"Failed to list users: {e}")
            return []

    def is_token_valid(self, user_id: str) -> bool:
        """
        Check if a user has valid tokens.

        Args:
            user_id: Unique user identifier

        Returns:
            True if tokens are valid, False otherwise
        """
        try:
            access_token = self.get_valid_access_token(user_id)
            return access_token is not None
        except Exception as e:
            self.logger.error(f"Failed to check token validity for user {user_id}: {e}")
            return False

    def get_token_info(self, user_id: str) -> dict[str, Any] | None:
        """
        Get detailed information about stored tokens.

        Args:
            user_id: Unique user identifier

        Returns:
            Token information dictionary or None if not found
        """
        try:
            tokens = self.load_tokens(user_id)
            if not tokens:
                return None

            # Add validity information
            expires_at_str = tokens.get("expires_at")
            is_expired = False
            time_until_expiry = None

            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str)
                is_expired = datetime.utcnow() >= expires_at
                if not is_expired:
                    time_until_expiry = expires_at - datetime.utcnow()

            token_info = {
                "user_id": user_id,
                "has_access_token": bool(tokens.get("access_token")),
                "has_refresh_token": bool(tokens.get("refresh_token")),
                "is_expired": is_expired,
                "time_until_expiry": (
                    str(time_until_expiry) if time_until_expiry else None
                ),
                "created_at": tokens.get("created_at"),
                "expires_at": expires_at_str,
                "additional_data": tokens.get("additional_data", {}),
            }

            return token_info

        except Exception as e:
            self.logger.error(f"Failed to get token info for user {user_id}: {e}")
            return None

    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired tokens for all users.

        Returns:
            Number of users whose tokens were cleaned up
        """
        try:
            users = self.list_users()
            cleaned_count = 0

            for user_id in users:
                if not self.is_token_valid(user_id):
                    self.revoke_tokens(user_id)
                    cleaned_count += 1

            self.logger.info(f"Cleaned up expired tokens for {cleaned_count} users")
            return cleaned_count

        except Exception as e:
            self.logger.error(f"Failed to cleanup expired tokens: {e}")
            return 0
