import polars as pl
from _typeshed import Incomplete
from contextlib import contextmanager
from datahub.utils.logger import logger as logger
from sqlalchemy.engine import Connection as Connection, Engine as Engine
from sqlalchemy.orm import Session as Session
from typing import Any, Generator, Literal

class Database:
    engine: Incomplete
    metadata: Incomplete
    schema: Incomplete
    session_factory: Incomplete
    def __init__(self, connection_string: str, pool_size: int = 3, max_overflow: int = 10, pool_timeout: int = 30, pool_recycle: int = 3600) -> None: ...
    def insert_many(self, table_name: str, data: list[dict[str, Any]]) -> int: ...
    def query(self, sql: str, return_format: Literal['dataframe', 'records'] = 'dataframe') -> pl.DataFrame | list[dict] | None: ...
    @contextmanager
    def get_session(self) -> Generator[Session, Any, None]: ...
    def query_with_session(self, sql: str, session: Session, return_format: Literal['dataframe', 'records'] = 'dataframe'): ...
