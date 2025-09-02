import unittest
from unittest.mock import Mock, patch

from gc_google_services_api.auth import Auth


class AuthTestSuite(unittest.TestCase):
    def _create_service_account_mock(self, service_account):
        from_service_account_info_mock = Mock()
        from_service_account_info_mock.from_service_account_info.return_value = (  # noqa: E501
            "CREDENTIALS"
        )

        service_account.Credentials = from_service_account_info_mock

        return service_account

    def _create_service_account_with_subject_mock(self, service_account):
        with_subject_mock = Mock()
        with_subject_mock.with_subject.return_value = (
            "CREDENTIALS_WITH_SUBJECT"  # noqa: E501
        )
        from_service_account_info_mock = Mock()
        from_service_account_info_mock.from_service_account_info.return_value = (  # noqa: E501
            with_subject_mock
        )

        service_account.Credentials = from_service_account_info_mock

        return service_account

    @patch("gc_google_services_api.auth.service_account")
    # @patch.dict(os.environ, {'GOOGLE_SERVICE_ACCOUNT_CREDENTIALS': '213'})
    def test_auth_set_google_credentials_with_scopes(self, service_account):
        service_account = self._create_service_account_mock(service_account)
        expected_result = "CREDENTIALS"
        scopes = ["scope1", "scope2"]
        response = Auth(scopes).get_credentials()

        self.assertEqual(response, expected_result)
        service_account.Credentials.from_service_account_info.assert_called_once_with(  # noqa: E501
            "", scopes=scopes
        )

    @patch("gc_google_services_api.auth.service_account")
    # @patch.dict(os.environ, {'GOOGLE_SERVICE_ACCOUNT_CREDENTIALS': '213'})
    def test_auth_set_google_credentials_with_subject(self, service_account):
        service_account = self._create_service_account_with_subject_mock(
            service_account
        )

        expected_result = "CREDENTIALS_WITH_SUBJECT"
        scopes = ["scope1", "scope2"]
        subject_email = "subject@email.com"
        response = Auth(scopes, subject_email).get_credentials()

        self.assertEqual(response, expected_result)
