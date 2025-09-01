import io
import logging
import mimetypes
import os
import sys
from datetime import datetime

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError, NoCredentialsError

from ms_utils.logging_lib import Logger

logger = Logger.setup_logger(__name__, level=logging.INFO)  # logging.DEBUG
logger.propagate = False


class ProgressPercentage:
    def __init__(self, file_size, object_name, bar_length=30):
        self._file_size = file_size / 1024 / 1024  # to Mo
        self._seen_so_far = 0
        self._object_name = object_name
        self._bar_length = bar_length

    def __call__(self, bytes_amount):
        self._seen_so_far += bytes_amount / 1024 / 1024  # to Mo
        percentage = (self._seen_so_far / self._file_size) * 100
        bar_filled_length = int(
            self._bar_length * self._seen_so_far // self._file_size
        )
        bar = "█" * bar_filled_length + "-" * (
            self._bar_length - bar_filled_length
        )
        sys.stdout.write(
            f"\r{self._object_name}: |{bar}| {self._seen_so_far:.2f} Mo / "
            f"{self._file_size:.2f} Mo ({percentage:.2f}%)"
        )
        sys.stdout.flush()
        if self._seen_so_far >= self._file_size:
            sys.stdout.write("\n")
            sys.stdout.flush()


class S3BucketClient:
    def __init__(
        self,
        bucket_type: str,
        endpoint_url: str = os.getenv("S3_ENDPOINT"),
        region_name: str = "fr-par",
        aws_access_key_id: str = os.getenv("S3_ACCESS_KEY_ID"),
        aws_secret_access_key: str = os.getenv("S3_SECRET_ACCESS_KEY"),
    ):
        """
        Initialize the S3BucketClient.

        Args:
            bucket_type: The type of the S3 bucket.
            endpoint_url: The custom endpoint URL for the S3 service.
            region_name: The Bucket region name.
        """
        self.bucket_type = bucket_type

        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url,
        )

    def test_connection(self) -> bool:
        """
        Test the connection to the S3 bucket.

        Returns:
            True if connection is successful, else False.
        """
        try:
            self.s3.list_buckets()
            return True
        except NoCredentialsError:
            print("Credentials not available")
            return False
        except ClientError as e:
            print(f"ClientError: {e}")
            return False

    def upload_file(
        self,
        file: str | io.BytesIO,
        bucket_name: str,
        object_name: str | None = None,
        metadata: dict | None = None,
    ) -> bool:
        """
        Upload a file to the S3 bucket.

        Args:
            file: The path to the file to upload or a BytesIO object representing the file.
            bucket_name: The name of the main bucket you want to put the object in
                (i.e. `bucket_name="test"` and `object_name="folder/myfile.json"`
                will put the file inside `"/test/folder/myfile.json")
            object_name: The S3 object name. If not specified, a default name is used.
            metadata: Metadata to set for the file.

        Returns:
            True if file was uploaded, else False.

        Raises:
            ValueError: If file is not a str or BytesIO.
        """
        if not isinstance(file, (str, io.BytesIO)):
            raise ValueError("file must be a str (file path) or BytesIO")

        if object_name is None:
            object_name = (
                file if isinstance(file, str) else "default_object_name"
            )

        if metadata is None:
            metadata = {}

        # Extract file information
        if isinstance(file, str):
            file_size = os.path.getsize(file)
            file_type, _ = mimetypes.guess_type(file)
            file_creation_time = datetime.fromtimestamp(
                os.path.getctime(file)
            ).isoformat()
            file_name = os.path.basename(file)

            # Populate metadata
            metadata.update(
                {
                    "FileName": file_name,
                    "FileSize": f"{file_size / (1024 * 1024):.2f} MB",
                    "FileType": file_type or "application/octet-stream",
                    "CreationTime": file_creation_time,
                }
            )
        else:
            file.seek(0, io.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            metadata.update(
                {
                    "FileSize": f"{file_size / (1024 * 1024):.2f} MB",
                    "FileType": "application/octet-stream",  # Default to binary file
                    "CreationTime": datetime.now().isoformat(),
                }
            )

        extra_args = {"Metadata": metadata}

        try:
            logger.info(
                f"Trying to upload file : "
                f"{file if isinstance(file, str) else 'BytesIO object'}"
            )
            progress_callback = ProgressPercentage(file_size, object_name)
            config = TransferConfig(use_threads=False)
            if isinstance(file, str):
                self.s3.upload_file(
                    file,
                    bucket_name,
                    object_name,
                    Config=config,
                    Callback=progress_callback,
                    ExtraArgs=extra_args,
                )
            else:
                self.s3.upload_fileobj(
                    file,
                    bucket_name,
                    object_name,
                    Config=config,
                    Callback=progress_callback,
                    ExtraArgs=extra_args,
                )
        except FileNotFoundError:
            logger.error("The file was not found")
            return False
        except NoCredentialsError:
            logger.error("Credentials not available")
            return False
        except ClientError as e:
            logger.error(f"ClientError: {e}")
            return False
        return True

    def download_file(
        self, bucket_name: str, object_name: str, save_to: str | None = None
    ) -> bool | io.BytesIO:
        """
        Download a file from the S3 bucket.

        Args:
            bucket_name: The name of the main bucket you want to get the object from
                (i.e. `bucket_name="test"` and `object_name="folder/myfile.json"`
                will download the file from `"/test/folder/myfile.json")
            object_name: The S3 object name.
            save_to: The local path to save the file. If not specified,
                     the file is returned as a BytesIO object.

        Returns:
            True if file was saved locally, else BytesIO object of the file content.

        Raises:
            ValueError: If save_to is not a str or None.
        """
        if save_to is not None and not isinstance(save_to, str):
            raise ValueError("save_to must be a str or None")

        try:
            logger.info(f"Trying to download file : {object_name}")
            # Récupérer la taille de l'objet
            obj = self.s3.head_object(Bucket=bucket_name, Key=object_name)
            file_size = obj["ContentLength"]

            progress_callback = ProgressPercentage(file_size, object_name)
            config = TransferConfig(use_threads=False)

            if save_to:
                self.s3.download_file(
                    bucket_name,
                    object_name,
                    save_to,
                    Config=config,
                    Callback=progress_callback,
                )
                return True
            else:
                file_obj = io.BytesIO()
                self.s3.download_fileobj(
                    bucket_name,
                    object_name,
                    file_obj,
                    Config=config,
                    Callback=progress_callback,
                )
                file_obj.seek(0)  # Reset the file pointer to the beginning
                return file_obj
        except FileNotFoundError:
            logger.error("The file was not found")
            return False
        except NoCredentialsError:
            logger.error("Credentials not available")
            return False
        except ClientError as e:
            logger.error(f"ClientError: {e}")
            return False

    def delete_file(self, bucket_name: str, object_name: str) -> bool:
        """
        Delete a file from the S3 bucket.

        Args:
            bucket_name: The name of the main bucket you want to delete the object from
                (i.e. `bucket_name="test"` and `object_name="folder/myfile.json"`
                will delete the file from `"/test/folder/myfile.json")
            object_name: The S3 object name.

        Returns:
            True if file was deleted, else False.
        """
        try:
            logger.info(f"Trying to delete file: {object_name}")
            self.s3.delete_object(Bucket=bucket_name, Key=object_name)
            return True
        except NoCredentialsError:
            logger.error("Credentials not available")
            return False
        except ClientError as e:
            logger.error(f"ClientError: {e}")
            return False

    def set_file_permission(
        self, bucket_name: str, object_name: str, permission: str
    ) -> bool:
        """
        Set permissions for a file in the S3 bucket.

        Args:
            bucket_name: The name of the main bucket you want to set the object permissions
                (i.e. `bucket_name="test"` and `object_name="folder/myfile.json"`
                will update permissions of `"/test/folder/myfile.json")
            object_name: The S3 object name.
            permission: The permission to set (e.g., 'public-read').

        Returns:
            True if permission was set, else False.
        """
        try:
            logger.info(
                f"Setting permission '{permission}' for file: {object_name}"
            )
            self.s3.put_object_acl(
                Bucket=bucket_name, Key=object_name, ACL=permission
            )
            return True
        except NoCredentialsError:
            logger.error("Credentials not available")
            return False
        except ClientError as e:
            logger.error(f"ClientError: {e}")
            return False

    def get_file_metadata(
        self, bucket_name: str, object_name: str
    ) -> dict | None:
        """
        Get metadata of a file in the S3 bucket.

        Args:
            bucket_name: The name of the main bucket you want to get the object metadata from
                (i.e. `bucket_name="test"` and `object_name="folder/myfile.json"`
                will get metadata of `"/test/folder/myfile.json")
            object_name: The S3 object name.

        Returns:
            Metadata of the file if found, else None.
        """
        try:
            logger.info(f"Getting metadata for file: {object_name}")
            response = self.s3.head_object(Bucket=bucket_name, Key=object_name)
            return response["Metadata"]
        except NoCredentialsError:
            logger.error("Credentials not available")
            return None
        except ClientError as e:
            logger.error(f"ClientError: {e}")
            return None

    def list_files(self, bucket_name: str) -> list:
        """
        List files in the S3 bucket.

        Args:
            bucket_name: The name of the main bucket you want to list files from
                (i.e. `bucket_name="test"` will list files of `"/test/*")

        Returns:
            A list of file names in the bucket.
        """
        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name)
            if "Contents" in response:
                return [obj["Key"] for obj in response["Contents"]]
            else:
                return []
        except ClientError as e:
            logger.error(f"ClientError: {e}")
            return []

    def list_buckets(self) -> list:
        """
        List all buckets in the S3 service.

        Returns:
            A list of bucket names, or an empty list if the request failed.
        """
        try:
            response = self.s3.list_buckets()
            if "Buckets" in response:
                return [bucket["Name"] for bucket in response["Buckets"]]
            else:
                logger.info("No buckets found in the response.")
                return []
        except NoCredentialsError:
            logger.error("Credentials not available")
            return []
        except ClientError as e:
            logger.error(f"ClientError: {e}")
            return []
