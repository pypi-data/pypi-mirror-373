import logging

from colorama import Fore, Style

from ec_tools_cli.auto_run.runner.auto_runner import AutoRunner


class CRunner(AutoRunner):

    def _run(self):
        dot_index = self.file_name.rfind(".")
        binary = self.file_name[:dot_index]
        result = self._cmd(f"g++ {self.file_name} -o {binary} -O2 -Wall -std=c++17")
        if result:
            logging.error(f"compile failed for %s", self.file_name)
            exit(-1)
        else:
            logging.info(f"compile successfully for %s", self.file_name)
        self._run_cmd(binary)

    def _applicable(self) -> bool:
        return self.file_name.endswith("cpp") or self.file_name.endswith("c")

    def _run_cmd(self, binary: str):
        in_file = binary + ".in"
        out_file = binary + ".out"
        txt_file = binary + ".txt"
        if self._exist(in_file) and self._exist(txt_file):
            in_data = self._read_file(in_file)
            self._cmd(
                f"./{binary} < {in_file} > {out_file};",
                call_prev=lambda: logging.info(f"{Fore.BLUE}{in_data}{Style.RESET_ALL}"),
                callback=lambda: self._diff(self._abs_path(txt_file), self._abs_path(out_file)),
            )
        elif self._exist(in_file):
            in_data = self._read_file(in_file)
            self._cmd(
                f"./{binary} < {in_file}",
                call_prev=lambda: logging.info(f"{Fore.BLUE}{in_data}{Style.RESET_ALL}"),
            )
        else:
            self._cmd(f"./{binary}")
