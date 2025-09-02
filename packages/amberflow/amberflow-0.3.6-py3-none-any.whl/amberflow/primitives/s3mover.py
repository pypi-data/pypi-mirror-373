from logging import Logger
from pathlib import Path

import boto3

from amberflow.primitives import dirpath_t, _run_command, BaseDataMover

__all__ = ("S3Mover",)


class S3Mover(BaseDataMover):
    """Data mover that uses AWS S3 via the boto3 library."""

    def __init__(self, bucket_name: str, s3_client=None):
        """
        Initializes the S3Mover.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_client: An optional pre-configured boto3 S3 client.
                       If not provided, a new client will be created.
        """
        self.bucket_name = bucket_name
        self.s3_client = s3_client or boto3.client("s3")

    def upload(self, local_path: dirpath_t, remote_path: dirpath_t, logger: Logger, **kwargs) -> None:
        """
        Uploads a directory from a local path to an S3 prefix, mimicking 'aws s3 sync --delete'.

        Args:
            local_path (dirpath_t): The local directory to upload from.
            remote_path (dirpath_t): The destination prefix (folder) in the S3 bucket.
            logger (Logger): Logger for outputting information.
        """
        logger.info(f"Uploading from '{local_path}' to 's3://{self.bucket_name}/{remote_path}' using boto3.")

        local_p = Path(local_path)

        # 1. Upload all local files
        for local_file_path in local_p.rglob("*"):
            if local_file_path.is_file():
                # Create the relative path to build the S3 key
                relative_path = local_file_path.relative_to(local_p)
                s3_key = str(Path(remote_path) / relative_path)

                try:
                    logger.debug(f"Uploading {local_file_path} to {s3_key}")
                    self.s3_client.upload_file(str(local_file_path), self.bucket_name, s3_key)
                except Exception as e:
                    logger.error(f"Failed to upload {local_file_path}: {e}")
                    raise

        # 2. Handle --delete: Remove remote files that are not present locally
        logger.info("Checking for remote files to delete...")
        remote_keys = set()
        paginator = self.s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=str(remote_path))
        for page in pages:
            if "Contents" in page:
                for obj in page["Contents"]:
                    remote_keys.add(obj["Key"])

        for s3_key in remote_keys:
            relative_key_path = Path(s3_key).relative_to(remote_path)
            local_equivalent_path = local_p / relative_key_path
            if not local_equivalent_path.exists():
                logger.info(f"Deleting remote file not found locally: {s3_key}")
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)

        logger.info("Upload sync complete.")

    def download(self, remote_path: dirpath_t, local_path: dirpath_t, logger: Logger, **kwargs) -> None:
        """
        Downloads a directory from an S3 prefix to a local path, mimicking 'aws s3 sync --delete'.

        Args:
            remote_path (dirpath_t): The source prefix (folder) in the S3 bucket.
            local_path (dirpath_t): The local directory to download to.
            logger (Logger): Logger for outputting information.
        """
        logger.info(f"Downloading from 's3://{self.bucket_name}/{remote_path}' to '{local_path}' using boto3.")
        local_p = Path(local_path)

        # 1. Download all remote files
        paginator = self.s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=str(remote_path))

        remote_keys_relative = set()
        for page in pages:
            if "Contents" not in page:
                continue
            for obj in page["Contents"]:
                s3_key = obj["Key"]
                relative_path = Path(s3_key).relative_to(remote_path)
                remote_keys_relative.add(str(relative_path))

                local_file_path = local_p / relative_path

                # Ensure the local directory exists
                local_file_path.parent.mkdir(parents=True, exist_ok=True)

                try:
                    logger.debug(f"Downloading {s3_key} to {local_file_path}")
                    self.s3_client.download_file(self.bucket_name, s3_key, str(local_file_path))
                except Exception as e:
                    logger.error(f"Failed to download {s3_key}: {e}")
                    raise

        # 2. Handle --delete: Remove local files that are not present remotely
        logger.info("Checking for local files to delete...")
        for local_file in local_p.rglob("*"):
            if local_file.is_file():
                relative_local_file = str(local_file.relative_to(local_p))
                if relative_local_file not in remote_keys_relative:
                    logger.info(f"Deleting local file not found remotely: {local_file}")
                    local_file.unlink()

        logger.info("Download sync complete.")
