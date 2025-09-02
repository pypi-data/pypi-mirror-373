import logging
import time

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.group",
    "https://www.googleapis.com/auth/admin.directory.user",
    "https://www.googleapis.com/auth/admin.directory.rolemanagement",
]

EMPTY_ARRAY = []
# Members Roles
OWNER_ROLE = "OWNER"
MEMBER_ROLE = "MEMBER"
MANAGER_ROLE = "MANAGER"
MAX_RETRIES = 5
BASE_DELAY = 2.0  # seconds for exponential backoff


class WorkSpace:
    """
    Google API documentation:
        - https://developers.google.com/resources/api-libraries/documentation/admin/directory_v1/python/latest/admin_directory_v1.groups.html # noqa: E501
        - https://googleapis.github.io/google-api-python-client/docs/dyn/admin_directory_v1.users.html
    """

    def __init__(self, credentials, domain) -> None:
        self.domain = domain
        self.service = build(
            "admin",
            "directory_v1",
            credentials=credentials,
        )

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

        next_page_token = results.get("nextPageToken", None)
        if next_page_token:
            logging.info("Requesting groups ({})...".format(next_page_token))
            groups += self.get_groups_by_email(email, next_page_token)

        return groups

    def get_all_groups(self, next_page_token=None):
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

        next_page_token = results.get("nextPageToken", None)
        if next_page_token:
            logging.info("Requesting groups ({})...".format(next_page_token))
            # self.get_all_groups(next_page_token)
            groups += self.get_all_groups(next_page_token)

        return groups

    def get_members_from_group(self, group_key):
        results = self.service.members().list(groupKey=group_key).execute()

        return results.get("members", EMPTY_ARRAY)

    def delete_email_for_group(self, group_id, email_to_delete):
        results = (
            self.service.members()
            .delete(
                groupKey=group_id,
                memberKey=email_to_delete,
            )
            .execute()
        )

        return results

    def add_user_membership(self, group_id, email_to_add, role):
        body = {
            "email": email_to_add,
            "role": role,
        }

        results = (
            self.service.members()
            .insert(
                groupKey=group_id,
                body=body,
            )
            .execute()
        )

        return results

    def find_groups_permission_for_email(self, groups, email_to_find):
        group_permissions_to_delete = []
        for group in groups:
            group_members = self.get_members_from_group(group["id"])

            for member in group_members:
                if member["email"] == email_to_find:
                    group_permissions_to_delete.append(
                        {
                            "group_name": group["name"],
                            "group_id": group["id"],
                        }
                    )
                    break

        return group_permissions_to_delete

    def get_group_by_email(self, project_email):
        try:
            results = (
                self.service.groups()
                .get(
                    groupKey=project_email,
                )
                .execute()
            )
        except HttpError as e:
            logging.error(
                f"[ERROR - Workspace:get_group_by_email]: Cannot get group by email: {e}"  # noqa: E501
            )
            results = None

        return results

    def create_group(
        self,
        group_email: str,
        group_members: list,
        group_admin_members: list,
        group_name=None,
    ):
        logging.info(
            f"Creating group {group_email} with {len(group_members)} members"
        )
        response = None
        try:
            results = (
                self.service.groups()
                .insert(
                    body={
                        "name": group_name if group_name else group_email,
                        "email": group_email,
                    },
                )
                .execute()
            )
        except HttpError as e:
            logging.error(
                f"[ERROR - Workspace:create_group]: Cannot create group: {e}"  # noqa: E501
            )
            results = None
        else:
            if isinstance(results, dict) and results.get("id", None):
                logging.info(f"Registering {group_email} members...")
                admin_member_results = self.add_group_members(
                    group_id=results["id"],
                    members=group_admin_members,
                    role=MANAGER_ROLE,
                )
                # We need to wait a few seconds to continue doing
                # request to Google API.
                time.sleep(5)
                member_results = self.add_group_members(
                    group_id=results["id"],
                    members=group_members,
                    role=MEMBER_ROLE,
                )
                response = {
                    "group_info": results,
                    "permissions": member_results + admin_member_results,
                }
            else:
                logging.error(
                    f"Cannot add members for group {group_email} with results: {results}"  # noqa: E501
                )

        return response

    def add_group_members(self, group_id: str, members: list, role: str):
        members_data = []
        failed_members = []

        for member in members:
            success = False
            retries = 0

            while not success and retries < MAX_RETRIES:
                try:
                    result = (
                        self.service.members()
                        .insert(
                            groupKey=group_id,
                            body={
                                "email": member,
                                "kind": "admin#directory#member",
                                "role": role,
                                "status": "ACTIVE",
                                "type": "USER",
                            },
                        )
                        .execute()
                    )
                    members_data.append(result)
                    success = True
                except HttpError as e:
                    retries += 1
                    wait_time = BASE_DELAY * (2 ** (retries - 1))
                    logging.warning(
                        f"[WARNING - Workspace:add_group_members] Attempt {retries}/{MAX_RETRIES} failed to add member {member} to group {group_id}: {e}. Retrying in {wait_time:.1f} seconds..."  # noqa: E501
                    )
                    time.sleep(wait_time)
                else:
                    time.sleep(2)

            if not success:
                logging.error(
                    f"[ERROR - Workspace:add_group_members] Could not add member {member} to group {group_id} after {MAX_RETRIES} attempts."  # noqa: E501
                )
                failed_members.append(member)

        if failed_members:
            logging.warning(
                f"[WARNING - Workspace:add_group_members] The following members could not be added to group {group_id}: {failed_members}"  # noqa: E501
            )

        return members_data
