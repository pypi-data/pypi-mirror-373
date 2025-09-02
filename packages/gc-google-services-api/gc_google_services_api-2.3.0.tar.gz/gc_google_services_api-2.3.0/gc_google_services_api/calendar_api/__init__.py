import os
from datetime import datetime

from googleapiclient.discovery import build

from gc_google_services_api.auth import Auth

DEFAULT_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S+01:00"
DEFAULT_MIN_DATE_TIME_FORMAT = "%Y-%m-%dT00:00:00+01:00"
DEFAULT_MAX_DATE_TIME_FORMAT = "%Y-%m-%dT23:59:59+01:00"
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]
SCOPES_DIRECTORY = [
    "https://www.googleapis.com/auth/admin.directory.resource.calendar"
]  # noqa: E501
AUTHENTICATION_EMAIL = os.getenv("AUTHENTICATION_EMAIL", "")


class Calendar:
    def __init__(self, minDate=None, maxDate=None, filterByCreator=None):
        self.minDate = minDate
        self.maxDate = maxDate
        self.filterByCreator = filterByCreator
        self.resources = []
        self.calendars = []
        self.calendar_events = {}

        self._initialize_authentication()

    def _initialize_authentication(self):
        self.credentials = Auth(SCOPES, AUTHENTICATION_EMAIL).get_credentials()
        self.credentials_directory = Auth(
            SCOPES_DIRECTORY, AUTHENTICATION_EMAIL
        ).get_credentials()

        self.service_calendar = build(
            "calendar",
            "v3",
            credentials=self.credentials,
        )
        self.service_directory = build(
            "admin", "directory_v1", credentials=self.credentials_directory
        )

    def get_all_resources(self):
        result = (
            self.service_directory.resources()
            .calendars()
            .list(customer="my_customer")
            .execute()
        )

        return result["items"]

    def request_calendars(self, pageToken=None):
        result = (
            self.service_calendar.calendarList()
            .list(
                pageToken=pageToken,
                showDeleted=False,
                showHidden=True,
            )
            .execute()
        )

        self.calendars.extend(result["items"])
        nextPageToken = result.get("nextPageToken", None)
        if nextPageToken:
            self.request_calendars(pageToken=nextPageToken)

    def request_calendar_events(self, calendar_id, pageToken=None):
        result = (
            self.service_calendar.events()
            .list(
                calendarId=calendar_id,
                pageToken=pageToken,
                showDeleted=False,
                timeMin=self.minDate.strftime(DEFAULT_MIN_DATE_TIME_FORMAT)
                if self.minDate
                else None,
            )
            .execute()
        )

        for event in result["items"]:
            if event["status"] != "cancelled":
                try:
                    if (
                        self.filterByCreator
                        and event["creator"]["email"] == self.filterByCreator
                    ):  # noqa: E501
                        if self.maxDate:
                            event_enddate = datetime.strptime(
                                event["end"]["dateTime"],
                                DEFAULT_DATE_TIME_FORMAT,
                            )
                            max_date = datetime.strptime(
                                self.maxDate.strftime(
                                    DEFAULT_MAX_DATE_TIME_FORMAT
                                ),  # noqa: E501
                                DEFAULT_DATE_TIME_FORMAT,
                            )

                            if event_enddate > max_date:
                                continue

                        if calendar_id not in self.calendar_events:
                            self.calendar_events[calendar_id] = []

                        self.calendar_events[calendar_id].append(event)
                except KeyError:
                    pass

        nextPageToken = result.get("nextPageToken", None)
        if nextPageToken:
            self.request_calendar_events(calendar_id, pageToken=nextPageToken)

    def remove_event(self, calendar_id, event_id):
        return (
            self.service_calendar.events()
            .delete(calendarId=calendar_id, eventId=event_id)
            .execute()
        )
