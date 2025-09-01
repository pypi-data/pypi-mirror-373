import os
from typing import List, Optional

import paramiko

from liveramp_automation.utils.log import Logger


class SFTPClient:
    """
    Encapsulates an SFTP session, providing methods for file upload and download.
    """

    def __init__(
        self,
        username: str,
        password: str,
        hostname: str = "files.liveramp.com",
        port: int = 22,
        private_key: Optional[str] = None,
        key_pass: Optional[str] = None,
        cnopts: Optional[dict] = None,
    ):
        """
        Initializes the SFTP session.

        Args:
            hostname: The hostname or IP address of the SFTP server.
            username: The username for authentication.
            password: The password for password authentication.
            port: The SFTP server port (default: 22).
            private_key: Path to the private key file for key authentication (optional).
            key_pass: Password for the private key (optional).
            cnopts: Optional connection options dict (kept for compatibility).
        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.private_key = private_key
        self.key_pass = key_pass
        self.cnopts = cnopts or {}
        self.transport = None
        self.sftp = None

    def __enter__(self):
        """
        Context manager entry: Establishes the SFTP connection.
        """
        try:
            # Create SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect using either password or private key (paramiko handles both automatically)
            ssh_client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                key_filename=self.private_key,
                passphrase=self.key_pass,
                **self.cnopts,
            )

            # Get SFTP client from SSH client
            self.transport = ssh_client.get_transport()
            self.sftp = self.transport.open_sftp_client()

            Logger.info(f"Successfully connected to {self.hostname}")
            return self
        except Exception as e:
            Logger.error(f"SFTP Connection error: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit: Closes the SFTP connection.
        """
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()
        Logger.info(f"Disconnected from {self.hostname}")

    def download_file(
        self, remote_filepath: str, local_filepath: str, use_getfo: bool = False
    ) -> bool:
        """
        Downloads a file from the SFTP server to a local path.

        Args:
            remote_filepath: The path to the file on the SFTP server.
            local_filepath: The local path where the file should be saved.
            use_getfo: If True, uses getfo() for file-like object handling.
                       If False, uses get(). (default: False)

        Returns:
            True on success, False on failure.
        """
        try:
            Logger.info(
                f"SFTP Downloading: {remote_filepath} from {self.hostname} to local: {local_filepath}"
            )
            # Ensure the local directory exists, create it if necessary
            local_dir = os.path.dirname(local_filepath)
            if local_dir:  # Only create directory if there is a directory path
                os.makedirs(local_dir, exist_ok=True)

            if use_getfo:
                # Use getfo() for downloading into a file-like object
                Logger.info("Using getfo() for file-like object handling.")
                with open(local_filepath, "wb") as lf:
                    self.sftp.getfo(remotepath=remote_filepath, flo=lf)
            else:
                # Use get() for direct file download
                Logger.info("Using get() for file download.")
                self.sftp.get(remotepath=remote_filepath, localpath=local_filepath)
            Logger.info("SFTP Download successful")
            return True
        except Exception as e:
            # Log any other unexpected errors
            Logger.error(f"Error downloading file: {e}")
            return False

    def upload_file(
        self, local_filepath: str, remote_filepath: str, use_putfo: bool = False
    ) -> bool:
        """
        Uploads a file from a local path to the SFTP server.

        Args:
            local_filepath: The local path to the file to upload.
            remote_filepath: The path to save the file on the SFTP server.
            use_putfo: If True, uses putfo() for file-like object handling.
                       If False, uses put(). (default: False)

        Returns:
            True on success, False on failure.
        """
        try:
            Logger.info(
                f"SFTP Uploading: {local_filepath} from local to {self.hostname}: {remote_filepath}"
            )
            if use_putfo:
                # Use putfo() for uploading from a file-like object
                with open(local_filepath, "rb") as f:
                    self.sftp.putfo(f, remote_filepath)
            else:
                # Use put() for direct file upload
                self.sftp.put(localpath=local_filepath, remotepath=remote_filepath)
            # Log success message
            Logger.info("SFTP Upload successful")
            return True
        except Exception as e:
            # Log any other unexpected errors
            Logger.error(f"Error uploading file: {e}")
            return False

    def upload_directory(
        self, local_dir: str, remote_dir: str, recursive: bool = False, **kwargs
    ) -> bool:
        """
        Uploads a directory from a local path to the SFTP server.

        Args:
            local_dir: The local path to the directory to upload.
            remote_dir: The path to save the directory on the SFTP server.
            recursive: If True, recursively uploads subdirectories. (default: False)

        Returns:
            True on success, False on failure.
        """
        try:
            Logger.info(
                f"SFTP Uploading directory: {local_dir} from local to {self.hostname}: {remote_dir}, recursive={recursive}"
            )

            if recursive:
                self._upload_directory_recursive(local_dir, remote_dir)
            else:
                self._upload_directory_simple(local_dir, remote_dir)

            Logger.info("SFTP Directory Upload successful")
            return True
        except Exception as e:
            Logger.error(f"Error uploading directory: {e}")
            return False

    def _upload_directory_simple(self, local_dir: str, remote_dir: str):
        """Upload a directory without recursion."""
        try:
            # Create remote directory if it doesn't exist
            try:
                self.sftp.stat(remote_dir)
            except FileNotFoundError:
                self.sftp.mkdir(remote_dir)

            # Upload files in the directory
            for item in os.listdir(local_dir):
                local_path = os.path.join(local_dir, item)
                remote_path = f"{remote_dir}/{item}"

                if os.path.isfile(local_path):
                    self.sftp.put(local_path, remote_path)
                # Note: directories are not handled in non-recursive mode
        except Exception as e:
            raise Exception(f"Error in simple directory upload: {e}")

    def _upload_directory_recursive(self, local_dir: str, remote_dir: str):
        """Upload a directory with recursion."""
        try:
            # Create remote directory if it doesn't exist
            try:
                self.sftp.stat(remote_dir)
            except FileNotFoundError:
                self.sftp.mkdir(remote_dir)

            # Walk through local directory
            for root, dirs, files in os.walk(local_dir):
                # Calculate relative path from local_dir
                rel_path = os.path.relpath(root, local_dir)
                if rel_path == ".":
                    remote_root = remote_dir
                else:
                    remote_root = f"{remote_dir}/{rel_path}"

                # Create remote subdirectories
                for dir_name in dirs:
                    remote_subdir = f"{remote_root}/{dir_name}"
                    try:
                        self.sftp.stat(remote_subdir)
                    except FileNotFoundError:
                        self.sftp.mkdir(remote_subdir)

                # Upload files
                for file_name in files:
                    local_file = os.path.join(root, file_name)
                    remote_file = f"{remote_root}/{file_name}"
                    self.sftp.put(local_file, remote_file)
        except Exception as e:
            raise Exception(f"Error in recursive directory upload: {e}")

    def download_directory(
        self, remote_dir: str, local_dir: str, recursive: bool = False, **kwargs
    ) -> bool:
        """
        Downloads a directory from the SFTP server to a local path.

        Args:
            remote_dir: The path to the directory on the SFTP server.
            local_dir: The local path where the directory should be saved.
            recursive: If True, recursively downloads subdirectories. (default: False)

        Returns:
            True on success, False on failure.
        """
        try:
            Logger.info(
                f"SFTP Downloading directory: {remote_dir} from {self.hostname} to local: {local_dir}, recursive={recursive}"
            )

            if recursive:
                self._download_directory_recursive(remote_dir, local_dir)
            else:
                self._download_directory_simple(remote_dir, local_dir)

            Logger.info("SFTP Directory Download successful")
            return True
        except Exception as e:
            # Log any other unexpected errors
            Logger.error(f"Error downloading directory: {e}")
            return False

    def _download_directory_simple(self, remote_dir: str, local_dir: str):
        """Download a directory without recursion."""
        try:
            # Create local directory if it doesn't exist
            os.makedirs(local_dir, exist_ok=True)

            # List and download files in the directory
            for item in self.sftp.listdir(remote_dir):
                remote_path = f"{remote_dir}/{item}"
                local_path = os.path.join(local_dir, item)

                try:
                    if (
                        self.sftp.stat(remote_path).st_mode & 0o40000
                    ):  # Check if directory
                        continue  # Skip directories in non-recursive mode
                    else:
                        self.sftp.get(remote_path, local_path)
                except Exception as e:
                    Logger.warning(f"Could not download {remote_path}: {e}")
        except Exception as e:
            raise Exception(f"Error in simple directory download: {e}")

    def _download_directory_recursive(self, remote_dir: str, local_dir: str):
        """Download a directory with recursion."""
        try:
            # Create local directory if it doesn't exist
            os.makedirs(local_dir, exist_ok=True)

            # Get list of items in remote directory
            for item in self.sftp.listdir(remote_dir):
                remote_path = f"{remote_dir}/{item}"
                local_path = os.path.join(local_dir, item)

                try:
                    stat = self.sftp.stat(remote_path)
                    if stat.st_mode & 0o40000:  # Directory
                        # Recursively download subdirectory
                        self._download_directory_recursive(remote_path, local_path)
                    else:
                        # Download file
                        self.sftp.get(remote_path, local_path)
                except Exception as e:
                    Logger.warning(f"Could not download {remote_path}: {e}")
        except Exception as e:
            raise Exception(f"Error in recursive directory download: {e}")

    def list_files(self, remote_dir: str) -> List[str]:
        """
        Lists the files in a directory on the SFTP server.

        Args:
            remote_dir: The path to the directory on the SFTP server.

        Returns:
            A list of strings, where each string is a filename in the directory.
            Returns an empty list on error.
        """
        try:
            files = []
            for item in self.sftp.listdir(remote_dir):
                remote_path = f"{remote_dir}/{item}"
                try:
                    if (
                        not self.sftp.stat(remote_path).st_mode & 0o40000
                    ):  # Not a directory
                        files.append(item)
                except Exception:
                    continue
            return files
        except Exception as e:
            Logger.error(f"Error listing files: {e}")
            return []

    def list_directories(self, remote_dir: str) -> List[str]:
        """
        Retrieve the names of all subdirectories within a specified directory on the SFTP server.

        This method iterates through all items in the given remote directory, checks each item's
        file mode to determine if it is a directory, and collects the names of those that are directories.
        If an error occurs while accessing an item, it is skipped and a warning is logged.
        If an error occurs while listing the directory itself, an error is logged and an empty list is returned.

        Args:
            remote_dir: The path to the directory on the SFTP server whose subdirectories are to be listed.

        Returns:
            A list of directory names (as strings) found within the specified remote directory.
            Returns an empty list if an error occurs.
        """
        try:
            directories = []
            for item in self.sftp.listdir(remote_dir):
                remote_path = f"{remote_dir}/{item}"
                try:
                    # Check if the current item is a directory by examining its st_mode.
                    if self.sftp.stat(remote_path).st_mode & 0o40000:
                        directories.append(item)
                        Logger.info(f"Found directory: {remote_path}")
                except Exception as e:
                    Logger.warning(
                        f"Could not access {remote_path} to check if it is a directory: {e}"
                    )
                    continue
            Logger.info(
                f"Total directories found in '{remote_dir}': {len(directories)}"
            )
            return directories
        except Exception as e:
            Logger.error(f"Error listing directories in '{remote_dir}': {e}")
            return []

"""
if __name__ == "__main__":
    # Example usage
    username = "E2E-BB-TEST-CONNECT"
    password = "Fr8shst8rt!"
    with SFTPClient(username=username, password=password) as sftp:
        sftp.list_directories(remote_dir="/uploads/")
        # sftp.upload_file(
        #     local_filepath="file.txt",
        #     remote_filepath="/uploads/br_delete_me/file.txt",
        # )
        # sftp.upload_directory(
        #     local_dir="/path/to/local/dir",
        #     remote_dir="/path/to/remote/dir",
        #     recursive=True,
        # )
        # sftp.download_directory(
        #     remote_dir="/path/to/remote/dir",
        #     local_dir="/path/to/local/dir",
        #     recursive=True,
        # )
        # Logger.info(sftp.list_files(remote_dir="/uploads/br_delete_me/"))
        # Logger.info(sftp.list_directories(remote_dir="/uploads/br_delete_me/"))
"""
