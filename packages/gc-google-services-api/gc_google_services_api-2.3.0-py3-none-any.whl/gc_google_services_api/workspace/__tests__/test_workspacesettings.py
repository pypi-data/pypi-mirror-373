import unittest
from unittest.mock import MagicMock, patch

from gc_google_services_api.workspace.settings import WorkSpaceSettings


class TestWorkSpace(unittest.TestCase):
    @patch("gc_google_services_api.workspace.settings.build")
    def test_get_groups_by_email(self, mock_build):
        credentials = MagicMock()
        group_email = "group@example.com"
        group_settings = {
            "whoCanContactOwner": "ALL_MEMBERS_CAN_CONTACT",
            "whoCanViewGroup": "ALL_MANAGERS_CAN_VIEW",
            "whoCanViewMembership": "ALL_MEMBERS_CAN_VIEW",
            "whoCanPostMessage": "ALL_MEMBERS_CAN_POST",
            "whoCanManageMembers": "MANAGERS_CAN_MANAGE",
            "whoCanJoin": "INVITED_CAN_JOIN",
            "whoCanModerateMembers": "OWNERS_AND_MANAGERS",
            "whoCanDiscoverGroup": "ALL_MEMBERS_CAN_DISCOVER",
            "whoCanAssistContent": "MANAGERS_ONLY",
            "allowExternalMembers": False,
            "membersCanPostAsTheGroup": False,
        }
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        workspace = WorkSpaceSettings(credentials)
        workspace.update_group_settings(
            group_email=group_email, group_settings=group_settings
        )

        mock_service.groups.return_value.patch.assert_called_once_with(
            groupUniqueId=group_email,
            body=group_settings,
        )
