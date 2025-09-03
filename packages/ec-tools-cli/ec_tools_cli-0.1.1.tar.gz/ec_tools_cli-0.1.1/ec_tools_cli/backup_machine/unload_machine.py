import dataclasses
import hashlib
import logging
import os
from zipfile import ZipFile

from cachetools import Cache, FIFOCache
from ec_tools.tools.cipher import chunk_encryption_utils
from ec_tools.utils.io_utils import chunk_read_file

from ec_tools_cli.backup_machine.data.config import Config
from ec_tools_cli.backup_machine.data.record import Record
from ec_tools_cli.backup_machine.utils import load_records, log_progress


@dataclasses.dataclass
class UnloadMachine:
    config: Config
    password: str

    cache: Cache = dataclasses.field(default_factory=lambda: FIFOCache(maxsize=100))

    def unload(self, dst_path: str):
        record_map = load_records(self.config.db_path)
        records = sorted(record_map.values(), key=lambda r: r.updated_at)
        total = len(records)
        logging.info("[UnloadMachine] Unloading %d records to %s", total, dst_path)
        for idx, record in enumerate(records):
            log_progress(idx, total, record.file_path, "Unloading file", self.config.pack_logging_interval)
            self._unload_file(record, dst_path)

    def _get_chunk_generator(self, record: Record):
        for storage_path in record.storage_paths:
            zip_path = storage_path.zip_path
            file_path = storage_path.file_path
            if zip_path not in self.cache:
                self.cache[zip_path] = ZipFile(os.path.join(self.config.zip_path, zip_path), "r")
            zip_file: ZipFile = self.cache[zip_path]
            with zip_file.open(file_path) as f:
                for chunk in chunk_read_file(
                    f, record.chunk_config.chunk_size + record.chunk_config.aes_mode.value.key_size * 2
                ):
                    yield chunk

    def _unload_file(self, record: Record, dst_path: str):
        target_file_path = os.path.join(dst_path, record.file_path)
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
        hasher = hashlib.md5()
        with open(target_file_path, "wb") as wf:
            for decrypted_chunk in chunk_encryption_utils.decrypt_by_chunk(
                self._get_chunk_generator(record), self.password, record.chunk_config
            ):
                hasher.update(decrypted_chunk)
                wf.write(decrypted_chunk)
                wf.flush()
        md5 = hasher.hexdigest()
        logging.debug("[UnloadMachine] Unloaded file %s with MD5 %s, expected is %s", target_file_path, md5, record.md5)
        if md5 != record.md5:
            logging.error(
                "[UnloadMachine] MD5 mismatch for file %s: expected %s, got %s", record.file_path, record.md5, md5
            )
