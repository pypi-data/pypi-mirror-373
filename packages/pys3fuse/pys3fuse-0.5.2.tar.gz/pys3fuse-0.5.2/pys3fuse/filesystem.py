import configparser
import errno
import os
import threading
from functools import cached_property
from pathlib import Path
from queue import Queue
from typing import Iterator

from fuse import FuseOSError, Operations, fuse_get_context

from . import pys3fuse_config_file
from .core.log_config import logger
from .core.schemas import FileAttrs
from .core.utils import full_path, log, on_error
from .s3service import S3Service
from .sync import Syncer, Task


class Filesystem(Operations):
    def __init__(
        self,
        root: str,
        bucket: str,
        queue: Queue[Task],
        *,
        offline: bool = False,
        service: S3Service | None = None,
        multi_user: bool = False,
        force: bool = False,
    ):
        self.root = Path(root)
        self.bucket = bucket
        self.offline = offline
        self.service = service
        self.multi_user = multi_user
        self.force = force
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(pys3fuse_config_file)

        self.syncer = Syncer(self.service, self.root, self.config_parser)
        self.queue = queue

        def worker():
            while True:
                item = self.queue.get()
                logger.debug(
                    f"Syncing: <{item.target.__name__}::{item.args}>",
                    extra={"worker_name": item.caller},
                )
                sync_result = item()
                logger.debug(sync_result, extra={"worker_name": item.caller})
                self.queue.task_done()

        threading.Thread(target=worker, daemon=True, name="Daemon").start()

    @cached_property
    def should_sync_multi_user(self):
        return (not self.offline) and self.multi_user

    @cached_property
    def should_sync(self):
        return not self.offline

    def _full_path(self, partial) -> Path:
        return self.root / partial.lstrip("/")

    @full_path
    @log
    def access(self, path: Path, mode: int):
        if not os.access(path, mode):
            raise FuseOSError(errno.EACCES)

    @full_path
    @log
    def chmod(self, path: Path, mode: int) -> None:
        st = os.lstat(path)
        try:
            os.chmod(path, mode)
        except OSError as exc:
            on_error(exc)
        else:
            if self.should_sync:
                attrs = FileAttrs.from_stat_result(st)
                attrs.st_mode = mode
                self.queue.put_nowait(
                    Task(self.syncer.update_attrs_on_s3, (path, attrs), "chmod")
                )

    @full_path
    @log
    def chown(self, path: Path, uid: int, gid: int) -> None:
        st = os.lstat(path)

        def change_xid(uid_, gid_) -> tuple[int, int]:
            uid_ = st.st_uid if uid_ == -1 else uid_
            gid_ = st.st_gid if gid_ == -1 else gid_
            return uid_, gid_

        try:
            os.chown(path, uid, gid)
        except OSError as exc:
            on_error(exc)
        else:
            if self.should_sync:
                attrs = FileAttrs.from_stat_result(st)
                u, g = change_xid(uid, gid)
                attrs.st_uid = u
                attrs.st_gid = g
                self.queue.put_nowait(
                    Task(self.syncer.update_attrs_on_s3, (path, attrs), "chown")
                )

    @log
    def getattr(self, path: str, fh=None) -> dict:
        full_path_ = self._full_path(path)
        st = os.lstat(full_path_)

        attrs = dict(
            (key, getattr(st, key))
            for key in (
                "st_atime",
                "st_ctime",
                "st_gid",
                "st_mode",
                "st_mtime",
                "st_nlink",
                "st_size",
                "st_uid",
            )
        )
        return attrs

    @full_path
    @log
    def readdir(self, path: Path, fh) -> Iterator[str]:
        if self.should_sync_multi_user:
            logger.debug(f"Syncing: : <sync_local_with_s3::{(self.force,)}>")
            sync_result = self.syncer.sync_local(self.force)
            logger.debug(sync_result)

        dirents = [".", ".."]
        if os.path.isdir(path):
            dirents.extend(os.listdir(path))
        for r in dirents:
            yield r

    @full_path
    @log
    def readlink(self, path) -> str:
        try:
            pathname = os.readlink(path)
        except OSError as exc:
            on_error(exc)
        else:
            if pathname.startswith("/"):
                return os.path.relpath(pathname, self.root)
            else:
                return pathname

    @full_path
    @log
    def mknod(self, path: Path, mode: int, dev) -> None:
        try:
            os.mknod(path, mode, dev)
        except OSError as exc:
            on_error(exc)

    @full_path
    @log
    def rmdir(self, path) -> None:
        try:
            os.rmdir(path)
        except FileNotFoundError as exc:
            on_error(exc)
        except OSError as exc:
            on_error(exc)

    @full_path
    @log
    def mkdir(self, path: Path, mode: int) -> None:
        try:
            os.mkdir(path, mode)
        except FileExistsError as exc:
            on_error(exc)
        except FileNotFoundError as exc:
            on_error(exc)
        except OSError as exc:
            on_error(exc)

    @full_path
    @log
    def statfs(self, path: Path) -> dict:
        try:
            stv = os.statvfs(path)
        except OSError as exc:
            on_error(exc)
        else:
            return dict(
                (key, getattr(stv, key))
                for key in (
                    "f_bavail",
                    "f_bfree",
                    "f_blocks",
                    "f_bsize",
                    "f_favail",
                    "f_ffree",
                    "f_files",
                    "f_flag",
                    "f_frsize",
                    "f_namemax",
                )
            )

    @full_path
    @log
    def unlink(self, path: Path) -> None:
        try:
            os.unlink(path)
        except FileNotFoundError as exc:
            on_error(exc)
        except OSError as exc:
            on_error(exc)
        else:
            if self.should_sync:
                self.queue.put_nowait(Task(self.syncer.delete_on_s3, (path,), "unlink"))

    @log
    def symlink(self, name, target, *args) -> None:
        path = self._full_path(name)
        uid, gid, pid = fuse_get_context()
        try:
            os.symlink(target, path)
            os.chown(path, uid, gid, follow_symlinks=False)
        except OSError as exc:
            on_error(exc)

    @log
    def rename(self, old: str, new: str) -> None:
        old_path = self._full_path(old)
        new_path = self._full_path(new)

        try:
            os.rename(old_path, new_path)
        except FileExistsError as exc:
            on_error(exc)
        except IsADirectoryError as exc:
            on_error(exc)
        except NotADirectoryError as exc:
            on_error(exc)
        except OSError as exc:
            on_error(exc)
        else:
            if self.should_sync:
                self.queue.put_nowait(
                    Task(self.syncer.rename_on_s3, (old_path, new_path), "rename")
                )

    @log
    def link(self, target, name) -> None:
        try:
            os.link(self._full_path(name), self._full_path(target))
        except OSError as exc:
            on_error(exc)

    @full_path
    @log
    def utimens(self, path: Path, times=None) -> None:
        try:
            os.utime(path, times)
        except OSError as exc:
            on_error(exc)
        else:
            if self.should_sync:
                attrs = FileAttrs.from_stat_result(os.lstat(path))
                self.queue.put_nowait(
                    Task(self.syncer.update_attrs_on_s3, (path, attrs), "utimens")
                )

    @full_path
    @log
    def open(self, path: Path, flags) -> int:
        try:
            return os.open(path, flags)
        except OSError as exc:
            on_error(exc)

    @full_path
    @log
    def create(self, path: Path, mode: int, fi=None) -> int:
        uid, gid, pid = fuse_get_context()
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT, mode)
            os.chown(path, uid, gid)
        except OSError as exc:
            on_error(exc)
        else:
            if self.should_sync:
                self.queue.put_nowait(Task(self.syncer.create_on_s3, (path,), "create"))
            return fd

    @log
    def read(self, path: str, length, offset, fh) -> bytes:
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    @log
    def write(self, path: str, buf, offset, fh) -> int:
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    @full_path
    @log
    def truncate(self, path: Path, length, fh: int = None) -> None:
        try:
            with open(path, "r+") as f:
                f.truncate(length)
        except OSError as exc:
            on_error(exc)
        else:
            if self.should_sync:
                self.queue.put_nowait(
                    Task(self.syncer.update_on_s3, (path,), "truncate")
                )

    @log
    def flush(self, path: str, fh) -> None:
        try:
            os.fsync(fh)
        except OSError as exc:
            on_error(exc)

    @full_path
    @log
    def release(self, path: Path, fh: int) -> None:
        try:
            os.close(fh)
        except OSError as exc:
            on_error(exc)
        else:
            if self.should_sync:
                self.queue.put_nowait(
                    Task(self.syncer.update_on_s3, (path,), "release")
                )

    @full_path
    @log
    def fsync(self, path: str, fdatasync, fh: int) -> None:
        self.flush(path, fh)
