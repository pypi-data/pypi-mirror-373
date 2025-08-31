import logging
import queue
from datetime import datetime
from logging import LogRecord
from logging.config import dictConfig
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from typing import cast

import boto3
import botocore
import rich.logging
import structlog
import urllib3
from rich.console import Console, ConsoleRenderable, RenderableType
from rich.containers import Renderables
from rich.table import Table
from rich.text import Text, TextType
from rich.traceback import Traceback

from .. import pys3fuse_dir

cons = Console(force_terminal=True)


class DefaultLogRender:
    def __init__(self, time_format="[%x %X]") -> None:
        self.time_format = time_format
        self.omit_repeated_times = False
        self.level_width = None
        self.last_func_name = None

    def __call__(
        self,
        console: Console,
        renderables: list[ConsoleRenderable],
        log_time: datetime,
        level: TextType,
        record: LogRecord,
    ) -> Table:
        output = Table.grid(padding=(0, 1))
        output.expand = True
        output.add_column(style="log.time")
        output.add_column(style="log.level")
        output.add_column()
        output.add_column(ratio=1, style="log.message", overflow="fold")

        row: list[RenderableType] = []

        log_time = log_time or console.get_datetime()
        log_time_display = Text(log_time.strftime(self.time_format))
        row.append(log_time_display)
        row.append(level)

        func_name = getattr(record, "func_name", None)
        if func_name is None:
            func_name = record.funcName
            func_name_text = Text()
            if func_name == "__call__":
                func_name_text.append("<main>", style="bright_yellow bold")
            elif (wn := getattr(record, "worker_name", None)) is not None:
                func_name_text.append(f"<{wn}>", style="bright_yellow bold")
            else:
                func_name_text.append(f"<{func_name}>", style="bright_yellow bold")
        else:
            func_name_text = Text()
            func_name_text.append(f"[{func_name:<8}]", style="magenta1 bold")

        row.append(func_name_text)
        row.append(Renderables(renderables))
        output.add_row(*row)
        return output


class PyS3FUSERichHandler(rich.logging.RichHandler):
    def __init__(self):
        super().__init__(
            console=cons,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=False,
            tracebacks_suppress=[boto3, botocore, urllib3],
            tracebacks_max_frames=1,
        )
        self._log_render = DefaultLogRender("%Y-%m-%d %H:%M:%S")

    def render(
        self,
        *,
        record: logging.LogRecord,
        traceback: Traceback | None,
        message_renderable: "ConsoleRenderable",
    ) -> "ConsoleRenderable":
        level = self.get_level_text(record)
        log_time = datetime.fromtimestamp(record.created)

        log_renderable = self._log_render(
            self.console,
            [message_renderable] if not traceback else [message_renderable, traceback],
            log_time,
            level,
            record,
        )
        return log_renderable


class PyS3FUSEQueueHandler(QueueHandler):
    listener: QueueListener

    def prepare(self, record: LogRecord) -> LogRecord:
        return record


class PyS3FUSEStructLogProcessor:
    def __call__(self, _, __, event_dict: dict):
        log_dict = {
            "timestamp": event_dict["timestamp"],
            "logger": event_dict["logger"],
            "level": event_dict["level"],
            "message": event_dict["message"],
        }
        if (exception := event_dict.get("exception", None)) is not None:
            log_dict["exception"] = exception
        return log_dict


dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "pys3fuse": {
                "level": logging.DEBUG,
                "handlers": ["console_handler", "file_queue_handler"],
            },
            "fuse": {
                "level": logging.ERROR,
                "handlers": ["console_handler", "file_queue_handler"],
            },
            "boto3": {
                "level": logging.ERROR,
                "handlers": ["console_handler", "file_queue_handler"],
            },
        },
        "handlers": {
            "console_handler": {"class": PyS3FUSERichHandler},
            "file_handler": {
                "class": RotatingFileHandler,
                "formatter": "file_formatter",
                "filename": pys3fuse_dir / "logs" / "pys3fuse.log",
                "maxBytes": 10 * 1024 * 1024,  # 10 MB
                "backupCount": 10,
                "encoding": "utf8",
            },
            "file_queue_handler": {
                "class": PyS3FUSEQueueHandler,
                "queue": queue.Queue(),
                "listener": QueueListener,
                "handlers": ["file_handler"],
            },
        },
        "formatters": {
            "file_formatter": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": [
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.add_logger_name,
                    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                    structlog.processors.ExceptionRenderer(
                        structlog.processors.ExceptionDictTransformer()
                    ),
                    structlog.processors.EventRenamer("message"),
                    PyS3FUSEStructLogProcessor(),
                    structlog.processors.LogfmtRenderer(),
                ],
            },
        },
    }
)

logger = logging.getLogger("pys3fuse")
file_queue_listener: QueueListener = cast(
    PyS3FUSEQueueHandler, logging.getHandlerByName("file_queue_handler")
).listener
