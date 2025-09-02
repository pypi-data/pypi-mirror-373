import logging
import os
import pathlib
import time
import uuid
from typing import Any, Generator, List, Optional

from minio import Minio, S3Error

from .exceptions import (
    S3ConnectionException,
    S3InitException,
    S3InputException,
    S3DownloadException
)

logger = logging.getLogger("tools.s3")


class S3Files:
    """ A class to manage file uploads and downloads from/to S3.
    """

    def __init__(
            self,
            url: Optional[str] = None,
            access_key: Optional[str] = None,
            secret_key: Optional[str] = None,
            bucket: Optional[str] = None,
            **minio_kwargs: dict[str, Any],
    ):
        if not url:
            raise S3InitException("S3 URL not set!")
        if not access_key:
            raise S3InitException("S3 access key not set!")
        if not secret_key:
            raise S3InitException("S3 secret key not set!")
        if not bucket:
            raise S3InitException("Bucket not set!")
        self.bucket = bucket
        self.minio_client = Minio(
            url,
            access_key=access_key,
            secret_key=secret_key,
            **minio_kwargs
        )
        # Check S3 connection
        try:
            self.minio_client.bucket_exists(bucket)
        except Exception as e:
            raise S3ConnectionException(f"Error connecting to bucket: {e}")

    def _put_file(self, file_path: str, s3_path_name: str):
        if not os.path.exists(file_path):
            raise S3InputException(f"File '{file_path}' does not exist in file system!")
        return self.minio_client.fput_object(self.bucket, s3_path_name, file_path)

    def list(self, prefix: Optional[str] = "", recursive: Optional[bool] = True) -> List:
        """Lists all available directories or files in S3 bucket.
        :param: prefix str: Limits the listing to a given prefix.
        :param: recursive bool: List files recursively.
        :return: List of file paths in S3.
        """
        list_of_objects = self.minio_client.list_objects(self.bucket, prefix=prefix, recursive=recursive)
        list_of_objects = [o.object_name for o in list_of_objects]
        return list_of_objects

    def delete(self, path: str) -> bool:
        """Deletes file in S3.
        :param: path str: Path of the file in S3 to be deleted.
        :return: True.
        """
        list_of_objects = self.minio_client.list_objects(self.bucket, prefix=path, recursive=True)
        list_of_objects = [o.object_name for o in list_of_objects]
        for path_to_delete in list_of_objects:
            self.minio_client.remove_object(self.bucket, path_to_delete)
        return True

    def download(self, path: str, download_dir: Optional[str] = ".") -> Generator[str, str, str]:
        """Downloads file or folder from S3.
        :param: path str: Path to the file or folder in S3.
        :param: download_dir str: Directory to download the files and folders into.
        :return: Generate listing of local paths of the downloaded files. 
        """
        list_of_objects = list(self.minio_client.list_objects(self.bucket, prefix=path, recursive=True))
        for minio_object in list_of_objects:
            full_path = os.path.join(download_dir, minio_object.object_name)
            self._download_file(minio_object.object_name, full_path)
            yield full_path

    def _download_file(self, path, download_dir=".", max_retries=3) -> str:
        """Download a single file with retry and resume support."""
        attempts = 0

        while attempts < max_retries:
            try:
                stat = self.minio_client.stat_object(self.bucket, path)
                file_size = stat.size
                temp_path = download_dir + ".part"
                pathlib.Path(temp_path).parent.mkdir(parents=True, exist_ok=True)

                # Check if a partial file exists
                downloaded_size = os.path.getsize(temp_path) if os.path.exists(temp_path) else 0

                if downloaded_size >= file_size:
                    os.rename(temp_path, download_dir)  # Rename to final filename
                    logger.info(f"Completed: {path}")
                    return str(pathlib.Path(download_dir) / path)

                logger.info(f"Downloading {path} ({downloaded_size}/{file_size} bytes)...")

                # Open file in append mode to resume download
                with open(temp_path, "ab") as f:
                    response = self.minio_client.get_object(self.bucket, path, offset=downloaded_size)
                    for data in response.stream(32 * 1024):  # 32KB chunks
                        f.write(data)
                    response.close()
                    response.release_conn()

                os.rename(temp_path, download_dir)  # Rename temp to final
                logger.info(f"Downloaded: {path}")
                return str(pathlib.Path(download_dir) / path)

            except S3Error as e:
                logger.info(f"Error downloading {path}, attempt {attempts + 1}: {e}")
                attempts += 1
                time.sleep(2 ** attempts)  # Exponential backoff

        raise S3DownloadException(f"Failed to download {path} after {max_retries} attempts.")

    def upload(self, path: str, prefix: Optional[str] = "") -> str:
        """Uploads file or folder to S3 bucket.
        :param: path str: Path to the file to upload in local file system.
        :param: prefix str: Optional prefix for S3 path.
        :returns: File path of the uploaded file or folder in S3.
        """
        # Manage directories
        if os.path.isdir(path):
            s3_path_prefix = f"{prefix}{uuid.uuid4().hex}"
            for root, _, files in os.walk(path):
                for file in files:
                    relative_prefix = root.removeprefix(path).lstrip("/")
                    file_path = os.path.join(root, file)
                    extension = file.split(".")[-1]
                    s3_path_name = os.path.join(s3_path_prefix, relative_prefix, file)
                    self._put_file(file_path, s3_path_name)
            return s3_path_prefix
        # Manage single files
        else:
            path_name = os.path.split(path)[-1]
            extension = path_name.split(".")[-1]
            s3_path_name = f"{prefix}{uuid.uuid4().hex}.{extension}"
            self._put_file(path, s3_path_name)
            return s3_path_name
