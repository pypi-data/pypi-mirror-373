import configparser
import os
from pathlib import Path

from boto3.s3.transfer import MB

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Self Dir ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
pys3fuse_dir = Path(os.getenv("HOME")) / ".pys3fuse"

if not pys3fuse_dir.exists():
    os.mkdir(pys3fuse_dir, mode=0o766)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Logs ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
pys3fuse_logs_dir = pys3fuse_dir / "logs"

if not pys3fuse_logs_dir.exists():
    os.mkdir(pys3fuse_logs_dir, 0o766)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Config ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
pys3fuse_config_file = pys3fuse_dir / "config.ini"

if not pys3fuse_config_file.exists():
    config_parser = configparser.ConfigParser()
    config_parser["log"] = {"level": "info"}
    config_parser["s3_transfer_config"] = {
        "multipart_threshold": 8 * MB,
        "max_concurrency": 10,
        "multipart_chunksize": 8 * MB,
    }
    config_parser["sync"] = {"dirty": "false"}

    with pys3fuse_config_file.open("w") as f:
        config_parser.write(f)  # noqa
