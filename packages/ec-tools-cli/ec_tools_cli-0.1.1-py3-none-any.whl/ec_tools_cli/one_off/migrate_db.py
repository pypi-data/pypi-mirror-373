import argparse
import logging
import os
from typing import List

from ec_tools.utils.io_utils import load_json

from ec_tools_cli.backup_machine.data.config import Config
from ec_tools_cli.backup_machine.data.record import StoragePath
from ec_tools_cli.backup_machine.utils import get_dao


def parse_args():
    parser = argparse.ArgumentParser(description="Migrate the database to the latest version.")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to the configuration file.",
    )
    return parser.parse_args()


def update_storage_paths(storage_paths: List[StoragePath], config: Config) -> List[StoragePath]:
    result = []
    for sp in storage_paths:
        if sp.zip_path.startswith("/"):
            result.append(
                StoragePath(
                    zip_path=os.path.relpath(sp.zip_path, config.zip_path),
                    file_path=sp.file_path,
                )
            )
        else:
            result.append(sp)
            logging.warning(f"StoragePath {sp} is already relative.")
    return result


def main():
    args = parse_args()
    config = Config(**load_json(args.config))
    dao = get_dao(config.db_path)
    offset = 0
    limit = 1024
    logging.info("Starting database migration...")
    while True:
        batch = dao.query_by_values(limit=limit, offset=offset)
        offset += limit
        if not batch:
            break
        for record in batch:
            record.storage_paths = update_storage_paths(record.storage_paths, config)
        logging.info(f"Processing records {offset} to {offset + len(batch)}")
        dao.insert_or_replace(batch)


if __name__ == "__main__":
    main()
