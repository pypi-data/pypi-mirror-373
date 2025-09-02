import errno
import inspect
import subprocess
from configparser import ConfigParser
from functools import singledispatch, wraps
from pathlib import Path
from typing import Never, ParamSpec

from fuse import FuseOSError

from .log_config import logger
from .. import pys3fuse_config_file


@singledispatch
def on_error(exc: Exception, *, errno_: int = 0) -> Never:
    """Log Exception and raise `FuseOSError`"""
    raise FuseOSError(errno_)


@on_error.register
def on_os_error(exc: OSError) -> Never:
    raise FuseOSError(exc.errno)


@on_error.register
def on_key_error(exc: KeyError) -> Never:
    raise FuseOSError(errno.ENOENT)


@on_error.register
def on_is_a_dir_error(exc: IsADirectoryError) -> Never:
    raise FuseOSError(exc.errno)


@on_error.register
def on_not_a_dir_error(exc: NotADirectoryError) -> Never:
    raise FuseOSError(exc.errno)


@on_error.register
def on_file_not_found_error(exc: FileNotFoundError) -> Never:
    raise FuseOSError(exc.errno)


@on_error.register
def on_file_exists(exc: FileExistsError) -> Never:
    raise FuseOSError(exc.errno)


def log(func):  # pragma: no cover
    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs):
        func_sig = inspect.signature(func)
        params = dict(zip(func_sig.parameters, args))
        del params["self"]

        log_msg = ", ".join(f"{k}={v}" for k, v in params.items())
        logger.debug(log_msg, extra={"func_name": func.__name__})
        return func(*args, **kwargs)

    return inner


P = ParamSpec("P")


def full_path(func):  # pragma: no cover
    def inner(*args: P.args, **kwargs: P.kwargs):
        func_sig = inspect.signature(func)
        params = dict(zip(func_sig.parameters, args))

        self = params["self"]
        params["path"] = self.root / params["path"].lstrip("/")

        args = tuple(params.values())
        return func(*args, **kwargs)

    return inner


def write_config(config_parser: ConfigParser) -> None:  # pragma: no cover
    """Write the mutated cofig to the config file"""
    with open(pys3fuse_config_file, "w") as f:
        config_parser.write(f)  # noqa


def get_mime_type(file_path: Path) -> str:
    return subprocess.getoutput(f"file --mime-type -b {str(file_path.absolute())}")
