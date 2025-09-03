import logging
from typing import Dict

from ec_tools.database import SqliteClient, SqliteDao

from ec_tools_cli.backup_machine.data.record import Record


def get_dao(path: str) -> SqliteDao[Record]:
    return SqliteDao[Record](SqliteClient(path), Record)


def log_progress(idx: int, total: int, cur_task: str, task: str, interval: int):
    if (idx + 1) % interval == 0 or idx == 0 or idx == total - 1:
        percent = (idx + 1) / max(1, total) * 100
        logging.info("[BackupMachine] %s [%.2f%%](%s/%s): %s", task, percent, idx + 1, total, cur_task)


def load_records(db_path, max_query=10 * 1024 * 1024) -> Dict[str, Record]:
    dao = get_dao(db_path)
    records = {record.file_path: record for record in dao.query_by_values(limit=max_query)}
    assert len(records) < max_query, "Too many existing files in the database"
    return records
