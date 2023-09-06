import boto3

import tempfile
import logging

from botocore.exceptions import NoCredentialsError
from botocore.client import BaseClient

from pathlib import Path
from os import PathLike
from typing import List

from .config import Config


class S3Client:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        path: str,
        final_dir: PathLike,
        delete: bool = False,
        **kwargs,
    ):
        self.s3 = self.connect(access_key, secret_key, **kwargs)
        self.bucket_name = bucket_name
        self.path = path
        self.final_dir = Path(final_dir)
        self.delete = delete

        self.final_dir.mkdir(exist_ok=True)
        assert (
            self.final_dir.is_dir()
        ), "Final directory does not exist or is not a directory"

    @classmethod
    def from_config(cls, config_file: PathLike, section: str = "S3") -> "S3Client":
        config = Config(config_file, section)
        return cls(
            config.access_key,
            config.secret_key,
            config.bucket_name,
            config.path,
            config.final_dir,
            config.delete,
            **config.kwargs,
        )

    def connect(self, access_key: str, secret_key: str, **kwargs) -> BaseClient:
        logging.debug("Connecting to S3")

        s3 = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            **kwargs,
        )
        return s3

    def list_files(self) -> List[str]:
        logging.debug("Listing files in S3")

        return [
            obj["Key"]
            for obj in self.s3.list_objects(
                Bucket=self.bucket_name, Prefix=self.path
            ).get("Contents", [])
        ]

    def download_files(self) -> bool:
        try:
            logging.debug("Downloading files")
            for obj in self.list_files():
                if not self._exists_local(obj):
                    self.download_file(obj)
                else:
                    logging.warn(f"File already exists locally, skipping: {obj}")

        except Exception as e:
            print(e)
            return False

        return True

    def download_file(self, filename: str) -> None:
        logging.info(f"Downloading file from S3: {filename}")
        with tempfile.TemporaryFile() as temp_file:
            self.s3.download_fileobj(self.bucket_name, filename, temp_file)
            temp_file.seek(0)
            self.move_file(temp_file, filename)

    def move_file(self, temp_file: tempfile.TemporaryFile, filename: str) -> None:
        logging.debug(f"Moving file to final directory: {filename}")
        
        with open(self.final_dir / Path(filename).name, "wb") as final_file:
            final_file.write(temp_file.read())

    def delete_files(self) -> None:
        logging.debug("Deleting files from S3")
        for obj in self.list_files():
            self.delete_file(obj)

    def delete_file(self, filename) -> None:
        logging.info(f"Deleting file from S3: {filename}")
        self.s3.delete_object(Bucket=self.bucket_name, Key=filename)

    def process_files(self) -> None:
        logging.debug("Processing files")

        if self.download_files() and self.delete:
            self.delete_files()

    def _exists_local(self, filename: str) -> bool:
        logging.debug(f"Checking if file exists locally: {filename}")

        return Path(self.final_dir / Path(filename).name).exists()
