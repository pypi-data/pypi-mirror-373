import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, call, patch

from gc_google_services_api.calendar_api import Calendar


class TestSuite(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.start_date = datetime.today()
        self.end_date = datetime.today() + timedelta(days=1)
        self.filterByCreator = "test@test.com"

    def _create_Auth_mock(self, Auth):
        auth_mock = Mock()
        auth_mock.get_credentials.return_value = "CREDENTIALS"

        Auth.return_value = auth_mock

        return Auth

    def _create_build_mock(self, build, items_value=[], event_items=[]):
        # Directory mock
        service = Mock()
        resources = Mock()
        calendars = Mock()
        list = Mock()

        list.execute.return_value = {"items": items_value}
        calendars.list.return_value = list
        resources.calendars.return_value = calendars
        service.resources.return_value = resources
        # End Directory mock
        # Calendar mock
        calendarList = Mock()
        calendarListMethod = Mock()
        events = Mock()
        events_list = Mock()
        delete = Mock()
        delete.execute.return_value = "DELETED"
        events_list.execute.return_value = {"items": event_items}
        events.list.return_value = events_list
        events.delete.return_value = delete
        calendarListMethod.execute.return_value = {"items": items_value}
        calendarList.list.return_value = calendarListMethod
        service.calendarList.return_value = calendarList
        service.events.return_value = events
        # EndCalendar mock

        build.return_value = service

        return build

    @patch("gc_google_services_api.calendar_api.Auth")
    @patch("gc_google_services_api.calendar_api.build")
    def test_calendar_constructor_should_initialize_authentication(
        self, build, Auth
    ):  # noqa: E501
        Auth = self._create_Auth_mock(Auth)
        build = self._create_build_mock(build)

        Calendar(self.start_date, self.end_date, self.filterByCreator)

        Auth.assert_has_calls(
            [
                call(
                    [
                        "https://www.googleapis.com/auth/calendar.readonly",
                        "https://www.googleapis.com/auth/calendar.events",
                    ],
                    "",
                )
            ],
            [
                call(
                    [
                        "https://www.googleapis.com/auth/admin.directory.resource.calendar",  # noqa: E501
                    ],
                    "",
                )
            ],
        )

        build.assert_has_calls(
            [call("calendar", "v3", credentials="CREDENTIALS")],
            [call("admin", "directory_v1", credentials="CREDENTIALS")],
        )

    @patch("gc_google_services_api.calendar_api.Auth")
    @patch("gc_google_services_api.calendar_api.build")
    def test_get_all_resources_should_return_items_response(
        self, build, Auth
    ):  # noqa: E501
        Auth = self._create_Auth_mock(Auth)
        build = self._create_build_mock(build)

        calendar_instance = Calendar(
            self.start_date, self.end_date, self.filterByCreator
        )
        resources = calendar_instance.get_all_resources()

        self.assertEqual(resources, [])

    @patch("gc_google_services_api.calendar_api.Auth")
    @patch("gc_google_services_api.calendar_api.build")
    def test_request_calendars_should_save_all_calendars(
        self, build, Auth
    ):  # noqa: E501
        Auth = self._create_Auth_mock(Auth)
        build = self._create_build_mock(build, [1, 2])

        calendar_instance = Calendar(
            self.start_date, self.end_date, self.filterByCreator
        )
        calendar_instance.request_calendars()

        self.assertEqual(calendar_instance.calendars, [1, 2])

        build().calendarList().list.assert_called_once_with(
            pageToken=None, showDeleted=False, showHidden=True
        )

    @patch("gc_google_services_api.calendar_api.Auth")
    @patch("gc_google_services_api.calendar_api.build")
    def test_request_calendar_events_should_request_events_with_correct_params(
        self, build, Auth
    ):  # noqa: E501
        Auth = self._create_Auth_mock(Auth)
        build = self._create_build_mock(build, [1, 2])

        calendar_instance = Calendar(
            self.start_date, self.end_date, self.filterByCreator
        )
        calendar_instance.request_calendar_events("1")

        self.assertEqual(calendar_instance.calendar_events, {})

        build().events().list.assert_called_once_with(
            calendarId="1",
            pageToken=None,
            showDeleted=False,
            timeMin=self.start_date.strftime("%Y-%m-%dT00:00:00+01:00"),
        )

    @patch("gc_google_services_api.calendar_api.Auth")
    @patch("gc_google_services_api.calendar_api.build")
    def test_request_calendar_events_should_filter_events_by_creator_and_dates(  # noqa: E501
        self, build, Auth
    ):  # noqa: E501
        Auth = self._create_Auth_mock(Auth)
        events_fixtures = [
            {
                "status": "confirmed",
                "creator": {"email": "test@test.com"},
                "end": {
                    "dateTime": self.start_date.strftime(
                        "%Y-%m-%dT10:00:00+01:00"
                    )  # noqa: E501
                },  # noqa: E501
            },
            {
                "status": "confirmed",
                "creator": {"email": "test@test.com"},
                "end": {
                    "dateTime": self.end_date.strftime(
                        "2054-%m-%dT10:00:00+01:00"
                    )  # noqa: E501
                },  # noqa: E501
            },
            {
                "status": "cancelled",
                "creator": {"email": "test@test.com"},
                "end": {
                    "dateTime": self.start_date.strftime(
                        "%Y-%m-%dT10:00:00+01:00"
                    )  # noqa: E501
                },  # noqa: E501
            },
            {
                "status": "confirmed",
                "creator": {"email": "other@test.com"},
                "end": {
                    "dateTime": self.start_date.strftime(
                        "%Y-%m-%dT10:00:00+01:00"
                    )  # noqa: E501
                },  # noqa: E501
            },
        ]
        build = self._create_build_mock(build, [1, 2], events_fixtures)

        calendar_instance = Calendar(
            self.start_date, self.end_date, self.filterByCreator
        )
        calendar_instance.request_calendar_events("1")

        self.assertDictEqual(
            calendar_instance.calendar_events,
            {
                "1": [
                    {
                        "status": "confirmed",
                        "creator": {"email": "test@test.com"},
                        "end": {
                            "dateTime": self.start_date.strftime(
                                "%Y-%m-%dT10:00:00+01:00"
                            )
                        },  # noqa: E501
                    }
                ]
            },
        )

    @patch("gc_google_services_api.calendar_api.Auth")
    @patch("gc_google_services_api.calendar_api.build")
    def test_remove_event_should_call_api_with_correct_params(
        self, build, Auth
    ):  # noqa: E501
        Auth = self._create_Auth_mock(Auth)
        build = self._create_build_mock(build)

        calendar_instance = Calendar(
            self.start_date, self.end_date, self.filterByCreator
        )
        response = calendar_instance.remove_event("1", "2")

        self.assertEqual(response, "DELETED")
        build().events().delete.assert_called_once_with(
            calendarId="1",
            eventId="2",
        )
