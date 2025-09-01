import os
import glob
from google.cloud import storage
from liveramp_automation.utils.log import Logger


class BucketHelper:
    def __init__(self, project_id, bucket_name):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.client = storage.Client(project=self.project_id)
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_file(self, local_file_path, cloud_blob_path):
        """Upload a local file or files under the folder to the cloud storage bucket.

        :param local_file_path: Local file path for uploading.
        :param cloud_blob_path: Destination blob path within the bucket.
        :return: None
        """
        try:
            Logger.debug("Start upload_file")
            Logger.debug(f"File = {local_file_path} on Path = {cloud_blob_path}")

            if not os.path.exists(local_file_path):
                Logger.error(f"Local file path does not exist: {local_file_path}")

            if os.path.isfile(local_file_path):
                blob = self.bucket.blob(os.path.join(cloud_blob_path, os.path.basename(local_file_path)))
                blob.upload_from_filename(local_file_path)
                Logger.debug(f"Item Uploaded on Path = {local_file_path}")

            for item in glob.glob(os.path.join(local_file_path, '*')):
                if os.path.isfile(item):
                    if item == ".keep":
                        continue
                    blob = self.bucket.blob(os.path.join(cloud_blob_path, os.path.basename(item)))
                    blob.upload_from_filename(item)
                else:  # Handle directories and their contents recursively
                    Logger.debug(f"Item = {item}")
                    Logger.debug(f"Os.path.basename(item) = {os.path.basename(item)}")
                    self.upload_file(item, os.path.join(cloud_blob_path, os.path.basename(item)))

        except Exception as e:
            Logger.error(f"Error uploading file: {str(e)}")

    def check_file_exists(self, file_path):
        """Check if a file exists in the bucket.

        :param file_path: Path to the bucket file.
        :return: Boolean.
        """

        Logger.debug("Start check_file_exists")
        Logger.debug(f"Path = {file_path}")
        blob = self.bucket.blob(file_path)
        result = blob.exists()
        Logger.debug(f"Result = {result}")
        Logger.debug("Finish check_file_exists")
        return result

    def download_files(self, source_blob_name, destination_file_path):
        """Download a file or files under the folder from the bucket.

        :param source_blob_name: Path to the bucket file.
        :param destination_file_path: Path to the download file.
        :return: A list of downloaded file name."""
        try:
            Logger.debug("Start download_files")
            Logger.debug(f"File = {source_blob_name} download on Path = {destination_file_path}")

            if not os.path.exists(destination_file_path):
                os.makedirs(destination_file_path)  # Create the destination directory if it doesn't exist

            downloaded_files = []

            blobs = self.bucket.list_blobs(prefix=source_blob_name)
            for blob in blobs:
                if blob.name.endswith("/"):
                    continue

                # Check if the destination file already exists
                file_name = os.path.join(destination_file_path, os.path.basename(blob.name))
                if os.path.exists(file_name):
                    Logger.warning(f"File already exists: {file_name}")
                    continue

                blob.download_to_filename(file_name)
                downloaded_files.append(file_name)
                Logger.debug(f"Downloaded file: {file_name}")

            Logger.debug("Finish download_file")
            return downloaded_files
        except Exception as e:
            Logger.error(f"Error downloading file: {str(e)}")
            return []

    def download_files_with_structure(self, source_blob_name, destination_file_path):
        """Download a file from the bucket while preserving folder structure.

        :param source_blob_name: Path to the bucket file.
        :param destination_file_path: Path to the download file.
        :return: A list of downloaded file paths."""
        try:
            Logger.debug("Start download_files_with_structure")
            Logger.debug(f"File = {source_blob_name} download on Path = {destination_file_path}")

            if not os.path.exists(destination_file_path):
                os.makedirs(destination_file_path)  # Create the destination directory if it doesn't exist

            downloaded_files = []

            blobs = self.bucket.list_blobs(prefix=source_blob_name)
            for blob in blobs:
                if blob.name.endswith("/"):
                    continue

                    # Extract the relative path from the blob name, preserving folder structure
                relative_path = os.path.relpath(blob.name, source_blob_name)
                local_file_path = os.path.join(destination_file_path, relative_path)
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                if os.path.exists(local_file_path):
                    Logger.warning(f"File already exists: {local_file_path}")
                    continue

                blob.download_to_filename(local_file_path)
                downloaded_files.append(local_file_path)
                Logger.debug(f"Downloaded file: {local_file_path}")

            Logger.debug("Finish download_file")
            return downloaded_files
        except Exception as e:
            Logger.error(f"Error downloading file: {str(e)}")
            return []

    def list_files_with_substring(self, substring):
        """Gets a list of files that contain a substring in the name.

        :param substring: string to find on the file name.
        :return: array with the match list."""

        Logger.debug("Start list_files_with_substring")
        Logger.debug(f"Substring = {substring}")
        blobs = self.bucket.list_blobs()
        matching_files = []

        for blob in blobs:
            if substring in blob.name:
                Logger.debug(f"Found Matching File = {blob.name}")
                matching_files.append(blob.name)

        Logger.debug(f"Result = {matching_files}")
        Logger.debug("Finish list_files_with_substring")
        return matching_files

    def get_total_rows(self, file_path):
        """Gets the total number of rows in a file.

        :param file_path: path of the file.
        :return: integer with the total row."""

        Logger.debug("Start get_total_rows")
        Logger.debug(f"Path = {file_path}")
        blob = self.bucket.blob(file_path)
        content = blob.download_as_text()
        total_rows = len(content.split('\n'))
        Logger.debug(f"Result = {total_rows}")
        Logger.debug("Finish get_total_rows")
        return total_rows

    def read_file_content(self, file_path):
        """Gets the entire content of a file.

        :param file_path: path of the file.
        :return: string content of the file."""

        Logger.debug("Start read_file_content")
        Logger.debug(f"Path = {file_path}")
        blob = self.bucket.blob(file_path)
        content = blob.download_as_text()
        Logger.debug(f"Result = {content}")
        Logger.debug("Finish read_file_content")
        return content

    def read_file_lines(self, file_path, num_lines):
        """Gets the first n lines of a file.

        :param file_path: path of the file.
        :param num_lines: number of fist lines.
        :return: string content of the file."""

        Logger.debug("Start read_file_lines")
        Logger.debug(f"First {num_lines} of the Path = {file_path}")
        blob = self.bucket.blob(file_path)
        content = blob.download_as_text()
        lines = content.split('\n')
        selected_lines = lines[:num_lines]
        result = '\n'.join(selected_lines)
        Logger.debug(f"Result = {result}")
        Logger.debug("Finish read_file_content")
        return result
