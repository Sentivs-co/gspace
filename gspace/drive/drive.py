from pathlib import Path
from typing import Any

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

from gspace.utils.logger import get_logger


class Drive:
    """
    Google Drive API wrapper with comprehensive file and folder operations.
    """

    def __init__(self, auth):
        """
        Initialize Drive service.

        Args:
            auth: AuthManager instance
        """
        self.logger = get_logger("gspace.drive")
        self.auth = auth
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize the Drive service."""
        try:
            self.service = self.auth.build_service("drive", "v3")
            self.logger.info("Drive service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Drive service: {e}")
            raise

    def list_files(
        self,
        page_size: int = 100,
        fields: str = "nextPageToken, files(id, name, mimeType, size, modifiedTime, parents)",
        q: str | None = None,
        order_by: str = "modifiedTime desc",
        spaces: str = "drive",
        include_items_from_all_drives: bool = False,
        supports_all_drives: bool = False,
    ) -> list[dict[str, Any]]:
        """
        List files and folders from Google Drive.

        Args:
            page_size: Number of files to return per page
            fields: Fields to include in response
            q: Query string for filtering files
            order_by: Order of results
            spaces: Spaces to search in
            include_items_from_all_drives: Whether to include items from all drives
            supports_all_drives: Whether the request supports both My Drive and shared drives

        Returns:
            List of file dictionaries
        """
        try:
            self.logger.info(f"Fetching up to {page_size} files from Drive")

            files = []
            page_token = None

            while True:
                result = (
                    self.service.files()
                    .list(
                        pageSize=page_size,
                        fields=fields,
                        q=q,
                        orderBy=order_by,
                        spaces=spaces,
                        includeItemsFromAllDrives=include_items_from_all_drives,
                        supportsAllDrives=supports_all_drives,
                        pageToken=page_token,
                    )
                    .execute()
                )

                files.extend(result.get("files", []))
                page_token = result.get("nextPageToken")

                if not page_token:
                    break

            self.logger.info(f"Successfully fetched {len(files)} files")
            return files

        except HttpError as e:
            self.logger.error(f"HTTP error listing files: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            raise

    def get_file(
        self, file_id: str, fields: str = "*", supports_all_drives: bool = False
    ) -> dict[str, Any]:
        """
        Get details of a specific file.

        Args:
            file_id: File ID
            fields: Fields to include in response
            supports_all_drives: Whether the request supports both My Drive and shared drives

        Returns:
            File details dictionary
        """
        try:
            self.logger.info(f"Fetching file details: {file_id}")

            file = (
                self.service.files()
                .get(
                    fileId=file_id, fields=fields, supportsAllDrives=supports_all_drives
                )
                .execute()
            )

            self.logger.info(
                f"Successfully fetched file: {file.get('name', 'Unknown')}"
            )
            return file

        except HttpError as e:
            self.logger.error(f"HTTP error getting file {file_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to get file {file_id}: {e}")
            raise

    def create_folder(
        self,
        name: str,
        parent_id: str | None = None,
        description: str | None = None,
        supports_all_drives: bool = False,
    ) -> dict[str, Any]:
        """
        Create a new folder in Google Drive.

        Args:
            name: Folder name
            parent_id: Parent folder ID (default: root)
            description: Folder description
            supports_all_drives: Whether the request supports both My Drive and shared drives

        Returns:
            Created folder dictionary
        """
        try:
            self.logger.info(f"Creating folder: {name}")

            folder_metadata = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
            }

            if parent_id:
                folder_metadata["parents"] = [parent_id]
            if description:
                folder_metadata["description"] = description

            folder = (
                self.service.files()
                .create(body=folder_metadata, supportsAllDrives=supports_all_drives)
                .execute()
            )

            self.logger.info(f"Successfully created folder: {folder.get('id')}")
            return folder

        except HttpError as e:
            self.logger.error(f"HTTP error creating folder: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create folder: {e}")
            raise

    def upload_file(
        self,
        file_path: str | Path,
        name: str | None = None,
        parent_id: str | None = None,
        mime_type: str | None = None,
        description: str | None = None,
        supports_all_drives: bool = False,
    ) -> dict[str, Any]:
        """
        Upload a file to Google Drive.

        Args:
            file_path: Path to the file to upload
            name: Custom name for the file (default: original filename)
            parent_id: Parent folder ID (default: root)
            mime_type: MIME type of the file
            description: File description
            supports_all_drives: Whether the request supports both My Drive and shared drives

        Returns:
            Uploaded file dictionary
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            if not name:
                name = file_path.name

            if not mime_type:
                import mimetypes

                mime_type, _ = mimetypes.guess_type(str(file_path))
                if not mime_type:
                    mime_type = "application/octet-stream"

            self.logger.info(f"Uploading file: {name}")

            # File metadata
            file_metadata = {"name": name, "mimeType": mime_type}

            if parent_id:
                file_metadata["parents"] = [parent_id]
            if description:
                file_metadata["description"] = description

            # Create media upload
            with open(file_path, "rb") as f:
                media = MediaIoBaseUpload(f, mimetype=mime_type, resumable=True)

                file = (
                    self.service.files()
                    .create(
                        body=file_metadata,
                        media_body=media,
                        supportsAllDrives=supports_all_drives,
                    )
                    .execute()
                )

            self.logger.info(f"Successfully uploaded file: {file.get('id')}")
            return file

        except HttpError as e:
            self.logger.error(f"HTTP error uploading file: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to upload file: {e}")
            raise

    def download_file(
        self,
        file_id: str,
        destination_path: str | Path,
        supports_all_drives: bool = False,
    ) -> bool:
        """
        Download a file from Google Drive.

        Args:
            file_id: File ID to download
            destination_path: Local path to save the file
            supports_all_drives: Whether the request supports both My Drive and shared drives

        Returns:
            True if successful
        """
        try:
            destination_path = Path(destination_path)
            self.logger.info(f"Downloading file {file_id} to {destination_path}")

            # Create destination directory if it doesn't exist
            destination_path.parent.mkdir(parents=True, exist_ok=True)

            # Download the file
            request = self.service.files().get_media(
                fileId=file_id, supportsAllDrives=supports_all_drives
            )

            with open(destination_path, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        self.logger.debug(
                            f"Download progress: {int(status.progress() * 100)}%"
                        )

            self.logger.info(f"Successfully downloaded file to {destination_path}")
            return True

        except HttpError as e:
            self.logger.error(f"HTTP error downloading file {file_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to download file {file_id}: {e}")
            raise

    def update_file(
        self, file_id: str, updates: dict[str, Any], supports_all_drives: bool = False
    ) -> dict[str, Any]:
        """
        Update file metadata.

        Args:
            file_id: File ID to update
            updates: Dictionary of fields to update
            supports_all_drives: Whether the request supports both My Drive and shared drives

        Returns:
            Updated file dictionary
        """
        try:
            self.logger.info(f"Updating file: {file_id}")

            updated_file = (
                self.service.files()
                .update(
                    fileId=file_id, body=updates, supportsAllDrives=supports_all_drives
                )
                .execute()
            )

            self.logger.info(f"Successfully updated file: {file_id}")
            return updated_file

        except HttpError as e:
            self.logger.error(f"HTTP error updating file {file_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to update file {file_id}: {e}")
            raise

    def delete_file(self, file_id: str, supports_all_drives: bool = False) -> bool:
        """
        Delete a file from Google Drive.

        Args:
            file_id: File ID to delete
            supports_all_drives: Whether the request supports both My Drive and shared drives

        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Deleting file: {file_id}")

            self.service.files().delete(
                fileId=file_id, supportsAllDrives=supports_all_drives
            ).execute()

            self.logger.info(f"Successfully deleted file: {file_id}")
            return True

        except HttpError as e:
            self.logger.error(f"HTTP error deleting file {file_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete file {file_id}: {e}")
            raise

    def copy_file(
        self,
        file_id: str,
        name: str | None = None,
        parent_id: str | None = None,
        supports_all_drives: bool = False,
    ) -> dict[str, Any]:
        """
        Copy a file in Google Drive.

        Args:
            file_id: File ID to copy
            name: Name for the copied file
            parent_id: Parent folder ID for the copy
            supports_all_drives: Whether the request supports both My Drive and shared drives

        Returns:
            Copied file dictionary
        """
        try:
            self.logger.info(f"Copying file: {file_id}")

            copy_metadata = {}
            if name:
                copy_metadata["name"] = name
            if parent_id:
                copy_metadata["parents"] = [parent_id]

            copied_file = (
                self.service.files()
                .copy(
                    fileId=file_id,
                    body=copy_metadata,
                    supportsAllDrives=supports_all_drives,
                )
                .execute()
            )

            self.logger.info(f"Successfully copied file: {copied_file.get('id')}")
            return copied_file

        except HttpError as e:
            self.logger.error(f"HTTP error copying file {file_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to copy file {file_id}: {e}")
            raise

    def move_file(
        self,
        file_id: str,
        new_parent_id: str,
        old_parent_id: str | None = None,
        supports_all_drives: bool = False,
    ) -> dict[str, Any]:
        """
        Move a file to a different folder.

        Args:
            file_id: File ID to move
            new_parent_id: New parent folder ID
            old_parent_id: Old parent folder ID (optional)
            supports_all_drives: Whether the request supports both My Drive and shared drives

        Returns:
            Moved file dictionary
        """
        try:
            self.logger.info(f"Moving file {file_id} to folder {new_parent_id}")

            # Get current file to check existing parents
            file = self.get_file(file_id)
            current_parents = file.get("parents", [])

            # Remove from old parent and add to new parent
            if old_parent_id:
                current_parents.remove(old_parent_id)
            current_parents.append(new_parent_id)

            # Update the file
            updated_file = self.update_file(
                file_id, {"parents": current_parents}, supports_all_drives
            )

            self.logger.info(f"Successfully moved file: {file_id}")
            return updated_file

        except Exception as e:
            self.logger.error(f"Failed to move file {file_id}: {e}")
            raise

    def share_file(
        self,
        file_id: str,
        email: str,
        role: str = "reader",
        type: str = "user",
        supports_all_drives: bool = False,
    ) -> dict[str, Any]:
        """
        Share a file with another user.

        Args:
            file_id: File ID to share
            email: Email address of the user to share with
            role: Permission role ("reader", "writer", "commenter", "owner")
            type: Permission type ("user", "group", "domain", "anyone")
            supports_all_drives: Whether the request supports both My Drive and shared drives

        Returns:
            Permission details
        """
        try:
            self.logger.info(f"Sharing file {file_id} with {email} as {role}")

            permission = {"type": type, "role": role}

            if type == "user":
                permission["emailAddress"] = email
            elif type == "group":
                permission["emailAddress"] = email
            elif type == "domain":
                permission["domain"] = email

            created_permission = (
                self.service.permissions()
                .create(
                    fileId=file_id,
                    body=permission,
                    supportsAllDrives=supports_all_drives,
                )
                .execute()
            )

            self.logger.info(f"Successfully shared file with {email}")
            return created_permission

        except HttpError as e:
            self.logger.error(f"HTTP error sharing file {file_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to share file {file_id}: {e}")
            raise

    def search_files(
        self,
        query: str,
        page_size: int = 100,
        fields: str = "nextPageToken, files(id, name, mimeType, size, modifiedTime)",
        order_by: str = "modifiedTime desc",
    ) -> list[dict[str, Any]]:
        """
        Search for files in Google Drive.

        Args:
            query: Search query string
            page_size: Number of results per page
            fields: Fields to include in response
            order_by: Order of results

        Returns:
            List of matching files
        """
        try:
            self.logger.info(f"Searching files with query: {query}")

            files = self.list_files(
                page_size=page_size, fields=fields, q=query, order_by=order_by
            )

            self.logger.info(f"Search returned {len(files)} files")
            return files

        except Exception as e:
            self.logger.error(f"Failed to search files: {e}")
            raise

    def get_file_permissions(
        self, file_id: str, supports_all_drives: bool = False
    ) -> list[dict[str, Any]]:
        """
        Get permissions for a file.

        Args:
            file_id: File ID
            supports_all_drives: Whether the request supports both My Drive and shared drives

        Returns:
            List of permission dictionaries
        """
        try:
            self.logger.info(f"Fetching permissions for file: {file_id}")

            result = (
                self.service.permissions()
                .list(fileId=file_id, supportsAllDrives=supports_all_drives)
                .execute()
            )

            permissions = result.get("permissions", [])
            self.logger.info(f"Successfully fetched {len(permissions)} permissions")
            return permissions

        except HttpError as e:
            self.logger.error(f"HTTP error getting permissions for file {file_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to get permissions for file {file_id}: {e}")
            raise

    def create_shortcut(
        self,
        target_id: str,
        name: str | None = None,
        parent_id: str | None = None,
        supports_all_drives: bool = False,
    ) -> dict[str, Any]:
        """
        Create a shortcut to another file.

        Args:
            target_id: ID of the target file
            name: Name for the shortcut
            parent_id: Parent folder ID
            supports_all_drives: Whether the request supports both My Drive and shared drives

        Returns:
            Created shortcut dictionary
        """
        try:
            self.logger.info(f"Creating shortcut to file: {target_id}")

            shortcut_metadata = {
                "name": name or f"Shortcut to {target_id}",
                "mimeType": "application/vnd.google-apps.shortcut",
                "targetId": target_id,
            }

            if parent_id:
                shortcut_metadata["parents"] = [parent_id]

            shortcut = (
                self.service.files()
                .create(body=shortcut_metadata, supportsAllDrives=supports_all_drives)
                .execute()
            )

            self.logger.info(f"Successfully created shortcut: {shortcut.get('id')}")
            return shortcut

        except HttpError as e:
            self.logger.error(f"HTTP error creating shortcut: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create shortcut: {e}")
            raise
