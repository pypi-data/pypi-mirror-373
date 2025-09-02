import os
import threading
from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, NamedTuple, Sized

from rich.prompt import Prompt

from .core.log_config import logger
from .core.schemas import FileAttrs, NodeSchema
from .core.utils import get_mime_type
from .s3service import S3Service


class SyncResult(NamedTuple):
    created_files: list[str] | set[str] = []
    updated_files: list[str] | set[str] = []
    deleted_files: list[str] | set[str] = []

    @property
    def created(self) -> int:
        return len(self.created_files)

    @property
    def updated(self):
        return len(self.updated_files)

    @property
    def deleted(self) -> int:
        return len(self.deleted_files)

    @property
    def synced(self) -> bool:
        return bool(self.created or self.updated or self.deleted)


class Syncer:
    def __init__(
        self,
        service: S3Service,
        root: Path,
        config_parser: ConfigParser,
    ):
        self.service = service
        self.root = root
        self.config_parser = config_parser
        self.lock = threading.Lock()

    def sync_initial(self, force_delete: bool = False):
        """Sync local or S3 respecting the dirtiness"""
        logger.debug("Getting nodes from S3...")

        s3_nodes = self._get_node_schema_from_bucket()
        s3_keys = {node.abspath for node in s3_nodes}
        source_keys = self._get_all_files(self.root)

        if self.config_parser["sync"]["dirty"] == "true":
            sync_result = self._sync_s3_with_local_objects(
                s3_nodes, s3_keys, source_keys, force_delete=force_delete
            )
            if sync_result.synced:
                logger.debug(
                    "Local filesystem is dirty. We have to sync S3 with here so"
                    " that local changes would appear on S3.",
                )
                logger.info(f"Syncing S3 with {self.root.name}...")
        else:
            sync_result = self._sync_local_with_s3_objects(
                s3_nodes, s3_keys, source_keys, force_delete=force_delete
            )
            if sync_result.synced:  # pragma: no cover
                logger.debug(
                    "Local filesystem is clean but S3 has changed so we have "
                    "to sync here with S3 so that S3 changes would appear here.",
                )
                logger.info(f"Syncing {self.root.name} with S3...")

        self.config_parser["sync"]["dirty"] = "false"
        if sync_result.synced:
            logger.info("Synced.")
            logger.info(sync_result)
        else:
            logger.info("Everything is up to date.")

    def sync_local(self, force_delete: bool = False) -> SyncResult:
        """Sync the local fs with S3 changes"""
        with self.lock:
            s3_nodes = self._get_node_schema_from_bucket()
            s3_paths = {node.abspath for node in s3_nodes}
            source_paths = self._get_all_files(self.root)

            return self._sync_local_with_s3_objects(
                s3_nodes, s3_paths, source_paths, force_delete
            )

    def sync_s3(self, force_delete: bool = False) -> SyncResult:
        """Sync S3 with the local fs changes"""
        with self.lock:
            s3_nodes = self._get_node_schema_from_bucket()
            s3_paths = {node.abspath for node in s3_nodes}
            source_paths = self._get_all_files(self.root)

            return self._sync_s3_with_local_objects(
                s3_nodes, s3_paths, source_paths, force_delete
            )

    def create_on_s3(self, path: Path) -> SyncResult:
        """A file has been created in local FS"""
        with self.lock:
            try:
                self._create_object_from_here_on_s3(path)
            except FileNotFoundError:
                return SyncResult()
        return SyncResult(created_files=[str(path)])

    def delete_on_s3(self, path: Path) -> SyncResult:
        """A file has been deleted in local FS"""
        with self.lock:
            key = self.service.get_key_from_path(path)
            self.service.delete_objects(key)
        return SyncResult(deleted_files=[str(path)])

    def update_attrs_on_s3(self, path: Path, attrs: FileAttrs):
        """Updates Attrs in metadata of the object"""
        mime_type = get_mime_type(path)

        with self.lock:
            key = self.service.get_key_from_path(path)
            self.service.copy_object(key, attrs, mime_type)
        return SyncResult(updated_files=[str(path)])

    def rename_on_s3(self, old_path: Path, new_path: Path) -> SyncResult:
        """Rename the object on s3"""
        with self.lock:
            old_key = self.service.get_key_from_path(old_path)
            new_key = self.service.get_key_from_path(new_path)
            self.service.rename_object(old_key, new_key)
        return SyncResult(updated_files=[str(old_path), str(new_path)])

    def update_on_s3(self, path: Path):
        with self.lock:
            try:
                self._create_object_from_here_on_s3(path)
            except FileNotFoundError:
                return SyncResult()
        return SyncResult(updated_files=[str(path)])

    def _sync_local_with_s3_objects(
        self,
        s3_nodes: list[NodeSchema],
        s3_paths: set[Path],
        source_paths: set[Path],
        force_delete: bool = False,
    ) -> SyncResult:
        """Update, Delete and Create files in local FS from S3"""
        to_be_updated = s3_paths & s3_paths
        to_update_nodes = list(filter(lambda n: n.abspath in to_be_updated, s3_nodes))

        try:
            with ThreadPoolExecutor(
                self._get_thread_count(to_update_nodes),
                "sync_update",
            ) as executor:
                for node in to_update_nodes:
                    executor.submit(self._update_object_in_local_from_s3, node)
        except ValueError:  # pragma: no cover
            pass

        to_be_created = s3_paths - source_paths
        to_create_nodes = list(filter(lambda n: n.abspath in to_be_created, s3_nodes))

        try:
            with ThreadPoolExecutor(
                self._get_thread_count(to_be_created),
                "sync_create",
            ) as executor:
                for node in to_create_nodes:
                    executor.submit(self._create_object_in_local_from_s3, node)
        except ValueError:  # pragma: no cover
            pass

        to_be_deleted = source_paths - s3_paths

        if force_delete:
            try:
                with ThreadPoolExecutor(
                    self._get_thread_count(to_be_deleted),
                    "sync_delete",
                ) as executor:
                    for file_path in to_be_deleted:
                        executor.submit(os.remove, file_path)
            except ValueError:  # pragma: no cover
                pass
            return SyncResult(
                list(map(lambda n: str(n.abspath), to_create_nodes)),
                list(map(lambda n: str(n.abspath), to_update_nodes)),
                list(map(str, to_be_deleted)),
            )

        if to_be_deleted:
            prompt = Prompt()
            res = prompt.ask(
                f"FS sync mechanism is going to delete: {list(map(str, to_be_deleted))} from local FS"
                f"\n'Should it precede?'",
                choices=["yes", "NO"],
                default="NO",
            )
            if res == "yes":
                with ThreadPoolExecutor(
                    self._get_thread_count(to_be_deleted),
                    "sync_delete",
                ) as executor:
                    for file_path in to_be_deleted:
                        executor.submit(os.remove, file_path)
            else:
                to_be_deleted = []
        return SyncResult(
            list(map(lambda n: str(n.abspath), to_create_nodes)),
            list(map(lambda n: str(n.abspath), to_update_nodes)),
            list(map(str, to_be_deleted)),
        )

    def _sync_s3_with_local_objects(
        self,
        s3_nodes: list[NodeSchema],
        s3_paths: set[Path],
        source_paths: set[Path],
        force_delete: bool = False,
    ) -> SyncResult:
        """Update, Upload and Delete objects of S3 that are new in local FS"""
        to_be_updated = s3_paths & s3_paths
        to_update_nodes = list(filter(lambda n: n.abspath in to_be_updated, s3_nodes))

        try:
            with ThreadPoolExecutor(
                self._get_thread_count(to_update_nodes),
                "sync_update",
            ) as executor:
                for node in to_update_nodes:
                    executor.submit(self._update_object_from_local_on_s3, node)
        except ValueError:  # pragma: no cover
            pass

        to_be_created = source_paths - s3_paths

        try:
            with ThreadPoolExecutor(
                self._get_thread_count(to_be_created),
                "sync_upload",
            ) as executor:
                for file_path in to_be_created:
                    executor.submit(
                        self._create_object_from_here_on_s3,
                        file_path,
                    )
        except ValueError:  # pragma: no cover
            pass

        to_be_deleted = s3_paths - source_paths
        if force_delete:
            to_delete_keys: list[NodeSchema] = list(
                map(
                    lambda n: n.key,
                    filter(lambda n: n.abspath in to_be_deleted, s3_nodes),
                )
            )
            self.service.delete_objects(*to_delete_keys)
            return SyncResult(
                list(map(str, to_be_created)),
                list(map(lambda n: str(n.abspath), to_update_nodes)),
                list(map(str, to_be_deleted)),
            )

        if to_be_deleted:
            prompt = Prompt()
            res = prompt.ask(
                f"FS sync mechanism is going to delete: {list(map(str, to_be_deleted))} from S3"
                f"\n'Should it precede?'",
                choices=["yes", "NO"],
                default="NO",
            )
            if res == "yes":
                to_delete_keys: list[NodeSchema] = list(
                    map(
                        lambda n: n.key,
                        filter(lambda n: n.abspath in to_be_deleted, s3_nodes),
                    )
                )
                self.service.delete_objects(*to_delete_keys)
            else:
                to_be_deleted = []
        return SyncResult(
            list(map(str, to_be_created)),
            list(map(lambda n: str(n.abspath), to_update_nodes)),
            list(map(str, to_be_deleted)),
        )

    def _create_object_from_here_on_s3(self, file_path: Path) -> None:
        """Upload single object to S3"""
        stat = os.lstat(file_path)

        mime_type = get_mime_type(file_path)
        with file_path.open("br") as f:
            self.service.upload_fileobj(
                f,
                self.service.get_key_from_path(file_path),
                FileAttrs.from_stat_result(stat),
                mime_type,
            )

    def _create_object_in_local_from_s3(self, node: NodeSchema) -> None:
        """Download and create object from S3"""
        node.abspath.parents[0].mkdir(parents=True, exist_ok=True)
        with node.abspath.open("bw") as f:
            self.service.download_fileobj(f, node.key)

    def _update_object_in_local_from_s3(self, node: NodeSchema) -> None:
        path = node.abspath
        st = os.lstat(path)
        node = self.service.head_object(node.key)

        if st.st_size != node.size:
            with path.open("bw") as f:
                self.service.download_fileobj(f, node.key)

        attrs = node.file_attrs
        os.utime(path, (attrs.st_atime, attrs.st_mtime))
        os.chown(path, attrs.st_uid, attrs.st_gid)
        os.chmod(path, attrs.st_mode)

    def _update_object_from_local_on_s3(self, node: NodeSchema) -> None:
        path = node.abspath
        key = self.service.get_key_from_path(path)

        st = os.lstat(path)
        attrs = FileAttrs.from_stat_result(st)

        mime_type = get_mime_type(path)

        if st.st_size != node.size:
            with path.open("br") as f:
                self.service.upload_fileobj(f, key, attrs, mime_type)
        else:
            mime_type = get_mime_type(path)
            self.service.copy_object(key, attrs, mime_type)

    def _get_all_files(self, source: Path) -> set[Path]:
        source_keys = set()
        for df in source.iterdir():
            if df.is_file():
                source_keys.add(df)
            else:
                source_keys |= self._get_all_files(df)
        return source_keys

    def _get_node_schema_from_bucket(self) -> list[NodeSchema]:
        response = self.service.list_objects()
        try:
            return [
                NodeSchema(
                    key=cont.Key,
                    last_modified=cont.LastModified,
                    size=cont.Size,
                    abspath=self.root / cont.Key,
                )
                for cont in response.Contents
            ]
        except TypeError:
            return []

    @staticmethod
    def _get_thread_count(keys: Sized) -> int:
        return min(32, len(keys))


@dataclass
class Task:
    target: Callable[..., SyncResult]
    args: tuple
    caller: str

    def __call__(self) -> SyncResult:  # pragma: no cover
        return self.target(*self.args)
