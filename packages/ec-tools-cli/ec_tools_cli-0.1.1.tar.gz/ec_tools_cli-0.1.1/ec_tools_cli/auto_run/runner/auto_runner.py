import abc
import dataclasses
import logging
import os
import subprocess
import sys
from typing import Callable, List

from colorama import Fore, Style
from ec_tools.utils.timer import Timer


@dataclasses.dataclass
class AutoRunner(abc.ABC):
    dir_path: str
    file_name: str

    def __call__(self) -> bool:
        if self._applicable():
            logging.info(f"run %s for %s", self.__class__.__name__, self.file_name)
            self._run()
            return True
        return False

    @abc.abstractmethod
    def _run(self): ...

    @abc.abstractmethod
    def _applicable(self) -> bool: ...

    def _cmd(
        self,
        cmd: str,
        *,
        call_prev: Callable = lambda: None,
        callback: Callable = lambda: None,
    ) -> int:
        with Timer(f"$ {cmd}"):
            call_prev()
            full_cmd = f'cd "{self.dir_path}"; {cmd}'
            pipe = subprocess.Popen(full_cmd, shell=True, stdout=sys.stdout, stdin=sys.stdin)
            pipe.communicate()
            callback()
        return pipe.returncode

    def _abs_path(self, file_name: str) -> str:
        if os.path.isabs(file_name):
            return file_name
        return os.path.join(self.dir_path, file_name)

    def _exist(self, file_name: str) -> bool:
        return os.path.exists(self._abs_path(file_name))

    def _read_file(self, file_name: str) -> str:
        with open(self._abs_path(file_name), "r") as f:
            return f.read().strip()

    def _diff(self, a: str, b: str):
        a_content = self._read_file(a).splitlines()
        b_content = self._read_file(b).splitlines()
        rows = len(a_content)
        j = 0
        for i in range(rows):
            row_a = a_content[i] if i < len(a_content) else ""
            row_b = b_content[j] if j < len(b_content) else ""
            while row_b.startswith("~") and row_a != row_b:
                j += 1
                logging.info(f"                {Fore.GREEN}{row_b}{Style.RESET_ALL}")
                row_b = b_content[j] if j < len(b_content) else ""

            if row_a != row_b:
                logging.info(f"#{i + 1:2d}: {Fore.RED}{row_a}{Style.RESET_ALL} {Fore.GREEN}{row_b}{Style.RESET_ALL}")
            else:
                logging.info(f"#{i + 1:2d}: {row_a}")
            j += 1


class SimpleRunner(AutoRunner):

    @abc.abstractmethod
    def _suffixes(self) -> List[str]: ...

    @abc.abstractmethod
    def _run_pattern(self) -> str: ...

    def _applicable(self) -> bool:
        return self.file_name.split(".")[-1] in self._suffixes()

    def _run(self):
        return self._cmd(self._run_pattern().format(file_name=self.file_name))
