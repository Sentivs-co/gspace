import base64
import mimetypes
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

from googleapiclient.errors import HttpError

from gspace.utils.logger import get_logger


class Gmail:
    """
    Gmail API wrapper with comprehensive email operations.
    """

    def __init__(self, auth):
        """
        Initialize Gmail service.

        Args:
            auth: AuthManager instance
        """
        self.logger = get_logger("gspace.gmail")
        self.auth = auth
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize the Gmail service."""
        try:
            self.service = self.auth.build_service("gmail", "v1")
            self.logger.info("Gmail service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gmail service: {e}")
            raise

    def send_email(
        self,
        to: str | list[str],
        subject: str,
        body: str,
        body_type: str = "plain",
        cc: str | list[str] | None = None,
        bcc: str | list[str] | None = None,
        reply_to: str | None = None,
        attachments: list[str | Path] | None = None,
        user_id: str = "me",
    ) -> dict[str, Any]:
        """
        Send an email with optional attachments.

        Args:
            to: Recipient email(s)
            subject: Email subject
            body: Email body content
            body_type: Body content type ("plain" or "html")
            cc: CC recipient(s)
            bcc: BCC recipient(s)
            reply_to: Reply-to email address
            attachments: List of file paths to attach
            user_id: Gmail user ID (default: "me")

        Returns:
            Sent message details
        """
        try:
            self.logger.info(f"Sending email to: {to}")

            # Create message
            message = MIMEMultipart()
            message["to"] = self._format_recipients(to)
            message["subject"] = subject

            if cc:
                message["cc"] = self._format_recipients(cc)
            if bcc:
                message["bcc"] = self._format_recipients(bcc)
            if reply_to:
                message["reply-to"] = reply_to

            # Add body
            text_part = MIMEText(body, body_type)
            message.attach(text_part)

            # Add attachments
            if attachments:
                for attachment_path in attachments:
                    self._add_attachment(message, attachment_path)

            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            sent_message = (
                self.service.users()
                .messages()
                .send(userId=user_id, body={"raw": raw_message})
                .execute()
            )

            self.logger.info(f"Successfully sent email: {sent_message.get('id')}")
            return sent_message

        except HttpError as e:
            self.logger.error(f"HTTP error sending email: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            raise

    def send_simple_email(
        self, to: str | list[str], subject: str, body: str, user_id: str = "me"
    ) -> dict[str, Any]:
        """
        Send a simple text email.

        Args:
            to: Recipient email(s)
            subject: Email subject
            body: Email body content
            user_id: Gmail user ID (default: "me")

        Returns:
            Sent message details
        """
        try:
            self.logger.info(f"Sending simple email to: {to}")

            message = MIMEText(body)
            message["to"] = self._format_recipients(to)
            message["subject"] = subject

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            sent_message = (
                self.service.users()
                .messages()
                .send(userId=user_id, body={"raw": raw_message})
                .execute()
            )

            self.logger.info(
                f"Successfully sent simple email: {sent_message.get('id')}"
            )
            return sent_message

        except Exception as e:
            self.logger.error(f"Failed to send simple email: {e}")
            raise

    def list_messages(
        self,
        user_id: str = "me",
        query: str | None = None,
        max_results: int = 100,
        label_ids: list[str] | None = None,
        include_spam_trash: bool = False,
    ) -> list[dict[str, Any]]:
        """
        List messages from Gmail.

        Args:
            user_id: Gmail user ID (default: "me")
            query: Gmail search query
            max_results: Maximum number of messages to return
            label_ids: List of label IDs to filter by
            include_spam_trash: Whether to include spam/trash messages

        Returns:
            List of message summaries
        """
        try:
            self.logger.info(f"Fetching up to {max_results} messages")

            messages = []
            page_token = None

            while True:
                result = (
                    self.service.users()
                    .messages()
                    .list(
                        userId=user_id,
                        q=query,
                        maxResults=max_results,
                        labelIds=label_ids,
                        includeSpamTrash=include_spam_trash,
                        pageToken=page_token,
                    )
                    .execute()
                )

                messages.extend(result.get("messages", []))
                page_token = result.get("nextPageToken")

                if not page_token or len(messages) >= max_results:
                    break

            self.logger.info(f"Successfully fetched {len(messages)} messages")
            return messages[:max_results]

        except HttpError as e:
            self.logger.error(f"HTTP error listing messages: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to list messages: {e}")
            raise

    def get_message(
        self,
        message_id: str,
        user_id: str = "me",
        format: str = "full",
        metadata_headers: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get a specific message by ID.

        Args:
            message_id: Message ID
            user_id: Gmail user ID (default: "me")
            format: Message format ("minimal", "full", "raw", "metadata")
            metadata_headers: Headers to include in metadata format

        Returns:
            Message details
        """
        try:
            self.logger.info(f"Fetching message: {message_id}")

            params = {"userId": user_id, "id": message_id, "format": format}

            if format == "metadata" and metadata_headers:
                params["metadataHeaders"] = metadata_headers

            message = self.service.users().messages().get(**params).execute()

            self.logger.info(f"Successfully fetched message: {message.get('id')}")
            return message

        except HttpError as e:
            self.logger.error(f"HTTP error getting message {message_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to get message {message_id}: {e}")
            raise

    def delete_message(self, message_id: str, user_id: str = "me") -> bool:
        """
        Delete a message.

        Args:
            message_id: Message ID
            user_id: Gmail user ID (default: "me")

        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Deleting message: {message_id}")

            self.service.users().messages().delete(
                userId=user_id, id=message_id
            ).execute()

            self.logger.info(f"Successfully deleted message: {message_id}")
            return True

        except HttpError as e:
            self.logger.error(f"HTTP error deleting message {message_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete message {message_id}: {e}")
            raise

    def modify_message_labels(
        self,
        message_id: str,
        add_label_ids: list[str] | None = None,
        remove_label_ids: list[str] | None = None,
        user_id: str = "me",
    ) -> dict[str, Any]:
        """
        Modify message labels.

        Args:
            message_id: Message ID
            add_label_ids: Labels to add
            remove_label_ids: Labels to remove
            user_id: Gmail user ID (default: "me")

        Returns:
            Modified message
        """
        try:
            self.logger.info(f"Modifying labels for message: {message_id}")

            body = {}
            if add_label_ids:
                body["addLabelIds"] = add_label_ids
            if remove_label_ids:
                body["removeLabelIds"] = remove_label_ids

            modified_message = (
                self.service.users()
                .messages()
                .modify(userId=user_id, id=message_id, body=body)
                .execute()
            )

            self.logger.info(f"Successfully modified message labels: {message_id}")
            return modified_message

        except HttpError as e:
            self.logger.error(f"HTTP error modifying message labels {message_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to modify message labels {message_id}: {e}")
            raise

    def list_labels(self, user_id: str = "me") -> list[dict[str, Any]]:
        """
        List all Gmail labels.

        Args:
            user_id: Gmail user ID (default: "me")

        Returns:
            List of label dictionaries
        """
        try:
            self.logger.info("Fetching Gmail labels")

            result = self.service.users().labels().list(userId=user_id).execute()
            labels = result.get("labels", [])

            self.logger.info(f"Successfully fetched {len(labels)} labels")
            return labels

        except HttpError as e:
            self.logger.error(f"HTTP error listing labels: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to list labels: {e}")
            raise

    def create_label(
        self,
        name: str,
        message_list_visibility: str = "show",
        label_list_visibility: str = "labelShow",
        user_id: str = "me",
    ) -> dict[str, Any]:
        """
        Create a new Gmail label.

        Args:
            name: Label name
            message_list_visibility: Message list visibility ("show", "hide")
            label_list_visibility: Label list visibility ("labelShow", "labelHide", "labelHideIfUnread")
            user_id: Gmail user ID (default: "me")

        Returns:
            Created label
        """
        try:
            self.logger.info(f"Creating label: {name}")

            label = {
                "name": name,
                "messageListVisibility": message_list_visibility,
                "labelListVisibility": label_list_visibility,
            }

            created_label = (
                self.service.users()
                .labels()
                .create(userId=user_id, body=label)
                .execute()
            )

            self.logger.info(f"Successfully created label: {created_label.get('id')}")
            return created_label

        except HttpError as e:
            self.logger.error(f"HTTP error creating label: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create label: {e}")
            raise

    def delete_label(self, label_id: str, user_id: str = "me") -> bool:
        """
        Delete a Gmail label.

        Args:
            label_id: Label ID
            user_id: Gmail user ID (default: "me")

        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Deleting label: {label_id}")

            self.service.users().labels().delete(userId=user_id, id=label_id).execute()

            self.logger.info(f"Successfully deleted label: {label_id}")
            return True

        except HttpError as e:
            self.logger.error(f"HTTP error deleting label {label_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete label {label_id}: {e}")
            raise

    def get_profile(self, user_id: str = "me") -> dict[str, Any]:
        """
        Get Gmail profile information.

        Args:
            user_id: Gmail user ID (default: "me")

        Returns:
            Profile information
        """
        try:
            self.logger.info("Fetching Gmail profile")

            profile = self.service.users().getProfile(userId=user_id).execute()

            self.logger.info("Successfully fetched Gmail profile")
            return profile

        except HttpError as e:
            self.logger.error(f"HTTP error getting profile: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to get profile: {e}")
            raise

    def search_messages(
        self, query: str, user_id: str = "me", max_results: int = 100
    ) -> list[dict[str, Any]]:
        """
        Search for messages using Gmail search syntax.

        Args:
            query: Gmail search query
            user_id: Gmail user ID (default: "me")
            max_results: Maximum number of results

        Returns:
            List of matching messages
        """
        try:
            self.logger.info(f"Searching messages with query: {query}")

            messages = self.list_messages(
                user_id=user_id, query=query, max_results=max_results
            )

            self.logger.info(f"Search returned {len(messages)} messages")
            return messages

        except Exception as e:
            self.logger.error(f"Failed to search messages: {e}")
            raise

    def _format_recipients(self, recipients: str | list[str]) -> str:
        """Format recipients list into comma-separated string."""
        if isinstance(recipients, str):
            return recipients
        return ", ".join(recipients)

    def _add_attachment(self, message: MIMEMultipart, file_path: str | Path):
        """Add a file attachment to the message."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                self.logger.warning(f"Attachment file not found: {file_path}")
                return

            # Determine MIME type
            content_type, encoding = mimetypes.guess_type(str(file_path))
            if content_type is None or encoding is not None:
                content_type = "application/octet-stream"

            main_type, sub_type = content_type.split("/", 1)

            # Create appropriate MIME part
            if main_type == "text":
                with open(file_path, encoding="utf-8") as f:
                    part = MIMEText(f.read(), _subtype=sub_type)
            elif main_type == "image":
                with open(file_path, "rb") as f:
                    part = MIMEImage(f.read(), _subtype=sub_type)
            elif main_type == "audio":
                with open(file_path, "rb") as f:
                    part = MIMEAudio(f.read(), _subtype=sub_type)
            else:
                with open(file_path, "rb") as f:
                    part = MIMEBase(main_type, sub_type)
                    part.set_payload(f.read())
                    part.add_header(
                        "Content-Disposition", "attachment", filename=file_path.name
                    )

            part.add_header(
                "Content-Disposition", "attachment", filename=file_path.name
            )
            message.attach(part)

            self.logger.debug(f"Added attachment: {file_path.name}")

        except Exception as e:
            self.logger.error(f"Failed to add attachment {file_path}: {e}")
            raise
