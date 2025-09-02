import logging
from urllib.error import HTTPError

from apiclient import discovery

from gc_google_services_api.auth import Auth

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

API_NAME = "sheets"
API_VERSION = "v4"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class GSheet(object):
    def __init__(self, subject_email=None) -> None:
        self.credentials = Auth(SCOPES, subject_email).get_credentials()
        self.service = discovery.build(
            API_NAME, API_VERSION, credentials=self.credentials
        )

    def read_gsheet(self, sheet_name, spreadsheet_id, spreadsheet_range):
        return (
            self.service.spreadsheets()
            .values()
            .get(
                spreadsheetId=spreadsheet_id,
                range="{}!{}".format(sheet_name, spreadsheet_range),
            )
            .execute()
        )

    def get_sheetnames(self, spreadsheet_id):
        return (
            self.service.spreadsheets()
            .get(
                spreadsheetId=spreadsheet_id,
            )
            .execute()
        )

    def create_spreadsheet(self, spreadsheet_body):
        try:
            spreadsheet = (
                self.service.spreadsheets()
                .create(body=spreadsheet_body, fields="spreadsheetId")
                .execute()
            )

            return spreadsheet.get("spreadsheetId")
        except HTTPError as error:
            logging.error(f"An error occurred: {error}")

            return error

    def write_in_spreadsheet(self, spreadsheet_id, range_name, body):
        try:
            results = (
                self.service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )

            return results
        except HTTPError as error:
            logging.error(f"An error occurred: {error}")

            return error
