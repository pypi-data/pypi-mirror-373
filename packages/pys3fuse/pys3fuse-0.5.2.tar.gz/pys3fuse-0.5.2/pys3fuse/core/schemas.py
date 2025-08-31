from datetime import datetime
from os import stat_result
from pathlib import Path
from typing import Any, List, Literal, Self, Union

from pydantic import BaseModel


class FileAttrs(BaseModel):
    st_atime: float
    st_ctime: float
    st_gid: int | None = None
    st_mode: int | None = None
    st_mtime: float
    st_nlink: int = 1
    st_size: int
    st_uid: int | None = None

    def model_dump(self, for_fs: bool = False) -> dict[str, Any]:  # noqa
        if for_fs:  # pragma: no cover
            return super().model_dump()

        d = super().model_dump(exclude_none=True)
        for k, v in d.items():
            d[k] = str(v)
        return d

    @classmethod
    def from_stat_result(cls, stat_res: stat_result) -> Self:
        return cls(
            st_atime=stat_res.st_atime,
            st_ctime=stat_res.st_ctime,
            st_mtime=stat_res.st_mtime,
            st_mode=stat_res.st_mode,
            st_gid=stat_res.st_gid,
            st_uid=stat_res.st_uid,
            st_nlink=stat_res.st_nlink,
            st_size=stat_res.st_size,
        )


class OwnerModel(BaseModel):
    DisplayName: str | None = None
    ID: str | None = None


class RestoreStatusModel(BaseModel):
    IsRestoreInProgress: bool
    RestoreExpiryDate: datetime | None = None


class CommonPrefixesModel(BaseModel):
    Prefix: str


class Content(BaseModel):
    Key: str
    LastModified: datetime
    ETag: str | None = None
    ChecksumAlgorithm: (
        list[
            Literal[
                "CRC32",
                "CRC32C",
                "SHA1",
                "SHA256",
                "CRC64NVME",
            ]
        ]
        | None
    ) = None
    ChecksumType: Literal["COMPOSITE", "FULL_OBJECT"] | None = None
    Size: int
    StorageClass: (
        Literal[
            "STANDARD",
            "REDUCED_REDUNDANCY",
            "GLACIER",
            "STANDARD_IA",
            "ONEZONE_IA",
            "INTELLIGENT_TIERING",
            "DEEP_ARCHIVE",
            "OUTPOSTS",
            "GLACIER_IR",
            "SNOW",
            "EXPRESS_ONEZONE",
            "FSX_OPENZFS",
        ]
        | None
    ) = None
    Owner: OwnerModel | None = None
    RestoreStatus: RestoreStatusModel | None = None


class S3ListObjectsResponse(BaseModel):
    ResponseMetadata: dict | None = None
    IsTruncated: bool
    Contents: list[Content] | None = None
    Name: str
    Prefix: str | None = None
    Delimiter: str | None = None
    MaxKeys: int
    CommonPrefixes: List[CommonPrefixesModel] | None = None
    EncodingType: Literal["url"] | None = None
    KeyCount: int
    ContinuationToken: str | None = None
    NextContinuationToken: str | None = None
    StartAfter: str | None = None
    RequestCharged: Literal["requester"] | None = None


class NodeSchema(BaseModel):
    key: str
    last_modified: datetime
    size: int
    abspath: Path | None = None
    content_type: str | None = None
    file_attrs: Union["FileAttrs", None] = None
