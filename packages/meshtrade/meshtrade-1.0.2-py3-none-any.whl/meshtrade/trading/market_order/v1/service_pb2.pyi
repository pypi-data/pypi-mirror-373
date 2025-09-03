from meshtrade.iam.role.v1 import role_pb2 as _role_pb2
from meshtrade.option.v1 import method_type_pb2 as _method_type_pb2
from meshtrade.trading.market_order.v1 import market_order_pb2 as _market_order_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetMarketOrderRequest(_message.Message):
    __slots__ = ("number",)
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    number: str
    def __init__(self, number: _Optional[str] = ...) -> None: ...
