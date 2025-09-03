from .monitor import Feishu as Feishu
from _typeshed import Incomplete
from typing import Callable, Literal

LOGURU_LEVEL: Incomplete

def timer_decorator(func: Callable) -> Callable: ...
def filter_log_level(record, level): ...

class Logger:
    log_dir: Incomplete
    retention: Incomplete
    name: Incomplete
    log_format: Incomplete
    trace: Incomplete
    debug: Incomplete
    info: Incomplete
    warning: Incomplete
    error: Incomplete
    exception: Incomplete
    min_level: Incomplete
    min_level_no: Incomplete
    monitor_type: Incomplete
    monitor: Incomplete
    def __init__(self, name: str, log_dir: str | None = None, retention: int = 5, monitor_type: Literal['Feishu'] = 'Feishu', prefix: str = '') -> None: ...

def main() -> None: ...
