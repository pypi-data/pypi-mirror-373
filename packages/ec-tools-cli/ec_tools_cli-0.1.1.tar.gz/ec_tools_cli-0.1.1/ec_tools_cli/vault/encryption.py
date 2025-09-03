import dataclasses

from ec_tools.database import CipherKvDao, KvDao, SqliteClient, SqliteKvDao
from ec_tools.tools.cipher import AesCipherGenerator, AesMode


@dataclasses.dataclass
class Encryption:
    _sqlite_client: SqliteClient
    _kv_dao: KvDao
    _cipher_dao: CipherKvDao

    def __init__(self, db_path: str):
        self._sqlite_client = SqliteClient(db_path)
        self._kv_dao = SqliteKvDao(self._sqlite_client, table_name="Vault")
        self._cipher_dao = CipherKvDao(
            self._kv_dao,
            AesCipherGenerator(encoding="utf-8", mode=AesMode.AES_256_CBC, pbkdf2_iterations=10000),
            encoding="utf-8",
        )

    def list_keys(self) -> list[str]:
        return self._cipher_dao.keys()

    def insert(self, password: str, key: str, value: bytes):
        return self._cipher_dao.set_bytes(key, password, value)

    def get(self, password: str, key: str) -> bytes:
        return self._cipher_dao.get_bytes(key, password)

    def delete(self, key: str):
        return self._cipher_dao.delete(key)
