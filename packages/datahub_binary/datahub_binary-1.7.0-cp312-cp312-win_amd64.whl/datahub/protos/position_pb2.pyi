import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PosType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    kPosTypeUndefined: _ClassVar[PosType]
    kPosTypeSod: _ClassVar[PosType]
    kPosTypeEod: _ClassVar[PosType]
    kPosTypeFrozen: _ClassVar[PosType]
    kPosTypeBuyIn: _ClassVar[PosType]
    kPosTypeSellOut: _ClassVar[PosType]
    kPosTypeTransIn: _ClassVar[PosType]
    kPosTypeTransOut: _ClassVar[PosType]
    kPosTypeTransAvl: _ClassVar[PosType]
    kPosTypeApplyAvl: _ClassVar[PosType]
    kPosTypeIntraday: _ClassVar[PosType]
    kPosTypeBuyinNodeal: _ClassVar[PosType]

class PosReqType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    kReplace: _ClassVar[PosReqType]
    kInit: _ClassVar[PosReqType]
    kDelta: _ClassVar[PosReqType]
    kTransIn: _ClassVar[PosReqType]
    kTransOut: _ClassVar[PosReqType]
    kQuery: _ClassVar[PosReqType]
    kFullQuery: _ClassVar[PosReqType]
    kSetting: _ClassVar[PosReqType]

class PosAccountType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    kSec: _ClassVar[PosAccountType]
    kCash: _ClassVar[PosAccountType]
kPosTypeUndefined: PosType
kPosTypeSod: PosType
kPosTypeEod: PosType
kPosTypeFrozen: PosType
kPosTypeBuyIn: PosType
kPosTypeSellOut: PosType
kPosTypeTransIn: PosType
kPosTypeTransOut: PosType
kPosTypeTransAvl: PosType
kPosTypeApplyAvl: PosType
kPosTypeIntraday: PosType
kPosTypeBuyinNodeal: PosType
kReplace: PosReqType
kInit: PosReqType
kDelta: PosReqType
kTransIn: PosReqType
kTransOut: PosReqType
kQuery: PosReqType
kFullQuery: PosReqType
kSetting: PosReqType
kSec: PosAccountType
kCash: PosAccountType

class QryFundReq(_message.Message):
    __slots__ = ("msg_type", "node_type", "node_name", "account_id", "request_id", "start_row", "page_size", "token")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    START_ROW_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_type: int
    node_name: str
    account_id: str
    request_id: str
    start_row: int
    page_size: int
    token: str
    def __init__(self, msg_type: _Optional[int] = ..., node_type: _Optional[int] = ..., node_name: _Optional[str] = ..., account_id: _Optional[str] = ..., request_id: _Optional[str] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., token: _Optional[str] = ...) -> None: ...

class QryFundRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "request_id", "total_row", "start_row", "page_size", "is_last", "status", "reason", "fund")
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
    FUND_FIELD_NUMBER: _ClassVar[int]
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
    fund: _containers.RepeatedCompositeFieldContainer[_common_pb2.Fund]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., request_id: _Optional[str] = ..., total_row: _Optional[int] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., is_last: bool = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., fund: _Optional[_Iterable[_Union[_common_pb2.Fund, _Mapping]]] = ...) -> None: ...

class QryPosiReq(_message.Message):
    __slots__ = ("msg_type", "node_type", "node_name", "request_id", "security_id", "market", "account_id", "token", "start_row", "page_size")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    START_ROW_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_type: int
    node_name: str
    request_id: str
    security_id: str
    market: str
    account_id: str
    token: str
    start_row: int
    page_size: int
    def __init__(self, msg_type: _Optional[int] = ..., node_type: _Optional[int] = ..., node_name: _Optional[str] = ..., request_id: _Optional[str] = ..., security_id: _Optional[str] = ..., market: _Optional[str] = ..., account_id: _Optional[str] = ..., token: _Optional[str] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ...) -> None: ...

class QryPosiRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "request_id", "total_row", "start_row", "page_size", "is_last", "status", "reason", "position")
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
    POSITION_FIELD_NUMBER: _ClassVar[int]
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
    position: _containers.RepeatedCompositeFieldContainer[_common_pb2.Position]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., request_id: _Optional[str] = ..., total_row: _Optional[int] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., is_last: bool = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., position: _Optional[_Iterable[_Union[_common_pb2.Position, _Mapping]]] = ...) -> None: ...

class QryBrokerPosiReq(_message.Message):
    __slots__ = ("msg_type", "node_type", "node_name", "request_id", "security_id", "market", "account_id", "token", "start_row", "page_size", "query_index")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    START_ROW_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    QUERY_INDEX_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_type: int
    node_name: str
    request_id: str
    security_id: str
    market: str
    account_id: str
    token: str
    start_row: int
    page_size: int
    query_index: str
    def __init__(self, msg_type: _Optional[int] = ..., node_type: _Optional[int] = ..., node_name: _Optional[str] = ..., request_id: _Optional[str] = ..., security_id: _Optional[str] = ..., market: _Optional[str] = ..., account_id: _Optional[str] = ..., token: _Optional[str] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., query_index: _Optional[str] = ...) -> None: ...

class QryBrokerPosiRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "request_id", "total_row", "start_row", "page_size", "is_last", "status", "reason", "position")
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
    POSITION_FIELD_NUMBER: _ClassVar[int]
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
    position: _containers.RepeatedCompositeFieldContainer[_common_pb2.Position]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., request_id: _Optional[str] = ..., total_row: _Optional[int] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., is_last: bool = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., position: _Optional[_Iterable[_Union[_common_pb2.Position, _Mapping]]] = ...) -> None: ...

class QryBrokerFundReq(_message.Message):
    __slots__ = ("msg_type", "node_type", "node_name", "account_id", "request_id", "start_row", "page_size", "token")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    START_ROW_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_type: int
    node_name: str
    account_id: str
    request_id: str
    start_row: int
    page_size: int
    token: str
    def __init__(self, msg_type: _Optional[int] = ..., node_type: _Optional[int] = ..., node_name: _Optional[str] = ..., account_id: _Optional[str] = ..., request_id: _Optional[str] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., token: _Optional[str] = ...) -> None: ...

class QryBrokerFundRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "request_id", "total_row", "start_row", "page_size", "is_last", "status", "reason", "fund")
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
    FUND_FIELD_NUMBER: _ClassVar[int]
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
    fund: _containers.RepeatedCompositeFieldContainer[_common_pb2.Fund]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., request_id: _Optional[str] = ..., total_row: _Optional[int] = ..., start_row: _Optional[int] = ..., page_size: _Optional[int] = ..., is_last: bool = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., fund: _Optional[_Iterable[_Union[_common_pb2.Fund, _Mapping]]] = ...) -> None: ...

class PositionQty(_message.Message):
    __slots__ = ("type", "qty")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    QTY_FIELD_NUMBER: _ClassVar[int]
    type: PosType
    qty: int
    def __init__(self, type: _Optional[_Union[PosType, str]] = ..., qty: _Optional[int] = ...) -> None: ...

class RequestForPosition(_message.Message):
    __slots__ = ("msg_type", "request_id", "pos_req_type", "account_id", "investor_id", "node_name", "version", "market", "security_id", "posi_side", "pos_qty")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    POS_REQ_TYPE_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    POSI_SIDE_FIELD_NUMBER: _ClassVar[int]
    POS_QTY_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    request_id: str
    pos_req_type: PosReqType
    account_id: str
    investor_id: str
    node_name: str
    version: int
    market: str
    security_id: str
    posi_side: int
    pos_qty: _containers.RepeatedCompositeFieldContainer[PositionQty]
    def __init__(self, msg_type: _Optional[int] = ..., request_id: _Optional[str] = ..., pos_req_type: _Optional[_Union[PosReqType, str]] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., node_name: _Optional[str] = ..., version: _Optional[int] = ..., market: _Optional[str] = ..., security_id: _Optional[str] = ..., posi_side: _Optional[int] = ..., pos_qty: _Optional[_Iterable[_Union[PositionQty, _Mapping]]] = ...) -> None: ...

class PositionReport(_message.Message):
    __slots__ = ("msg_type", "msg_sequence", "node_name", "node_type", "request_id", "pos_req_type", "pos_account_type", "pos_rpt_id", "status", "text", "is_last", "version", "account_id", "investor_id", "market", "security_id", "balance", "available", "cost_price", "realized_pnl", "cost_amt", "symbol", "security_type", "posi_side", "instrument_id", "is_support_trans", "pos_qty")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    POS_REQ_TYPE_FIELD_NUMBER: _ClassVar[int]
    POS_ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    POS_RPT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    COST_PRICE_FIELD_NUMBER: _ClassVar[int]
    REALIZED_PNL_FIELD_NUMBER: _ClassVar[int]
    COST_AMT_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    SECURITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    POSI_SIDE_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    IS_SUPPORT_TRANS_FIELD_NUMBER: _ClassVar[int]
    POS_QTY_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    msg_sequence: int
    node_name: str
    node_type: int
    request_id: str
    pos_req_type: PosReqType
    pos_account_type: PosAccountType
    pos_rpt_id: str
    status: int
    text: str
    is_last: bool
    version: int
    account_id: str
    investor_id: str
    market: str
    security_id: str
    balance: int
    available: int
    cost_price: float
    realized_pnl: float
    cost_amt: float
    symbol: str
    security_type: str
    posi_side: int
    instrument_id: str
    is_support_trans: bool
    pos_qty: _containers.RepeatedCompositeFieldContainer[PositionQty]
    def __init__(self, msg_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ..., pos_req_type: _Optional[_Union[PosReqType, str]] = ..., pos_account_type: _Optional[_Union[PosAccountType, str]] = ..., pos_rpt_id: _Optional[str] = ..., status: _Optional[int] = ..., text: _Optional[str] = ..., is_last: bool = ..., version: _Optional[int] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., market: _Optional[str] = ..., security_id: _Optional[str] = ..., balance: _Optional[int] = ..., available: _Optional[int] = ..., cost_price: _Optional[float] = ..., realized_pnl: _Optional[float] = ..., cost_amt: _Optional[float] = ..., symbol: _Optional[str] = ..., security_type: _Optional[str] = ..., posi_side: _Optional[int] = ..., instrument_id: _Optional[str] = ..., is_support_trans: bool = ..., pos_qty: _Optional[_Iterable[_Union[PositionQty, _Mapping]]] = ...) -> None: ...

class FundQty(_message.Message):
    __slots__ = ("type", "qty")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    QTY_FIELD_NUMBER: _ClassVar[int]
    type: PosType
    qty: float
    def __init__(self, type: _Optional[_Union[PosType, str]] = ..., qty: _Optional[float] = ...) -> None: ...

class FundReport(_message.Message):
    __slots__ = ("msg_type", "msg_sequence", "node_name", "node_type", "request_id", "pos_req_type", "report_id", "status", "text", "is_last", "version", "account_id", "investor_id", "balance", "available", "currency_id", "is_support_trans", "fund_qty")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    POS_REQ_TYPE_FIELD_NUMBER: _ClassVar[int]
    REPORT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    IS_SUPPORT_TRANS_FIELD_NUMBER: _ClassVar[int]
    FUND_QTY_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    msg_sequence: int
    node_name: str
    node_type: int
    request_id: str
    pos_req_type: PosReqType
    report_id: str
    status: int
    text: str
    is_last: bool
    version: int
    account_id: str
    investor_id: str
    balance: float
    available: float
    currency_id: str
    is_support_trans: bool
    fund_qty: _containers.RepeatedCompositeFieldContainer[FundQty]
    def __init__(self, msg_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ..., pos_req_type: _Optional[_Union[PosReqType, str]] = ..., report_id: _Optional[str] = ..., status: _Optional[int] = ..., text: _Optional[str] = ..., is_last: bool = ..., version: _Optional[int] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., balance: _Optional[float] = ..., available: _Optional[float] = ..., currency_id: _Optional[str] = ..., is_support_trans: bool = ..., fund_qty: _Optional[_Iterable[_Union[FundQty, _Mapping]]] = ...) -> None: ...

class PosiEvent(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "position")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    position: _common_pb2.Position
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., position: _Optional[_Union[_common_pb2.Position, _Mapping]] = ...) -> None: ...

class QrySblListReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "sbl_ids", "request_id", "last_timestamp")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SBL_IDS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    sbl_ids: _containers.RepeatedScalarFieldContainer[str]
    request_id: str
    last_timestamp: int
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., sbl_ids: _Optional[_Iterable[str]] = ..., request_id: _Optional[str] = ..., last_timestamp: _Optional[int] = ...) -> None: ...

class SblList(_message.Message):
    __slots__ = ("sbl_id", "broker", "trade_date", "instrument_id", "intrate", "avail_sbl_qty")
    SBL_ID_FIELD_NUMBER: _ClassVar[int]
    BROKER_FIELD_NUMBER: _ClassVar[int]
    TRADE_DATE_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    INTRATE_FIELD_NUMBER: _ClassVar[int]
    AVAIL_SBL_QTY_FIELD_NUMBER: _ClassVar[int]
    sbl_id: str
    broker: str
    trade_date: str
    instrument_id: str
    intrate: float
    avail_sbl_qty: int
    def __init__(self, sbl_id: _Optional[str] = ..., broker: _Optional[str] = ..., trade_date: _Optional[str] = ..., instrument_id: _Optional[str] = ..., intrate: _Optional[float] = ..., avail_sbl_qty: _Optional[int] = ...) -> None: ...

class QrySblListRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "sbl_list", "request_id", "status", "reason", "last_timestamp")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SBL_LIST_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    sbl_list: _containers.RepeatedCompositeFieldContainer[SblList]
    request_id: str
    status: int
    reason: str
    last_timestamp: int
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., sbl_list: _Optional[_Iterable[_Union[SblList, _Mapping]]] = ..., request_id: _Optional[str] = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., last_timestamp: _Optional[int] = ...) -> None: ...

class LockSblReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "strategy_id", "instrument_id", "lock_qty", "cl_order_id", "last_timestamp", "sbl_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    LOCK_QTY_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SBL_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    strategy_id: int
    instrument_id: str
    lock_qty: int
    cl_order_id: str
    last_timestamp: int
    sbl_id: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., strategy_id: _Optional[int] = ..., instrument_id: _Optional[str] = ..., lock_qty: _Optional[int] = ..., cl_order_id: _Optional[str] = ..., last_timestamp: _Optional[int] = ..., sbl_id: _Optional[str] = ...) -> None: ...

class LockSblRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "strategy_id", "account_id", "instrument_id", "locked_qty", "intrate", "status", "duration", "reason", "cl_order_id", "last_timestamp", "sbl_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    LOCKED_QTY_FIELD_NUMBER: _ClassVar[int]
    INTRATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SBL_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    strategy_id: int
    account_id: str
    instrument_id: str
    locked_qty: int
    intrate: float
    status: int
    duration: int
    reason: str
    cl_order_id: str
    last_timestamp: int
    sbl_id: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., strategy_id: _Optional[int] = ..., account_id: _Optional[str] = ..., instrument_id: _Optional[str] = ..., locked_qty: _Optional[int] = ..., intrate: _Optional[float] = ..., status: _Optional[int] = ..., duration: _Optional[int] = ..., reason: _Optional[str] = ..., cl_order_id: _Optional[str] = ..., last_timestamp: _Optional[int] = ..., sbl_id: _Optional[str] = ...) -> None: ...

class QryLockRecordReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "strategy_id", "instrument_id", "request_id", "last_timestamp")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    strategy_id: int
    instrument_id: str
    request_id: str
    last_timestamp: int
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., strategy_id: _Optional[int] = ..., instrument_id: _Optional[str] = ..., request_id: _Optional[str] = ..., last_timestamp: _Optional[int] = ...) -> None: ...

class LockRecord(_message.Message):
    __slots__ = ("sbl_id", "instrument_id", "locked_qty", "intrate", "status", "reason", "cl_order_id", "duration", "request_time", "response_time", "counter_order_id")
    SBL_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    LOCKED_QTY_FIELD_NUMBER: _ClassVar[int]
    INTRATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TIME_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TIME_FIELD_NUMBER: _ClassVar[int]
    COUNTER_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    sbl_id: str
    instrument_id: str
    locked_qty: int
    intrate: float
    status: int
    reason: str
    cl_order_id: str
    duration: int
    request_time: int
    response_time: int
    counter_order_id: int
    def __init__(self, sbl_id: _Optional[str] = ..., instrument_id: _Optional[str] = ..., locked_qty: _Optional[int] = ..., intrate: _Optional[float] = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., cl_order_id: _Optional[str] = ..., duration: _Optional[int] = ..., request_time: _Optional[int] = ..., response_time: _Optional[int] = ..., counter_order_id: _Optional[int] = ...) -> None: ...

class QryLockRecordRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "account_id", "strategy_id", "lock_records", "request_id", "status", "reason", "last_timestamp")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    LOCK_RECORDS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    account_id: str
    strategy_id: int
    lock_records: _containers.RepeatedCompositeFieldContainer[LockRecord]
    request_id: str
    status: int
    reason: str
    last_timestamp: int
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., account_id: _Optional[str] = ..., strategy_id: _Optional[int] = ..., lock_records: _Optional[_Iterable[_Union[LockRecord, _Mapping]]] = ..., request_id: _Optional[str] = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., last_timestamp: _Optional[int] = ...) -> None: ...

class QryLockPositionReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "strategy_id", "instrument_id", "last_timestamp", "request_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    strategy_id: int
    instrument_id: str
    last_timestamp: int
    request_id: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., strategy_id: _Optional[int] = ..., instrument_id: _Optional[str] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ...) -> None: ...

class LockPosition(_message.Message):
    __slots__ = ("trade_date", "instrument_id", "long_quota_limit_qty", "long_available_qty", "short_quota_limit_qty", "short_available_qty", "update_time")
    TRADE_DATE_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    LONG_QUOTA_LIMIT_QTY_FIELD_NUMBER: _ClassVar[int]
    LONG_AVAILABLE_QTY_FIELD_NUMBER: _ClassVar[int]
    SHORT_QUOTA_LIMIT_QTY_FIELD_NUMBER: _ClassVar[int]
    SHORT_AVAILABLE_QTY_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    trade_date: str
    instrument_id: str
    long_quota_limit_qty: int
    long_available_qty: int
    short_quota_limit_qty: int
    short_available_qty: int
    update_time: int
    def __init__(self, trade_date: _Optional[str] = ..., instrument_id: _Optional[str] = ..., long_quota_limit_qty: _Optional[int] = ..., long_available_qty: _Optional[int] = ..., short_quota_limit_qty: _Optional[int] = ..., short_available_qty: _Optional[int] = ..., update_time: _Optional[int] = ...) -> None: ...

class QryLockPositionRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "strategy_id", "account_id", "lock_positions", "status", "reason", "last_timestamp", "request_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    LOCK_POSITIONS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    strategy_id: int
    account_id: str
    lock_positions: _containers.RepeatedCompositeFieldContainer[LockPosition]
    status: int
    reason: str
    last_timestamp: int
    request_id: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., strategy_id: _Optional[int] = ..., account_id: _Optional[str] = ..., lock_positions: _Optional[_Iterable[_Union[LockPosition, _Mapping]]] = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ...) -> None: ...
