import logging

from googleapiclient.discovery import build

from gc_google_services_api.auth import Auth

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.group",
    "https://www.googleapis.com/auth/admin.directory.user",
    "https://www.googleapis.com/auth/admin.directory.rolemanagement",
]
EMPTY_ARRAY = []


class WorkSpace:
    """
    Google API documentation:
        - https://developers.google.com/resources/api-libraries/documentation/admin/directory_v1/python/latest/admin_directory_v1.groups.html # noqa: E501
        - https://googleapis.github.io/google-api-python-client/docs/dyn/admin_directory_v1.users.html
    """

    def __init__(self, subject_email, domain) -> None:
        self.domain = domain
        self.credentials = Auth(SCOPES, subject_email).get_credentials()
        self.service = build(
            "admin",
            "directory_v1",
            credentials=self.credentials,
        )
        self.groups_to_delete = []

    def _add_groups(self, group):
        self.groups_to_delete.append(group)

    def store_groups(self, groups):
        for group in groups:
            self._add_groups(group)

    def get_groups_by_email(self, email, next_page_token=None):
        results = (
            self.service.groups()
            .list(
                domain=self.domain,
                maxResults=200,
                pageToken=next_page_token,
                userKey=email,
            )
            .execute()
        )

        groups = results.get("groups", EMPTY_ARRAY)
        self.store_groups(groups)

        next_page_token = results.get("nextPageToken", None)
        if next_page_token:
            logging.info("Requesting groups ({})...".format(next_page_token))
            self.get_groups_by_email(email, next_page_token)

    def get_all_groups(self, next_page_token=None):
        # TODO: Almacenar en una variable todos los grupos
        results = (
            self.service.groups()
            .list(
                domain=self.domain,
                maxResults=200,
                pageToken=next_page_token,
            )
            .execute()
        )

        groups = results.get("groups", EMPTY_ARRAY)
        self.store_groups(groups)

        next_page_token = results.get("nextPageToken", None)
        if next_page_token:
            logging.info("Requesting groups ({})...".format(next_page_token))
            self.get_all_groups(next_page_token)

    def get_members_from_group(self, group_key):
        results = self.service.members().list(groupKey=group_key).execute()

        return results.get("members", EMPTY_ARRAY)

    def delete_group_permission(self, group_id, email_to_delete):
        results = (
            self.service.members()
            .delete(
                groupKey=group_id,
                memberKey=email_to_delete,
            )
            .execute()
        )

        return results

    def find_groups_permission_to_delete(self, groups, email_to_delete):
        group_permissions_to_delete = []
        for group in groups:
            group_members = self.get_members_from_group(group["id"])

            for member in group_members:
                if member["email"] == email_to_delete:
                    group_permissions_to_delete.append(
                        {
                            "group_name": group["name"],
                            "group_id": group["id"],
                        }
                    )
                    break

        return group_permissions_to_delete
