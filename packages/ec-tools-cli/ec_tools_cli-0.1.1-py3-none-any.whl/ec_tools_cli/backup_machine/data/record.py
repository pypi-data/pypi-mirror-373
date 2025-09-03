import dataclasses
import json
from typing import List

from ec_tools.database import SqliteDataObject
from ec_tools.tools.cipher.chunk_config import ChunkConfig


@dataclasses.dataclass
class StoragePath:
    zip_path: str
    file_path: str


@dataclasses.dataclass
class Record(SqliteDataObject):
    file_path: str
    version: str
    mtime: str
    md5: str
    size: int
    storage_paths: List[StoragePath] = dataclasses.field(default_factory=list)
    chunk_config: ChunkConfig = dataclasses.field(default=None)

    @classmethod
    def primary_keys(cls) -> List[str]:
        return ["file_path"]

    @classmethod
    def unique_keys(cls) -> List[List[str]]:
        return [["file_path"]]

    @classmethod
    def _dump__storage_paths(cls, value: List[StoragePath]) -> str:
        return json.dumps([dataclasses.asdict(item) for item in value])

    @classmethod
    def _load__storage_paths(cls, value: str) -> List[StoragePath]:
        return [StoragePath(**item) for item in json.loads(value)]

    @classmethod
    def _dump__chunk_config(cls, value: ChunkConfig) -> str:
        return value.to_json_bytes().decode("utf-8")

    @classmethod
    def _load__chunk_config(cls, value: str) -> ChunkConfig:
        return ChunkConfig.from_json(value)
