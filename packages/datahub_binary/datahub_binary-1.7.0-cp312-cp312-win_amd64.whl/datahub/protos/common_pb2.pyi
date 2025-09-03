from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OpUser(_message.Message):
    __slots__ = ("user_id", "party_id", "post_id", "datetime", "region_id", "ip", "mac", "sn", "uuid", "local_ip", "cpu", "sno", "pcn", "pi", "vol", "osv", "terminal_type", "text", "props")
    class PropsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    DATETIME_FIELD_NUMBER: _ClassVar[int]
    REGION_ID_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    MAC_FIELD_NUMBER: _ClassVar[int]
    SN_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    LOCAL_IP_FIELD_NUMBER: _ClassVar[int]
    CPU_FIELD_NUMBER: _ClassVar[int]
    SNO_FIELD_NUMBER: _ClassVar[int]
    PCN_FIELD_NUMBER: _ClassVar[int]
    PI_FIELD_NUMBER: _ClassVar[int]
    VOL_FIELD_NUMBER: _ClassVar[int]
    OSV_FIELD_NUMBER: _ClassVar[int]
    TERMINAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    party_id: str
    post_id: str
    datetime: str
    region_id: int
    ip: str
    mac: str
    sn: str
    uuid: str
    local_ip: str
    cpu: str
    sno: str
    pcn: str
    pi: str
    vol: str
    osv: str
    terminal_type: str
    text: str
    props: _containers.ScalarMap[str, str]
    def __init__(self, user_id: _Optional[str] = ..., party_id: _Optional[str] = ..., post_id: _Optional[str] = ..., datetime: _Optional[str] = ..., region_id: _Optional[int] = ..., ip: _Optional[str] = ..., mac: _Optional[str] = ..., sn: _Optional[str] = ..., uuid: _Optional[str] = ..., local_ip: _Optional[str] = ..., cpu: _Optional[str] = ..., sno: _Optional[str] = ..., pcn: _Optional[str] = ..., pi: _Optional[str] = ..., vol: _Optional[str] = ..., osv: _Optional[str] = ..., terminal_type: _Optional[str] = ..., text: _Optional[str] = ..., props: _Optional[_Mapping[str, str]] = ...) -> None: ...

class OpStatus(_message.Message):
    __slots__ = ("status", "reason", "data")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    status: int
    reason: str
    data: str
    def __init__(self, status: _Optional[int] = ..., reason: _Optional[str] = ..., data: _Optional[str] = ...) -> None: ...

class PackageInfo(_message.Message):
    __slots__ = ("instrument_id", "component_instrument_id", "component_qty", "is_sub_cash_replace", "is_sub_cash_replace_amount", "is_withdraw_cash", "is_withdraw_cash_replace_amount")
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_QTY_FIELD_NUMBER: _ClassVar[int]
    IS_SUB_CASH_REPLACE_FIELD_NUMBER: _ClassVar[int]
    IS_SUB_CASH_REPLACE_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    IS_WITHDRAW_CASH_FIELD_NUMBER: _ClassVar[int]
    IS_WITHDRAW_CASH_REPLACE_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    instrument_id: str
    component_instrument_id: str
    component_qty: int
    is_sub_cash_replace: int
    is_sub_cash_replace_amount: float
    is_withdraw_cash: int
    is_withdraw_cash_replace_amount: float
    def __init__(self, instrument_id: _Optional[str] = ..., component_instrument_id: _Optional[str] = ..., component_qty: _Optional[int] = ..., is_sub_cash_replace: _Optional[int] = ..., is_sub_cash_replace_amount: _Optional[float] = ..., is_withdraw_cash: _Optional[int] = ..., is_withdraw_cash_replace_amount: _Optional[float] = ...) -> None: ...

class SignalInfoL2(_message.Message):
    __slots__ = ("l2_signal_id", "source_signal_id", "l2_signal_name", "comments", "weight", "source_signal_name")
    L2_SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    L2_SIGNAL_NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    SOURCE_SIGNAL_NAME_FIELD_NUMBER: _ClassVar[int]
    l2_signal_id: int
    source_signal_id: int
    l2_signal_name: str
    comments: str
    weight: float
    source_signal_name: str
    def __init__(self, l2_signal_id: _Optional[int] = ..., source_signal_id: _Optional[int] = ..., l2_signal_name: _Optional[str] = ..., comments: _Optional[str] = ..., weight: _Optional[float] = ..., source_signal_name: _Optional[str] = ...) -> None: ...

class Currency(_message.Message):
    __slots__ = ("currency_id", "fx_rate_cny", "comments", "update_time")
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    FX_RATE_CNY_FIELD_NUMBER: _ClassVar[int]
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    currency_id: str
    fx_rate_cny: float
    comments: str
    update_time: str
    def __init__(self, currency_id: _Optional[str] = ..., fx_rate_cny: _Optional[float] = ..., comments: _Optional[str] = ..., update_time: _Optional[str] = ...) -> None: ...

class Instrument(_message.Message):
    __slots__ = ("instrument_id", "market", "security_id", "symbol", "instrument_type", "security_type", "lot_size", "price_tick", "contract_unit", "intraday_trading", "is_sub", "is_withdraw", "fund_etfpr_minnav", "withdraw_basket_volume", "long_posi_limit", "short_posi_limit", "intraday_open_limit", "max_up", "max_down", "underlying_instrument_id", "chain_codes", "fund_etfpr_estcash", "wind_market", "comments", "is_replace_price", "replace_price", "quote_currency_id", "settle_currency_id", "total_share", "posi_qty_ratio_limit", "price_cage", "instrument_sub_type", "min_size", "max_size", "list_date", "delist_date", "settle_date")
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SECURITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    LOT_SIZE_FIELD_NUMBER: _ClassVar[int]
    PRICE_TICK_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_UNIT_FIELD_NUMBER: _ClassVar[int]
    INTRADAY_TRADING_FIELD_NUMBER: _ClassVar[int]
    IS_SUB_FIELD_NUMBER: _ClassVar[int]
    IS_WITHDRAW_FIELD_NUMBER: _ClassVar[int]
    FUND_ETFPR_MINNAV_FIELD_NUMBER: _ClassVar[int]
    WITHDRAW_BASKET_VOLUME_FIELD_NUMBER: _ClassVar[int]
    LONG_POSI_LIMIT_FIELD_NUMBER: _ClassVar[int]
    SHORT_POSI_LIMIT_FIELD_NUMBER: _ClassVar[int]
    INTRADAY_OPEN_LIMIT_FIELD_NUMBER: _ClassVar[int]
    MAX_UP_FIELD_NUMBER: _ClassVar[int]
    MAX_DOWN_FIELD_NUMBER: _ClassVar[int]
    UNDERLYING_INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    CHAIN_CODES_FIELD_NUMBER: _ClassVar[int]
    FUND_ETFPR_ESTCASH_FIELD_NUMBER: _ClassVar[int]
    WIND_MARKET_FIELD_NUMBER: _ClassVar[int]
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    IS_REPLACE_PRICE_FIELD_NUMBER: _ClassVar[int]
    REPLACE_PRICE_FIELD_NUMBER: _ClassVar[int]
    QUOTE_CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    SETTLE_CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SHARE_FIELD_NUMBER: _ClassVar[int]
    POSI_QTY_RATIO_LIMIT_FIELD_NUMBER: _ClassVar[int]
    PRICE_CAGE_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_SUB_TYPE_FIELD_NUMBER: _ClassVar[int]
    MIN_SIZE_FIELD_NUMBER: _ClassVar[int]
    MAX_SIZE_FIELD_NUMBER: _ClassVar[int]
    LIST_DATE_FIELD_NUMBER: _ClassVar[int]
    DELIST_DATE_FIELD_NUMBER: _ClassVar[int]
    SETTLE_DATE_FIELD_NUMBER: _ClassVar[int]
    instrument_id: str
    market: str
    security_id: str
    symbol: str
    instrument_type: str
    security_type: str
    lot_size: int
    price_tick: float
    contract_unit: float
    intraday_trading: int
    is_sub: int
    is_withdraw: int
    fund_etfpr_minnav: int
    withdraw_basket_volume: int
    long_posi_limit: int
    short_posi_limit: int
    intraday_open_limit: int
    max_up: float
    max_down: float
    underlying_instrument_id: str
    chain_codes: _containers.RepeatedScalarFieldContainer[str]
    fund_etfpr_estcash: float
    wind_market: str
    comments: str
    is_replace_price: int
    replace_price: float
    quote_currency_id: str
    settle_currency_id: str
    total_share: int
    posi_qty_ratio_limit: float
    price_cage: float
    instrument_sub_type: str
    min_size: int
    max_size: int
    list_date: str
    delist_date: str
    settle_date: str
    def __init__(self, instrument_id: _Optional[str] = ..., market: _Optional[str] = ..., security_id: _Optional[str] = ..., symbol: _Optional[str] = ..., instrument_type: _Optional[str] = ..., security_type: _Optional[str] = ..., lot_size: _Optional[int] = ..., price_tick: _Optional[float] = ..., contract_unit: _Optional[float] = ..., intraday_trading: _Optional[int] = ..., is_sub: _Optional[int] = ..., is_withdraw: _Optional[int] = ..., fund_etfpr_minnav: _Optional[int] = ..., withdraw_basket_volume: _Optional[int] = ..., long_posi_limit: _Optional[int] = ..., short_posi_limit: _Optional[int] = ..., intraday_open_limit: _Optional[int] = ..., max_up: _Optional[float] = ..., max_down: _Optional[float] = ..., underlying_instrument_id: _Optional[str] = ..., chain_codes: _Optional[_Iterable[str]] = ..., fund_etfpr_estcash: _Optional[float] = ..., wind_market: _Optional[str] = ..., comments: _Optional[str] = ..., is_replace_price: _Optional[int] = ..., replace_price: _Optional[float] = ..., quote_currency_id: _Optional[str] = ..., settle_currency_id: _Optional[str] = ..., total_share: _Optional[int] = ..., posi_qty_ratio_limit: _Optional[float] = ..., price_cage: _Optional[float] = ..., instrument_sub_type: _Optional[str] = ..., min_size: _Optional[int] = ..., max_size: _Optional[int] = ..., list_date: _Optional[str] = ..., delist_date: _Optional[str] = ..., settle_date: _Optional[str] = ...) -> None: ...

class AlgoParams(_message.Message):
    __slots__ = ("algo_name", "begin_time", "end_time", "duration_seconds", "interval_seconds", "order_price_level", "shift_price_tick", "price_limit", "max_active_order_nums", "price_cage", "custom_param", "expire_time")
    ALGO_NAME_FIELD_NUMBER: _ClassVar[int]
    BEGIN_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_SECONDS_FIELD_NUMBER: _ClassVar[int]
    ORDER_PRICE_LEVEL_FIELD_NUMBER: _ClassVar[int]
    SHIFT_PRICE_TICK_FIELD_NUMBER: _ClassVar[int]
    PRICE_LIMIT_FIELD_NUMBER: _ClassVar[int]
    MAX_ACTIVE_ORDER_NUMS_FIELD_NUMBER: _ClassVar[int]
    PRICE_CAGE_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_PARAM_FIELD_NUMBER: _ClassVar[int]
    EXPIRE_TIME_FIELD_NUMBER: _ClassVar[int]
    algo_name: str
    begin_time: int
    end_time: int
    duration_seconds: int
    interval_seconds: int
    order_price_level: int
    shift_price_tick: int
    price_limit: float
    max_active_order_nums: int
    price_cage: float
    custom_param: str
    expire_time: int
    def __init__(self, algo_name: _Optional[str] = ..., begin_time: _Optional[int] = ..., end_time: _Optional[int] = ..., duration_seconds: _Optional[int] = ..., interval_seconds: _Optional[int] = ..., order_price_level: _Optional[int] = ..., shift_price_tick: _Optional[int] = ..., price_limit: _Optional[float] = ..., max_active_order_nums: _Optional[int] = ..., price_cage: _Optional[float] = ..., custom_param: _Optional[str] = ..., expire_time: _Optional[int] = ...) -> None: ...

class Order(_message.Message):
    __slots__ = ("order_id", "cl_order_id", "counter_order_id", "order_date", "order_time", "security_id", "market", "security_type", "instrument_id", "appl_id", "contract_unit", "strategy_id", "strategy_name", "account_id", "investor_id", "order_type", "side", "position_effect", "time_in_force", "purpose", "business_type", "order_qty", "order_price", "order_amt", "order_status", "match_qty", "match_amt", "cancel_qty", "reject_qty", "is_pass", "owner_type", "reject_reason", "text", "is_pre_order", "trigger_time", "parent_order_id", "algo_type", "algo_params", "order_source", "attachment", "cancel_time", "user_id", "risk_info", "op_marks", "symbol", "basket_id")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    COUNTER_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_DATE_FIELD_NUMBER: _ClassVar[int]
    ORDER_TIME_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SECURITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    APPL_ID_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_UNIT_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    POSITION_EFFECT_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_FORCE_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    BUSINESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    ORDER_QTY_FIELD_NUMBER: _ClassVar[int]
    ORDER_PRICE_FIELD_NUMBER: _ClassVar[int]
    ORDER_AMT_FIELD_NUMBER: _ClassVar[int]
    ORDER_STATUS_FIELD_NUMBER: _ClassVar[int]
    MATCH_QTY_FIELD_NUMBER: _ClassVar[int]
    MATCH_AMT_FIELD_NUMBER: _ClassVar[int]
    CANCEL_QTY_FIELD_NUMBER: _ClassVar[int]
    REJECT_QTY_FIELD_NUMBER: _ClassVar[int]
    IS_PASS_FIELD_NUMBER: _ClassVar[int]
    OWNER_TYPE_FIELD_NUMBER: _ClassVar[int]
    REJECT_REASON_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    IS_PRE_ORDER_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_TIME_FIELD_NUMBER: _ClassVar[int]
    PARENT_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ALGO_TYPE_FIELD_NUMBER: _ClassVar[int]
    ALGO_PARAMS_FIELD_NUMBER: _ClassVar[int]
    ORDER_SOURCE_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENT_FIELD_NUMBER: _ClassVar[int]
    CANCEL_TIME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    RISK_INFO_FIELD_NUMBER: _ClassVar[int]
    OP_MARKS_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    BASKET_ID_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    cl_order_id: str
    counter_order_id: str
    order_date: int
    order_time: int
    security_id: str
    market: str
    security_type: str
    instrument_id: str
    appl_id: str
    contract_unit: float
    strategy_id: int
    strategy_name: str
    account_id: str
    investor_id: str
    order_type: int
    side: int
    position_effect: int
    time_in_force: int
    purpose: int
    business_type: str
    order_qty: int
    order_price: float
    order_amt: float
    order_status: int
    match_qty: int
    match_amt: float
    cancel_qty: int
    reject_qty: int
    is_pass: int
    owner_type: int
    reject_reason: int
    text: str
    is_pre_order: int
    trigger_time: int
    parent_order_id: str
    algo_type: int
    algo_params: AlgoParams
    order_source: str
    attachment: str
    cancel_time: int
    user_id: str
    risk_info: str
    op_marks: str
    symbol: str
    basket_id: str
    def __init__(self, order_id: _Optional[str] = ..., cl_order_id: _Optional[str] = ..., counter_order_id: _Optional[str] = ..., order_date: _Optional[int] = ..., order_time: _Optional[int] = ..., security_id: _Optional[str] = ..., market: _Optional[str] = ..., security_type: _Optional[str] = ..., instrument_id: _Optional[str] = ..., appl_id: _Optional[str] = ..., contract_unit: _Optional[float] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., order_type: _Optional[int] = ..., side: _Optional[int] = ..., position_effect: _Optional[int] = ..., time_in_force: _Optional[int] = ..., purpose: _Optional[int] = ..., business_type: _Optional[str] = ..., order_qty: _Optional[int] = ..., order_price: _Optional[float] = ..., order_amt: _Optional[float] = ..., order_status: _Optional[int] = ..., match_qty: _Optional[int] = ..., match_amt: _Optional[float] = ..., cancel_qty: _Optional[int] = ..., reject_qty: _Optional[int] = ..., is_pass: _Optional[int] = ..., owner_type: _Optional[int] = ..., reject_reason: _Optional[int] = ..., text: _Optional[str] = ..., is_pre_order: _Optional[int] = ..., trigger_time: _Optional[int] = ..., parent_order_id: _Optional[str] = ..., algo_type: _Optional[int] = ..., algo_params: _Optional[_Union[AlgoParams, _Mapping]] = ..., order_source: _Optional[str] = ..., attachment: _Optional[str] = ..., cancel_time: _Optional[int] = ..., user_id: _Optional[str] = ..., risk_info: _Optional[str] = ..., op_marks: _Optional[str] = ..., symbol: _Optional[str] = ..., basket_id: _Optional[str] = ...) -> None: ...

class Trade(_message.Message):
    __slots__ = ("order_id", "cl_order_id", "order_date", "order_time", "trade_id", "trade_time", "order_type", "side", "position_effect", "owner_type", "security_id", "market", "security_type", "instrument_id", "appl_id", "contract_unit", "strategy_id", "strategy_name", "account_id", "investor_id", "business_type", "last_qty", "last_px", "last_amt", "match_place", "algo_type", "order_source", "attachment", "user_id", "counter_cl_order_id", "counter_order_id", "symbol", "parent_order_id", "basket_id")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_DATE_FIELD_NUMBER: _ClassVar[int]
    ORDER_TIME_FIELD_NUMBER: _ClassVar[int]
    TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    TRADE_TIME_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    POSITION_EFFECT_FIELD_NUMBER: _ClassVar[int]
    OWNER_TYPE_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SECURITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    APPL_ID_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_UNIT_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    BUSINESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_QTY_FIELD_NUMBER: _ClassVar[int]
    LAST_PX_FIELD_NUMBER: _ClassVar[int]
    LAST_AMT_FIELD_NUMBER: _ClassVar[int]
    MATCH_PLACE_FIELD_NUMBER: _ClassVar[int]
    ALGO_TYPE_FIELD_NUMBER: _ClassVar[int]
    ORDER_SOURCE_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENT_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    COUNTER_CL_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    COUNTER_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    PARENT_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    BASKET_ID_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    cl_order_id: str
    order_date: int
    order_time: int
    trade_id: str
    trade_time: int
    order_type: int
    side: int
    position_effect: int
    owner_type: int
    security_id: str
    market: str
    security_type: str
    instrument_id: str
    appl_id: str
    contract_unit: float
    strategy_id: int
    strategy_name: str
    account_id: str
    investor_id: str
    business_type: str
    last_qty: int
    last_px: float
    last_amt: float
    match_place: int
    algo_type: int
    order_source: str
    attachment: str
    user_id: str
    counter_cl_order_id: str
    counter_order_id: str
    symbol: str
    parent_order_id: str
    basket_id: str
    def __init__(self, order_id: _Optional[str] = ..., cl_order_id: _Optional[str] = ..., order_date: _Optional[int] = ..., order_time: _Optional[int] = ..., trade_id: _Optional[str] = ..., trade_time: _Optional[int] = ..., order_type: _Optional[int] = ..., side: _Optional[int] = ..., position_effect: _Optional[int] = ..., owner_type: _Optional[int] = ..., security_id: _Optional[str] = ..., market: _Optional[str] = ..., security_type: _Optional[str] = ..., instrument_id: _Optional[str] = ..., appl_id: _Optional[str] = ..., contract_unit: _Optional[float] = ..., strategy_id: _Optional[int] = ..., strategy_name: _Optional[str] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., business_type: _Optional[str] = ..., last_qty: _Optional[int] = ..., last_px: _Optional[float] = ..., last_amt: _Optional[float] = ..., match_place: _Optional[int] = ..., algo_type: _Optional[int] = ..., order_source: _Optional[str] = ..., attachment: _Optional[str] = ..., user_id: _Optional[str] = ..., counter_cl_order_id: _Optional[str] = ..., counter_order_id: _Optional[str] = ..., symbol: _Optional[str] = ..., parent_order_id: _Optional[str] = ..., basket_id: _Optional[str] = ...) -> None: ...

class Fund(_message.Message):
    __slots__ = ("account_id", "investor_id", "currency_id", "sod", "balance", "frozen", "available", "intraday", "trans_in", "trans_out", "version")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    SOD_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    FROZEN_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    INTRADAY_FIELD_NUMBER: _ClassVar[int]
    TRANS_IN_FIELD_NUMBER: _ClassVar[int]
    TRANS_OUT_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    investor_id: str
    currency_id: str
    sod: float
    balance: float
    frozen: float
    available: float
    intraday: float
    trans_in: float
    trans_out: float
    version: int
    def __init__(self, account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., currency_id: _Optional[str] = ..., sod: _Optional[float] = ..., balance: _Optional[float] = ..., frozen: _Optional[float] = ..., available: _Optional[float] = ..., intraday: _Optional[float] = ..., trans_in: _Optional[float] = ..., trans_out: _Optional[float] = ..., version: _Optional[int] = ...) -> None: ...

class Position(_message.Message):
    __slots__ = ("account_id", "investor_id", "market", "security_id", "security_type", "symbol", "posi_side", "instrument_id", "sod", "balance", "available", "frozen", "buy_in", "sell_out", "trans_in", "trans_out", "trans_avl", "apply_avl", "cost_price", "realized_pnl", "version", "cost_amt", "intraday_trading", "buy_in_nodeal")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    POSI_SIDE_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    SOD_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    FROZEN_FIELD_NUMBER: _ClassVar[int]
    BUY_IN_FIELD_NUMBER: _ClassVar[int]
    SELL_OUT_FIELD_NUMBER: _ClassVar[int]
    TRANS_IN_FIELD_NUMBER: _ClassVar[int]
    TRANS_OUT_FIELD_NUMBER: _ClassVar[int]
    TRANS_AVL_FIELD_NUMBER: _ClassVar[int]
    APPLY_AVL_FIELD_NUMBER: _ClassVar[int]
    COST_PRICE_FIELD_NUMBER: _ClassVar[int]
    REALIZED_PNL_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    COST_AMT_FIELD_NUMBER: _ClassVar[int]
    INTRADAY_TRADING_FIELD_NUMBER: _ClassVar[int]
    BUY_IN_NODEAL_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    investor_id: str
    market: str
    security_id: str
    security_type: str
    symbol: str
    posi_side: int
    instrument_id: str
    sod: int
    balance: int
    available: int
    frozen: int
    buy_in: int
    sell_out: int
    trans_in: int
    trans_out: int
    trans_avl: int
    apply_avl: int
    cost_price: float
    realized_pnl: float
    version: int
    cost_amt: float
    intraday_trading: int
    buy_in_nodeal: int
    def __init__(self, account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., market: _Optional[str] = ..., security_id: _Optional[str] = ..., security_type: _Optional[str] = ..., symbol: _Optional[str] = ..., posi_side: _Optional[int] = ..., instrument_id: _Optional[str] = ..., sod: _Optional[int] = ..., balance: _Optional[int] = ..., available: _Optional[int] = ..., frozen: _Optional[int] = ..., buy_in: _Optional[int] = ..., sell_out: _Optional[int] = ..., trans_in: _Optional[int] = ..., trans_out: _Optional[int] = ..., trans_avl: _Optional[int] = ..., apply_avl: _Optional[int] = ..., cost_price: _Optional[float] = ..., realized_pnl: _Optional[float] = ..., version: _Optional[int] = ..., cost_amt: _Optional[float] = ..., intraday_trading: _Optional[int] = ..., buy_in_nodeal: _Optional[int] = ...) -> None: ...

class StrategyInstrument(_message.Message):
    __slots__ = ("instrument_id", "market", "security_id", "sod_qty", "sod_amount")
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    SECURITY_ID_FIELD_NUMBER: _ClassVar[int]
    SOD_QTY_FIELD_NUMBER: _ClassVar[int]
    SOD_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    instrument_id: str
    market: str
    security_id: str
    sod_qty: int
    sod_amount: float
    def __init__(self, instrument_id: _Optional[str] = ..., market: _Optional[str] = ..., security_id: _Optional[str] = ..., sod_qty: _Optional[int] = ..., sod_amount: _Optional[float] = ...) -> None: ...

class RiskItem(_message.Message):
    __slots__ = ("account_id", "instrument_id", "status", "single_order_qty", "long_posi_qty_up", "short_posi_qty_up", "prev_price_deviation", "last_price_deviation", "best_price_deviation", "posi_concentration", "fund_available", "total_buy_order_qty", "total_sell_order_qty", "total_buy_order_amt", "total_sell_order_amt", "total_buy_trade_qty", "total_sell_trade_qty", "total_buy_trade_amt", "total_sell_trade_amt", "total_buy_active_qty", "total_sell_active_qty", "total_buy_order_nums", "total_sell_order_nums", "warning_ratio")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SINGLE_ORDER_QTY_FIELD_NUMBER: _ClassVar[int]
    LONG_POSI_QTY_UP_FIELD_NUMBER: _ClassVar[int]
    SHORT_POSI_QTY_UP_FIELD_NUMBER: _ClassVar[int]
    PREV_PRICE_DEVIATION_FIELD_NUMBER: _ClassVar[int]
    LAST_PRICE_DEVIATION_FIELD_NUMBER: _ClassVar[int]
    BEST_PRICE_DEVIATION_FIELD_NUMBER: _ClassVar[int]
    POSI_CONCENTRATION_FIELD_NUMBER: _ClassVar[int]
    FUND_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_BUY_ORDER_QTY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SELL_ORDER_QTY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_BUY_ORDER_AMT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SELL_ORDER_AMT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_BUY_TRADE_QTY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SELL_TRADE_QTY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_BUY_TRADE_AMT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SELL_TRADE_AMT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_BUY_ACTIVE_QTY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SELL_ACTIVE_QTY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_BUY_ORDER_NUMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SELL_ORDER_NUMS_FIELD_NUMBER: _ClassVar[int]
    WARNING_RATIO_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    instrument_id: str
    status: int
    single_order_qty: int
    long_posi_qty_up: int
    short_posi_qty_up: int
    prev_price_deviation: float
    last_price_deviation: float
    best_price_deviation: float
    posi_concentration: float
    fund_available: float
    total_buy_order_qty: int
    total_sell_order_qty: int
    total_buy_order_amt: float
    total_sell_order_amt: float
    total_buy_trade_qty: int
    total_sell_trade_qty: int
    total_buy_trade_amt: float
    total_sell_trade_amt: float
    total_buy_active_qty: int
    total_sell_active_qty: int
    total_buy_order_nums: int
    total_sell_order_nums: int
    warning_ratio: float
    def __init__(self, account_id: _Optional[str] = ..., instrument_id: _Optional[str] = ..., status: _Optional[int] = ..., single_order_qty: _Optional[int] = ..., long_posi_qty_up: _Optional[int] = ..., short_posi_qty_up: _Optional[int] = ..., prev_price_deviation: _Optional[float] = ..., last_price_deviation: _Optional[float] = ..., best_price_deviation: _Optional[float] = ..., posi_concentration: _Optional[float] = ..., fund_available: _Optional[float] = ..., total_buy_order_qty: _Optional[int] = ..., total_sell_order_qty: _Optional[int] = ..., total_buy_order_amt: _Optional[float] = ..., total_sell_order_amt: _Optional[float] = ..., total_buy_trade_qty: _Optional[int] = ..., total_sell_trade_qty: _Optional[int] = ..., total_buy_trade_amt: _Optional[float] = ..., total_sell_trade_amt: _Optional[float] = ..., total_buy_active_qty: _Optional[int] = ..., total_sell_active_qty: _Optional[int] = ..., total_buy_order_nums: _Optional[int] = ..., total_sell_order_nums: _Optional[int] = ..., warning_ratio: _Optional[float] = ...) -> None: ...

class RiskMarketParams(_message.Message):
    __slots__ = ("account_id", "market", "risk_code", "risk_name", "control_type", "control_point", "status", "set_value", "params", "comments", "create_by", "update_by", "create_time", "update_time")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    RISK_CODE_FIELD_NUMBER: _ClassVar[int]
    RISK_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTROL_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTROL_POINT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SET_VALUE_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    CREATE_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATE_BY_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    market: str
    risk_code: str
    risk_name: str
    control_type: str
    control_point: str
    status: int
    set_value: float
    params: str
    comments: str
    create_by: str
    update_by: str
    create_time: str
    update_time: str
    def __init__(self, account_id: _Optional[str] = ..., market: _Optional[str] = ..., risk_code: _Optional[str] = ..., risk_name: _Optional[str] = ..., control_type: _Optional[str] = ..., control_point: _Optional[str] = ..., status: _Optional[int] = ..., set_value: _Optional[float] = ..., params: _Optional[str] = ..., comments: _Optional[str] = ..., create_by: _Optional[str] = ..., update_by: _Optional[str] = ..., create_time: _Optional[str] = ..., update_time: _Optional[str] = ...) -> None: ...

class TradingSession(_message.Message):
    __slots__ = ("market", "time_slices")
    class TimeSlice(_message.Message):
        __slots__ = ("start_time", "end_time")
        START_TIME_FIELD_NUMBER: _ClassVar[int]
        END_TIME_FIELD_NUMBER: _ClassVar[int]
        start_time: str
        end_time: str
        def __init__(self, start_time: _Optional[str] = ..., end_time: _Optional[str] = ...) -> None: ...
    MARKET_FIELD_NUMBER: _ClassVar[int]
    TIME_SLICES_FIELD_NUMBER: _ClassVar[int]
    market: str
    time_slices: _containers.RepeatedCompositeFieldContainer[TradingSession.TimeSlice]
    def __init__(self, market: _Optional[str] = ..., time_slices: _Optional[_Iterable[_Union[TradingSession.TimeSlice, _Mapping]]] = ...) -> None: ...

class CounterAccount(_message.Message):
    __slots__ = ("counter_id", "account_id", "investor_id", "investor_flag", "ip", "password", "props", "params")
    class PropsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    COUNTER_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_ID_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_FLAG_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    PROPS_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    counter_id: str
    account_id: str
    investor_id: str
    investor_flag: str
    ip: str
    password: str
    props: _containers.ScalarMap[str, str]
    params: str
    def __init__(self, counter_id: _Optional[str] = ..., account_id: _Optional[str] = ..., investor_id: _Optional[str] = ..., investor_flag: _Optional[str] = ..., ip: _Optional[str] = ..., password: _Optional[str] = ..., props: _Optional[_Mapping[str, str]] = ..., params: _Optional[str] = ...) -> None: ...
