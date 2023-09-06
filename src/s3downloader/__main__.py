from .classes.client import S3Client
from .classes.config import Config

import logging

from argparse import ArgumentParser

def main():
    parser = ArgumentParser()

    parser.add_argument(
        "--config",
        type=str,
        default="settings.ini",
        help="Path to configuration file",
    )

    parser.add_argument(
        "--section",
        type=str,
        default="S3",
        help="Section in configuration file",
    )

    parser.add_argument(
        "--log",
        type=str,
        default="INFO",
        help="Logging level",
    )

    args = parser.parse_args()

    logging.basicConfig(level=args.log)

    client = S3Client.from_config(args.config, args.section)

    client.process_files()

if __name__ == '__main__':
    main()
