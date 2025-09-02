import json
import unittest
from unittest.mock import Mock, patch

from gc_google_services_api.pubsub import PubSub

UUID_TEST = "84790aab-465c-4d91-808f-e8d6bfad6198"


def create_pubsub_mock(mock_pubsub_v1):
    publisher_mock = Mock()
    publisher_mock.topic_path.return_value = "TEST_TOPIC_RESPONSE"
    publisher_mock.publish.return_value = True

    subscriber_mock = Mock()
    subscriber_mock.subscription_path.return_value = "TEST_SUBSCRIPTION_PATH"
    subscriber_mock.pull.side_effect = [
        Mock(
            received_messages=[
                Mock(
                    ack_id="1",
                    message=Mock(
                        data=json.dumps(
                            {
                                "projects": {"key": "value"},
                                "id": UUID_TEST,
                            }
                        ).encode("utf-8")
                    ),
                )
            ]
        ),
        Mock(received_messages=[]),
    ]

    mock_pubsub_v1.PublisherClient.from_service_account_info.return_value = (
        publisher_mock
    )

    mock_pubsub_v1.SubscriberClient.from_service_account_info.return_value = (
        subscriber_mock
    )

    return mock_pubsub_v1


def uuid_mock():
    uuid_mock = Mock()

    uuid_mock.uuid4.return_value = UUID_TEST

    return uuid_mock


class TestPubSub(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.project_name = "project_name"
        self.topic_name = "test_topic"
        self.credentials = "test_credentials"

    @patch("gc_google_services_api.pubsub.uuid", new=uuid_mock())
    @patch("gc_google_services_api.pubsub.pubsub_v1")
    def test_send_message_execute_publish_method_from_pubsub(
        self,
        mock_pubsub_v1,
    ):
        mock_pubsub_v1 = create_pubsub_mock(mock_pubsub_v1)
        data = {"key": "value"}
        pubsub_instance = PubSub(self.credentials, self.project_name)

        # Assert
        mock_pubsub_v1.PublisherClient.from_service_account_info.assert_called_once_with(  # noqa: E501
            info=self.credentials,
        )

        # Running send message
        pubsub_instance.send_message(self.topic_name, data)

        # Asserts
        expected_topic_path = "TEST_TOPIC_RESPONSE"
        expected_data = {"data": data, "id": UUID_TEST}

        mock_pubsub_v1.PublisherClient.from_service_account_info().topic_path.assert_called_once_with(  # noqa: E501
            self.project_name,
            self.topic_name,
        )

        mock_pubsub_v1.PublisherClient.from_service_account_info().publish.assert_called_once_with(  # noqa: E501
            expected_topic_path,
            json.dumps(expected_data).encode("utf-8"),
        )

    @patch("gc_google_services_api.pubsub.uuid", new=uuid_mock())
    @patch("gc_google_services_api.pubsub.pubsub_v1")
    @patch("gc_google_services_api.pubsub.logging")
    def test_terminate_message_execute_acknowledge_method_from_subscriber(
        self,
        mock_logging,
        mock_pubsub_v1,
    ):
        mock_pubsub_v1 = create_pubsub_mock(mock_pubsub_v1)
        ack_id = "1"
        message_id = "2"
        subscription_path = "SUBSCRIPTION_PATH_TEST"
        pubsub_instance = PubSub(self.credentials, self.project_name)

        # Assert
        mock_pubsub_v1.SubscriberClient.from_service_account_info.assert_called_once_with(  # noqa: E501
            info=self.credentials,
        )

        # Running send message
        pubsub_instance.terminate_message(
            ack_id=ack_id,
            message_id=message_id,
            subscription_path=subscription_path,
        )

        # Asserts
        mock_pubsub_v1.SubscriberClient.from_service_account_info().acknowledge.assert_called_once_with(  # noqa: E501
            subscription=subscription_path, ack_ids=[ack_id]
        )
        mock_logging.info.assert_called_once_with(
            f"Terminating message: {message_id}"
        )  # noqa: E501

    @patch("gc_google_services_api.pubsub.uuid", new=uuid_mock())
    @patch("gc_google_services_api.pubsub.pubsub_v1")
    def test_subscribe_topic_receives_and_processes_messages(
        self,
        mock_pubsub_v1,
    ):
        mock_pubsub_v1 = create_pubsub_mock(mock_pubsub_v1)
        callback_mock = Mock()

        pubsub_instance = PubSub(self.credentials, self.project_name)

        pubsub_instance.subscribe_topic(
            self.topic_name,
            callback=callback_mock,
            max_simultaneous_messages=1,
            time_to_wait_between_messages=0,
            default_timeout_for_any_message=1,
        )

        mock_pubsub_v1.SubscriberClient.from_service_account_info.assert_called_once_with(  # noqa: E501
            info=self.credentials,
        )

        mock_pubsub_v1.SubscriberClient.from_service_account_info().subscription_path.assert_called_once_with(  # noqa: E501
            self.project_name,
            f"{self.topic_name}-sub",
        )

        mock_pubsub_v1.SubscriberClient.from_service_account_info().pull.assert_called_with(  # noqa: E501
            request=mock_pubsub_v1.types.PullRequest(
                subscription="TEST_SUBSCRIPTION_PATH",
                max_messages=1,
            ),
            timeout=1,
        )

        callback_mock.assert_called_once_with(
            json.dumps(
                {
                    "projects": {"key": "value"},
                    "id": UUID_TEST,
                }
            ).encode("utf-8")
        )
