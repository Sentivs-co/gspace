from typing import Any

from googleapiclient.errors import HttpError

from gspace.utils.logger import get_logger


class Docs:
    """
    Google Docs API wrapper with comprehensive document operations.
    """

    def __init__(self, auth):
        """
        Initialize Docs service.

        Args:
            auth: AuthManager instance
        """
        self.logger = get_logger("gspace.docs")
        self.auth = auth
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize the Docs service."""
        try:
            self.service = self.auth.build_service("docs", "v1")
            self.logger.info("Docs service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Docs service: {e}")
            raise

    def create_document(self, title: str) -> dict[str, Any]:
        """
        Create a new Google Document.

        Args:
            title: Document title

        Returns:
            Created document dictionary
        """
        try:
            self.logger.info(f"Creating document: {title}")

            document = {"title": title}

            created_document = self.service.documents().create(body=document).execute()

            self.logger.info(
                f"Successfully created document: {created_document.get('documentId')}"
            )
            return created_document

        except HttpError as e:
            self.logger.error(f"HTTP error creating document: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create document: {e}")
            raise

    def get_document(
        self,
        document_id: str,
        suggestions_view_mode: str = "DEFAULT_FOR_CURRENT_ACCESS",
    ) -> dict[str, Any]:
        """
        Get a document by ID.

        Args:
            document_id: Document ID
            suggestions_view_mode: How suggestions should be displayed

        Returns:
            Document details
        """
        try:
            self.logger.info(f"Fetching document: {document_id}")

            document = (
                self.service.documents()
                .get(documentId=document_id, suggestionsViewMode=suggestions_view_mode)
                .execute()
            )

            self.logger.info(
                f"Successfully fetched document: {document.get('title', 'Unknown')}"
            )
            return document

        except HttpError as e:
            self.logger.error(f"HTTP error getting document {document_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to get document {document_id}: {e}")
            raise

    def batch_update(
        self, document_id: str, requests: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Apply multiple updates to a document.

        Args:
            document_id: Document ID
            requests: List of update requests

        Returns:
            Batch update response
        """
        try:
            self.logger.info(f"Applying {len(requests)} batch updates to document")

            body = {"requests": requests}

            result = (
                self.service.documents()
                .batchUpdate(documentId=document_id, body=body)
                .execute()
            )

            self.logger.info("Successfully applied batch updates to document")
            return result

        except HttpError as e:
            self.logger.error(f"HTTP error applying batch updates: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to apply batch updates: {e}")
            raise

    def insert_text(self, document_id: str, location: int, text: str) -> dict[str, Any]:
        """
        Insert text at a specific location in a document.

        Args:
            document_id: Document ID
            location: Index where to insert text
            text: Text to insert

        Returns:
            Insert text response
        """
        try:
            self.logger.info(f"Inserting text at location {location}")

            request = {"insertText": {"location": {"index": location}, "text": text}}

            result = self.batch_update(document_id, [request])

            self.logger.info(f"Successfully inserted text at location {location}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to insert text: {e}")
            raise

    def delete_content(
        self, document_id: str, start_index: int, end_index: int
    ) -> dict[str, Any]:
        """
        Delete content from a document.

        Args:
            document_id: Document ID
            start_index: Start index of content to delete
            end_index: End index of content to delete

        Returns:
            Delete content response
        """
        try:
            self.logger.info(
                f"Deleting content from index {start_index} to {end_index}"
            )

            request = {
                "deleteContentRange": {
                    "range": {"startIndex": start_index, "endIndex": end_index}
                }
            }

            result = self.batch_update(document_id, [request])

            self.logger.info(
                f"Successfully deleted content from index {start_index} to {end_index}"
            )
            return result

        except Exception as e:
            self.logger.error(f"Failed to delete content: {e}")
            raise

    def replace_all_text(
        self, document_id: str, contains_text: str, replace_text: str
    ) -> dict[str, Any]:
        """
        Replace all occurrences of text in a document.

        Args:
            document_id: Document ID
            contains_text: Text to find
            replace_text: Text to replace with

        Returns:
            Replace all text response
        """
        try:
            self.logger.info(
                f"Replacing all occurrences of '{contains_text}' with '{replace_text}'"
            )

            request = {
                "replaceAllText": {
                    "containsText": {"text": contains_text},
                    "replaceText": replace_text,
                }
            }

            result = self.batch_update(document_id, [request])

            self.logger.info("Successfully replaced all occurrences of text")
            return result

        except Exception as e:
            self.logger.error(f"Failed to replace all text: {e}")
            raise

    def insert_table(
        self, document_id: str, location: int, rows: int, columns: int
    ) -> dict[str, Any]:
        """
        Insert a table into a document.

        Args:
            document_id: Document ID
            location: Index where to insert table
            rows: Number of rows
            columns: Number of columns

        Returns:
            Insert table response
        """
        try:
            self.logger.info(f"Inserting {rows}x{columns} table at location {location}")

            request = {
                "insertTable": {
                    "location": {"index": location},
                    "rows": rows,
                    "columns": columns,
                }
            }

            result = self.batch_update(document_id, [request])

            self.logger.info(f"Successfully inserted table at location {location}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to insert table: {e}")
            raise

    def insert_table_row(
        self, document_id: str, table_cell_location: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Insert a row into a table.

        Args:
            document_id: Document ID
            table_cell_location: Location of a cell in the table

        Returns:
            Insert table row response
        """
        try:
            self.logger.info("Inserting table row")

            request = {"insertTableRow": {"tableCellLocation": table_cell_location}}

            result = self.batch_update(document_id, [request])

            self.logger.info("Successfully inserted table row")
            return result

        except Exception as e:
            self.logger.error(f"Failed to insert table row: {e}")
            raise

    def delete_table_row(
        self, document_id: str, table_cell_location: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Delete a row from a table.

        Args:
            document_id: Document ID
            table_cell_location: Location of a cell in the row to delete

        Returns:
            Delete table row response
        """
        try:
            self.logger.info("Deleting table row")

            request = {"deleteTableRow": {"tableCellLocation": table_cell_location}}

            result = self.batch_update(document_id, [request])

            self.logger.info("Successfully deleted table row")
            return result

        except Exception as e:
            self.logger.error(f"Failed to delete table row: {e}")
            raise

    def insert_image(
        self,
        document_id: str,
        location: int,
        uri: str,
        width: int | None = None,
        height: int | None = None,
    ) -> dict[str, Any]:
        """
        Insert an image into a document.

        Args:
            document_id: Document ID
            location: Index where to insert image
            uri: URI of the image
            width: Image width in points
            height: Image height in points

        Returns:
            Insert image response
        """
        try:
            self.logger.info(f"Inserting image at location {location}")

            request = {
                "insertInlineImage": {"location": {"index": location}, "uri": uri}
            }

            if width and height:
                request["insertInlineImage"]["objectSize"] = {
                    "height": {"magnitude": height, "unit": "PT"},
                    "width": {"magnitude": width, "unit": "PT"},
                }

            result = self.batch_update(document_id, [request])

            self.logger.info(f"Successfully inserted image at location {location}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to insert image: {e}")
            raise

    def update_paragraph_style(
        self, document_id: str, start_index: int, end_index: int, style: str
    ) -> dict[str, Any]:
        """
        Update paragraph style in a document.

        Args:
            document_id: Document ID
            start_index: Start index of paragraph
            end_index: End index of paragraph
            style: Paragraph style to apply

        Returns:
            Update paragraph style response
        """
        try:
            self.logger.info(
                f"Updating paragraph style to '{style}' from index {start_index} to {end_index}"
            )

            request = {
                "updateParagraphStyle": {
                    "range": {"startIndex": start_index, "endIndex": end_index},
                    "paragraphStyle": {"namedStyleType": style},
                    "fields": "namedStyleType",
                }
            }

            result = self.batch_update(document_id, [request])

            self.logger.info(f"Successfully updated paragraph style to '{style}'")
            return result

        except Exception as e:
            self.logger.error(f"Failed to update paragraph style: {e}")
            raise

    def update_text_style(
        self,
        document_id: str,
        start_index: int,
        end_index: int,
        bold: bool | None = None,
        italic: bool | None = None,
        underline: bool | None = None,
        strikethrough: bool | None = None,
        font_size: int | None = None,
        foreground_color: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Update text style in a document.

        Args:
            document_id: Document ID
            start_index: Start index of text
            end_index: End index of text
            bold: Whether text should be bold
            italic: Whether text should be italic
            underline: Whether text should be underlined
            strikethrough: Whether text should be strikethrough
            font_size: Font size in points
            foreground_color: Foreground color object

        Returns:
            Update text style response
        """
        try:
            self.logger.info(
                f"Updating text style from index {start_index} to {end_index}"
            )

            text_style = {}
            fields = []

            if bold is not None:
                text_style["bold"] = bold
                fields.append("bold")
            if italic is not None:
                text_style["italic"] = italic
                fields.append("italic")
            if underline is not None:
                text_style["underline"] = underline
                fields.append("underline")
            if strikethrough is not None:
                text_style["strikethrough"] = strikethrough
                fields.append("strikethrough")
            if font_size is not None:
                text_style["fontSize"] = {"magnitude": font_size, "unit": "PT"}
                fields.append("fontSize")
            if foreground_color is not None:
                text_style["foregroundColor"] = foreground_color
                fields.append("foregroundColor")

            request = {
                "updateTextStyle": {
                    "range": {"startIndex": start_index, "endIndex": end_index},
                    "textStyle": text_style,
                    "fields": ",".join(fields),
                }
            }

            result = self.batch_update(document_id, [request])

            self.logger.info("Successfully updated text style")
            return result

        except Exception as e:
            self.logger.error(f"Failed to update text style: {e}")
            raise

    def create_comment(
        self, document_id: str, location: int, content: str
    ) -> dict[str, Any]:
        """
        Create a comment in a document.

        Args:
            document_id: Document ID
            location: Index where to create comment
            content: Comment content

        Returns:
            Create comment response
        """
        try:
            self.logger.info(f"Creating comment at location {location}")

            request = {
                "createComment": {"location": {"index": location}, "content": content}
            }

            result = self.batch_update(document_id, [request])

            self.logger.info(f"Successfully created comment at location {location}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to create comment: {e}")
            raise

    def insert_page_break(self, document_id: str, location: int) -> dict[str, Any]:
        """
        Insert a page break in a document.

        Args:
            document_id: Document ID
            location: Index where to insert page break

        Returns:
            Insert page break response
        """
        try:
            self.logger.info(f"Inserting page break at location {location}")

            request = {"insertPageBreak": {"location": {"index": location}}}

            result = self.batch_update(document_id, [request])

            self.logger.info(f"Successfully inserted page break at location {location}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to insert page break: {e}")
            raise

    def insert_section_break(self, document_id: str, location: int) -> dict[str, Any]:
        """
        Insert a section break in a document.

        Args:
            document_id: Document ID
            location: Index where to insert section break

        Returns:
            Insert section break response
        """
        try:
            self.logger.info(f"Inserting section break at location {location}")

            request = {"insertSectionBreak": {"location": {"index": location}}}

            result = self.batch_update(document_id, [request])

            self.logger.info(
                f"Successfully inserted section break at location {location}"
            )
            return result

        except Exception as e:
            self.logger.error(f"Failed to insert section break: {e}")
            raise

    def get_document_revisions(self, document_id: str) -> list[dict[str, Any]]:
        """
        Get revision history of a document.

        Args:
            document_id: Document ID

        Returns:
            List of revision dictionaries
        """
        try:
            self.logger.info(f"Fetching revision history for document: {document_id}")

            revisions = self.service.revisions().list(documentId=document_id).execute()

            revision_list = revisions.get("revisions", [])
            self.logger.info(f"Successfully fetched {len(revision_list)} revisions")
            return revision_list

        except HttpError as e:
            self.logger.error(
                f"HTTP error getting revisions for document {document_id}: {e}"
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Failed to get revisions for document {document_id}: {e}"
            )
            raise
