import base64
import json
import logging
import os

from google.oauth2 import service_account

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


CREDENTIALS_BASE64 = os.environ.get("GOOGLE_SERVICE_ACCOUNT_CREDENTIALS", "")

try:
    CREDENTIALS_CONTENT = json.loads(base64.b64decode(CREDENTIALS_BASE64))
except json.JSONDecodeError as e:
    logging.error("[ERROR CREDENTIALS_CONTENT]: ", e)
    CREDENTIALS_CONTENT = ""


class Auth:
    def __init__(self, scopes, subject_email=None) -> None:
        self.scopes = scopes
        self.subject_email = subject_email

    def get_credentials(self):
        credentials = service_account.Credentials.from_service_account_info(
            CREDENTIALS_CONTENT, scopes=self.scopes
        )

        if self.subject_email:
            credentials = credentials.with_subject(self.subject_email)

        return credentials
