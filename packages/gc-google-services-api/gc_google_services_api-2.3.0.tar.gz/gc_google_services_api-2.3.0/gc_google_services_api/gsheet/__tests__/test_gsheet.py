import unittest
from unittest.mock import Mock, patch

from gc_google_services_api.gsheet import API_NAME, API_VERSION, GSheet


class TestSuite(unittest.TestCase):
    def _create_discovery_mock(self, discovery):
        service_mock = Mock()
        values_mock = Mock()
        get_mock = Mock()
        execute_mock = Mock()

        execute_mock.execute.return_value = "RESULT"
        get_mock.get.return_value = execute_mock
        values_mock.values.return_value = get_mock
        values_mock.get.return_value = execute_mock

        service_mock.spreadsheets.return_value = values_mock

        discovery.build.return_value = service_mock

        return discovery

    def _create_service_account_mock(self, service_account):
        with_subject_mock = Mock()
        with_subject_mock.with_subject.return_value = "CREDENTIALS_TEST"
        service_account.Credentials.from_service_account_info.return_value = (
            with_subject_mock  # noqa: E501
        )

        return service_account

    @patch("gc_google_services_api.gsheet.discovery")
    @patch("gc_google_services_api.auth.service_account")
    def test_read_gsheet_should_call_google_api_with_credentials_and_correct_params(  # noqa: E501
        self, service_account, discovery
    ):
        discovery = self._create_discovery_mock(discovery)
        service_account = self._create_service_account_mock(service_account)

        expected_result = "RESULT"
        credentials = "CREDENTIALS_TEST"
        sheet_name = "SHEET_NAME_TEST"
        spreadsheet_id = "SPREADSHEET_ID_TEST"
        spreadsheet_range = "SPREADSHEET_RANGE_TEST"
        subject_email = "TEST_SUBJECT_EMAIL"

        response = GSheet(subject_email).read_gsheet(
            sheet_name, spreadsheet_id, spreadsheet_range
        )

        self.assertEqual(response, expected_result)

        service_account.Credentials.from_service_account_info.assert_called_once_with(  # noqa: E501
            "", scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )

        discovery.build.assert_called_once_with(
            API_NAME, API_VERSION, credentials=credentials
        )

        discovery.build().spreadsheets().values().get.assert_called_once_with(
            spreadsheetId=spreadsheet_id,
            range="SHEET_NAME_TEST!SPREADSHEET_RANGE_TEST",
        )

        discovery.build().spreadsheets().values().get().execute.assert_called_once()  # noqa: E501

    @patch("gc_google_services_api.gsheet.discovery")
    @patch("gc_google_services_api.auth.service_account")
    def test_get_sheetnames_should_call_google_api_with_credentials_and_correct_params(  # noqa: E501
        self, service_account, discovery
    ):
        discovery = self._create_discovery_mock(discovery)
        service_account = self._create_service_account_mock(service_account)

        expected_result = "RESULT"
        credentials = "CREDENTIALS_TEST"
        spreadsheet_id = "SPREADSHEET_ID_TEST"
        subject_email = "TEST_SUBJECT_EMAIL"

        response = GSheet(subject_email).get_sheetnames(spreadsheet_id)

        self.assertEqual(response, expected_result)

        service_account.Credentials.from_service_account_info.assert_called_once_with(  # noqa: E501
            "", scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )

        discovery.build.assert_called_once_with(
            API_NAME, API_VERSION, credentials=credentials
        )

        discovery.build().spreadsheets().get.assert_called_once_with(
            spreadsheetId=spreadsheet_id
        )

        discovery.build().spreadsheets().get().execute.assert_called_once()
