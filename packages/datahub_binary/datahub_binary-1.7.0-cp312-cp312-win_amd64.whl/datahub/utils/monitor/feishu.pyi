from .base import Monitor as Monitor
from _typeshed import Incomplete
from dataclasses import dataclass, field

TARGET: Incomplete

@dataclass
class Feishu(Monitor):
    app_id: str = ...
    app_secret: str = ...
    users: dict = field(default_factory=Incomplete)
    chats: dict = field(default_factory=Incomplete)
    def to(self, who: TARGET): ...
    def at(self, who: TARGET): ...
