import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Ping(_message.Message):
    __slots__ = ("msg_type", "msg_sequence")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    msg_sequence: int
    def __init__(self, msg_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ...) -> None: ...

class Pong(_message.Message):
    __slots__ = ("msg_type", "msg_sequence")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    msg_sequence: int
    def __init__(self, msg_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ...) -> None: ...

class ManagerNotLogin(_message.Message):
    __slots__ = ("msg_type", "last_timestamp")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    last_timestamp: int
    def __init__(self, msg_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ...) -> None: ...

class ManagerErrorMsg(_message.Message):
    __slots__ = ("msg_type", "error_msg", "last_timestamp", "request_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MSG_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    error_msg: str
    last_timestamp: int
    request_id: str
    def __init__(self, msg_type: _Optional[int] = ..., error_msg: _Optional[str] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ...) -> None: ...

class LoginReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ...) -> None: ...

class LoginRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id", "is_succ", "text")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    IS_SUCC_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    is_succ: bool
    text: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ..., is_succ: bool = ..., text: _Optional[str] = ...) -> None: ...

class StrategyControlReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "operate_type", "strategy_id", "strategy_name", "control_type", "op_user")
    class ControlType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        kInit: _ClassVar[StrategyControlReq.ControlType]
        kRun: _ClassVar[StrategyControlReq.ControlType]
        kPause: _ClassVar[StrategyControlReq.ControlType]
        kStop: _ClassVar[StrategyControlReq.ControlType]
        kClose: _ClassVar[StrategyControlReq.ControlType]
    kInit: StrategyControlReq.ControlType
    kRun: StrategyControlReq.ControlType
    kPause: StrategyControlReq.ControlType
    kStop: StrategyControlReq.ControlType
    kClose: StrategyControlReq.ControlType
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTROL_TYPE_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    operate_type: int
    strategy_id: int
    strategy_name: str
    control_type: StrategyControlReq.ControlType
    op_user: _common_pb2.OpUser
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., operate_type: _Optional[int] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., control_type: _Optional[_Union[StrategyControlReq.ControlType, str]] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ...) -> None: ...

class StrategyControlRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "strategy_name", "strategy_id", "status", "text")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    strategy_name: str
    strategy_id: int
    status: int
    text: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., strategy_name: _Optional[str] = ..., strategy_id: _Optional[int] = ..., status: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class UpdateStrategyParamsReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "operate_type", "strategy_name", "strategy_id", "text", "strategy_params", "monitor_params", "strategy_instruments", "signal_id", "signal_name", "target_qty", "op_user")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_PARAMS_FIELD_NUMBER: _ClassVar[int]
    MONITOR_PARAMS_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_INSTRUMENTS_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_NAME_FIELD_NUMBER: _ClassVar[int]
    TARGET_QTY_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    operate_type: int
    strategy_name: str
    strategy_id: int
    text: str
    strategy_params: str
    monitor_params: str
    strategy_instruments: _containers.RepeatedCompositeFieldContainer[_common_pb2.StrategyInstrument]
    signal_id: int
    signal_name: str
    target_qty: int
    op_user: _common_pb2.OpUser
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., operate_type: _Optional[int] = ..., strategy_name: _Optional[str] = ..., strategy_id: _Optional[int] = ..., text: _Optional[str] = ..., strategy_params: _Optional[str] = ..., monitor_params: _Optional[str] = ..., strategy_instruments: _Optional[_Iterable[_Union[_common_pb2.StrategyInstrument, _Mapping]]] = ..., signal_id: _Optional[int] = ..., signal_name: _Optional[str] = ..., target_qty: _Optional[int] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ...) -> None: ...

class UpdateStrategyParamsRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "strategy_name", "strategy_id", "status", "request_id", "text", "strategy_params", "monitor_params", "strategy_instruments", "signal_id", "signal_name", "target_qty")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_PARAMS_FIELD_NUMBER: _ClassVar[int]
    MONITOR_PARAMS_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_INSTRUMENTS_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_NAME_FIELD_NUMBER: _ClassVar[int]
    TARGET_QTY_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    strategy_name: str
    strategy_id: int
    status: int
    request_id: str
    text: str
    strategy_params: str
    monitor_params: str
    strategy_instruments: _containers.RepeatedCompositeFieldContainer[_common_pb2.StrategyInstrument]
    signal_id: int
    signal_name: str
    target_qty: int
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., strategy_name: _Optional[str] = ..., strategy_id: _Optional[int] = ..., status: _Optional[int] = ..., request_id: _Optional[str] = ..., text: _Optional[str] = ..., strategy_params: _Optional[str] = ..., monitor_params: _Optional[str] = ..., strategy_instruments: _Optional[_Iterable[_Union[_common_pb2.StrategyInstrument, _Mapping]]] = ..., signal_id: _Optional[int] = ..., signal_name: _Optional[str] = ..., target_qty: _Optional[int] = ...) -> None: ...

class UpdateStrategyGlobalParamsReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "operate_type", "strategy_template_id", "text", "strategy_params", "monitor_params", "op_user")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_PARAMS_FIELD_NUMBER: _ClassVar[int]
    MONITOR_PARAMS_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    operate_type: int
    strategy_template_id: str
    text: str
    strategy_params: str
    monitor_params: str
    op_user: _common_pb2.OpUser
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., operate_type: _Optional[int] = ..., strategy_template_id: _Optional[str] = ..., text: _Optional[str] = ..., strategy_params: _Optional[str] = ..., monitor_params: _Optional[str] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ...) -> None: ...

class UpdateStrategyGlobalParamsRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "strategy_template_id", "status", "request_id", "text", "strategy_params", "monitor_params")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_PARAMS_FIELD_NUMBER: _ClassVar[int]
    MONITOR_PARAMS_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    strategy_template_id: str
    status: int
    request_id: str
    text: str
    strategy_params: str
    monitor_params: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., strategy_template_id: _Optional[str] = ..., status: _Optional[int] = ..., request_id: _Optional[str] = ..., text: _Optional[str] = ..., strategy_params: _Optional[str] = ..., monitor_params: _Optional[str] = ...) -> None: ...

class StrategyStatDetail(_message.Message):
    __slots__ = ("strategy_id", "strategy_name", "status", "instrument_id", "sod_amount", "sod_qty", "current_qty", "posi_amount", "last_px", "buy_amount", "sell_amount", "buy_qty", "sell_qty", "exposure", "active_order_nums", "text", "avail_qty", "posi_side", "target_qty", "depth_quote", "bid_premium_rate", "ask_premium_rate", "impact_factor", "theory_price", "original_price", "cost_price", "pre_close_price", "float_pnl", "contract_unit", "posi_adjust_rate", "signal_id", "signal_name", "active_order_qty", "total_order_qty", "bid_price", "ask_price", "stat_fields", "stat_status", "account_id", "total_order_nums", "total_cancel_nums")
    class QuoteLevelData(_message.Message):
        __slots__ = ("bid_price", "bid_volume", "ask_price", "ask_volume")
        BID_PRICE_FIELD_NUMBER: _ClassVar[int]
        BID_VOLUME_FIELD_NUMBER: _ClassVar[int]
        ASK_PRICE_FIELD_NUMBER: _ClassVar[int]
        ASK_VOLUME_FIELD_NUMBER: _ClassVar[int]
        bid_price: int
        bid_volume: int
        ask_price: int
        ask_volume: int
        def __init__(self, bid_price: _Optional[int] = ..., bid_volume: _Optional[int] = ..., ask_price: _Optional[int] = ..., ask_volume: _Optional[int] = ...) -> None: ...
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    SOD_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    SOD_QTY_FIELD_NUMBER: _ClassVar[int]
    CURRENT_QTY_FIELD_NUMBER: _ClassVar[int]
    POSI_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    LAST_PX_FIELD_NUMBER: _ClassVar[int]
    BUY_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    SELL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BUY_QTY_FIELD_NUMBER: _ClassVar[int]
    SELL_QTY_FIELD_NUMBER: _ClassVar[int]
    EXPOSURE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_ORDER_NUMS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    AVAIL_QTY_FIELD_NUMBER: _ClassVar[int]
    POSI_SIDE_FIELD_NUMBER: _ClassVar[int]
    TARGET_QTY_FIELD_NUMBER: _ClassVar[int]
    DEPTH_QUOTE_FIELD_NUMBER: _ClassVar[int]
    BID_PREMIUM_RATE_FIELD_NUMBER: _ClassVar[int]
    ASK_PREMIUM_RATE_FIELD_NUMBER: _ClassVar[int]
    IMPACT_FACTOR_FIELD_NUMBER: _ClassVar[int]
    THEORY_PRICE_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_PRICE_FIELD_NUMBER: _ClassVar[int]
    COST_PRICE_FIELD_NUMBER: _ClassVar[int]
    PRE_CLOSE_PRICE_FIELD_NUMBER: _ClassVar[int]
    FLOAT_PNL_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_UNIT_FIELD_NUMBER: _ClassVar[int]
    POSI_ADJUST_RATE_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_NAME_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_ORDER_QTY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ORDER_QTY_FIELD_NUMBER: _ClassVar[int]
    BID_PRICE_FIELD_NUMBER: _ClassVar[int]
    ASK_PRICE_FIELD_NUMBER: _ClassVar[int]
    STAT_FIELDS_FIELD_NUMBER: _ClassVar[int]
    STAT_STATUS_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ORDER_NUMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CANCEL_NUMS_FIELD_NUMBER: _ClassVar[int]
    strategy_id: int
    strategy_name: str
    status: str
    instrument_id: str
    sod_amount: float
    sod_qty: int
    current_qty: int
    posi_amount: float
    last_px: float
    buy_amount: float
    sell_amount: float
    buy_qty: int
    sell_qty: int
    exposure: float
    active_order_nums: int
    text: str
    avail_qty: int
    posi_side: int
    target_qty: int
    depth_quote: _containers.RepeatedCompositeFieldContainer[StrategyStatDetail.QuoteLevelData]
    bid_premium_rate: float
    ask_premium_rate: float
    impact_factor: float
    theory_price: float
    original_price: float
    cost_price: float
    pre_close_price: float
    float_pnl: float
    contract_unit: float
    posi_adjust_rate: float
    signal_id: int
    signal_name: str
    active_order_qty: int
    total_order_qty: int
    bid_price: float
    ask_price: float
    stat_fields: str
    stat_status: int
    account_id: str
    total_order_nums: int
    total_cancel_nums: int
    def __init__(self, strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., status: _Optional[str] = ..., instrument_id: _Optional[str] = ..., sod_amount: _Optional[float] = ..., sod_qty: _Optional[int] = ..., current_qty: _Optional[int] = ..., posi_amount: _Optional[float] = ..., last_px: _Optional[float] = ..., buy_amount: _Optional[float] = ..., sell_amount: _Optional[float] = ..., buy_qty: _Optional[int] = ..., sell_qty: _Optional[int] = ..., exposure: _Optional[float] = ..., active_order_nums: _Optional[int] = ..., text: _Optional[str] = ..., avail_qty: _Optional[int] = ..., posi_side: _Optional[int] = ..., target_qty: _Optional[int] = ..., depth_quote: _Optional[_Iterable[_Union[StrategyStatDetail.QuoteLevelData, _Mapping]]] = ..., bid_premium_rate: _Optional[float] = ..., ask_premium_rate: _Optional[float] = ..., impact_factor: _Optional[float] = ..., theory_price: _Optional[float] = ..., original_price: _Optional[float] = ..., cost_price: _Optional[float] = ..., pre_close_price: _Optional[float] = ..., float_pnl: _Optional[float] = ..., contract_unit: _Optional[float] = ..., posi_adjust_rate: _Optional[float] = ..., signal_id: _Optional[int] = ..., signal_name: _Optional[str] = ..., active_order_qty: _Optional[int] = ..., total_order_qty: _Optional[int] = ..., bid_price: _Optional[float] = ..., ask_price: _Optional[float] = ..., stat_fields: _Optional[str] = ..., stat_status: _Optional[int] = ..., account_id: _Optional[str] = ..., total_order_nums: _Optional[int] = ..., total_cancel_nums: _Optional[int] = ...) -> None: ...

class QryStrategyStatReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "strategy_id", "strategy_name", "text", "op_user")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    strategy_id: int
    strategy_name: str
    text: str
    op_user: _common_pb2.OpUser
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., text: _Optional[str] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ...) -> None: ...

class QryStrategyStatRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "strategy_id", "strategy_name", "strategy_stat")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_STAT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    strategy_id: int
    strategy_name: str
    strategy_stat: _containers.RepeatedCompositeFieldContainer[StrategyStatDetail]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., strategy_stat: _Optional[_Iterable[_Union[StrategyStatDetail, _Mapping]]] = ...) -> None: ...

class StrategyStatEvent(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "msg_sequence", "strategy_id", "strategy_name", "strategy_stat")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_STAT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    msg_sequence: int
    strategy_id: int
    strategy_name: str
    strategy_stat: _containers.RepeatedCompositeFieldContainer[StrategyStatDetail]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., strategy_stat: _Optional[_Iterable[_Union[StrategyStatDetail, _Mapping]]] = ...) -> None: ...

class StrategyLogEvent(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "strategy_id", "strategy_name", "log_level", "occur_time", "file_name", "function_name", "line", "text")
    class LogLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRACE: _ClassVar[StrategyLogEvent.LogLevel]
        DEBUG: _ClassVar[StrategyLogEvent.LogLevel]
        INFO: _ClassVar[StrategyLogEvent.LogLevel]
        WARN: _ClassVar[StrategyLogEvent.LogLevel]
        ERROR: _ClassVar[StrategyLogEvent.LogLevel]
        FATAL: _ClassVar[StrategyLogEvent.LogLevel]
    TRACE: StrategyLogEvent.LogLevel
    DEBUG: StrategyLogEvent.LogLevel
    INFO: StrategyLogEvent.LogLevel
    WARN: StrategyLogEvent.LogLevel
    ERROR: StrategyLogEvent.LogLevel
    FATAL: StrategyLogEvent.LogLevel
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    LOG_LEVEL_FIELD_NUMBER: _ClassVar[int]
    OCCUR_TIME_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_NAME_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    strategy_id: int
    strategy_name: str
    log_level: StrategyLogEvent.LogLevel
    occur_time: int
    file_name: str
    function_name: str
    line: int
    text: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., log_level: _Optional[_Union[StrategyLogEvent.LogLevel, str]] = ..., occur_time: _Optional[int] = ..., file_name: _Optional[str] = ..., function_name: _Optional[str] = ..., line: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class StrategyEvent(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "control_status", "text")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CONTROL_STATUS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    control_status: int
    text: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., control_status: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class MonitorEvent(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "metric_name", "labels", "value")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    METRIC_NAME_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    metric_name: str
    labels: str
    value: float
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., metric_name: _Optional[str] = ..., labels: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...

class BookStatDetail(_message.Message):
    __slots__ = ("strategy_name", "instrument_id", "sod_qty", "avail_qty", "trade_date", "strategy_id", "current_qty", "posi_amount", "last_px", "contract_unit", "posi_side", "buy_qty", "sell_qty", "buy_amount", "sell_amount", "active_order_nums", "sod_amount", "status")
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    SOD_QTY_FIELD_NUMBER: _ClassVar[int]
    AVAIL_QTY_FIELD_NUMBER: _ClassVar[int]
    TRADE_DATE_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENT_QTY_FIELD_NUMBER: _ClassVar[int]
    POSI_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    LAST_PX_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_UNIT_FIELD_NUMBER: _ClassVar[int]
    POSI_SIDE_FIELD_NUMBER: _ClassVar[int]
    BUY_QTY_FIELD_NUMBER: _ClassVar[int]
    SELL_QTY_FIELD_NUMBER: _ClassVar[int]
    BUY_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    SELL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_ORDER_NUMS_FIELD_NUMBER: _ClassVar[int]
    SOD_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    strategy_name: str
    instrument_id: str
    sod_qty: int
    avail_qty: int
    trade_date: str
    strategy_id: int
    current_qty: int
    posi_amount: float
    last_px: float
    contract_unit: float
    posi_side: int
    buy_qty: int
    sell_qty: int
    buy_amount: float
    sell_amount: float
    active_order_nums: int
    sod_amount: float
    status: str
    def __init__(self, strategy_name: _Optional[str] = ..., instrument_id: _Optional[str] = ..., sod_qty: _Optional[int] = ..., avail_qty: _Optional[int] = ..., trade_date: _Optional[str] = ..., strategy_id: _Optional[int] = ..., current_qty: _Optional[int] = ..., posi_amount: _Optional[float] = ..., last_px: _Optional[float] = ..., contract_unit: _Optional[float] = ..., posi_side: _Optional[int] = ..., buy_qty: _Optional[int] = ..., sell_qty: _Optional[int] = ..., buy_amount: _Optional[float] = ..., sell_amount: _Optional[float] = ..., active_order_nums: _Optional[int] = ..., sod_amount: _Optional[float] = ..., status: _Optional[str] = ...) -> None: ...

class BookStatEvent(_message.Message):
    __slots__ = ("msg_type", "book_id", "comments", "settle_currency_id", "exposure", "mock_book", "is_auto_hedge", "auto_hedge_strategy_id", "book_stat_details")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    SETTLE_CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    EXPOSURE_FIELD_NUMBER: _ClassVar[int]
    MOCK_BOOK_FIELD_NUMBER: _ClassVar[int]
    IS_AUTO_HEDGE_FIELD_NUMBER: _ClassVar[int]
    AUTO_HEDGE_STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    BOOK_STAT_DETAILS_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    book_id: str
    comments: str
    settle_currency_id: str
    exposure: float
    mock_book: str
    is_auto_hedge: int
    auto_hedge_strategy_id: int
    book_stat_details: _containers.RepeatedCompositeFieldContainer[BookStatDetail]
    def __init__(self, msg_type: _Optional[int] = ..., book_id: _Optional[str] = ..., comments: _Optional[str] = ..., settle_currency_id: _Optional[str] = ..., exposure: _Optional[float] = ..., mock_book: _Optional[str] = ..., is_auto_hedge: _Optional[int] = ..., auto_hedge_strategy_id: _Optional[int] = ..., book_stat_details: _Optional[_Iterable[_Union[BookStatDetail, _Mapping]]] = ...) -> None: ...

class QryBookStatReq(_message.Message):
    __slots__ = ("msg_type", "book_id", "request_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    book_id: str
    request_id: str
    def __init__(self, msg_type: _Optional[int] = ..., book_id: _Optional[str] = ..., request_id: _Optional[str] = ...) -> None: ...

class QryBookStatRsp(_message.Message):
    __slots__ = ("msg_type", "books", "request_id", "status", "text")
    class Book(_message.Message):
        __slots__ = ("book_id", "comments", "settle_currency_id", "exposure", "mock_book", "is_auto_hedge", "auto_hedge_strategy_id", "book_stat_details")
        BOOK_ID_FIELD_NUMBER: _ClassVar[int]
        COMMENTS_FIELD_NUMBER: _ClassVar[int]
        SETTLE_CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
        EXPOSURE_FIELD_NUMBER: _ClassVar[int]
        MOCK_BOOK_FIELD_NUMBER: _ClassVar[int]
        IS_AUTO_HEDGE_FIELD_NUMBER: _ClassVar[int]
        AUTO_HEDGE_STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
        BOOK_STAT_DETAILS_FIELD_NUMBER: _ClassVar[int]
        book_id: str
        comments: str
        settle_currency_id: str
        exposure: float
        mock_book: str
        is_auto_hedge: int
        auto_hedge_strategy_id: int
        book_stat_details: _containers.RepeatedCompositeFieldContainer[BookStatDetail]
        def __init__(self, book_id: _Optional[str] = ..., comments: _Optional[str] = ..., settle_currency_id: _Optional[str] = ..., exposure: _Optional[float] = ..., mock_book: _Optional[str] = ..., is_auto_hedge: _Optional[int] = ..., auto_hedge_strategy_id: _Optional[int] = ..., book_stat_details: _Optional[_Iterable[_Union[BookStatDetail, _Mapping]]] = ...) -> None: ...
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    BOOKS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    books: _containers.RepeatedCompositeFieldContainer[QryBookStatRsp.Book]
    request_id: str
    status: int
    text: str
    def __init__(self, msg_type: _Optional[int] = ..., books: _Optional[_Iterable[_Union[QryBookStatRsp.Book, _Mapping]]] = ..., request_id: _Optional[str] = ..., status: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class ArbitrageStrategyStatEvent(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "strategy_id", "strategy_name", "signal_id", "status", "reason", "last_timestamp")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    strategy_id: int
    strategy_name: str
    signal_id: int
    status: str
    reason: str
    last_timestamp: int
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., signal_id: _Optional[int] = ..., status: _Optional[str] = ..., reason: _Optional[str] = ..., last_timestamp: _Optional[int] = ...) -> None: ...
