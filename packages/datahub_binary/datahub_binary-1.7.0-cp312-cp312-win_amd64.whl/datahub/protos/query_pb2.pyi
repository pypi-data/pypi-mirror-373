import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QryOrdersReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "token", "start_row", "page_size", "request_id", "instrument_id", "strategy_id", "account_id", "cl_order_id", "order_id", "is_active", "owner_type")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    START_ROW_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    OWNER_TYPE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    token: str
    start_row: int
    page_size: int
    request_id: str
    instrument_id: str
    strategy_id: int
    account_id: str
    cl_order_id: str
    order_id: str
    is_active: int
    owner_type: int
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., token: _Optional[str] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., request_id: _Optional[str] = ..., instrument_id: _Optional[str] = ..., strategy_id: _Optional[int] = ..., account_id: _Optional[str] = ..., cl_order_id: _Optional[str] = ..., order_id: _Optional[str] = ..., is_active: _Optional[int] = ..., owner_type: _Optional[int] = ...) -> None: ...

class QryOrdersRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "request_id", "total_row", "start_row", "page_size", "is_last", "status", "reason", "order")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ROW_FIELD_NUMBER: _ClassVar[int]
    START_ROW_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    request_id: str
    total_row: int
    start_row: int
    page_size: int
    is_last: bool
    status: int
    reason: str
    order: _containers.RepeatedCompositeFieldContainer[_common_pb2.Order]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., request_id: _Optional[str] = ..., total_row: _Optional[int] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., is_last: bool = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., order: _Optional[_Iterable[_Union[_common_pb2.Order, _Mapping]]] = ...) -> None: ...

class QryTradesReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "token", "start_row", "page_size", "request_id", "security_id", "market", "instrument_id", "appl_id", "strategy_id", "strategy_name", "account_id", "cl_order_id", "order_id", "is_active")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    START_ROW_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    APPL_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    token: str
    start_row: int
    page_size: int
    request_id: str
    security_id: str
    market: str
    instrument_id: str
    appl_id: str
    strategy_id: int
    strategy_name: str
    account_id: str
    cl_order_id: str
    order_id: str
    is_active: int
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., token: _Optional[str] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., request_id: _Optional[str] = ..., security_id: _Optional[str] = ..., market: _Optional[str] = ..., instrument_id: _Optional[str] = ..., appl_id: _Optional[str] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., account_id: _Optional[str] = ..., cl_order_id: _Optional[str] = ..., order_id: _Optional[str] = ..., is_active: _Optional[int] = ...) -> None: ...

class QryTradesRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "request_id", "total_row", "start_row", "page_size", "is_last", "status", "reason", "trade")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ROW_FIELD_NUMBER: _ClassVar[int]
    START_ROW_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    TRADE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    request_id: str
    total_row: int
    start_row: int
    page_size: int
    is_last: bool
    status: int
    reason: str
    trade: _containers.RepeatedCompositeFieldContainer[_common_pb2.Trade]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., request_id: _Optional[str] = ..., total_row: _Optional[int] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., is_last: bool = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., trade: _Optional[_Iterable[_Union[_common_pb2.Trade, _Mapping]]] = ...) -> None: ...

class QryBrokerOrdersReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "token", "start_row", "page_size", "request_id", "instrument_id", "strategy_id", "account_id", "cl_order_id", "order_id", "is_active")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    START_ROW_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    token: str
    start_row: int
    page_size: int
    request_id: str
    instrument_id: str
    strategy_id: int
    account_id: str
    cl_order_id: str
    order_id: str
    is_active: int
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., token: _Optional[str] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., request_id: _Optional[str] = ..., instrument_id: _Optional[str] = ..., strategy_id: _Optional[int] = ..., account_id: _Optional[str] = ..., cl_order_id: _Optional[str] = ..., order_id: _Optional[str] = ..., is_active: _Optional[int] = ...) -> None: ...

class QryBrokerOrdersRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "request_id", "total_row", "start_row", "page_size", "is_last", "status", "reason", "order")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ROW_FIELD_NUMBER: _ClassVar[int]
    START_ROW_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    request_id: str
    total_row: int
    start_row: int
    page_size: int
    is_last: bool
    status: int
    reason: str
    order: _containers.RepeatedCompositeFieldContainer[_common_pb2.Order]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., request_id: _Optional[str] = ..., total_row: _Optional[int] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., is_last: bool = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., order: _Optional[_Iterable[_Union[_common_pb2.Order, _Mapping]]] = ...) -> None: ...

class QryBrokerTradesReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "token", "start_row", "page_size", "request_id", "instrument_id", "strategy_id", "account_id", "cl_order_id", "order_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    START_ROW_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    token: str
    start_row: int
    page_size: int
    request_id: str
    instrument_id: str
    strategy_id: int
    account_id: str
    cl_order_id: str
    order_id: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., token: _Optional[str] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., request_id: _Optional[str] = ..., instrument_id: _Optional[str] = ..., strategy_id: _Optional[int] = ..., account_id: _Optional[str] = ..., cl_order_id: _Optional[str] = ..., order_id: _Optional[str] = ...) -> None: ...

class QryBrokerTradesRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "request_id", "total_row", "start_row", "page_size", "is_last", "status", "reason", "trade")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ROW_FIELD_NUMBER: _ClassVar[int]
    START_ROW_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    TRADE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    request_id: str
    total_row: int
    start_row: int
    page_size: int
    is_last: bool
    status: int
    reason: str
    trade: _containers.RepeatedCompositeFieldContainer[_common_pb2.Trade]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., request_id: _Optional[str] = ..., total_row: _Optional[int] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., is_last: bool = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., trade: _Optional[_Iterable[_Union[_common_pb2.Trade, _Mapping]]] = ...) -> None: ...

class QryBrokerInstrumentReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "token", "start_row", "page_size", "request_id", "security_id", "market", "instrument_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    START_ROW_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    token: str
    start_row: int
    page_size: int
    request_id: str
    security_id: str
    market: str
    instrument_id: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., token: _Optional[str] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., request_id: _Optional[str] = ..., security_id: _Optional[str] = ..., market: _Optional[str] = ..., instrument_id: _Optional[str] = ...) -> None: ...

class QryBrokerInstrumentRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "request_id", "total_row", "start_row", "page_size", "is_last", "status", "reason", "instrument")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ROW_FIELD_NUMBER: _ClassVar[int]
    START_ROW_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    request_id: str
    total_row: int
    start_row: int
    page_size: int
    is_last: bool
    status: int
    reason: str
    instrument: _containers.RepeatedCompositeFieldContainer[_common_pb2.Instrument]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., request_id: _Optional[str] = ..., total_row: _Optional[int] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., is_last: bool = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., instrument: _Optional[_Iterable[_Union[_common_pb2.Instrument, _Mapping]]] = ...) -> None: ...
