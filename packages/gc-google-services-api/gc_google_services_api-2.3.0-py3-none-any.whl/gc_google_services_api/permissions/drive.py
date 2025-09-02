import logging
import time

from googleapiclient.discovery import build

from gc_google_services_api.auth import Auth

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
EMPTY_ARRAY = []


class Drive:
    """
    Google API documentation:
        - https://developers.google.com/drive/api/guides/manage-shareddrives  # noqa: E501
    """

    def __init__(self, subject_email) -> None:
        self.credentials = Auth(SCOPES, subject_email).get_credentials()
        self.service = build("drive", "v3", credentials=self.credentials)
        self.shared_drives = []

    def _add_shared_drive(self, shared_drive):
        self.shared_drives.append(shared_drive)

    def store_drives(self, drives):
        for drive in drives:
            if drive["name"].startswith("AC -"):
                self._add_shared_drive(drive)

    def get_permissions_from_file(self, file_id):
        results = (
            self.service.permissions()
            .list(
                fileId=file_id,
                useDomainAdminAccess=True,
                supportsAllDrives=True,
                fields="permissions/id,permissions/displayName,permissions/role,permissions/emailAddress",  # noqa: E501
            )
            .execute()
        )

        return results.get("permissions", EMPTY_ARRAY)

    def get_shared_drives(self, next_page_token=None) -> None:
        results = (
            self.service.drives()
            .list(
                fields="nextPageToken, drives(id, name)",
                q=None,
                useDomainAdminAccess=True,
                pageToken=next_page_token,
                pageSize=100,
            )
            .execute()
        )

        drives = results.get("drives", EMPTY_ARRAY)
        self.store_drives(drives)

        next_page_token = results.get("nextPageToken", None)
        if next_page_token:
            logging.info(
                "Requesting shared drives ({})...".format(next_page_token)
            )  # noqa: E501
            self.get_shared_drives(next_page_token)

    def find_email_in_permissions(self, email_to_delete):
        shared_drives = []
        for num, drive in enumerate(self.shared_drives):
            logging.info(
                "Requesting permissions for file {}/{}".format(
                    num + 1, len(self.shared_drives)
                )
            )
            if num > 0 and (num % 25 == 0):
                time.sleep(2)

            permissions = self.get_permissions_from_file(drive["id"])
            for permission in permissions:
                if permission["emailAddress"] == email_to_delete:
                    shared_drives.append(
                        {
                            "drive_name": drive["name"],
                            "drive_id": drive["id"],
                            "permission_id": permission["id"],
                        }
                    )

        return shared_drives

    def delete_file_permission(self, file_id, permission_id):
        results = (
            self.service.permissions()
            .delete(
                fileId=file_id,
                permissionId=permission_id,
                useDomainAdminAccess=True,
                supportsAllDrives=True,
            )
            .execute()
        )

        return results
