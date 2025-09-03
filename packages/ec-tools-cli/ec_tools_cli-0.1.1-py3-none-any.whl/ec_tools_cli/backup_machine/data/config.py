import dataclasses
import logging
from typing import List, Optional, Set


@dataclasses.dataclass
class Config:
    db_path: str
    src_path: str
    zip_path: str
    sub_dirs: Optional[List[str]] = None

    logging_level: str = "INFO"
    extensions: Optional[Set[str]] = None
    ignored_extensions: Optional[Set[str]] = None

    max_pack_count: int = 256
    max_pack_size: int = 2 * 1024 * 1024 * 1024  # 1GB
    chunk_size: int = 1024 * 1024 * 10  # 10MB
    batch_size: int = 1024

    scan_logging_interval: int = 100
    pack_logging_interval: int = 10

    pbkdf2_iters: int = 10000

    def __post_init__(self):
        if self.extensions is not None:
            self.extensions = set(self.extensions)
        if self.ignored_extensions is not None:
            self.ignored_extensions = set(self.ignored_extensions)
        logging.basicConfig(level=self.logging_level.upper())

        assert self.db_path is not None, "db_path cannot be None"
        assert self.src_path is not None, "src_path cannot be None"
        assert self.zip_path is not None, "dst_path cannot be None"

        self.max_pack_count = int(self.max_pack_count)
        self.max_pack_size = int(self.max_pack_size)
        self.chunk_size = int(self.chunk_size)
        self.batch_size = int(self.batch_size)

        self.scan_logging_interval = int(self.scan_logging_interval)
        self.pack_logging_interval = int(self.pack_logging_interval)

        self.pbkdf2_iters = int(self.pbkdf2_iters)
