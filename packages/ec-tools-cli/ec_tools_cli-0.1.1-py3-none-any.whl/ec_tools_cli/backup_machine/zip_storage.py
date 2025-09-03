import dataclasses
import os
from zipfile import ZIP_DEFLATED, ZipFile

from ec_tools_cli.backup_machine.data.config import Config
from ec_tools_cli.backup_machine.data.record import StoragePath


@dataclasses.dataclass
class Package:
    cnt: int
    size: int
    zipfile: ZipFile
    zip_root_path: str

    def __init__(self, name: str, zip_root_path: str):
        self.cnt = 0
        self.size = 0
        self.zipfile = ZipFile(name, mode="a", compression=ZIP_DEFLATED, compresslevel=9)
        self.zip_root_path = zip_root_path

    def __del__(self):
        if self.zipfile:
            self.zipfile.close()

    def add(self, data: bytes) -> StoragePath:
        self.cnt += 1
        file_name = "{:06d}.bin".format(self.cnt)
        self.zipfile.writestr(data=data, zinfo_or_arcname=file_name)
        info = self.zipfile.getinfo(file_name)
        compressed_size = info.compress_size  # Compressed size
        self.size += compressed_size
        fn = os.path.relpath(self.zipfile.filename, self.zip_root_path)
        return StoragePath(zip_path=fn, file_path=file_name)

    def overload(self, config: Config):
        return self.size >= config.max_pack_size or self.cnt >= config.max_pack_count


@dataclasses.dataclass
class ZipStorage:
    zip_root_path: str
    output_path: str
    config: Config

    _zip_cnt: int = dataclasses.field(init=False, default=0)
    _cur_package: Package = dataclasses.field(init=False, default=None)

    def _get_cur_package(self) -> Package:
        os.makedirs(self.output_path, exist_ok=True)
        if not self._cur_package or self._cur_package.overload(self.config):
            if self._cur_package:
                del self._cur_package
                self._cur_package = None
            self._zip_cnt += 1
            zip_path = os.path.join(self.output_path, "{:06}.zip".format(self._zip_cnt))
            self._cur_package = Package(zip_path, self.zip_root_path)
        return self._cur_package

    def append_file(self, file_data: bytes) -> StoragePath:
        return self._get_cur_package().add(file_data)
