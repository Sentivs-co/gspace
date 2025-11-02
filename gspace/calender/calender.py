from datetime import datetime, timedelta
from typing import Any

from googleapiclient.errors import HttpError

from gspace.utils.logger import get_logger


class Calendar:
    """
    Google Calendar API wrapper with comprehensive calendar operations.
    """

    def __init__(self, auth):
        """
        Initialize Calendar service.

        Args:
            auth: AuthManager instance
        """
        self.logger = get_logger("gspace.calendar")
        self.auth = auth
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize the calendar service."""
        try:
            self.service = self.auth.build_service("calendar", "v3")
            self.logger.info("Calendar service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize calendar service: {e}")
            raise

    def list_calendars(self, max_results: int = 250) -> list[dict[str, Any]]:
        """
        List all available calendars.

        Args:
            max_results: Maximum number of calendars to return

        Returns:
            List of calendar dictionaries
        """
        try:
            self.logger.info(f"Fetching up to {max_results} calendars")

            calendars = []
            page_token = None

            while True:
                result = (
                    self.service.calendarList()
                    .list(maxResults=max_results, pageToken=page_token)
                    .execute()
                )

                calendars.extend(result.get("items", []))
                page_token = result.get("nextPageToken")

                if not page_token:
                    break

            self.logger.info(f"Successfully fetched {len(calendars)} calendars")
            return calendars

        except HttpError as e:
            self.logger.error(f"HTTP error listing calendars: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to list calendars: {e}")
            raise

    def get_calendar(self, calendar_id: str = "primary") -> dict[str, Any]:
        """
        Get details of a specific calendar.

        Args:
            calendar_id: Calendar ID (default: "primary")

        Returns:
            Calendar details dictionary
        """
        try:
            self.logger.info(f"Fetching calendar details for: {calendar_id}")

            calendar = self.service.calendars().get(calendarId=calendar_id).execute()

            self.logger.info(
                f"Successfully fetched calendar: {calendar.get('summary', 'Unknown')}"
            )
            return calendar

        except HttpError as e:
            self.logger.error(f"HTTP error getting calendar {calendar_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to get calendar {calendar_id}: {e}")
            raise

    def create_event(
        self,
        summary: str,
        start_time: str | datetime,
        end_time: str | datetime,
        calendar_id: str = "primary",
        description: str | None = None,
        location: str | None = None,
        attendees: list[str] | None = None,
        reminders: dict[str, Any] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Create a new calendar event.

        Args:
            summary: Event summary/title
            start_time: Event start time (ISO string or datetime)
            end_time: Event end time (ISO string or datetime)
            calendar_id: Calendar ID (default: "primary")
            description: Event description
            location: Event location
            attendees: List of attendee email addresses
            reminders: Reminder settings
            **kwargs: Additional event properties

        Returns:
            Created event dictionary
        """
        try:
            self.logger.info(f"Creating event: {summary}")

            # Convert datetime to ISO format if needed
            if isinstance(start_time, datetime):
                start_time = start_time.isoformat()
            if isinstance(end_time, datetime):
                end_time = end_time.isoformat()

            event = {
                "summary": summary,
                "start": {"dateTime": start_time, "timeZone": "UTC"},
                "end": {"dateTime": end_time, "timeZone": "UTC"},
            }

            if description:
                event["description"] = description
            if location:
                event["location"] = location
            if attendees:
                event["attendees"] = [{"email": email} for email in attendees]
            if reminders:
                event["reminders"] = reminders

            # Add any additional properties
            event.update(kwargs)

            created_event = (
                self.service.events()
                .insert(calendarId=calendar_id, body=event)
                .execute()
            )

            self.logger.info(f"Successfully created event: {created_event.get('id')}")
            return created_event

        except HttpError as e:
            self.logger.error(f"HTTP error creating event: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create event: {e}")
            raise

    def get_event(self, event_id: str, calendar_id: str = "primary") -> dict[str, Any]:
        """
        Get details of a specific event.

        Args:
            event_id: Event ID
            calendar_id: Calendar ID (default: "primary")

        Returns:
            Event details dictionary
        """
        try:
            self.logger.info(f"Fetching event: {event_id}")

            event = (
                self.service.events()
                .get(calendarId=calendar_id, eventId=event_id)
                .execute()
            )

            self.logger.info(
                f"Successfully fetched event: {event.get('summary', 'Unknown')}"
            )
            return event

        except HttpError as e:
            self.logger.error(f"HTTP error getting event {event_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to get event {event_id}: {e}")
            raise

    def list_events(
        self,
        calendar_id: str = "primary",
        time_min: str | datetime | None = None,
        time_max: str | datetime | None = None,
        max_results: int = 250,
        single_events: bool = True,
        order_by: str = "startTime",
        q: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        List events from a calendar.

        Args:
            calendar_id: Calendar ID (default: "primary")
            time_min: Start time for events (ISO string or datetime)
            time_max: End time for events (ISO string or datetime)
            max_results: Maximum number of events to return
            single_events: Whether to expand recurring events
            order_by: Order events by startTime or updated
            q: Free text search terms

        Returns:
            List of event dictionaries
        """
        try:
            self.logger.info(f"Fetching events from calendar: {calendar_id}")

            # Set default time range if not provided
            if not time_min:
                time_min = datetime.now().isoformat() + "Z"
            if not time_max:
                time_max = (datetime.now() + timedelta(days=30)).isoformat() + "Z"

            # Convert datetime to ISO format if needed
            if isinstance(time_min, datetime):
                time_min = time_min.isoformat() + "Z"
            if isinstance(time_max, datetime):
                time_max = time_max.isoformat() + "Z"

            events = []
            page_token = None

            while True:
                result = (
                    self.service.events()
                    .list(
                        calendarId=calendar_id,
                        timeMin=time_min,
                        timeMax=time_max,
                        maxResults=max_results,
                        singleEvents=single_events,
                        orderBy=order_by,
                        q=q,
                        pageToken=page_token,
                    )
                    .execute()
                )

                events.extend(result.get("items", []))
                page_token = result.get("nextPageToken")

                if not page_token:
                    break

            self.logger.info(f"Successfully fetched {len(events)} events")
            return events

        except HttpError as e:
            self.logger.error(f"HTTP error listing events: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to list events: {e}")
            raise

    def update_event(
        self, event_id: str, updates: dict[str, Any], calendar_id: str = "primary"
    ) -> dict[str, Any]:
        """
        Update an existing event.

        Args:
            event_id: Event ID
            updates: Dictionary of fields to update
            calendar_id: Calendar ID (default: "primary")

        Returns:
            Updated event dictionary
        """
        try:
            self.logger.info(f"Updating event: {event_id}")

            updated_event = (
                self.service.events()
                .patch(calendarId=calendar_id, eventId=event_id, body=updates)
                .execute()
            )

            self.logger.info(f"Successfully updated event: {event_id}")
            return updated_event

        except HttpError as e:
            self.logger.error(f"HTTP error updating event {event_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to update event {event_id}: {e}")
            raise

    def delete_event(
        self, event_id: str, calendar_id: str = "primary", send_updates: str = "all"
    ) -> bool:
        """
        Delete an event.

        Args:
            event_id: Event ID
            calendar_id: Calendar ID (default: "primary")
            send_updates: Whether to send updates to attendees ("all", "none", "externalOnly")

        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Deleting event: {event_id}")

            self.service.events().delete(
                calendarId=calendar_id, eventId=event_id, sendUpdates=send_updates
            ).execute()

            self.logger.info(f"Successfully deleted event: {event_id}")
            return True

        except HttpError as e:
            self.logger.error(f"HTTP error deleting event {event_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete event {event_id}: {e}")
            raise

    def create_calendar(
        self,
        summary: str,
        description: str | None = None,
        location: str | None = None,
        time_zone: str = "UTC",
    ) -> dict[str, Any]:
        """
        Create a new calendar.

        Args:
            summary: Calendar name
            description: Calendar description
            location: Calendar location
            time_zone: Calendar timezone

        Returns:
            Created calendar dictionary
        """
        try:
            self.logger.info(f"Creating calendar: {summary}")

            calendar = {"summary": summary, "timeZone": time_zone}

            if description:
                calendar["description"] = description
            if location:
                calendar["location"] = location

            created_calendar = self.service.calendars().insert(body=calendar).execute()

            self.logger.info(
                f"Successfully created calendar: {created_calendar.get('id')}"
            )
            return created_calendar

        except HttpError as e:
            self.logger.error(f"HTTP error creating calendar: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create calendar: {e}")
            raise

    def delete_calendar(self, calendar_id: str) -> bool:
        """
        Delete a calendar.

        Args:
            calendar_id: Calendar ID

        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Deleting calendar: {calendar_id}")

            self.service.calendars().delete(calendarId=calendar_id).execute()

            self.logger.info(f"Successfully deleted calendar: {calendar_id}")
            return True

        except HttpError as e:
            self.logger.error(f"HTTP error deleting calendar {calendar_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete calendar {calendar_id}: {e}")
            raise

    def get_free_busy(
        self,
        time_min: str | datetime,
        time_max: str | datetime,
        items: list[dict[str, str]],
    ) -> dict[str, Any]:
        """
        Get free/busy information for calendars.

        Args:
            time_min: Start time (ISO string or datetime)
            time_max: End time (ISO string or datetime)
            items: List of calendar items to check

        Returns:
            Free/busy information dictionary
        """
        try:
            self.logger.info("Fetching free/busy information")

            # Convert datetime to ISO format if needed
            if isinstance(time_min, datetime):
                time_min = time_min.isoformat() + "Z"
            if isinstance(time_max, datetime):
                time_max = time_max.isoformat() + "Z"

            body = {"timeMin": time_min, "timeMax": time_max, "items": items}

            free_busy = self.service.freebusy().query(body=body).execute()

            self.logger.info("Successfully fetched free/busy information")
            return free_busy

        except HttpError as e:
            self.logger.error(f"HTTP error getting free/busy: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to get free/busy: {e}")
            raise

    def add_attendee(
        self, event_id: str, email: str, calendar_id: str = "primary"
    ) -> dict[str, Any]:
        """
        Add an attendee to an event.

        Args:
            event_id: Event ID
            email: Attendee email address
            calendar_id: Calendar ID (default: "primary")

        Returns:
            Updated event dictionary
        """
        try:
            self.logger.info(f"Adding attendee {email} to event {event_id}")

            # Get current event
            event = self.get_event(event_id, calendar_id)

            # Add new attendee
            if "attendees" not in event:
                event["attendees"] = []

            # Check if attendee already exists
            existing_emails = [a.get("email") for a in event["attendees"]]
            if email not in existing_emails:
                event["attendees"].append({"email": email})

                # Update the event
                updated_event = self.update_event(event_id, event, calendar_id)
                self.logger.info(f"Successfully added attendee {email}")
                return updated_event
            else:
                self.logger.info(f"Attendee {email} already exists in event")
                return event

        except Exception as e:
            self.logger.error(f"Failed to add attendee {email}: {e}")
            raise

    def remove_attendee(
        self, event_id: str, email: str, calendar_id: str = "primary"
    ) -> dict[str, Any]:
        """
        Remove an attendee from an event.

        Args:
            event_id: Event ID
            email: Attendee email address
            calendar_id: Calendar ID (default: "primary")

        Returns:
            Updated event dictionary
        """
        try:
            self.logger.info(f"Removing attendee {email} from event {event_id}")

            # Get current event
            event = self.get_event(event_id, calendar_id)

            if "attendees" in event:
                # Remove attendee
                event["attendees"] = [
                    a for a in event["attendees"] if a.get("email") != email
                ]

                # Update the event
                updated_event = self.update_event(event_id, event, calendar_id)
                self.logger.info(f"Successfully removed attendee {email}")
                return updated_event
            else:
                self.logger.info("No attendees found in event")
                return event

        except Exception as e:
            self.logger.error(f"Failed to remove attendee {email}: {e}")
            raise
