from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/apps.groups.settings",
]


class WorkSpaceSettings:
    """
    Google API documentation:
        - https://google-api-client-libraries.appspot.com/documentation/groupssettings/v1/python/latest/groupssettings_v1.groups.html#update # noqa: E501
    """

    def __init__(self, credentials) -> None:
        self.service = build(
            "groupssettings",
            "v1",
            credentials=credentials,
        )

    def update_group_settings(self, group_email: str, group_settings: dict):
        self.service.groups().patch(
            groupUniqueId=group_email,
            body=group_settings,
        ).execute()
