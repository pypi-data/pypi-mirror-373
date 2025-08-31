from .cli import parser
from .core.log_config import file_queue_listener

if __name__ == "__main__":
    file_queue_listener.start()

    try:
        args = parser.parse_args()
        try:
            args.cls(args)
        except AttributeError:
            parser.print_help()
            exit(-1)
    finally:
        file_queue_listener.start()
