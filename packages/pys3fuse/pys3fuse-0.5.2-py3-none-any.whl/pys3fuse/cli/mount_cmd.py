import configparser
import logging
import queue
from argparse import Namespace
from pathlib import Path

import botocore.config
import botocore.errorfactory
from boto3_type_annotations.s3 import Client
from botocore.exceptions import ClientError, EndpointConnectionError
from fuse import FUSE

from .. import pys3fuse_config_file
from ..core.config import settings
from ..core.exceptions import PysClientError, S3ConnectionError
from ..core.log_config import logger
from ..core.utils import write_config
from ..filesystem import Filesystem
from ..s3service import S3Service, session
from ..sync import Syncer, Task


class MountHandler:
    def __init__(self):
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(pys3fuse_config_file)

        # fmt: off
        logger.setLevel(
            logging.INFO
            if self.config_parser["log"]["level"] == "info"
            else logging.DEBUG
        )
        # fmt: on

        self.queue = queue.Queue[Task]()
        self.client: Client | None = None
        self.service: S3Service | None = None

    def __call__(self, args: Namespace) -> None:
        if args.debug:
            logger.setLevel(logging.DEBUG)

        self.args = args
        try:
            if args.offline is True:
                self.config_parser["sync"]["dirty"] = "true"
            else:
                self.check_s3()
                syncer = Syncer(
                    self.service,
                    Path(args.source),
                    self.config_parser,
                )
                syncer.sync_initial(force_delete=args.force)
            write_config(self.config_parser)
            self.mount()
        except S3ConnectionError:
            logger.error(
                f"Exiting... <S3: Bucket={args.bucket}> is not available. "
                f"If you are not connected to the internet pass `--offline` option."
            )
        except PysClientError as e:
            logger.error(str(e))
        except Exception as e:
            logger.exception(str(e), exc_info=e)
        finally:
            print()
            logger.info("Unmounting...")
            if self.client is not None:
                logger.debug("Finishing any pending s3 operations...")
                self.queue.join()
                logger.debug("Closing s3 client connections...")
                self.client.close()
            logger.info("Unmounted.")

    def check_s3(self):
        """Check the connection between FS and S3"""
        args = self.args
        logger.debug("Checking S3 Connection...")
        try:
            self.client = client = session.client(
                "s3",
                endpoint_url=settings.S3_API,
                config=botocore.config.Config(
                    tcp_keepalive=True,
                    max_pool_connections=10,
                ),
            )
            self.service = service = S3Service(client, args.bucket, self.config_parser)
            service.get_bucket_acl()
        except EndpointConnectionError:
            raise S3ConnectionError() from None
        except ClientError as e:
            raise PysClientError(str(e)) from None
        except Exception:
            raise
        else:
            logger.info("S3 Connection is established.")

    def mount(self):
        """Mount the FS"""
        logger.info("Mounting...")
        args = self.args
        FUSE(
            Filesystem(
                args.source,
                args.bucket,
                self.queue,
                offline=args.offline,
                service=self.service,
                multi_user=args.multi_user,
                force=args.force,
            ),
            args.mountpoint,
            foreground=True,
            allow_other=True,
        )
