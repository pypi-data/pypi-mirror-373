import base64
import logging
from email.message import EmailMessage
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from gc_google_services_api.auth import Auth

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
]


class Gmail:
    def __init__(self, subject_email, type="raw") -> None:
        self.message_type = type
        self.credentials = Auth(SCOPES, subject_email).get_credentials()
        self.service = build("gmail", "v1", credentials=self.credentials)

    def send_email(self, email_message, email_subject, from_email, to=[]):
        def _create_message():
            if self.message_type == "raw":
                message = EmailMessage()

                message.set_content(email_message)
            else:
                message = MIMEText(email_message, "html")

            message["to"] = to
            message["from"] = from_email
            message["subject"] = email_subject

            return message

        try:
            message = _create_message()

            # encoded message
            encoded_message = base64.urlsafe_b64encode(
                message.as_bytes(),
            ).decode()

            create_message = {"raw": encoded_message}
            send_message = (
                self.service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
        except HttpError as error:
            logging.error(f"An error occurred: {error}")
            send_message = None

        return send_message
