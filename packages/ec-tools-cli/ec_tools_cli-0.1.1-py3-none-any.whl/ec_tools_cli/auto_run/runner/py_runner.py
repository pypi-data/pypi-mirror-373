from typing import List

from ec_tools_cli.auto_run.runner.auto_runner import SimpleRunner


class PyRunner(SimpleRunner):

    def _suffixes(self) -> List[str]:
        return ["py"]

    def _run_pattern(self) -> str:
        return "python3 {file_name}"
