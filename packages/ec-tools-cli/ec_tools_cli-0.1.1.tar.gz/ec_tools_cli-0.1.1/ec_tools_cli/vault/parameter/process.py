import dataclasses
import logging
import re
import sys
from getpass import getpass

from ec_tools_cli.vault.parameter.parameter import Parameter


@dataclasses.dataclass
class ParameterProcessor:
    _log: logging.Logger
    _PASSWORD_PATTERN = re.compile(r'^[\w!@#$%^&*()_+\-=\[\]{};\'\\:"|<,./<>?]{8,}$')

    def get_value(self, parameter: Parameter) -> bytes:
        if parameter.value is not None:
            return parameter.value.encode("utf-8")
        elif parameter.file:
            with open(parameter.file, "rb") as f:
                return f.read()
        else:
            self._log.info("Press Ctrl+D (or Ctrl+Z on Windows) to end input if reading from stdin.")
            return sys.stdin.read().encode("utf-8")

    def verify_key(self, key: str) -> str:
        if key is None:
            key = input("input the key: ")
        key = key.strip()
        if not key:
            self._log("Error: Key is empty.")
            exit(-1)
        if len(key) > 255:
            self._log.error("Error: Key length exceeds 255 characters.")
            exit(-1)
        return key

    def verify_value(self, value: bytes) -> bytes:
        value = value.strip()
        if not value:
            self._log.error("Error: Value is empty.")
            exit(-1)
        if len(value) > 10 * 1024 * 1024:
            self._log.error("Error: Value size exceeds 10MB.")
            exit(-1)
        return value

    def verify_password(self, password: str) -> str:
        if password is None:
            p1 = getpass("Password: ")
            p2 = getpass("Repeat: ")
            if p1 != p2:
                self._log.error("Two passwords not match!")
                exit(-1)
            password = p1
        if not password or not self._PASSWORD_PATTERN.match(password):
            self._log.error(
                "Error: Password must be at least 8 characters long and contain only letters, digits, and special characters."
            )
            exit(-1)
        return password
