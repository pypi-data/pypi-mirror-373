from argparse import ArgumentParser

from .config_cmd import ConfigHandler
from .mount_cmd import MountHandler

parser = ArgumentParser(
    "PyS3FUSE", description="A FUSE layer to mount S3 buckets in your local filesystem."
)
subparsers = parser.add_subparsers(
    title="commands", description="Different commands on PyS3FUSE"
)
config_parser = subparsers.add_parser(
    "config", help="Config different parts of PyS3FUSE"
)
config_parser.add_argument(
    "--show",
    help="Print the current config",
    required=False,
    action="store_true",
)
config_parser.add_argument(
    "-ll",
    "--log-level",
    help="Default log level of PyS3FUSE",
    choices=["debug", "info"],
    required=False,
)
config_parser.add_argument(
    "-mt",
    "--multipart-threshold",
    help="The transfer size threshold for which multipart uploads, downloads, and copies will automatically be triggered.",
    choices=["100KB", "250KB", "500KB", "1MB", "2MB", "5MB", "8MB", "10MB"],
    required=False,
    dest="multipart_threshold",
)
config_parser.add_argument(
    "-xc",
    "--max-concurrency",
    help="The maximum number of threads that will be making requests to perform a transfer.",
    choices=["2", "5", "10", "20"],
    required=False,
    dest="max_concurrency",
)
config_parser.add_argument(
    "-mc",
    "--multipart-chunksize",
    help="The partition size of each part for a multipart transfer.",
    choices=["100KB", "250KB", "500KB", "1MB", "2MB", "5MB", "8MB", "10MB"],
    required=False,
    dest="multipart_chunksize",
)
config_parser.set_defaults(cls=ConfigHandler(config_parser))

mount_parser = subparsers.add_parser("mount", help="Mound an S3 bucket to work with")
mount_parser.add_argument(
    "source",
    type=str,
    help="Directory tree to mirror",
)
mount_parser.add_argument(
    "mountpoint",
    type=str,
    help="Where to mount the file system",
)
mount_parser.add_argument(
    "--bucket", required=True, type=str, help="S3 Bucket you want to mound."
)
mount_parser.add_argument(
    "--debug",
    action="store_true",
    default=False,
    help="Enable debugging output",
)
mount_parser.add_argument(
    "--offline",
    action="store_true",
    default=False,
    help="Set when you don't have connection to your S3 service and want to manipulate the mountpoint on yourself. Later PyS3FUSE will sync your mountpoint with your S3 bucket.",
)
mount_parser.add_argument(
    "--multi-user",
    action="store_true",
    default=False,
    help="If you are online and somebody else has mounted the bucket OR you are online but somebody else is connected to S3 pass this option so that on some syscalls FS will sync it self with S3. Either case S3 has precedence.",
    dest="multi_user",
)
mount_parser.add_argument(
    "-f",
    "--force",
    action="store_true",
    default=False,
    help="In the initial synchronization of program, there maybe some objects that have to be deleted in local FS or S3. Default behaviour is to ask the user whether to delete them or not but if this options is passed no prompt will be shown and all will be deleted.",
    dest="force",
)
mount_parser.set_defaults(cls=MountHandler())
