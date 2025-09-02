import unittest
from unittest.mock import MagicMock, patch

from gc_google_services_api.drive import Drive


class TestDrive(unittest.TestCase):
    @patch("gc_google_services_api.drive.build")
    def setUp(self, mock_build):
        self.mock_credentials = MagicMock()
        self.mock_service = MagicMock()
        mock_build.return_value = self.mock_service

        self.drive = Drive(self.mock_credentials)

    def test_store_drives(self):
        drives = [{"name": "AC - Test Drive"}, {"name": "Non AC Drive"}]
        self.drive._add_shared_drive = MagicMock()
        self.drive.store_drives(drives)
        self.drive._add_shared_drive.assert_called_once_with(drives[0])

    def test_get_permissions_from_file(self):
        file_id = "test_file_id"
        mock_permissions = {
            "permissions": [
                {
                    "id": "1",
                    "displayName": "User 1",
                    "role": "reader",
                    "emailAddress": "user1@example.com",
                }
            ]
        }
        self.mock_service.permissions().list().execute.return_value = (
            mock_permissions  # noqa: E501
        )
        permissions = self.drive.get_permissions_from_file(file_id)
        self.assertEqual(permissions, mock_permissions["permissions"])

    def test_get_shared_drives(self):
        mock_drives = {
            "drives": [{"id": "drive_id_1", "name": "Drive 1"}],
            "nextPageToken": None,
        }
        self.mock_service.drives().list().execute.return_value = mock_drives
        drives = self.drive.get_shared_drives()
        self.assertEqual(drives, mock_drives["drives"])

    def test_get_shared_drive_by_name(self):
        name = "Test Drive"
        mock_drives = {"drives": [{"id": "drive_id_1", "name": "Test Drive"}]}
        self.mock_service.drives().list().execute.return_value = mock_drives
        drives = self.drive.get_shared_drive_by_name(name)
        self.assertEqual(drives, mock_drives["drives"])

    @patch("time.sleep", return_value=None)
    def test_create_shared_drive(self, mock_sleep):
        name = "New Drive"

        mock_drive = {"id": "new_drive_id"}
        self.mock_service.drives().create().execute.return_value = mock_drive
        shared_drive = self.drive.create_shared_drive(name)
        self.assertEqual(shared_drive, mock_drive)

    @patch("time.sleep", return_value=None)
    def test_set_group_in_shared_drive_permissions(self, mock_sleep):
        drive_id = "drive_id"
        group_email = "group@example.com"
        mock_permission_result = {"id": "permission_id"}
        self.mock_service.permissions().create().execute.return_value = (
            mock_permission_result
        )
        success = self.drive.set_group_in_shared_drive_permissions(
            drive_id, group_email
        )
        self.assertTrue(success)

    @patch("time.sleep", return_value=None)
    def test_set_shared_drive_admin_permissions(self, mock_sleep):
        drive_id = "drive_id"
        users = ["user1@example.com", "user2@example.com"]
        mock_permission_result = {"id": "permission_id"}
        self.mock_service.permissions().create().execute.return_value = (
            mock_permission_result
        )
        success = self.drive.set_shared_drive_admin_permissions(
            drive_id, users
        )  # noqa: E501
        self.assertTrue(success)

    def test_create_folder_structure(self):
        parent_id = "parent_folder_id"
        folder_structure = {
            "Folder1": {},
            "Folder2": {"Subfolder1": {}, "Subfolder2": {}},
        }

        success = self.drive.create_folder_structure(
            parent_id, folder_structure
        )

        self.assertTrue(success)
        self.assertEqual(
            self.mock_service.files().create.call_count, 4
        )
