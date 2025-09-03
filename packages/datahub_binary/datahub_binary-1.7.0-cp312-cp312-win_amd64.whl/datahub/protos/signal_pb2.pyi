import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SignalControlReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "operate_type", "signal_id", "signal_name", "control_type", "op_user")
    class ControlType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        kInit: _ClassVar[SignalControlReq.ControlType]
        kRun: _ClassVar[SignalControlReq.ControlType]
        kPause: _ClassVar[SignalControlReq.ControlType]
        kStop: _ClassVar[SignalControlReq.ControlType]
        kClose: _ClassVar[SignalControlReq.ControlType]
    kInit: SignalControlReq.ControlType
    kRun: SignalControlReq.ControlType
    kPause: SignalControlReq.ControlType
    kStop: SignalControlReq.ControlType
    kClose: SignalControlReq.ControlType
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTROL_TYPE_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    operate_type: int
    signal_id: int
    signal_name: str
    control_type: SignalControlReq.ControlType
    op_user: _common_pb2.OpUser
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., operate_type: _Optional[int] = ..., signal_id: _Optional[int] = ..., signal_name: _Optional[str] = ..., control_type: _Optional[_Union[SignalControlReq.ControlType, str]] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ...) -> None: ...

class SignalControlRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "signal_name", "signal_id", "status", "text")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_NAME_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    signal_name: str
    signal_id: int
    status: int
    text: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., signal_name: _Optional[str] = ..., signal_id: _Optional[int] = ..., status: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class UpdateSignalGlobalParamsReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "operate_type", "signal_template_id", "text", "signal_params", "op_user")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_PARAMS_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    operate_type: int
    signal_template_id: str
    text: str
    signal_params: str
    op_user: _common_pb2.OpUser
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., operate_type: _Optional[int] = ..., signal_template_id: _Optional[str] = ..., text: _Optional[str] = ..., signal_params: _Optional[str] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ...) -> None: ...

class UpdateSignalGlobalParamsRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "signal_template_id", "status", "request_id", "text", "signal_params")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_PARAMS_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    signal_template_id: str
    status: int
    request_id: str
    text: str
    signal_params: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., signal_template_id: _Optional[str] = ..., status: _Optional[int] = ..., request_id: _Optional[str] = ..., text: _Optional[str] = ..., signal_params: _Optional[str] = ...) -> None: ...

class UpdateSignalParamsReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "operate_type", "signal_name", "signal_id", "text", "signal_params", "fund_etfpr_minnav", "fund_etfpr_estcash", "package_info", "signal_info_l2", "op_user")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_NAME_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_PARAMS_FIELD_NUMBER: _ClassVar[int]
    FUND_ETFPR_MINNAV_FIELD_NUMBER: _ClassVar[int]
    FUND_ETFPR_ESTCASH_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_INFO_L2_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    operate_type: int
    signal_name: str
    signal_id: int
    text: str
    signal_params: str
    fund_etfpr_minnav: float
    fund_etfpr_estcash: float
    package_info: _containers.RepeatedCompositeFieldContainer[_common_pb2.PackageInfo]
    signal_info_l2: _containers.RepeatedCompositeFieldContainer[_common_pb2.SignalInfoL2]
    op_user: _common_pb2.OpUser
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., operate_type: _Optional[int] = ..., signal_name: _Optional[str] = ..., signal_id: _Optional[int] = ..., text: _Optional[str] = ..., signal_params: _Optional[str] = ..., fund_etfpr_minnav: _Optional[float] = ..., fund_etfpr_estcash: _Optional[float] = ..., package_info: _Optional[_Iterable[_Union[_common_pb2.PackageInfo, _Mapping]]] = ..., signal_info_l2: _Optional[_Iterable[_Union[_common_pb2.SignalInfoL2, _Mapping]]] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ...) -> None: ...

class UpdateSignalParamsRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "signal_name", "signal_id", "status", "request_id", "text", "signal_params", "fund_etfpr_minnav", "fund_etfpr_estcash", "package_info", "signal_info_l2")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_NAME_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_PARAMS_FIELD_NUMBER: _ClassVar[int]
    FUND_ETFPR_MINNAV_FIELD_NUMBER: _ClassVar[int]
    FUND_ETFPR_ESTCASH_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_INFO_L2_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    signal_name: str
    signal_id: int
    status: int
    request_id: str
    text: str
    signal_params: str
    fund_etfpr_minnav: float
    fund_etfpr_estcash: float
    package_info: _containers.RepeatedCompositeFieldContainer[_common_pb2.PackageInfo]
    signal_info_l2: _containers.RepeatedCompositeFieldContainer[_common_pb2.SignalInfoL2]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., signal_name: _Optional[str] = ..., signal_id: _Optional[int] = ..., status: _Optional[int] = ..., request_id: _Optional[str] = ..., text: _Optional[str] = ..., signal_params: _Optional[str] = ..., fund_etfpr_minnav: _Optional[float] = ..., fund_etfpr_estcash: _Optional[float] = ..., package_info: _Optional[_Iterable[_Union[_common_pb2.PackageInfo, _Mapping]]] = ..., signal_info_l2: _Optional[_Iterable[_Union[_common_pb2.SignalInfoL2, _Mapping]]] = ...) -> None: ...

class UpdateCurrencyPriceReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "currency_id", "currency_price", "text", "op_user")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_PRICE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    currency_id: str
    currency_price: int
    text: str
    op_user: _common_pb2.OpUser
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., currency_id: _Optional[str] = ..., currency_price: _Optional[int] = ..., text: _Optional[str] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ...) -> None: ...

class UpdateCurrencyPriceRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "status", "request_id", "text")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    status: int
    request_id: str
    text: str
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., status: _Optional[int] = ..., request_id: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class SignalStatDetail(_message.Message):
    __slots__ = ("signal_id", "signal_name", "status", "text", "instrument_id", "md_type", "md_time", "signal_value", "last_price")
    SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    MD_TYPE_FIELD_NUMBER: _ClassVar[int]
    MD_TIME_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    LAST_PRICE_FIELD_NUMBER: _ClassVar[int]
    signal_id: int
    signal_name: str
    status: str
    text: str
    instrument_id: str
    md_type: int
    md_time: int
    signal_value: int
    last_price: int
    def __init__(self, signal_id: _Optional[int] = ..., signal_name: _Optional[str] = ..., status: _Optional[str] = ..., text: _Optional[str] = ..., instrument_id: _Optional[str] = ..., md_type: _Optional[int] = ..., md_time: _Optional[int] = ..., signal_value: _Optional[int] = ..., last_price: _Optional[int] = ...) -> None: ...

class QrySignalStatReq(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "signal_id", "op_user")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    OP_USER_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    signal_id: int
    op_user: _common_pb2.OpUser
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., signal_id: _Optional[int] = ..., op_user: _Optional[_Union[_common_pb2.OpUser, _Mapping]] = ...) -> None: ...

class QrySignalStatRsp(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "request_id", "signal_stat")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_STAT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    request_id: str
    signal_stat: _containers.RepeatedCompositeFieldContainer[SignalStatDetail]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ..., signal_stat: _Optional[_Iterable[_Union[SignalStatDetail, _Mapping]]] = ...) -> None: ...

class SignalStatEvent(_message.Message):
    __slots__ = ("msg_type", "node_name", "node_type", "last_timestamp", "msg_sequence", "signal_id", "signal_name", "signal_stat")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODE_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_ID_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_NAME_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_STAT_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    node_name: str
    node_type: int
    last_timestamp: int
    msg_sequence: int
    signal_id: int
    signal_name: str
    signal_stat: _containers.RepeatedCompositeFieldContainer[SignalStatDetail]
    def __init__(self, msg_type: _Optional[int] = ..., node_name: _Optional[str] = ..., node_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., signal_id: _Optional[int] = ..., signal_name: _Optional[str] = ..., signal_stat: _Optional[_Iterable[_Union[SignalStatDetail, _Mapping]]] = ...) -> None: ...
