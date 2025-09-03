import argparse
import logging

from ec_tools.utils.io_utils import load_json

from ec_tools_cli.backup_machine.backup_machine import BackupMachine
from ec_tools_cli.backup_machine.data.config import Config
from ec_tools_cli.backup_machine.unload_machine import UnloadMachine


def get_args():
    parser = argparse.ArgumentParser(description="Backup Machine")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    parser.add_argument("-c", "--config", type=str, required=True, help="Path to the configuration file")
    parser.add_argument("-p", "--password", type=str, required=True, help="Password for encryption")
    parser.add_argument(
        "-l",
        "--level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error"],
    )

    subparsers.add_parser("backup")
    unpack_parser = subparsers.add_parser("unpack")
    unpack_parser.add_argument("-o", "--output", type=str, required=True, help="Unpack path")

    return parser.parse_args()


def main():
    args = get_args()
    config = Config(**load_json(args.config), logging_level=args.level)
    logging.info(f"Password len is {len(args.password)}")

    if args.mode == "backup":
        backup_machine = BackupMachine(config, args.password)
        backup_machine.pack_up()
    else:
        unload_machine = UnloadMachine(config, args.password)
        unload_machine.unload(args.output)


if __name__ == "__main__":
    main()
