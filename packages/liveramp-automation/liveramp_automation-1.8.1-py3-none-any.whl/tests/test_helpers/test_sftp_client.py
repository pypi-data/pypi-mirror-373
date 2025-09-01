from unittest import TestCase
from unittest.mock import MagicMock, patch, call

import paramiko
import os

from liveramp_automation.helpers.sftp_client import SFTPClient
import pytest


class TestSFTPClient(TestCase):
    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_context_manager_connection_success(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        cnopts = {"look_for_keys": False}
        with SFTPClient(
            username="user", password="pass", hostname="host", cnopts=cnopts
        ) as client:
            self.assertIsNotNone(client.sftp)
            mock_ssh.connect.assert_called_once_with(
                hostname="host",
                port=22,
                username="user",
                password="pass",
                key_filename=None,
                passphrase=None,
                **cnopts,
            )
            mock_ssh.set_missing_host_key_policy.assert_called_once()
            mock_ssh.get_transport.assert_called_once()
            mock_transport.open_sftp_client.assert_called_once()

        mock_logger.info.assert_any_call("Successfully connected to host")
        mock_logger.info.assert_any_call("Disconnected from host")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_context_manager_connection_failure(self, mock_ssh_client):
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_ssh.connect.side_effect = paramiko.ssh_exception.AuthenticationException(
            "Auth failed"
        )

        with self.assertRaises(paramiko.ssh_exception.AuthenticationException):
            with SFTPClient(username="user", password="pass"):
                pass

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_file_success(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        with patch("os.path.dirname", return_value=""), patch("os.makedirs"):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.download_file("remote.txt", "local.txt")
                self.assertTrue(result)
                mock_sftp.get.assert_called_once_with(
                    remotepath="remote.txt", localpath="local.txt"
                )
        mock_logger.info.assert_any_call("SFTP Download successful")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_file_create_directory_success(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        mock_makedirs = MagicMock()
        with patch("os.path.dirname", return_value="local_dir"), patch(
            "os.makedirs", mock_makedirs
        ):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.download_file("remote.txt", "local_dir/local.txt")
                self.assertTrue(result)
                mock_makedirs.assert_called_once_with("local_dir", exist_ok=True)
                mock_sftp.get.assert_called_once_with(
                    remotepath="remote.txt", localpath="local_dir/local.txt"
                )
        mock_logger.info.assert_any_call("SFTP Download successful")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_file_success_use_getfo(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        with patch("os.path.dirname", return_value=""), patch("os.makedirs"), patch(
            "builtins.open", MagicMock()
        ) as mock_open:
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.download_file(
                    "remote.txt", "local.txt", use_getfo=True
                )
                self.assertTrue(result)
                mock_sftp.getfo.assert_called_once()
                mock_sftp.getfo.assert_called_with(
                    remotepath="remote.txt", flo=mock_open().__enter__()
                )

        mock_logger.info.assert_any_call("SFTP Download successful")
        mock_logger.info.assert_any_call("Using getfo() for file-like object handling.")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_file_failure(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp
        mock_sftp.get.side_effect = Exception("Download error")

        with patch("os.path.dirname", return_value=""), patch("os.makedirs"):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.download_file("remote.txt", "local.txt")
                self.assertFalse(result)
        mock_logger.error.assert_called_with("Error downloading file: Download error")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_file_success(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            result = client.upload_file("local.txt", "remote.txt")
            self.assertTrue(result)
            mock_sftp.put.assert_called_once_with(
                localpath="local.txt", remotepath="remote.txt"
            )
        mock_logger.info.assert_any_call("SFTP Upload successful")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_file_failure(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp
        mock_sftp.put.side_effect = Exception("Upload error")

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            result = client.upload_file("local.txt", "remote.txt")
            self.assertFalse(result)
        mock_logger.error.assert_called_with("Error uploading file: Upload error")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_file_putfo_success(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        mock_file_context = MagicMock()
        mock_file = MagicMock()
        mock_file_context.__enter__.return_value = mock_file
        with patch("builtins.open", return_value=mock_file_context):
            with SFTPClient(username="user", password="pass", hostname="host") as client:
                result = client.upload_file("local.txt", "remote.txt", use_putfo=True)
                self.assertTrue(result)
                mock_sftp.putfo.assert_called_once_with(mock_file, "remote.txt")
        mock_logger.info.assert_any_call("SFTP Upload successful")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_file_permission_denied(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp
        mock_sftp.put.side_effect = Exception("Permission denied")

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            result = client.upload_file("local.txt", "remote.txt")
            self.assertFalse(result)
        mock_logger.error.assert_called_with("Error uploading file: Permission denied")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_list_files_success(self, mock_ssh_client):
        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock stat to return file mode (not directory)
        mock_stat = MagicMock()
        mock_stat.st_mode = 0o644  # Regular file mode
        mock_sftp.stat.return_value = mock_stat
        mock_sftp.listdir.return_value = ["file1.txt", "file2.txt"]

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            files = client.list_files("remote_dir")
            self.assertEqual(files, ["file1.txt", "file2.txt"])

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_list_files_stat_exception(self, mock_ssh_client):
        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock stat to raise an exception for 'file1.txt' and return a valid stat for 'file2.txt'
        def mock_stat_side_effect(path):
            if path == "remote_dir/file1.txt":
                raise Exception("Stat error")
            else:
                mock_stat = MagicMock()
                mock_stat.st_mode = 0o644  # Regular file mode
                return mock_stat

        mock_sftp.stat.side_effect = mock_stat_side_effect
        mock_sftp.listdir.return_value = ["file1.txt", "file2.txt"]

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            files = client.list_files("remote_dir")
            self.assertEqual(files, ["file2.txt"])

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_list_files_trailing_slash(self, mock_ssh_client):
        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock stat to return file mode (not directory)
        mock_stat = MagicMock()
        mock_stat.st_mode = 0o644  # Regular file mode
        mock_sftp.stat.return_value = mock_stat
        mock_sftp.listdir.return_value = ["file1.txt", "file2.txt"]

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            files = client.list_files("remote_dir/")  # Note the trailing slash
            self.assertEqual(files, ["file1.txt", "file2.txt"])

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_list_files_failure(self, mock_ssh_client):
        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp
        mock_sftp.listdir.side_effect = Exception("List error")

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            files = client.list_files("remote_dir")
            self.assertEqual(files, [])

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_list_directories_success(self, mock_ssh_client):
        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock stat to return directory mode for specific paths
        def mock_stat_side_effect(path):
            mock_stat = MagicMock()
            if "dir1" in path:
                mock_stat.st_mode = 0o40755  # Directory mode (0o40000 | 0o755)
            else:
                mock_stat.st_mode = 0o644  # Regular file mode
            return mock_stat

        mock_sftp.stat.side_effect = mock_stat_side_effect
        mock_sftp.listdir.return_value = ["dir1", "file1.txt"]

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            directories = client.list_directories("remote_dir")
            self.assertEqual(directories, ["dir1"])

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_directory_simple(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock directory operations
        mock_sftp.stat.side_effect = FileNotFoundError()
        mock_sftp.mkdir.return_value = None

        with (
            patch("os.listdir", return_value=["file1.txt", "file2.txt"]),
            patch("os.path.isfile", return_value=True),
            patch("os.path.join", side_effect=lambda *args: "/".join(args)),
        ):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.upload_directory(
                    "/local/dir", "/remote/dir", recursive=False
                )
                self.assertTrue(result)
                mock_sftp.mkdir.assert_called_once_with("/remote/dir")
                self.assertEqual(mock_sftp.put.call_count, 2)

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_directory_simple(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock directory operations
        mock_sftp.listdir.return_value = ["file1.txt", "dir1"]
        mock_stat = MagicMock()
        mock_stat.st_mode = 0o644  # Regular file mode
        mock_sftp.stat.return_value = mock_stat

        def mock_stat_side_effect(path):
            mock_stat = MagicMock()
            if path.endswith("dir1"):
                mock_stat.st_mode = 0o40755  # Directory mode
            else:
                mock_stat.st_mode = 0o644  # Regular file mode
            return mock_stat

        mock_sftp.stat.side_effect = mock_stat_side_effect

        with patch("os.makedirs"):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.download_directory(
                    "/remote/dir", "/local/dir", recursive=False
                )
                self.assertTrue(result)
                mock_sftp.get.assert_called_once_with(
                    "/remote/dir/file1.txt", "/local/dir/file1.txt"
                )

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_directory_simple_file_exists(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock directory operations
        mock_sftp.listdir.return_value = ["file1.txt", "file2.txt"]
        mock_stat = MagicMock()
        mock_stat.st_mode = 0o644  # Regular file mode
        mock_sftp.stat.return_value = mock_stat

        # Create dummy files in the local directory to simulate existing files
        with patch("os.makedirs", return_value=None), patch("os.path.exists", return_value=True):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.download_directory(
                    "/remote/dir", "/local/dir", recursive=False
                )
                self.assertTrue(result)
                self.assertEqual(mock_sftp.get.call_count, 2)

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_directory_recursive_happy_path(self, mock_ssh_client):
        """
        Tests recursive directory upload for a nested structure,
        verifying directory creation and file uploads.
        """
        # Setup mocks for SSH and SFTP clients
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock that remote directories do not exist initially to trigger mkdir
        mock_sftp.stat.side_effect = FileNotFoundError

        local_dir = "/local/dir"
        remote_dir = "/remote/dir"

        # Mock the local directory structure that os.walk would return
        # This represents a directory with one file and one subdirectory,
        # which in turn contains another file.
        walk_data = [
            (local_dir, ["subdir"], ["file1.txt"]),
            (os.path.join(local_dir, "subdir"), [], ["file2.txt"]),
        ]

        with patch("os.walk", return_value=walk_data):
            with SFTPClient(username="user", password="pass", hostname="host") as client:
                result = client.upload_directory(local_dir, remote_dir, recursive=True)

                # Assert that the overall operation was successful
                self.assertTrue(result)

                # Verify that the remote base directory and subdirectory were created
                mkdir_calls = [
                    call(remote_dir),
                    call(f"{remote_dir}/subdir"),
                ]
                mock_sftp.mkdir.assert_has_calls(mkdir_calls, any_order=True)
                self.assertEqual(mock_sftp.mkdir.call_count, 2)

                # Verify that all files from the local structure were uploaded
                # to their corresponding remote locations
                put_calls = [
                    call(
                        os.path.join(local_dir, "file1.txt"),
                        f"{remote_dir}/file1.txt",
                    ),
                    call(
                        os.path.join(local_dir, "subdir", "file2.txt"),
                        f"{remote_dir}/subdir/file2.txt",
                    ),
                ]
                mock_sftp.put.assert_has_calls(put_calls, any_order=True)
                self.assertEqual(mock_sftp.put.call_count, 2)

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_directory_recursive_upload_failure(self, mock_ssh_client):
        """
        Tests recursive directory upload failure when sftp.put raises an exception.
        """
        # Setup mocks for SSH and SFTP clients
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock that remote directories do not exist initially to trigger mkdir
        mock_sftp.stat.side_effect = FileNotFoundError

        # Make the first sftp.put call raise an exception
        mock_sftp.put.side_effect = Exception("Upload failed")

        local_dir = "/local/dir"
        remote_dir = "/remote/dir"

        # Mock the local directory structure that os.walk would return
        walk_data = [
            (local_dir, ["subdir"], ["file1.txt"]),
            (os.path.join(local_dir, "subdir"), [], ["file2.txt"]),
        ]

        with patch("os.walk", return_value=walk_data):
            with SFTPClient(username="user", password="pass", hostname="host") as client:
                result = client.upload_directory(local_dir, remote_dir, recursive=True)

                # Assert that the overall operation failed
                self.assertFalse(result)

                # Assert that mkdir was called (at least once)
                mock_sftp.mkdir.assert_called()

                # Assert that put was called (at least once before failing)
                mock_sftp.put.assert_called()

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_directory_recursive_special_chars(self, mock_ssh_client):
        """
        Tests recursive directory upload with special characters and spaces in file names,
        verifying correct remote path construction.
        """
        # Setup mocks for SSH and SFTP clients
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock that remote directory does not exist initially to trigger mkdir
        mock_sftp.stat.side_effect = FileNotFoundError

        local_dir = "/local/dir with spaces"
        remote_dir = "/remote/dir"
        file_name = "file with spaces and !@#$.txt"
        local_file_path = os.path.join(local_dir, file_name)

        # Mock the local directory structure that os.walk would return
        walk_data = [(local_dir, [], [file_name])]

        with patch("os.walk", return_value=walk_data):
            with SFTPClient(username="user", password="pass", hostname="host") as client:
                result = client.upload_directory(local_dir, remote_dir, recursive=True)

                # Assert that the overall operation was successful
                self.assertTrue(result)

                # Verify that the remote directory was created
                mock_sftp.mkdir.assert_called_once_with(remote_dir)

                # Verify that the file was uploaded to the correct remote location
                expected_remote_path = f"{remote_dir}/{file_name}"
                mock_sftp.put.assert_called_once_with(local_file_path, expected_remote_path)

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_directory_recursive_file_exists(self, mock_ssh_client):
        """
        Tests the scenario where remote files already exist.
        It asserts that the function proceeds with uploading (overwriting)
        the files without checking.
        """
        # Setup mocks for SSH and SFTP clients
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock that remote files already exist
        mock_sftp.stat.return_value = MagicMock()  # Simulate file exists

        local_dir = "/local/dir"
        remote_dir = "/remote/dir"

        # Mock the local directory structure
        walk_data = [
            (local_dir, [], ["file1.txt"]),
        ]

        with patch("os.walk", return_value=walk_data):
            with SFTPClient(username="user", password="pass", hostname="host") as client:
                result = client.upload_directory(local_dir, remote_dir, recursive=True)

                # Assert that the overall operation was successful
                self.assertTrue(result)

                # Verify that put is called, even though the file exists remotely
                mock_sftp.put.assert_called_once_with(
                    os.path.join(local_dir, "file1.txt"), f"{remote_dir}/file1.txt"
                )

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_directory_recursive_symlink_loop(self, mock_ssh_client):
        """
        Tests that _upload_directory_recursive handles symbolic links
        that create circular references without causing infinite recursion.
        """
        # Setup mocks for SSH and SFTP clients
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock that remote directories do not exist initially to trigger mkdir
        mock_sftp.stat.side_effect = FileNotFoundError

        local_dir = "/local/dir"
        remote_dir = "/remote/dir"

        # Create a directory structure with a symbolic link
        # that points back to the parent directory.
        walk_data = [
            (local_dir, ["symlink_dir"], ["file1.txt"]),
            (os.path.join(local_dir, "symlink_dir"), [], ["file2.txt"]),
        ]

        # Mock os.walk to return the directory structure.
        # The 'symlink_dir' is intended to be a symbolic link
        # pointing back to local_dir, but os.walk doesn't resolve symlinks by default.
        # We limit the walk to a few iterations to avoid infinite loops.
        with patch("os.walk", return_value=walk_data):
            with SFTPClient(username="user", password="pass", hostname="host") as client:
                result = client.upload_directory(local_dir, remote_dir, recursive=True)

                # Assert that the overall operation was successful
                self.assertTrue(result)

                # Assert that sftp.put is called a limited number of times,
                # indicating that the recursion was controlled.
                # The exact number of calls depends on the mocked directory structure.
                # Here, we expect two files to be uploaded.
                self.assertEqual(mock_sftp.put.call_count, 2)

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_directory_recursive_creates_empty_subdirectories(
        self, mock_ssh_client
    ):
        """
        Tests that _upload_directory_recursive creates empty subdirectories on the remote server.
        """
        # Setup mocks for SSH and SFTP clients
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock that remote directories do not exist initially to trigger mkdir
        mock_sftp.stat.side_effect = FileNotFoundError

        local_dir = "/local/dir"
        remote_dir = "/remote/dir"

        # Mock the local directory structure that os.walk would return
        # This represents a directory with one empty subdirectory.
        walk_data = [
            (local_dir, ["empty_subdir"], []),
            (os.path.join(local_dir, "empty_subdir"), [], []),
        ]

        with patch("os.walk", return_value=walk_data):
            with SFTPClient(username="user", password="pass", hostname="host") as client:
                result = client.upload_directory(local_dir, remote_dir, recursive=True)

                # Assert that the overall operation was successful
                self.assertTrue(result)

                # Verify that the remote base directory and empty subdirectory were created
                mkdir_calls = [
                    call(remote_dir),
                    call(f"{remote_dir}/empty_subdir"),
                ]
                mock_sftp.mkdir.assert_has_calls(mkdir_calls, any_order=True)
                self.assertEqual(mock_sftp.mkdir.call_count, 2)

                # Verify that no files were uploaded
                self.assertEqual(mock_sftp.put.call_count, 0)

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_directory_recursive_success(self, mock_ssh_client):
        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        with patch(
            "liveramp_automation.helpers.sftp_client.SFTPClient._upload_directory_recursive"
        ) as mock_upload_directory_recursive:
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.upload_directory(
                    "/local/dir", "/remote/dir", recursive=True
                )
                self.assertTrue(result)
                mock_upload_directory_recursive.assert_called_once_with(
                    "/local/dir", "/remote/dir"
                )

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_directory_recursive_success(self, mock_ssh_client):
        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        mock_download_directory_recursive = MagicMock()

        with patch(
            "liveramp_automation.helpers.sftp_client.SFTPClient._download_directory_recursive",
            mock_download_directory_recursive,
        ):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.download_directory(
                    "/remote/dir", "/local/dir", recursive=True
                )
                self.assertTrue(result)
                mock_download_directory_recursive.assert_called_once_with(
                    "/remote/dir", "/local/dir"
                )

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_directory_recursive_failure(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock _download_directory_recursive to raise an exception
        with patch.object(
            SFTPClient, "_download_directory_recursive", side_effect=Exception("Recursive download error")
        ):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.download_directory(
                    "/remote/dir", "/local/dir", recursive=True
                )
                self.assertFalse(result)
        mock_logger.error.assert_called_with(
            "Error downloading directory: Recursive download error"
        )

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_directory_recursive_permission_error(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock directory operations
        mock_sftp.listdir.side_effect = Exception("Permission denied")

        with patch("os.makedirs"):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.download_directory(
                    "/remote/dir", "/local/dir", recursive=True
                )
                self.assertFalse(result)
        mock_logger.error.assert_called_with(
            "Error downloading directory: Error in recursive directory download: Permission denied"
        )

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_directory_file_exists(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock os.makedirs to raise FileExistsError
        def mock_makedirs(path, exist_ok=False):
            raise FileExistsError()

        with patch("os.makedirs", side_effect=mock_makedirs):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.download_directory(
                    "/remote/dir", "/local/dir", recursive=False
                )
                self.assertFalse(result)

        mock_logger.error.assert_called_with("Error downloading directory: Error in simple directory download: ")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_directory_recursive_happy_path(self, mock_ssh_client):
        # Setup mocks for SSH and SFTP clients
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Define the remote file system structure
        remote_structure = {
            "/remote/dir": ["file1.txt", "subdir"],
            "/remote/dir/subdir": ["file2.txt"],
        }

        # Mock listdir to return contents based on path
        mock_sftp.listdir.side_effect = lambda path: remote_structure.get(path, [])

        # Mock stat to distinguish between files and directories
        def mock_stat_side_effect(path):
            mock_stat = MagicMock()
            # The st_mode for a directory is identified by the S_IFDIR flag, which is 0o040000.
            # The st_mode for a regular file is identified by the S_IFREG flag, which is 0o100000.
            if path.endswith("subdir"):
                mock_stat.st_mode = 0o40000  # Directory mode
            else:
                mock_stat.st_mode = 0o100644  # File mode
            return mock_stat

        mock_sftp.stat.side_effect = mock_stat_side_effect

        with patch("liveramp_automation.helpers.sftp_client.os.makedirs") as mock_makedirs:
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                # Execute the recursive download
                client._download_directory_recursive(
                    "/remote/dir", "/local/dir"
                )

                # Assert local directories were created
                expected_makedirs_calls = [
                    call("/local/dir", exist_ok=True),
                    call(os.path.join("/local/dir", "subdir"), exist_ok=True),
                ]
                mock_makedirs.assert_has_calls(expected_makedirs_calls, any_order=True)

                # Assert files were downloaded correctly
                expected_get_calls = [
                    call(
                        "/remote/dir/file1.txt",
                        os.path.join("/local/dir", "file1.txt"),
                    ),
                    call(
                        "/remote/dir/subdir/file2.txt",
                        os.path.join("/local/dir", "subdir", "file2.txt"),
                    ),
                ]
                mock_sftp.get.assert_has_calls(expected_get_calls, any_order=True)
                self.assertEqual(mock_sftp.get.call_count, 2)

    @patch("liveramp_automation.helpers.sftp_client.os.makedirs")
    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_directory_recursive_nonexistent_remote_dir(self, mock_ssh_client, mock_makedirs):
        """
        Tests the scenario where the remote directory does not exist.
        """
        # Setup mocks for SSH and SFTP clients
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock sftp.listdir to raise FileNotFoundError
        mock_sftp.listdir.side_effect = FileNotFoundError("No such directory")

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            with self.assertRaisesRegex(Exception, "Error in recursive directory download: No such directory"):
                client._download_directory_recursive("/remote/dir", "/local/dir")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_directory_recursive_unusual_directory_mode(self, mock_ssh_client):
        """
        Tests how _download_directory_recursive handles unusual file modes where the directory bit is set,
        but other bits indicate it's not a typical directory.
        """
        # Setup mocks for SSH and SFTP clients
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Define a remote directory with an unusual file mode (directory bit + some other bits)
        remote_dir = "/remote/dir"
        unusual_mode = 0o41777  # Directory bit (0o40000) + some other permissions

        # Mock sftp.listdir to return the directory
        mock_sftp.listdir.return_value = ["unusual_dir"]

        # Mock sftp.stat to return the unusual file mode for the directory
        mock_stat = MagicMock()

        # Create a counter to track calls to sftp.stat
        stat_call_count = 0

        def mock_stat_side_effect(path):
            nonlocal stat_call_count
            mock_stat = MagicMock()

            # Only return directory mode for the first call
            if stat_call_count == 0:
                mock_stat.st_mode = unusual_mode  # Directory bit + other bits
            else:
                mock_stat.st_mode = 0o100644  # Regular file mode

            stat_call_count += 1
            return mock_stat

        mock_sftp.stat.side_effect = mock_stat_side_effect

        with patch("liveramp_automation.helpers.sftp_client.os.makedirs") as mock_makedirs:
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                # Execute the recursive download
                client._download_directory_recursive(remote_dir, "/local/dir")

                # Assert that os.makedirs was called to create the local directory
                mock_makedirs.assert_called_with("/local/dir/unusual_dir", exist_ok=True)

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_directory_recursive_symbolic_link_cycle(self, mock_ssh_client):
        """
        Tests that _download_directory_recursive handles symbolic link cycles without infinite recursion.
        """
        # Setup mocks for SSH and SFTP clients
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Define the remote file system structure with a symbolic link cycle
        remote_structure = {
            "/remote/dir": ["link_to_self"],
        }

        # Mock listdir to return contents based on path
        mock_sftp.listdir.side_effect = lambda path: remote_structure.get(path, [])

        # Mock stat to indicate a symbolic link (directory)
        mock_stat = MagicMock()
        mock_stat.st_mode = 0o40000  # Directory mode (treat symlinks as directories to trigger the loop)
        mock_sftp.stat.return_value = mock_stat

        with patch("liveramp_automation.helpers.sftp_client.os.makedirs") as mock_makedirs:
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                # Execute the recursive download
                client._download_directory_recursive(
                    "/remote/dir", "/local/dir"
                )

                # Assert that get and stat are not called excessively, indicating a cycle was detected and broken
                self.assertLess(mock_sftp.get.call_count, 5, "Too many get calls, likely infinite recursion")
                self.assertLess(mock_sftp.stat.call_count, 5, "Too many stat calls, likely infinite recursion")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_directory_simple_empty_directory(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock directory operations: empty directory
        mock_sftp.listdir.return_value = []

        with patch("os.makedirs") as mock_makedirs:
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.download_directory(
                    "/remote/dir", "/local/dir", recursive=False
                )
                self.assertTrue(result)
                mock_sftp.get.assert_not_called()
                mock_makedirs.assert_called_once()

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_context_manager_exit_success(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            client.sftp = mock_sftp
            client.transport = mock_transport

        mock_sftp.close.assert_called_once()
        mock_transport.close.assert_called_once()
        mock_logger.info.assert_any_call("Disconnected from host")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_exit_only_sftp_set(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_sftp = MagicMock()

        client = SFTPClient(username="user", password="pass", hostname="host")
        client.sftp = mock_sftp
        client.transport = None

        client.__exit__(None, None, None)

        mock_sftp.close.assert_called_once()
        mock_logger.info.assert_called_with("Disconnected from host")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_exit_closes_transport_only(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()

        client = SFTPClient(username="user", password="pass", hostname="host")
        client.transport = mock_transport
        client.sftp = None

        client.__exit__(None, None, None)

        mock_transport.close.assert_called_once()
        mock_logger.info.assert_called_with("Disconnected from host")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_exit_with_none_sftp_and_transport(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            client.sftp = None
            client.transport = None

        mock_sftp.close.assert_not_called()
        mock_transport.close.assert_not_called()
        mock_logger.info.assert_any_call("Disconnected from host")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_context_manager_exception_propagation(self, mock_ssh_client):
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        with pytest.raises(ValueError, match="Test exception"):
            with SFTPClient(username="user", password="pass", hostname="host"):
                raise ValueError("Test exception")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_file_remote_dir_not_exists(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp
        mock_sftp.put.side_effect = IOError("No such directory")

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            result = client.upload_file("local.txt", "remote/nonexistent/file.txt")
            self.assertFalse(result)
        mock_logger.error.assert_called_with(
            "Error uploading file: No such directory"
        )

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_directory_simple_remote_exists(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock directory operations
        mock_sftp.stat.return_value = None  # remote dir exists

        with (
            patch("os.listdir", return_value=["file1.txt", "file2.txt"]),
            patch("os.path.isfile", return_value=True),
            patch("os.path.join", side_effect=lambda *args: "/".join(args)),
        ):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.upload_directory(
                    "/local/dir", "/remote/dir", recursive=False
                )
                self.assertTrue(result)
                mock_sftp.mkdir.assert_not_called()
                self.assertEqual(mock_sftp.put.call_count, 2)

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_directory_simple_parent_dir_missing(self, mock_ssh_client):
        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock directory operations
        mock_sftp.stat.side_effect = FileNotFoundError()
        mock_sftp.mkdir.side_effect = paramiko.sftp_client.SFTPError(
            "No such parent directory"
        )

        with (
            patch("os.listdir", return_value=["file1.txt", "file2.txt"]),
            patch("os.path.isfile", return_value=True),
            patch("os.path.join", side_effect=lambda *args: "/".join(args)),
        ):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.upload_directory(
                    "/local/dir", "/remote/parent/dir", recursive=False
                )
                self.assertFalse(result)

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_directory_simple_file_exists_as_directory(self, mock_ssh_client):
        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock directory operations
        mock_sftp.stat.side_effect = FileNotFoundError()
        mock_sftp.mkdir.return_value = None
        mock_sftp.put.side_effect = Exception("Is a directory")

        with (
            patch("os.listdir", return_value=["file1.txt"]),
            patch("os.path.isfile", return_value=True),
            patch("os.path.join", side_effect=lambda *args: "/".join(args)),
        ):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.upload_directory(
                    "/local/dir", "/remote/dir", recursive=False
                )
                self.assertFalse(result)

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_directory_simple_permission_error(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock directory operations
        mock_sftp.listdir.return_value = ["file1.txt", "file2.txt"]
        mock_stat = MagicMock()
        mock_stat.st_mode = 0o644  # Regular file mode
        mock_sftp.stat.return_value = mock_stat
        mock_sftp.get.side_effect = [None, Exception("Permission denied")]

        with patch("os.makedirs"):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.download_directory(
                    "/remote/dir", "/local/dir", recursive=False
                )
                self.assertTrue(result)
                self.assertEqual(mock_sftp.get.call_count, 2)
                mock_logger.warning.assert_called_with(
                    "Could not download /remote/dir/file2.txt: Permission denied"
                )

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_directory_simple_all_files_fail(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock directory operations
        mock_sftp.listdir.return_value = ["file1.txt", "file2.txt"]
        mock_stat = MagicMock()
        mock_stat.st_mode = 0o644  # Regular file mode
        mock_sftp.stat.return_value = mock_stat
        mock_sftp.get.side_effect = Exception("Download error")

        with patch("os.makedirs"):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.download_directory(
                    "/remote/dir", "/local/dir", recursive=False
                )
                self.assertTrue(result)
        self.assertEqual(mock_sftp.get.call_count, 2)
        mock_logger.warning.assert_called()

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_list_files_unusual_permissions(self, mock_ssh_client):
        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock stat to return an unusual file mode (not directory)
        mock_stat = MagicMock()
        mock_stat.st_mode = 0o100  # Execute only
        mock_sftp.stat.return_value = mock_stat
        mock_sftp.listdir.return_value = ["file1.txt"]

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            files = client.list_files("remote_dir")
            self.assertEqual(files, ["file1.txt"])

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_list_files_empty_directory(self, mock_ssh_client):
        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock listdir to return an empty list, simulating an empty directory
        mock_sftp.listdir.return_value = []

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            files = client.list_files("remote_dir")
            self.assertEqual(files, [])