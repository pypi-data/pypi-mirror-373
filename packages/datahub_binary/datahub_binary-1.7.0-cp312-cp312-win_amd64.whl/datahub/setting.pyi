from dataclasses import dataclass

@dataclass
class RedisSetting:
    url: str
    ident: str

@dataclass
class SftpSetting:
    host: str
    port: int
    username: str
    password: str
    home_path: str

@dataclass
class StarRocksSetting:
    host: str
    db_port: int
    http_port: int
    username: str
    password: str
    timezone: str = ...
    force_query: bool = ...
    sftp: SftpSetting | None = ...

@dataclass
class PostgresSetting:
    host: str
    db_port: int
    username: str
    password: str

@dataclass
class CronServerSetting:
    host: str
    port: int

@dataclass
class Setting:
    redis: RedisSetting | None = ...
    starrocks: StarRocksSetting | None = ...
    postgres: PostgresSetting | None = ...
    sftp: SftpSetting | None = ...
    cron_server: CronServerSetting | None = ...
    timezone: str = ...
