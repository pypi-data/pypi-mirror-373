import dataclasses
import enum
from typing import Optional


class Method(enum.Enum):
    LIST = "list"
    INSERT = "insert"
    GET = "get"
    DELETE = "delete"

    @classmethod
    def from_str(cls, method_str: str) -> "Method":
        for method in cls:
            if method.value.lower() == method_str.lower():
                return method
        raise ValueError(f"Unknown method: {method_str}")


@dataclasses.dataclass
class Parameter:
    method: Method
    db_path: str
    password: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    file: Optional[str] = None
    output: Optional[str] = None
    silent: Optional[bool] = None
