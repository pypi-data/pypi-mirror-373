import json
import logging
import time
import uuid
from typing import Callable

from google.cloud import pubsub_v1

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class PubSub:
    def __init__(self, credentials: str, project_name: str):
        self.publisher = pubsub_v1.PublisherClient.from_service_account_info(
            info=credentials,
        )
        self.subscriber = pubsub_v1.SubscriberClient.from_service_account_info(
            info=credentials,
        )
        self.project_name = project_name

    def send_message(self, topic_name: str, data: dict):
        topic_path = self.publisher.topic_path(self.project_name, topic_name)

        self.publisher.publish(
            topic_path,
            json.dumps(
                {
                    "data": data,
                    "id": str(uuid.uuid4()),
                }
            ).encode("utf-8"),
        )

    def terminate_message(
        self,
        ack_id: str,
        message_id: str,
        subscription_path,
    ):
        logging.info(f"Terminating message: {message_id}")
        self.subscriber.acknowledge(
            subscription=subscription_path,
            ack_ids=[ack_id],
        )

    def subscribe_topic(
        self,
        topic_name: str,
        callback: Callable[[], str],
        max_simultaneous_messages: int = 1,
        time_to_wait_between_messages: int = 10,
        default_timeout_for_any_message: int = 6 * 60,
    ):
        subscription_path = self.subscriber.subscription_path(
            self.project_name,
            f"{topic_name}-sub",
        )

        request = pubsub_v1.types.PullRequest(
            subscription=subscription_path,
            max_messages=max_simultaneous_messages,
        )

        while True:
            try:
                response = self.subscriber.pull(
                    request=request,
                    timeout=default_timeout_for_any_message,
                )

                if not response.received_messages:
                    logging.error(
                        "Closing the subscription to the topic due to lack of messages"  # noqa: E501
                    )
                    break
                else:
                    for received_message in response.received_messages:
                        message_id = received_message.ack_id
                        message_data = received_message.message.data

                        message_data_json = json.loads(message_data)
                        batch_message_id = message_data_json["id"]

                        # Processing projects
                        callback(message_data)

                        logging.info(
                            f"Message ({batch_message_id}) processed."
                        )  # noqa: E501
                        time.sleep(time_to_wait_between_messages)
                        self.terminate_message(
                            ack_id=message_id,
                            message_id=batch_message_id,
                            subscription_path=subscription_path,
                        )
            except Exception as e:
                import traceback

                traceback.print_exc()

                logging.error(f"Error processing project with error: {e}")
