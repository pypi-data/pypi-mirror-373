import datetime

from meshtrade.type.v1 import token_pb2 as _token_pb2
from meshtrade.type.v1 import amount_pb2 as _amount_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Narrative(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NARRATIVE_UNSPECIFIED: _ClassVar[Narrative]
    NARRATIVE_YIELD: _ClassVar[Narrative]
    NARRATIVE_COUPON: _ClassVar[Narrative]
NARRATIVE_UNSPECIFIED: Narrative
NARRATIVE_YIELD: Narrative
NARRATIVE_COUPON: Narrative

class Entry(_message.Message):
    __slots__ = ("asset_name", "token", "date", "description", "narrative", "amount", "reported_currency_value")
    ASSET_NAME_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    NARRATIVE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    REPORTED_CURRENCY_VALUE_FIELD_NUMBER: _ClassVar[int]
    asset_name: str
    token: _token_pb2.Token
    date: _timestamp_pb2.Timestamp
    description: str
    narrative: Narrative
    amount: _amount_pb2.Amount
    reported_currency_value: _amount_pb2.Amount
    def __init__(self, asset_name: _Optional[str] = ..., token: _Optional[_Union[_token_pb2.Token, _Mapping]] = ..., date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., description: _Optional[str] = ..., narrative: _Optional[_Union[Narrative, str]] = ..., amount: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ..., reported_currency_value: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ...) -> None: ...
