import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlaceOrder(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "cl_order_id", "market", "security_id", "instrument_id", "security_type", "appl_id", "user_id", "op_user", "strategy_id", "strategy_name", "account_id", "investor_id", "is_pre_order", "trigger_time", "order_type", "side", "position_effect", "time_in_force", "purpose", "stop_px", "order_price", "order_qty", "is_pass", "owner_type", "algo_type", "algo_params", "order_source", "attachment", "parent_order_id", "basket_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    APPL_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    IS_PRE_ORDER_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_TIME_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    POSITION_EFFECT_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_FORCE_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    STOP_PX_FIELD_NUMBER: _ClassVar[int]
    ORDER_PRICE_FIELD_NUMBER: _ClassVar[int]
    ORDER_QTY_FIELD_NUMBER: _ClassVar[int]
    IS_PASS_FIELD_NUMBER: _ClassVar[int]
    OWNER_TYPE_FIELD_NUMBER: _ClassVar[int]
    ALGO_TYPE_FIELD_NUMBER: _ClassVar[int]
    ALGO_PARAMS_FIELD_NUMBER: _ClassVar[int]
    ORDER_SOURCE_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENT_FIELD_NUMBER: _ClassVar[int]
    PARENT_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    BASKET_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    cl_order_id: str
    market: str
    security_id: str
    instrument_id: str
    security_type: str
    appl_id: str
    user_id: str
    op_user: _common_pb2.OpUser
    strategy_id: int
    strategy_name: str
    account_id: str
    investor_id: str
    is_pre_order: int
    trigger_time: int
    order_type: int
    side: int
    position_effect: int
    time_in_force: int
    purpose: int
    stop_px: float
    order_price: float
    order_qty: int
    is_pass: int
    owner_type: int
    algo_type: int
    algo_params: _common_pb2.AlgoParams
    order_source: str
    attachment: str
    parent_order_id: str
    basket_id: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., cl_order_id: _Optional[str] = ..., market: _Optional[str] = ..., security_id: _Optional[str] = ..., instrument_id: _Optional[str] = ..., security_type: _Optional[str] = ..., appl_id: _Optional[str] = ..., user_id: _Optional[str] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., is_pre_order: _Optional[int] = ..., trigger_time: _Optional[int] = ..., order_type: _Optional[int] = ..., side: _Optional[int] = ..., position_effect: _Optional[int] = ..., time_in_force: _Optional[int] = ..., purpose: _Optional[int] = ..., stop_px: _Optional[float] = ..., order_price: _Optional[float] = ..., order_qty: _Optional[int] = ..., is_pass: _Optional[int] = ..., owner_type: _Optional[int] = ..., algo_type: _Optional[int] = ..., algo_params: _Optional[_Union[_common_pb2.AlgoParams, _Mapping]] = ..., order_source: _Optional[str] = ..., attachment: _Optional[str] = ..., parent_order_id: _Optional[str] = ..., basket_id: _Optional[str] = ...) -> None: ...

class OrderPendingConfirm(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "cl_order_id", "order_id", "security_id", "market", "instrument_id", "appl_id", "strategy_id", "strategy_name", "account_id", "investor_id", "confirm_qty", "reject_qty", "is_pass", "order_price", "contract_unit", "position_effect")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    APPL_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIRM_QTY_FIELD_NUMBER: _ClassVar[int]
    REJECT_QTY_FIELD_NUMBER: _ClassVar[int]
    IS_PASS_FIELD_NUMBER: _ClassVar[int]
    ORDER_PRICE_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_UNIT_FIELD_NUMBER: _ClassVar[int]
    POSITION_EFFECT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    cl_order_id: str
    order_id: str
    security_id: str
    market: str
    instrument_id: str
    appl_id: str
    strategy_id: int
    strategy_name: str
    account_id: str
    investor_id: str
    confirm_qty: int
    reject_qty: int
    is_pass: int
    order_price: float
    contract_unit: float
    position_effect: int
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., cl_order_id: _Optional[str] = ..., order_id: _Optional[str] = ..., security_id: _Optional[str] = ..., market: _Optional[str] = ..., instrument_id: _Optional[str] = ..., appl_id: _Optional[str] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., confirm_qty: _Optional[int] = ..., reject_qty: _Optional[int] = ..., is_pass: _Optional[int] = ..., order_price: _Optional[float] = ..., contract_unit: _Optional[float] = ..., position_effect: _Optional[int] = ...) -> None: ...

class OrderConfirm(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "cl_order_id", "order_id", "counter_order_id", "security_id", "market", "instrument_id", "appl_id", "strategy_id", "strategy_name", "account_id", "investor_id", "confirm_qty", "reject_qty", "is_pass", "order_price", "contract_unit", "position_effect")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    COUNTER_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    APPL_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIRM_QTY_FIELD_NUMBER: _ClassVar[int]
    REJECT_QTY_FIELD_NUMBER: _ClassVar[int]
    IS_PASS_FIELD_NUMBER: _ClassVar[int]
    ORDER_PRICE_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_UNIT_FIELD_NUMBER: _ClassVar[int]
    POSITION_EFFECT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    cl_order_id: str
    order_id: str
    counter_order_id: str
    security_id: str
    market: str
    instrument_id: str
    appl_id: str
    strategy_id: int
    strategy_name: str
    account_id: str
    investor_id: str
    confirm_qty: int
    reject_qty: int
    is_pass: int
    order_price: float
    contract_unit: float
    position_effect: int
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., cl_order_id: _Optional[str] = ..., order_id: _Optional[str] = ..., counter_order_id: _Optional[str] = ..., security_id: _Optional[str] = ..., market: _Optional[str] = ..., instrument_id: _Optional[str] = ..., appl_id: _Optional[str] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., confirm_qty: _Optional[int] = ..., reject_qty: _Optional[int] = ..., is_pass: _Optional[int] = ..., order_price: _Optional[float] = ..., contract_unit: _Optional[float] = ..., position_effect: _Optional[int] = ...) -> None: ...

class OrderReject(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "cl_order_id", "order_id", "reject_reason", "text", "security_id", "market", "instrument_id", "appl_id", "strategy_id", "strategy_name", "account_id", "investor_id", "reject_qty", "is_pass", "order_price", "contract_unit", "exchange_reject_reason")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    REJECT_REASON_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    APPL_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    REJECT_QTY_FIELD_NUMBER: _ClassVar[int]
    IS_PASS_FIELD_NUMBER: _ClassVar[int]
    ORDER_PRICE_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_UNIT_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_REJECT_REASON_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    cl_order_id: str
    order_id: str
    reject_reason: int
    text: str
    security_id: str
    market: str
    instrument_id: str
    appl_id: str
    strategy_id: int
    strategy_name: str
    account_id: str
    investor_id: str
    reject_qty: int
    is_pass: int
    order_price: float
    contract_unit: float
    exchange_reject_reason: int
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., cl_order_id: _Optional[str] = ..., order_id: _Optional[str] = ..., reject_reason: _Optional[int] = ..., text: _Optional[str] = ..., security_id: _Optional[str] = ..., market: _Optional[str] = ..., instrument_id: _Optional[str] = ..., appl_id: _Optional[str] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., reject_qty: _Optional[int] = ..., is_pass: _Optional[int] = ..., order_price: _Optional[float] = ..., contract_unit: _Optional[float] = ..., exchange_reject_reason: _Optional[int] = ...) -> None: ...

class TradeConfirm(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "cl_order_id", "order_id", "counter_order_id", "trade_id", "trade_time", "last_px", "last_qty", "security_id", "market", "instrument_id", "appl_id", "strategy_id", "strategy_name", "account_id", "investor_id", "match_place", "counterparty_id", "is_maker", "side", "position_effect", "trade_amt", "order_qty", "order_price", "contract_unit", "order_type", "order_source", "user_id", "counter_cl_order_id", "owner_type", "business_type", "symbol", "parent_order_id", "algo_type", "attachment", "basket_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    COUNTER_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    TRADE_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_PX_FIELD_NUMBER: _ClassVar[int]
    LAST_QTY_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    APPL_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    MATCH_PLACE_FIELD_NUMBER: _ClassVar[int]
    COUNTERPARTY_ID_FIELD_NUMBER: _ClassVar[int]
    IS_MAKER_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    POSITION_EFFECT_FIELD_NUMBER: _ClassVar[int]
    TRADE_AMT_FIELD_NUMBER: _ClassVar[int]
    ORDER_QTY_FIELD_NUMBER: _ClassVar[int]
    ORDER_PRICE_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_UNIT_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    ORDER_SOURCE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    COUNTER_CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_TYPE_FIELD_NUMBER: _ClassVar[int]
    BUSINESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    PARENT_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ALGO_TYPE_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENT_FIELD_NUMBER: _ClassVar[int]
    BASKET_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    cl_order_id: str
    order_id: str
    counter_order_id: str
    trade_id: str
    trade_time: int
    last_px: float
    last_qty: int
    security_id: str
    market: str
    instrument_id: str
    appl_id: str
    strategy_id: int
    strategy_name: str
    account_id: str
    investor_id: str
    match_place: int
    counterparty_id: str
    is_maker: int
    side: int
    position_effect: int
    trade_amt: float
    order_qty: int
    order_price: float
    contract_unit: float
    order_type: int
    order_source: str
    user_id: str
    counter_cl_order_id: str
    owner_type: int
    business_type: str
    symbol: str
    parent_order_id: str
    algo_type: int
    attachment: str
    basket_id: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., cl_order_id: _Optional[str] = ..., order_id: _Optional[str] = ..., counter_order_id: _Optional[str] = ..., trade_id: _Optional[str] = ..., trade_time: _Optional[int] = ..., last_px: _Optional[float] = ..., last_qty: _Optional[int] = ..., security_id: _Optional[str] = ..., market: _Optional[str] = ..., instrument_id: _Optional[str] = ..., appl_id: _Optional[str] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., match_place: _Optional[int] = ..., counterparty_id: _Optional[str] = ..., is_maker: _Optional[int] = ..., side: _Optional[int] = ..., position_effect: _Optional[int] = ..., trade_amt: _Optional[float] = ..., order_qty: _Optional[int] = ..., order_price: _Optional[float] = ..., contract_unit: _Optional[float] = ..., order_type: _Optional[int] = ..., order_source: _Optional[str] = ..., user_id: _Optional[str] = ..., counter_cl_order_id: _Optional[str] = ..., owner_type: _Optional[int] = ..., business_type: _Optional[str] = ..., symbol: _Optional[str] = ..., parent_order_id: _Optional[str] = ..., algo_type: _Optional[int] = ..., attachment: _Optional[str] = ..., basket_id: _Optional[str] = ...) -> None: ...

class CancelOrder(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "account_id", "investor_id", "cl_order_id", "original_order_id", "original_cl_order_id", "security_id", "market", "instrument_id", "appl_id", "op_user", "strategy_id", "strategy_name", "owner_type", "parent_order_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    APPL_ID_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARENT_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    account_id: str
    investor_id: str
    cl_order_id: str
    original_order_id: str
    original_cl_order_id: str
    security_id: str
    market: str
    instrument_id: str
    appl_id: str
    op_user: _common_pb2.OpUser
    strategy_id: int
    strategy_name: str
    owner_type: int
    parent_order_id: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., cl_order_id: _Optional[str] = ..., original_order_id: _Optional[str] = ..., original_cl_order_id: _Optional[str] = ..., security_id: _Optional[str] = ..., market: _Optional[str] = ..., instrument_id: _Optional[str] = ..., appl_id: _Optional[str] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., owner_type: _Optional[int] = ..., parent_order_id: _Optional[str] = ...) -> None: ...

class CancelAllOrder(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "op_user", "cl_order_id", "account_id", "investor_id", "security_id", "market", "instrument_id", "strategy_id", "strategy_name", "owner_type")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_TYPE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    op_user: _common_pb2.OpUser
    cl_order_id: str
    account_id: str
    investor_id: str
    security_id: str
    market: str
    instrument_id: str
    strategy_id: int
    strategy_name: str
    owner_type: int
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ..., cl_order_id: _Optional[str] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., security_id: _Optional[str] = ..., market: _Optional[str] = ..., instrument_id: _Optional[str] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., owner_type: _Optional[int] = ...) -> None: ...

class CancelPendingConfirm(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "cl_order_id", "original_order_id", "original_cl_order_id", "original_counter_order_id", "security_id", "market", "instrument_id", "appl_id", "strategy_id", "strategy_name", "account_id", "investor_id", "cancel_qty", "reason", "text")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_COUNTER_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    APPL_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    CANCEL_QTY_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    cl_order_id: str
    original_order_id: str
    original_cl_order_id: str
    original_counter_order_id: str
    security_id: str
    market: str
    instrument_id: str
    appl_id: str
    strategy_id: int
    strategy_name: str
    account_id: str
    investor_id: str
    cancel_qty: int
    reason: int
    text: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., cl_order_id: _Optional[str] = ..., original_order_id: _Optional[str] = ..., original_cl_order_id: _Optional[str] = ..., original_counter_order_id: _Optional[str] = ..., security_id: _Optional[str] = ..., market: _Optional[str] = ..., instrument_id: _Optional[str] = ..., appl_id: _Optional[str] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., cancel_qty: _Optional[int] = ..., reason: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class CancelConfirm(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "cl_order_id", "original_order_id", "original_cl_order_id", "original_counter_order_id", "security_id", "market", "instrument_id", "appl_id", "strategy_id", "strategy_name", "account_id", "investor_id", "cancel_qty", "reason", "text")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_COUNTER_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    APPL_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    CANCEL_QTY_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    cl_order_id: str
    original_order_id: str
    original_cl_order_id: str
    original_counter_order_id: str
    security_id: str
    market: str
    instrument_id: str
    appl_id: str
    strategy_id: int
    strategy_name: str
    account_id: str
    investor_id: str
    cancel_qty: int
    reason: int
    text: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., cl_order_id: _Optional[str] = ..., original_order_id: _Optional[str] = ..., original_cl_order_id: _Optional[str] = ..., original_counter_order_id: _Optional[str] = ..., security_id: _Optional[str] = ..., market: _Optional[str] = ..., instrument_id: _Optional[str] = ..., appl_id: _Optional[str] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., cancel_qty: _Optional[int] = ..., reason: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class CancelReject(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "cl_order_id", "original_order_id", "original_cl_order_id", "original_counter_order_id", "security_id", "market", "instrument_id", "appl_id", "strategy_id", "strategy_name", "account_id", "investor_id", "reject_reason", "text")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_COUNTER_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    APPL_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    REJECT_REASON_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    cl_order_id: str
    original_order_id: str
    original_cl_order_id: str
    original_counter_order_id: str
    security_id: str
    market: str
    instrument_id: str
    appl_id: str
    strategy_id: int
    strategy_name: str
    account_id: str
    investor_id: str
    reject_reason: int
    text: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., cl_order_id: _Optional[str] = ..., original_order_id: _Optional[str] = ..., original_cl_order_id: _Optional[str] = ..., original_counter_order_id: _Optional[str] = ..., security_id: _Optional[str] = ..., market: _Optional[str] = ..., instrument_id: _Optional[str] = ..., appl_id: _Optional[str] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., reject_reason: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class ExternalOrderEvent(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "cl_order_id", "order_id", "order_date", "security_id", "market", "instrument_id", "security_type", "appl_id", "strategy_id", "account_id", "investor_id", "order_type", "side", "position_effect", "time_in_force", "purpose", "stop_px", "order_qty", "order_price", "owner_type")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_DATE_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    APPL_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    POSITION_EFFECT_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_FORCE_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    STOP_PX_FIELD_NUMBER: _ClassVar[int]
    ORDER_QTY_FIELD_NUMBER: _ClassVar[int]
    ORDER_PRICE_FIELD_NUMBER: _ClassVar[int]
    OWNER_TYPE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    cl_order_id: str
    order_id: str
    order_date: int
    security_id: str
    market: str
    instrument_id: str
    security_type: str
    appl_id: str
    strategy_id: int
    account_id: str
    investor_id: str
    order_type: int
    side: int
    position_effect: int
    time_in_force: int
    purpose: int
    stop_px: float
    order_qty: int
    order_price: float
    owner_type: int
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., cl_order_id: _Optional[str] = ..., order_id: _Optional[str] = ..., order_date: _Optional[int] = ..., security_id: _Optional[str] = ..., market: _Optional[str] = ..., instrument_id: _Optional[str] = ..., security_type: _Optional[str] = ..., appl_id: _Optional[str] = ..., strategy_id: _Optional[int] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., order_type: _Optional[int] = ..., side: _Optional[int] = ..., position_effect: _Optional[int] = ..., time_in_force: _Optional[int] = ..., purpose: _Optional[int] = ..., stop_px: _Optional[float] = ..., order_qty: _Optional[int] = ..., order_price: _Optional[float] = ..., owner_type: _Optional[int] = ...) -> None: ...

class Heartbeat(_message.Message):
    __slots__ = ("msg_type", "node_type", "node_name", "timestamp", "is_login", "request_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    IS_LOGIN_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_type: int
    node_name: str
    timestamp: int
    is_login: int
    request_id: str
    def __init__(self, msg_type: _Optional[int] = ..., node_type: _Optional[int] = ..., node_name: _Optional[str] = ..., timestamp: _Optional[int] = ..., is_login: _Optional[int] = ..., request_id: _Optional[str] = ...) -> None: ...

class Breakpoint(_message.Message):
    __slots__ = ("msg_type", "node_type", "node_name", "msg_sequence")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_type: int
    node_name: str
    msg_sequence: int
    def __init__(self, msg_type: _Optional[int] = ..., node_type: _Optional[int] = ..., node_name: _Optional[str] = ..., msg_sequence: _Optional[int] = ...) -> None: ...

class BlankPoint(_message.Message):
    __slots__ = ("msg_type", "node_type", "node_name", "msg_sequence")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_type: int
    node_name: str
    msg_sequence: int
    def __init__(self, msg_type: _Optional[int] = ..., node_type: _Optional[int] = ..., node_name: _Optional[str] = ..., msg_sequence: _Optional[int] = ...) -> None: ...

class BizInstructions(_message.Message):
    __slots__ = ("msg_type", "node_type", "node_name", "msg_sequence", "instruction_type", "instruction_id", "instruction")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTION_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTION_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_type: int
    node_name: str
    msg_sequence: int
    instruction_type: int
    instruction_id: str
    instruction: str
    def __init__(self, msg_type: _Optional[int] = ..., node_type: _Optional[int] = ..., node_name: _Optional[str] = ..., msg_sequence: _Optional[int] = ..., instruction_type: _Optional[int] = ..., instruction_id: _Optional[str] = ..., instruction: _Optional[str] = ...) -> None: ...

class UserMockRequest(_message.Message):
    __slots__ = ("msg_type", "sequence", "orig_cl_order_id", "exec_type", "trade_id", "trade_price", "trade_qty", "cancel_qty", "reject_qty", "account_id")
    class ExecType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        kUnknown: _ClassVar[UserMockRequest.ExecType]
        kNew: _ClassVar[UserMockRequest.ExecType]
        kCanceled: _ClassVar[UserMockRequest.ExecType]
        kPendingCancel: _ClassVar[UserMockRequest.ExecType]
        kRejected: _ClassVar[UserMockRequest.ExecType]
        kPendingNew: _ClassVar[UserMockRequest.ExecType]
        kTrade: _ClassVar[UserMockRequest.ExecType]
        kCancelRejected: _ClassVar[UserMockRequest.ExecType]
    kUnknown: UserMockRequest.ExecType
    kNew: UserMockRequest.ExecType
    kCanceled: UserMockRequest.ExecType
    kPendingCancel: UserMockRequest.ExecType
    kRejected: UserMockRequest.ExecType
    kPendingNew: UserMockRequest.ExecType
    kTrade: UserMockRequest.ExecType
    kCancelRejected: UserMockRequest.ExecType
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    ORIG_CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    EXEC_TYPE_FIELD_NUMBER: _ClassVar[int]
    TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    TRADE_PRICE_FIELD_NUMBER: _ClassVar[int]
    TRADE_QTY_FIELD_NUMBER: _ClassVar[int]
    CANCEL_QTY_FIELD_NUMBER: _ClassVar[int]
    REJECT_QTY_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    sequence: int
    orig_cl_order_id: str
    exec_type: UserMockRequest.ExecType
    trade_id: str
    trade_price: float
    trade_qty: int
    cancel_qty: int
    reject_qty: int
    account_id: str
    def __init__(self, msg_type: _Optional[int] = ..., sequence: _Optional[int] = ..., orig_cl_order_id: _Optional[str] = ..., exec_type: _Optional[_Union[UserMockRequest.ExecType, str]] = ..., trade_id: _Optional[str] = ..., trade_price: _Optional[float] = ..., trade_qty: _Optional[int] = ..., cancel_qty: _Optional[int] = ..., reject_qty: _Optional[int] = ..., account_id: _Optional[str] = ...) -> None: ...

class UpdateOrderReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "op_user", "order_action", "order", "trade")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    ORDER_ACTION_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    TRADE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    op_user: _common_pb2.OpUser
    order_action: str
    order: _common_pb2.Order
    trade: _containers.RepeatedCompositeFieldContainer[_common_pb2.Trade]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ..., order_action: _Optional[str] = ..., order: _Optional[_Union[_common_pb2.Order, _Mapping]] = ..., trade: _Optional[_Iterable[_Union[_common_pb2.Trade, _Mapping]]] = ...) -> None: ...

class UpdateOrderRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "status", "text")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    status: int
    text: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., status: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class OrderEvent(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "order")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    order: _common_pb2.Order
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., order: _Optional[_Union[_common_pb2.Order, _Mapping]] = ...) -> None: ...

class RiskResult(_message.Message):
    __slots__ = ("risk_code", "risk_info", "risk_status", "order_action", "order_id", "account_id", "instrument_id", "risk_id", "set_value", "real_value")
    RISK_CODE_FIELD_NUMBER: _ClassVar[int]
    RISK_INFO_FIELD_NUMBER: _ClassVar[int]
    RISK_STATUS_FIELD_NUMBER: _ClassVar[int]
    ORDER_ACTION_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    RISK_ID_FIELD_NUMBER: _ClassVar[int]
    SET_VALUE_FIELD_NUMBER: _ClassVar[int]
    REAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    risk_code: str
    risk_info: str
    risk_status: int
    order_action: int
    order_id: str
    account_id: str
    instrument_id: str
    risk_id: int
    set_value: float
    real_value: float
    def __init__(self, risk_code: _Optional[str] = ..., risk_info: _Optional[str] = ..., risk_status: _Optional[int] = ..., order_action: _Optional[int] = ..., order_id: _Optional[str] = ..., account_id: _Optional[str] = ..., instrument_id: _Optional[str] = ..., risk_id: _Optional[int] = ..., set_value: _Optional[float] = ..., real_value: _Optional[float] = ...) -> None: ...

class RiskEvent(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "msg_sequence", "timestamp", "risk_result")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RISK_RESULT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    msg_sequence: int
    timestamp: int
    risk_result: _containers.RepeatedCompositeFieldContainer[RiskResult]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., timestamp: _Optional[int] = ..., risk_result: _Optional[_Iterable[_Union[RiskResult, _Mapping]]] = ...) -> None: ...

class UpdateRiskParamsReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "operate_type", "op_user", "risk_item")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    RISK_ITEM_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    operate_type: str
    op_user: _common_pb2.OpUser
    risk_item: _containers.RepeatedCompositeFieldContainer[_common_pb2.RiskItem]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., operate_type: _Optional[str] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ..., risk_item: _Optional[_Iterable[_Union[_common_pb2.RiskItem, _Mapping]]] = ...) -> None: ...

class UpdateRiskParamsRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "operate_type", "status", "text", "risk_item")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    RISK_ITEM_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    operate_type: str
    status: int
    text: str
    risk_item: _containers.RepeatedCompositeFieldContainer[_common_pb2.RiskItem]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., operate_type: _Optional[str] = ..., status: _Optional[int] = ..., text: _Optional[str] = ..., risk_item: _Optional[_Iterable[_Union[_common_pb2.RiskItem, _Mapping]]] = ...) -> None: ...

class UpdateRiskStatReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "op_user", "account_id", "instrument_id", "risk_code", "risk_stat_value")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    RISK_CODE_FIELD_NUMBER: _ClassVar[int]
    RISK_STAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    op_user: _common_pb2.OpUser
    account_id: str
    instrument_id: str
    risk_code: str
    risk_stat_value: float
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ..., account_id: _Optional[str] = ..., instrument_id: _Optional[str] = ..., risk_code: _Optional[str] = ..., risk_stat_value: _Optional[float] = ...) -> None: ...

class UpdateRiskStatRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "status", "text", "account_id", "instrument_id", "risk_code", "risk_stat_value")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    RISK_CODE_FIELD_NUMBER: _ClassVar[int]
    RISK_STAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    status: int
    text: str
    account_id: str
    instrument_id: str
    risk_code: str
    risk_stat_value: float
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., status: _Optional[int] = ..., text: _Optional[str] = ..., account_id: _Optional[str] = ..., instrument_id: _Optional[str] = ..., risk_code: _Optional[str] = ..., risk_stat_value: _Optional[float] = ...) -> None: ...

class UpdateRiskMarketParamsReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "operate_type", "op_user", "risk_params")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    RISK_PARAMS_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    operate_type: str
    op_user: _common_pb2.OpUser
    risk_params: _containers.RepeatedCompositeFieldContainer[_common_pb2.RiskMarketParams]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., operate_type: _Optional[str] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ..., risk_params: _Optional[_Iterable[_Union[_common_pb2.RiskMarketParams, _Mapping]]] = ...) -> None: ...

class UpdateRiskMarketParamsRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "operate_type", "status", "text", "risk_params")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    RISK_PARAMS_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    operate_type: str
    status: int
    text: str
    risk_params: _containers.RepeatedCompositeFieldContainer[_common_pb2.RiskMarketParams]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., operate_type: _Optional[str] = ..., status: _Optional[int] = ..., text: _Optional[str] = ..., risk_params: _Optional[_Iterable[_Union[_common_pb2.RiskMarketParams, _Mapping]]] = ...) -> None: ...

class UpdateNodeConfigReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "operate_type", "op_user", "trading_session", "counter_account")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    TRADING_SESSION_FIELD_NUMBER: _ClassVar[int]
    COUNTER_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    operate_type: str
    op_user: _common_pb2.OpUser
    trading_session: _containers.RepeatedCompositeFieldContainer[_common_pb2.TradingSession]
    counter_account: _containers.RepeatedCompositeFieldContainer[_common_pb2.CounterAccount]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., operate_type: _Optional[str] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ..., trading_session: _Optional[_Iterable[_Union[_common_pb2.TradingSession, _Mapping]]] = ..., counter_account: _Optional[_Iterable[_Union[_common_pb2.CounterAccount, _Mapping]]] = ...) -> None: ...

class UpdateNodeConfigRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "operate_type", "status", "text", "trading_session", "counter_account")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    TRADING_SESSION_FIELD_NUMBER: _ClassVar[int]
    COUNTER_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    operate_type: str
    status: int
    text: str
    trading_session: _containers.RepeatedCompositeFieldContainer[_common_pb2.TradingSession]
    counter_account: _containers.RepeatedCompositeFieldContainer[_common_pb2.CounterAccount]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., operate_type: _Optional[str] = ..., status: _Optional[int] = ..., text: _Optional[str] = ..., trading_session: _Optional[_Iterable[_Union[_common_pb2.TradingSession, _Mapping]]] = ..., counter_account: _Optional[_Iterable[_Union[_common_pb2.CounterAccount, _Mapping]]] = ...) -> None: ...
