import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HttpLoginReq(_message.Message):
    __slots__ = ("user_id", "passwd")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PASSWD_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    passwd: str
    def __init__(self, user_id: _Optional[str] = ..., passwd: _Optional[str] = ...) -> None: ...

class HttpLoginRsp(_message.Message):
    __slots__ = ("status", "data")
    class Data(_message.Message):
        __slots__ = ("token",)
        TOKEN_FIELD_NUMBER: _ClassVar[int]
        token: str
        def __init__(self, token: _Optional[str] = ...) -> None: ...
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    status: str
    data: HttpLoginRsp.Data
    def __init__(self, status: _Optional[str] = ..., data: _Optional[_Union[HttpLoginRsp.Data, _Mapping]] = ...) -> None: ...

class QryInstrumentReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id", "instrument_id", "basket_instrument_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    BASKET_INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    instrument_id: str
    basket_instrument_id: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ..., instrument_id: _Optional[str] = ..., basket_instrument_id: _Optional[str] = ...) -> None: ...

class QryInstrumentRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id", "status", "reason", "is_last", "data")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    status: int
    reason: str
    is_last: bool
    data: _containers.RepeatedCompositeFieldContainer[_common_pb2.Instrument]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., is_last: bool = ..., data: _Optional[_Iterable[_Union[_common_pb2.Instrument, _Mapping]]] = ...) -> None: ...

class HttpQryInstrumentRsp(_message.Message):
    __slots__ = ("status", "page", "page_size", "total_page", "total_size", "data")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PAGE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    status: str
    page: int
    page_size: int
    total_page: int
    total_size: int
    data: _containers.RepeatedCompositeFieldContainer[_common_pb2.Instrument]
    def __init__(self, status: _Optional[str] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., total_page: _Optional[int] = ..., total_size: _Optional[int] = ..., data: _Optional[_Iterable[_Union[_common_pb2.Instrument, _Mapping]]] = ...) -> None: ...

class StrategyInfo(_message.Message):
    __slots__ = ("strategy_id", "strategy_name", "book_id", "status", "comment", "node_id", "node_name", "account_id", "trade_date", "params", "monitor_params", "signal_id", "signal_name", "strategy_instruments", "target_qty", "counter_id", "counter_account_id")
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    TRADE_DATE_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    MONITOR_PARAMS_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_NAME_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_INSTRUMENTS_FIELD_NUMBER: _ClassVar[int]
    TARGET_QTY_FIELD_NUMBER: _ClassVar[int]
    COUNTER_ID_FIELD_NUMBER: _ClassVar[int]
    COUNTER_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    strategy_id: int
    strategy_name: str
    book_id: str
    status: str
    comment: str
    node_id: int
    node_name: str
    account_id: str
    trade_date: str
    params: str
    monitor_params: str
    signal_id: int
    signal_name: str
    strategy_instruments: _containers.RepeatedCompositeFieldContainer[_common_pb2.StrategyInstrument]
    target_qty: int
    counter_id: str
    counter_account_id: str
    def __init__(self, strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., book_id: _Optional[str] = ..., status: _Optional[str] = ..., comment: _Optional[str] = ..., node_id: _Optional[int] = ..., node_name: _Optional[str] = ..., account_id: _Optional[str] = ..., trade_date: _Optional[str] = ..., params: _Optional[str] = ..., monitor_params: _Optional[str] = ..., signal_id: _Optional[int] = ..., signal_name: _Optional[str] = ..., strategy_instruments: _Optional[_Iterable[_Union[_common_pb2.StrategyInstrument, _Mapping]]] = ..., target_qty: _Optional[int] = ..., counter_id: _Optional[str] = ..., counter_account_id: _Optional[str] = ...) -> None: ...

class QryStrategyInfoReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id", "strategy_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    strategy_id: int
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ..., strategy_id: _Optional[int] = ...) -> None: ...

class QryStrategyInfoRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id", "status", "reason", "is_last", "data")
    class StrategyInfoData(_message.Message):
        __slots__ = ("strategy_template_id", "strategy_template_type", "strategy_type", "global_params", "strategy_list")
        STRATEGY_TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
        STRATEGY_TEMPLATE_TYPE_FIELD_NUMBER: _ClassVar[int]
        STRATEGY_TYPE_FIELD_NUMBER: _ClassVar[int]
        GLOBAL_PARAMS_FIELD_NUMBER: _ClassVar[int]
        STRATEGY_LIST_FIELD_NUMBER: _ClassVar[int]
        strategy_template_id: str
        strategy_template_type: str
        strategy_type: str
        global_params: str
        strategy_list: _containers.RepeatedCompositeFieldContainer[StrategyInfo]
        def __init__(self, strategy_template_id: _Optional[str] = ..., strategy_template_type: _Optional[str] = ..., strategy_type: _Optional[str] = ..., global_params: _Optional[str] = ..., strategy_list: _Optional[_Iterable[_Union[StrategyInfo, _Mapping]]] = ...) -> None: ...
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    status: int
    reason: str
    is_last: bool
    data: _containers.RepeatedCompositeFieldContainer[QryStrategyInfoRsp.StrategyInfoData]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., is_last: bool = ..., data: _Optional[_Iterable[_Union[QryStrategyInfoRsp.StrategyInfoData, _Mapping]]] = ...) -> None: ...

class SignalInfo(_message.Message):
    __slots__ = ("signal_id", "signal_name", "instrument_id", "instrument_type", "market", "security_id", "status", "comment", "node_id", "node_name", "trade_date", "fund_etfpr_minnav", "fund_etfpr_estcash", "params", "package_info", "signal_info_l2")
    SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_NAME_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    TRADE_DATE_FIELD_NUMBER: _ClassVar[int]
    FUND_ETFPR_MINNAV_FIELD_NUMBER: _ClassVar[int]
    FUND_ETFPR_ESTCASH_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_INFO_L2_FIELD_NUMBER: _ClassVar[int]
    signal_id: int
    signal_name: str
    instrument_id: str
    instrument_type: str
    market: str
    security_id: str
    status: str
    comment: str
    node_id: int
    node_name: str
    trade_date: str
    fund_etfpr_minnav: float
    fund_etfpr_estcash: float
    params: str
    package_info: _containers.RepeatedCompositeFieldContainer[_common_pb2.PackageInfo]
    signal_info_l2: _containers.RepeatedCompositeFieldContainer[_common_pb2.SignalInfoL2]
    def __init__(self, signal_id: _Optional[int] = ..., signal_name: _Optional[str] = ..., instrument_id: _Optional[str] = ..., instrument_type: _Optional[str] = ..., market: _Optional[str] = ..., security_id: _Optional[str] = ..., status: _Optional[str] = ..., comment: _Optional[str] = ..., node_id: _Optional[int] = ..., node_name: _Optional[str] = ..., trade_date: _Optional[str] = ..., fund_etfpr_minnav: _Optional[float] = ..., fund_etfpr_estcash: _Optional[float] = ..., params: _Optional[str] = ..., package_info: _Optional[_Iterable[_Union[_common_pb2.PackageInfo, _Mapping]]] = ..., signal_info_l2: _Optional[_Iterable[_Union[_common_pb2.SignalInfoL2, _Mapping]]] = ...) -> None: ...

class QrySignalInfoReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id", "signal_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    signal_id: int
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ..., signal_id: _Optional[int] = ...) -> None: ...

class QrySignalInfoRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id", "status", "reason", "is_last", "data")
    class SignalInfoData(_message.Message):
        __slots__ = ("signal_template_id", "global_params", "signal_list")
        SIGNAL_TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
        GLOBAL_PARAMS_FIELD_NUMBER: _ClassVar[int]
        SIGNAL_LIST_FIELD_NUMBER: _ClassVar[int]
        signal_template_id: str
        global_params: str
        signal_list: _containers.RepeatedCompositeFieldContainer[SignalInfo]
        def __init__(self, signal_template_id: _Optional[str] = ..., global_params: _Optional[str] = ..., signal_list: _Optional[_Iterable[_Union[SignalInfo, _Mapping]]] = ...) -> None: ...
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    status: int
    reason: str
    is_last: bool
    data: _containers.RepeatedCompositeFieldContainer[QrySignalInfoRsp.SignalInfoData]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., is_last: bool = ..., data: _Optional[_Iterable[_Union[QrySignalInfoRsp.SignalInfoData, _Mapping]]] = ...) -> None: ...

class QryCurrencyReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ...) -> None: ...

class QryCurrencyRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id", "status", "reason", "is_last", "data")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    status: int
    reason: str
    is_last: bool
    data: _containers.RepeatedCompositeFieldContainer[_common_pb2.Currency]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., is_last: bool = ..., data: _Optional[_Iterable[_Union[_common_pb2.Currency, _Mapping]]] = ...) -> None: ...

class Counter(_message.Message):
    __slots__ = ("counter_id", "counter_type", "account_id", "investor_id", "sec_investor_id", "passwd", "ip_address", "params", "comment")
    class SecInvestor(_message.Message):
        __slots__ = ("market", "sec_investor_id")
        MARKET_FIELD_NUMBER: _ClassVar[int]
        SEC_INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
        market: str
        sec_investor_id: str
        def __init__(self, market: _Optional[str] = ..., sec_investor_id: _Optional[str] = ...) -> None: ...
    COUNTER_ID_FIELD_NUMBER: _ClassVar[int]
    COUNTER_TYPE_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    SEC_INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    PASSWD_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    counter_id: str
    counter_type: str
    account_id: str
    investor_id: str
    sec_investor_id: _containers.RepeatedCompositeFieldContainer[Counter.SecInvestor]
    passwd: str
    ip_address: str
    params: str
    comment: str
    def __init__(self, counter_id: _Optional[str] = ..., counter_type: _Optional[str] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., sec_investor_id: _Optional[_Iterable[_Union[Counter.SecInvestor, _Mapping]]] = ..., passwd: _Optional[str] = ..., ip_address: _Optional[str] = ..., params: _Optional[str] = ..., comment: _Optional[str] = ...) -> None: ...

class QryCounterReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ...) -> None: ...

class QryCounterRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id", "status", "reason", "is_last", "data")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    status: int
    reason: str
    is_last: bool
    data: _containers.RepeatedCompositeFieldContainer[Counter]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., is_last: bool = ..., data: _Optional[_Iterable[_Union[Counter, _Mapping]]] = ...) -> None: ...

class QryRiskItemReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id", "account_id", "instrument_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    account_id: _containers.RepeatedScalarFieldContainer[str]
    instrument_id: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ..., account_id: _Optional[_Iterable[str]] = ..., instrument_id: _Optional[_Iterable[str]] = ...) -> None: ...

class QryRiskItemRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id", "status", "reason", "is_last", "data")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    status: int
    reason: str
    is_last: bool
    data: _containers.RepeatedCompositeFieldContainer[_common_pb2.RiskItem]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., is_last: bool = ..., data: _Optional[_Iterable[_Union[_common_pb2.RiskItem, _Mapping]]] = ...) -> None: ...

class QryRiskMarketParamsReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id", "account_id", "market")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    account_id: _containers.RepeatedScalarFieldContainer[str]
    market: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ..., account_id: _Optional[_Iterable[str]] = ..., market: _Optional[_Iterable[str]] = ...) -> None: ...

class QryRiskMarketParamsRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id", "status", "reason", "is_last", "data")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    status: int
    reason: str
    is_last: bool
    data: _containers.RepeatedCompositeFieldContainer[_common_pb2.RiskMarketParams]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., is_last: bool = ..., data: _Optional[_Iterable[_Union[_common_pb2.RiskMarketParams, _Mapping]]] = ...) -> None: ...

class QryNodeConfigReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ...) -> None: ...

class QryNodeConfigRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "request_id", "status", "reason", "is_last", "trading_session", "counter_account")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    TRADING_SESSION_FIELD_NUMBER: _ClassVar[int]
    COUNTER_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    request_id: str
    status: int
    reason: str
    is_last: bool
    trading_session: _containers.RepeatedCompositeFieldContainer[_common_pb2.TradingSession]
    counter_account: _containers.RepeatedCompositeFieldContainer[_common_pb2.CounterAccount]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., request_id: _Optional[str] = ..., status: _Optional[int] = ..., reason: _Optional[str] = ..., is_last: bool = ..., trading_session: _Optional[_Iterable[_Union[_common_pb2.TradingSession, _Mapping]]] = ..., counter_account: _Optional[_Iterable[_Union[_common_pb2.CounterAccount, _Mapping]]] = ...) -> None: ...
