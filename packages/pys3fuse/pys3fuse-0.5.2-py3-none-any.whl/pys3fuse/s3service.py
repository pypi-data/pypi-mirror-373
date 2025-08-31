import configparser
import os
from os import stat_result
from pathlib import Path
from typing import IO

import boto3
from boto3.s3.transfer import TransferConfig
from boto3_type_annotations.s3 import Client
from botocore.response import StreamingBody
from pydantic_core import ValidationError

from . import pys3fuse_config_file
from .core.config import settings
from .core.log_config import logger
from .core.schemas import FileAttrs, NodeSchema, S3ListObjectsResponse

session = boto3.Session(
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
)


class S3Service:
    def __init__(
        self, client: Client, bucket: str, config_parser: configparser.ConfigParser
    ):
        self.client = client
        self.bucket = bucket

        if os.getenv("RUN_ENV") != "test":
            config_parser.read(pys3fuse_config_file)
            mt = config_parser["s3_transfer_config"].getint("multipart_threshold")
            xc = config_parser["s3_transfer_config"].getint("max_concurrency")
            mc = config_parser["s3_transfer_config"].getint("multipart_chunksize")
            self.config = TransferConfig(
                multipart_threshold=mt,
                max_concurrency=xc,
                multipart_chunksize=mc,
            )
        else:
            self.config = TransferConfig()

    def get_bucket_acl(self):
        return self.client.get_bucket_acl(Bucket=self.bucket)

    def list_objects(self) -> S3ListObjectsResponse:
        try:
            response = S3ListObjectsResponse(
                **self.client.list_objects_v2(Bucket=self.bucket)
            )
            return response
        except Exception as e:
            logger.exception(str(e), exc_info=e)
            raise

    def get_object(self, key: str) -> bytes:
        try:
            response: StreamingBody = self.client.get_object(
                Bucket=self.bucket, Key=key
            )["Body"]
            fileobj = response.read()
            return fileobj
        except Exception as e:
            logger.exception(str(e), exc_info=e)
            raise

    def head_object(self, key: str) -> NodeSchema:
        try:
            response = self.client.head_object(Bucket=self.bucket, Key=key)
        except Exception as e:
            logger.exception(str(e), exc_info=e)
            raise
        try:
            file_attrs = FileAttrs(**response["Metadata"])
        except ValidationError:
            file_attrs = None

        return NodeSchema(
            key=key,
            last_modified=response["LastModified"],
            size=response["ContentLength"],
            content_type=response["ContentType"],
            file_attrs=file_attrs,
        )

    def put_object(self, file_path: Path, stat: stat_result, mime_type: str):
        key = self.get_key_from_path(file_path)
        file_attrs = FileAttrs.from_stat_result(stat)
        try:
            with open(file_path, "br") as f:
                self.client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=f.read(),
                    ContentType=mime_type,
                    Metadata=file_attrs.model_dump(),
                )
        except FileNotFoundError:
            return

    def upload_fileobj(
        self, fileobj: IO, key: str, file_attrs: FileAttrs, mime_type: str
    ):
        try:
            self.client.upload_fileobj(
                Fileobj=fileobj,
                Bucket=self.bucket,
                Key=key,
                ExtraArgs={
                    "ContentType": mime_type,
                    "Metadata": file_attrs.model_dump(),
                },
                Config=self.config,
            )
        except Exception as e:
            logger.exception(str(e), exc_info=e)
            return

    def delete_objects(self, *keys) -> None:
        if not keys:  # pragma: no cover
            return
        delete = {"Objects": [{"Key": k} for k in keys]}
        try:
            self.client.delete_objects(Bucket=self.bucket, Delete=delete)
        except Exception as e:
            logger.exception(str(e), exc_info=e)
            raise

    def copy_object(self, key: str, attrs: FileAttrs, mime_type: str):
        try:
            self.client.copy_object(
                Bucket=self.bucket,
                CopySource={"Bucket": self.bucket, "Key": key},
                Key=key,
                ContentType=mime_type,
                Metadata=attrs.model_dump(),
                MetadataDirective="REPLACE",
            )
        except Exception as e:
            logger.exception(str(e), exc_info=e)
            raise

    def rename_object(self, old_key: str, new_key: str):
        try:
            self.client.copy_object(
                Bucket=self.bucket,
                CopySource={"Bucket": self.bucket, "Key": old_key},
                Key=new_key,
            )
            self.client.delete_object(Bucket=self.bucket, Key=old_key)
        except Exception as e:
            logger.exception(str(e))
            raise

    def download_fileobj(self, fileobj: IO, key: str):
        try:
            self.client.download_fileobj(
                Fileobj=fileobj,
                Bucket=self.bucket,
                Key=key,
                Config=self.config,
            )
        except Exception as e:
            logger.exception(str(e), exc_info=e)
            raise

    @staticmethod
    def get_key_from_path(file_path: Path) -> str:
        _, *dirs, _ = file_path.parts
        key = f"{'/'.join(dirs)}/{file_path.name}"
        return key
