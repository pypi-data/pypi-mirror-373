import unittest
from unittest.mock import MagicMock, call, patch

from gc_google_services_api.workspace import WorkSpace


class TestWorkSpace(unittest.TestCase):
    @patch("gc_google_services_api.workspace.build")
    def test_get_groups_by_email(self, mock_build):
        credentials = MagicMock()
        domain = "example.com"
        email = "user@example.com"
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        workspace = WorkSpace(credentials, domain)

        mock_execute = {"groups": [1, 2]}
        mock_service.groups.return_value.list.return_value.execute.return_value = (  # noqa: E501
            mock_execute
        )

        result = workspace.get_groups_by_email(email)

        self.assertEqual(result, [1, 2])
        mock_service.groups.return_value.list.assert_called_once_with(
            domain=domain,
            maxResults=200,
            pageToken=None,
            userKey=email,
        )

    @patch("gc_google_services_api.workspace.build")
    def test_get_all_groups(self, mock_build):
        credentials = MagicMock()
        domain = "example.com"
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        workspace = WorkSpace(credentials, domain)

        mock_execute_1 = MagicMock()
        mock_execute_2 = MagicMock()

        mock_service.groups.return_value.list.side_effect = [
            mock_execute_1,
            mock_execute_2,
        ]
        mock_execute_1.execute.return_value = {
            "groups": [{"group1": "data1"}],
            "nextPageToken": "token",
        }
        mock_execute_2.execute.return_value = {
            "groups": [{"group2": "data2"}],
        }

        result = workspace.get_all_groups()

        self.assertEqual(result, [{"group1": "data1"}, {"group2": "data2"}])
        self.assertEqual(mock_service.groups.return_value.list.call_count, 2)
        mock_service.groups.return_value.list.assert_called_with(
            domain=domain,
            maxResults=200,
            pageToken="token",
        )
        mock_execute_1.execute.assert_called_once()
        mock_execute_2.execute.assert_called_once()

    @patch("gc_google_services_api.workspace.build")
    def test_get_members_from_group(self, mock_build):
        credentials = MagicMock()
        domain = "example.com"
        group_key = "group123"
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        workspace = WorkSpace(credentials, domain)

        mock_execute = {"members": [1, 2]}
        mock_service.members.return_value.list.return_value.execute.return_value = (  # noqa: E501
            mock_execute
        )

        result = workspace.get_members_from_group(group_key)

        # Assertions
        self.assertEqual(result, mock_execute["members"])
        mock_service.members.return_value.list.assert_called_once_with(
            groupKey=group_key
        )
        mock_service.members.return_value.list.return_value.execute.assert_called_once()  # noqa: E501

    @patch("gc_google_services_api.workspace.build")
    def test_delete_email_for_group(self, mock_build):
        credentials = MagicMock()
        domain = "example.com"
        group_id = "group123"
        email_to_delete = "user@example.com"
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        workspace = WorkSpace(credentials, domain)

        mock_execute = MagicMock()
        mock_service.members.return_value.delete.return_value.execute = (
            mock_execute  # noqa: E501
        )

        result = workspace.delete_email_for_group(group_id, email_to_delete)

        self.assertEqual(result, mock_execute.return_value)
        mock_service.members.return_value.delete.assert_called_once_with(
            groupKey=group_id,
            memberKey=email_to_delete,
        )
        mock_execute.assert_called_once()

    @patch("gc_google_services_api.workspace.build")
    def test_find_groups_permission_for_email(self, mock_build):
        def execute_side_effect(**kwargs):
            expected_results = {
                "group1": {"members": [{"email": "test1@example.com"}]},
                "group2": {"members": [{"email": "test2@example.com"}]},
            }

            group_key = kwargs.get("groupKey")
            execute_mock = MagicMock()
            execute_mock.execute.return_value = expected_results.get(
                group_key, {"members": []}
            )

            return execute_mock

        credentials = MagicMock()
        domain = "example.com"
        groups = [
            {"id": "group1", "name": "Group 1"},
            {"id": "group2", "name": "Group 2"},
        ]
        email_to_find = "test1@example.com"
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        workspace = WorkSpace(credentials, domain)

        mock_service.members.return_value.list.side_effect = (
            execute_side_effect  # noqa: E501
        )

        result = workspace.find_groups_permission_for_email(
            groups, email_to_find
        )  # noqa: E501

        expected_result = [
            {"group_id": "group1", "group_name": "Group 1"},
        ]
        self.assertEqual(result, expected_result)

    @patch("gc_google_services_api.workspace.build")
    def test_get_group_by_email(self, mock_build):
        credentials = MagicMock()
        domain = "example.com"
        project_email = "project@example.com"
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        workspace = WorkSpace(credentials, domain)

        mock_execute = MagicMock()
        mock_service.groups.return_value.get.return_value.execute = (
            mock_execute  # noqa: E501
        )

        result = workspace.get_group_by_email(project_email)

        self.assertEqual(result, mock_execute.return_value)
        mock_service.groups.return_value.get.assert_called_once_with(
            groupKey=project_email,
        )
        mock_execute.assert_called_once()

    @patch("gc_google_services_api.workspace.time")
    @patch("gc_google_services_api.workspace.build")
    def test_create_group_call_apis_to_add_users(self, mock_build, mock_time):
        domain = "example.com"
        project_email = "project@example.com"
        group_members = ["test1@test.com"]
        group_admin_members = ["admin1@test.com"]
        credentials = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_time.sleep = MagicMock()

        workspace = WorkSpace(credentials, domain)

        mock_service.groups.return_value.insert.return_value.execute.return_value = {  # noqa: E501
            "id": "NEW_GROUP_ID"
        }
        mock_service.members.return_value.insert.return_value.execute.return_value = (  # noqa: E501
            {}
        )

        workspace.create_group(
            group_email=project_email,
            group_members=group_members,
            group_admin_members=group_admin_members,
        )

        mock_service.groups.return_value.insert.assert_called_once_with(
            body={
                "name": "project@example.com",
                "email": "project@example.com",
            }
        )

        member_calls = [
            call(
                groupKey="NEW_GROUP_ID",
                body={
                    "email": "admin1@test.com",
                    "kind": "admin#directory#member",
                    "role": "MANAGER",
                    "status": "ACTIVE",
                    "type": "USER",
                },
            ),
            call(
                groupKey="NEW_GROUP_ID",
                body={
                    "email": "test1@test.com",
                    "kind": "admin#directory#member",
                    "role": "MEMBER",
                    "status": "ACTIVE",
                    "type": "USER",
                },
            ),
        ]

        time_calls = [
            call(2),
            call(5),
            call(2),
        ]

        self.assertTrue(
            mock_service.members.return_value.insert.call_args_list
            == member_calls  # noqa: E501
        )

        self.assertTrue(mock_time.sleep.call_args_list == time_calls)
