import configparser
from argparse import ArgumentParser, Namespace
from typing import assert_never

import rich
from boto3.s3.transfer import KB, MB
from rich.syntax import Syntax

from pys3fuse import pys3fuse_config_file


class ConfigHandler:
    def __init__(self, parser: ArgumentParser):
        self.parser = parser

    def __call__(self, args: Namespace) -> None:
        config_parser = configparser.ConfigParser()
        config_parser.read(pys3fuse_config_file)

        if args.show:
            with open(pys3fuse_config_file) as f:
                rich.print(Syntax(f.read(), "ini", line_numbers=True))
            exit(0)

        if (
            args.log_level is None
            and args.multipart_threshold is None
            and args.max_concurrency is None
            and args.multipart_chunksize is None
            and args.create_on_the_fly is None
        ):
            self.parser.print_help()
            exit(-1)

        if (v := args.log_level) is not None:
            config_parser["log"]["level"] = v

        if (v := args.multipart_threshold) is not None:
            num, suf = int("".join(filter(str.isdigit, v))), v[-2:]  # noqa
            match suf:
                case "KB":
                    v = num * KB
                case "MB":
                    v = num * MB
                case _:
                    assert_never(suf)

            config_parser["s3_transfer_config"]["multipart_threshold"] = str(v)

        if (v := args.max_concurrency) is not None:
            config_parser["s3_transfer_config"]["max_concurrency"] = v

        if (v := args.multipart_chunksize) is not None:
            num, suf = int("".join(filter(str.isdigit, v))), v[-2:]  # noqa
            match suf:
                case "KB":
                    v = num * KB
                case "MB":
                    v = num * MB
                case _:
                    assert_never(suf)
            config_parser["s3_transfer_config"]["multipart_chunksize"] = str(v)

        with open(pys3fuse_config_file, "w") as f:
            config_parser.write(f)  # noqa
