from typing import Any

from googleapiclient.errors import HttpError

from gspace.utils.logger import get_logger


class Sheets:
    """
    Google Sheets API wrapper with comprehensive spreadsheet operations.
    """

    def __init__(self, auth):
        """
        Initialize Sheets service.

        Args:
            auth: AuthManager instance
        """
        self.logger = get_logger("gspace.sheets")
        self.auth = auth
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize the Sheets service."""
        try:
            self.service = self.auth.build_service("sheets", "v4")
            self.logger.info("Sheets service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Sheets service: {e}")
            raise

    def create_spreadsheet(
        self, title: str, sheets: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """
        Create a new Google Spreadsheet.

        Args:
            title: Spreadsheet title
            sheets: List of sheet configurations

        Returns:
            Created spreadsheet dictionary
        """
        try:
            self.logger.info(f"Creating spreadsheet: {title}")

            spreadsheet = {"properties": {"title": title}}

            if sheets:
                spreadsheet["sheets"] = sheets

            created_spreadsheet = (
                self.service.spreadsheets().create(body=spreadsheet).execute()
            )

            self.logger.info(
                f"Successfully created spreadsheet: {created_spreadsheet.get('spreadsheetId')}"
            )
            return created_spreadsheet

        except HttpError as e:
            self.logger.error(f"HTTP error creating spreadsheet: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create spreadsheet: {e}")
            raise

    def get_spreadsheet(
        self,
        spreadsheet_id: str,
        ranges: list[str] | None = None,
        include_grid_data: bool = True,
    ) -> dict[str, Any]:
        """
        Get a spreadsheet by ID.

        Args:
            spreadsheet_id: Spreadsheet ID
            ranges: List of ranges to retrieve
            include_grid_data: Whether to include grid data

        Returns:
            Spreadsheet details
        """
        try:
            self.logger.info(f"Fetching spreadsheet: {spreadsheet_id}")

            params = {
                "spreadsheetId": spreadsheet_id,
                "includeGridData": include_grid_data,
            }

            if ranges:
                params["ranges"] = ranges

            spreadsheet = self.service.spreadsheets().get(**params).execute()

            self.logger.info(
                f"Successfully fetched spreadsheet: {spreadsheet.get('properties', {}).get('title', 'Unknown')}"
            )
            return spreadsheet

        except HttpError as e:
            self.logger.error(f"HTTP error getting spreadsheet {spreadsheet_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to get spreadsheet {spreadsheet_id}: {e}")
            raise

    def get_values(
        self, spreadsheet_id: str, range_name: str, major_dimension: str = "ROWS"
    ) -> dict[str, Any]:
        """
        Get values from a specific range in a spreadsheet.

        Args:
            spreadsheet_id: Spreadsheet ID
            range_name: Range in A1 notation (e.g., "Sheet1!A1:D10")
            major_dimension: Major dimension ("ROWS" or "COLUMNS")

        Returns:
            Values response
        """
        try:
            self.logger.info(f"Fetching values from range: {range_name}")

            result = (
                self.service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    majorDimension=major_dimension,
                )
                .execute()
            )

            values = result.get("values", [])
            self.logger.info(
                f"Successfully fetched {len(values)} rows from range {range_name}"
            )
            return result

        except HttpError as e:
            self.logger.error(f"HTTP error getting values from range {range_name}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to get values from range {range_name}: {e}")
            raise

    def update_values(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: list[list[Any]],
        value_input_option: str = "RAW",
    ) -> dict[str, Any]:
        """
        Update values in a specific range.

        Args:
            spreadsheet_id: Spreadsheet ID
            range_name: Range in A1 notation
            values: 2D array of values to write
            value_input_option: How input data should be interpreted

        Returns:
            Update response
        """
        try:
            self.logger.info(f"Updating values in range: {range_name}")

            body = {"values": values}

            result = (
                self.service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute()
            )

            self.logger.info(
                f"Successfully updated {result.get('updatedCells', 0)} cells in range {range_name}"
            )
            return result

        except HttpError as e:
            self.logger.error(f"HTTP error updating values in range {range_name}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to update values in range {range_name}: {e}")
            raise

    def append_values(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: list[list[Any]],
        value_input_option: str = "RAW",
        insert_data_option: str = "INSERT_ROWS",
    ) -> dict[str, Any]:
        """
        Append values to a range.

        Args:
            spreadsheet_id: Spreadsheet ID
            range_name: Range in A1 notation
            values: 2D array of values to append
            value_input_option: How input data should be interpreted
            insert_data_option: How the input data should be inserted

        Returns:
            Append response
        """
        try:
            self.logger.info(f"Appending values to range: {range_name}")

            body = {"values": values}

            result = (
                self.service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    insertDataOption=insert_data_option,
                    body=body,
                )
                .execute()
            )

            self.logger.info(f"Successfully appended values to range {range_name}")
            return result

        except HttpError as e:
            self.logger.error(f"HTTP error appending values to range {range_name}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to append values to range {range_name}: {e}")
            raise

    def clear_values(self, spreadsheet_id: str, range_name: str) -> dict[str, Any]:
        """
        Clear values from a range.

        Args:
            spreadsheet_id: Spreadsheet ID
            range_name: Range in A1 notation

        Returns:
            Clear response
        """
        try:
            self.logger.info(f"Clearing values from range: {range_name}")

            result = (
                self.service.spreadsheets()
                .values()
                .clear(spreadsheetId=spreadsheet_id, range=range_name, body={})
                .execute()
            )

            self.logger.info(f"Successfully cleared values from range {range_name}")
            return result

        except HttpError as e:
            self.logger.error(
                f"HTTP error clearing values from range {range_name}: {e}"
            )
            raise
        except Exception as e:
            self.logger.error(f"Failed to clear values from range {range_name}: {e}")
            raise

    def batch_update(
        self, spreadsheet_id: str, requests: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Apply multiple updates to a spreadsheet.

        Args:
            spreadsheet_id: Spreadsheet ID
            requests: List of update requests

        Returns:
            Batch update response
        """
        try:
            self.logger.info(f"Applying {len(requests)} batch updates to spreadsheet")

            body = {"requests": requests}

            result = (
                self.service.spreadsheets()
                .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
                .execute()
            )

            self.logger.info("Successfully applied batch updates to spreadsheet")
            return result

        except HttpError as e:
            self.logger.error(f"HTTP error applying batch updates: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to apply batch updates: {e}")
            raise

    def add_sheet(
        self,
        spreadsheet_id: str,
        title: str,
        grid_properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Add a new sheet to a spreadsheet.

        Args:
            spreadsheet_id: Spreadsheet ID
            title: Sheet title
            grid_properties: Grid properties for the new sheet

        Returns:
            Add sheet response
        """
        try:
            self.logger.info(f"Adding sheet '{title}' to spreadsheet")

            request = {"addSheet": {"properties": {"title": title}}}

            if grid_properties:
                request["addSheet"]["properties"]["gridProperties"] = grid_properties

            result = self.batch_update(spreadsheet_id, [request])

            self.logger.info(f"Successfully added sheet '{title}' to spreadsheet")
            return result

        except Exception as e:
            self.logger.error(f"Failed to add sheet '{title}': {e}")
            raise

    def delete_sheet(self, spreadsheet_id: str, sheet_id: int) -> dict[str, Any]:
        """
        Delete a sheet from a spreadsheet.

        Args:
            spreadsheet_id: Spreadsheet ID
            sheet_id: Sheet ID to delete

        Returns:
            Delete sheet response
        """
        try:
            self.logger.info(f"Deleting sheet with ID: {sheet_id}")

            request = {"deleteSheet": {"sheetId": sheet_id}}

            result = self.batch_update(spreadsheet_id, [request])

            self.logger.info(f"Successfully deleted sheet with ID: {sheet_id}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to delete sheet with ID {sheet_id}: {e}")
            raise

    def format_cells(
        self, spreadsheet_id: str, range_name: str, format_properties: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Format cells in a range.

        Args:
            spreadsheet_id: Spreadsheet ID
            range_name: Range in A1 notation
            format_properties: Format properties to apply

        Returns:
            Format response
        """
        try:
            self.logger.info(f"Formatting cells in range: {range_name}")

            request = {
                "repeatCell": {
                    "range": {
                        "sheetId": self._get_sheet_id_from_range(
                            spreadsheet_id, range_name
                        ),
                        "startRowIndex": 0,
                        "endRowIndex": 1000,
                        "startColumnIndex": 0,
                        "endColumnIndex": 26,
                    },
                    "cell": {"userEnteredFormat": format_properties},
                    "fields": "userEnteredFormat",
                }
            }

            result = self.batch_update(spreadsheet_id, [request])

            self.logger.info(f"Successfully formatted cells in range {range_name}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to format cells in range {range_name}: {e}")
            raise

    def set_column_width(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        start_column: int,
        end_column: int,
        width: int,
    ) -> dict[str, Any]:
        """
        Set column width in a sheet.

        Args:
            spreadsheet_id: Spreadsheet ID
            sheet_id: Sheet ID
            start_column: Start column index
            end_column: End column index
            width: Column width in pixels

        Returns:
            Set column width response
        """
        try:
            self.logger.info(
                f"Setting column width for columns {start_column}-{end_column}"
            )

            request = {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": start_column,
                        "endIndex": end_column,
                    },
                    "properties": {"pixelSize": width},
                    "fields": "pixelSize",
                }
            }

            result = self.batch_update(spreadsheet_id, [request])

            self.logger.info(
                f"Successfully set column width for columns {start_column}-{end_column}"
            )
            return result

        except Exception as e:
            self.logger.error(f"Failed to set column width: {e}")
            raise

    def set_row_height(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        start_row: int,
        end_row: int,
        height: int,
    ) -> dict[str, Any]:
        """
        Set row height in a sheet.

        Args:
            spreadsheet_id: Spreadsheet ID
            sheet_id: Sheet ID
            start_row: Start row index
            end_row: End row index
            height: Row height in pixels

        Returns:
            Set row height response
        """
        try:
            self.logger.info(f"Setting row height for rows {start_row}-{end_row}")

            request = {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": start_row,
                        "endIndex": end_row,
                    },
                    "properties": {"pixelSize": height},
                    "fields": "pixelSize",
                }
            }

            result = self.batch_update(spreadsheet_id, [request])

            self.logger.info(
                f"Successfully set row height for rows {start_row}-{end_row}"
            )
            return result

        except Exception as e:
            self.logger.error(f"Failed to set row height: {e}")
            raise

    def merge_cells(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        start_row: int,
        end_row: int,
        start_column: int,
        end_column: int,
    ) -> dict[str, Any]:
        """
        Merge cells in a range.

        Args:
            spreadsheet_id: Spreadsheet ID
            sheet_id: Sheet ID
            start_row: Start row index
            end_row: End row index
            start_column: Start column index
            end_column: End column index

        Returns:
            Merge cells response
        """
        try:
            self.logger.info(
                f"Merging cells in range {start_row}:{start_column}-{end_row}:{end_column}"
            )

            request = {
                "mergeCells": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": start_row,
                        "endRowIndex": end_row,
                        "startColumnIndex": start_column,
                        "endColumnIndex": end_column,
                    },
                    "mergeType": "MERGE_ALL",
                }
            }

            result = self.batch_update(spreadsheet_id, [request])

            self.logger.info("Successfully merged cells in range")
            return result

        except Exception as e:
            self.logger.error(f"Failed to merge cells: {e}")
            raise

    def _get_sheet_id_from_range(self, spreadsheet_id: str, range_name: str) -> int:
        """Extract sheet ID from range name."""
        try:
            # Parse range to get sheet name
            if "!" in range_name:
                sheet_name = range_name.split("!")[0]
            else:
                sheet_name = range_name

            # Get spreadsheet to find sheet ID
            spreadsheet = self.get_spreadsheet(spreadsheet_id)
            sheets = spreadsheet.get("sheets", [])

            for sheet in sheets:
                if sheet.get("properties", {}).get("title") == sheet_name:
                    return sheet.get("properties", {}).get("sheetId")

            # Default to first sheet if not found
            return sheets[0].get("properties", {}).get("sheetId") if sheets else 0

        except Exception as e:
            self.logger.warning(
                f"Could not determine sheet ID from range {range_name}: {e}"
            )
            return 0
