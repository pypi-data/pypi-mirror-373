import unittest
from unittest.mock import Mock, patch

from gc_google_services_api.gmail import Gmail


class TestSuite(unittest.TestCase):
    def _create_build_mock(self, build):
        build_service = Mock()
        users = Mock()
        messages = Mock()
        execute = Mock()

        execute.execute.return_value = "execute"

        messages.send.return_value = execute

        users.messages.return_value = messages

        build_service.users.return_value = users

        build.return_value = build_service

        return build

    def _create_service_account_mock(self, service_account):
        with_subject_mock = Mock()
        with_subject_mock.with_subject.return_value = "CREDENTIALS_TEST"
        service_account.Credentials.from_service_account_info.return_value = (
            with_subject_mock  # noqa: E501
        )

        return service_account

    @patch("gc_google_services_api.gmail.build")
    @patch("gc_google_services_api.auth.service_account")
    def test_gmail_call_auth_when_instance_is_created(
        self, service_account, build
    ):  # noqa: E501
        self._create_build_mock(build)
        service_account = self._create_service_account_mock(service_account)
        subject_email = "TEST_SUBJECT_EMAIL"

        Gmail(subject_email)

        service_account.Credentials.from_service_account_info.assert_called_once_with(  # noqa: E501
            "", scopes=["https://www.googleapis.com/auth/gmail.send"]
        )
        build.assert_called_once_with(
            "gmail",
            "v1",
            credentials="CREDENTIALS_TEST",
        )

    @patch("gc_google_services_api.gmail.build")
    @patch("gc_google_services_api.auth.service_account")
    def test_gmail_call_send_email_service_whith_all_content(
        self, service_account, build
    ):  # noqa: E501
        build = self._create_build_mock(build)
        service_account = self._create_service_account_mock(service_account)
        subject_email = "TEST_SUBJECT_EMAIL@test.com"

        response = Gmail(subject_email).send_email(
            email_message="test message",
            email_subject="test@test.com",
            from_email="fromtest@test.com",
            to="totest@test.com",
        )

        service_account.Credentials.from_service_account_info.assert_called_once_with(  # noqa: E501
            "", scopes=["https://www.googleapis.com/auth/gmail.send"]
        )

        build().users().messages().send.assert_called_once_with(
            userId="me",
            body={
                "raw": "Q29udGVudC1UeXBlOiB0ZXh0L3BsYWluOyBjaGFyc2V0PSJ1dGYtOCIKQ29udGVudC1UcmFuc2Zlci1FbmNvZGluZzogN2JpdApNSU1FLVZlcnNpb246IDEuMAp0bzogdG90ZXN0QHRlc3QuY29tCmZyb206IGZyb210ZXN0QHRlc3QuY29tCnN1YmplY3Q6IHRlc3RAdGVzdC5jb20KCnRlc3QgbWVzc2FnZQo="  # noqa: E501
            },
        )
        build().users().messages().send().execute.assert_called_once_with()

        self.assertEqual(response, "execute")
