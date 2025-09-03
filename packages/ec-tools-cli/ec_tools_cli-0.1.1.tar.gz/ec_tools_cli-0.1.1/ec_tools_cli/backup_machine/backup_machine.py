import dataclasses
import logging
import os
import shutil
import time
from typing import Generator, List, Optional

from ec_tools.tools.cipher import AesMode, chunk_encryption_utils
from ec_tools.tools.cipher.chunk_config import ChunkConfig
from ec_tools.utils.hash_utils import calc_md5
from ec_tools.utils.io_utils import chunk_read_file
from ec_tools.utils.misc import get_batch

from ec_tools_cli.backup_machine.data.config import Config
from ec_tools_cli.backup_machine.data.record import Record
from ec_tools_cli.backup_machine.utils import get_dao, load_records, log_progress
from ec_tools_cli.backup_machine.zip_storage import ZipStorage


@dataclasses.dataclass
class BackupMachine:
    config: Config
    password: str

    def __post_init__(self):
        os.makedirs(os.path.dirname(self.config.db_path), exist_ok=True)
        get_dao(self.config.db_path)

    def pack_up(self):
        logging.info("[BackupMachine] pack up with config: %s", self.config)
        root_path = os.path.abspath(self.config.src_path)
        zip_path = os.path.abspath(self.config.zip_path)
        all_files = self._get_all_files(root_path)
        generator = self._get_candidate_files(all_files, root_path)

        for batch in get_batch(generator, self.config.batch_size):
            version = self._generate_version()
            self.pack_up_once(version, zip_path, batch)

    def pack_up_once(self, version: str, zip_path: str, candidate_records: List[Record]) -> Optional[str]:
        version_path = os.path.join(zip_path, version)
        os.makedirs(version_path, exist_ok=True)
        zip_storage = ZipStorage(zip_root_path=zip_path, output_path=version_path, config=self.config)
        logging.info("[BackupMachine] path: %s, process %s files", version_path, len(candidate_records))
        new_db_path = os.path.join(version_path, os.path.basename(self.config.db_path))
        shutil.copy(self.config.db_path, new_db_path)
        records = []
        for idx, record in enumerate(candidate_records):
            log_progress(
                idx, len(candidate_records), record.file_path, "Packing file", self.config.pack_logging_interval
            )
            file_path = os.path.join(self.config.src_path, record.file_path)
            file_size = os.stat(file_path).st_size
            chunk_config = ChunkConfig(
                salt=os.urandom(32),
                aes_mode=AesMode.AES_256_CBC,
                iterations=self.config.pbkdf2_iters,
                chunk_size=self.config.chunk_size,
                file_size=file_size,
            )
            record.chunk_config = chunk_config
            record.version = version
            with open(file_path, "rb") as fp:
                for chunk in chunk_encryption_utils.encrypt_by_chunk(
                    chunk_read_file(fp, self.config.chunk_size),
                    self.password,
                    chunk_config.salt,
                    chunk_config.aes_mode,
                    chunk_config.iterations,
                ):
                    record.storage_paths.append(zip_storage.append_file(chunk))
            records.append(record)
        if records:
            dao = get_dao(new_db_path)
            dao.insert_or_replace(records)
            logging.info("[BackupMachine] %s records inserted into the database", len(records))
        shutil.copy(new_db_path, self.config.db_path)

    @classmethod
    def _generate_version(cls) -> str:
        return "{}-{}".format(time.strftime("%Y%m%d%H%M%S"), os.urandom(8).hex())

    def _list_files(self, path: str) -> List[str]:
        result = []
        for dp, _, fns in os.walk(path):
            for fn in fns:
                fp = os.path.join(dp, fn)
                extension = fp.split(".")[-1].lower()
                if self.config.ignored_extensions is not None and extension in self.config.ignored_extensions:
                    ...
                elif self.config.extensions is None or extension in self.config.extensions:
                    result.append(fp)
                else:
                    logging.warning("unchecked file found: %s %s", extension, fp)
        logging.info("%d files found in %s, preview: %s", len(result), path, result[:3])
        return result

    def _get_candidate_files(self, all_files: List[str], root_path: str) -> Generator[Record, None, None]:
        record_map = load_records(self.config.db_path, 10 * 1024 * 1024)
        for idx, fp in enumerate(all_files):
            log_progress(idx, len(all_files), fp, "Scanning file", self.config.scan_logging_interval)
            record = self._determine_record(root_path, fp, record_map.get(fp))
            if record:
                yield record

    def _determine_record(self, root_path: str, fp: str, record: Optional[Record]) -> Optional[Record]:
        mtime = str(os.path.getmtime(os.path.join(root_path, fp)))
        size = os.stat(os.path.join(root_path, fp)).st_size
        if record and mtime == record.mtime and size == record.size:
            return None
        md5_value = calc_md5(os.path.join(root_path, fp), 65536)
        if record and md5_value == record.md5:
            return None
        return Record(file_path=fp, version="", mtime=mtime, md5=md5_value, size=size)

    def _get_all_files(self, root_path: str) -> List[str]:
        all_files = []
        if self.config.sub_dirs is None:
            all_files += self._list_files(root_path)
        else:
            for root in self.config.sub_dirs:
                all_files += self._list_files(os.path.join(root_path, root))
        for fp in all_files:
            assert fp.startswith(root_path)
        all_files = [fp[len(root_path) + 1 :] for fp in all_files]
        logging.info("[BackupMachine] %s files found", len(all_files))
        return sorted(all_files)
