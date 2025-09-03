import logging
import os
import sys

from colorama import init as colorama_init

from ec_tools_cli.auto_run.runner.cpp_runner import CRunner
from ec_tools_cli.auto_run.runner.py_runner import PyRunner


def init():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    colorama_init()


def main():
    init()
    args = sys.argv[1:]
    assert len(args) == 1, f"Expect 1 argument, but got {args}"
    path = args[0]
    runners = [CRunner(os.getcwd(), path), PyRunner(os.getcwd(), path)]
    for runner in runners:
        if runner():
            break
    logging.error("No runner found for %s", path)


if __name__ == "__main__":
    main()
