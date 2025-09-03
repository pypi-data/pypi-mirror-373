import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from meshtrade.type.v1 import token_pb2 as _token_pb2
from meshtrade.type.v1 import address_pb2 as _address_pb2
from meshtrade.reporting.income_report.v1 import disclaimer_pb2 as _disclaimer_pb2
from meshtrade.reporting.income_report.v1 import entry_pb2 as _entry_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class IncomeReport(_message.Message):
    __slots__ = ("entries", "reporting_currency", "period", "generation_date", "account_number", "disclaimers", "client_address", "client_name", "copyright")
    class Period(_message.Message):
        __slots__ = ("to",)
        FROM_FIELD_NUMBER: _ClassVar[int]
        TO_FIELD_NUMBER: _ClassVar[int]
        to: _timestamp_pb2.Timestamp
        def __init__(self, to: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., **kwargs) -> None: ...
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    REPORTING_CURRENCY_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    GENERATION_DATE_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    DISCLAIMERS_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CLIENT_NAME_FIELD_NUMBER: _ClassVar[int]
    COPYRIGHT_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[_entry_pb2.Entry]
    reporting_currency: _token_pb2.Token
    period: IncomeReport.Period
    generation_date: _timestamp_pb2.Timestamp
    account_number: str
    disclaimers: _containers.RepeatedCompositeFieldContainer[_disclaimer_pb2.Disclaimer]
    client_address: _address_pb2.Address
    client_name: str
    copyright: str
    def __init__(self, entries: _Optional[_Iterable[_Union[_entry_pb2.Entry, _Mapping]]] = ..., reporting_currency: _Optional[_Union[_token_pb2.Token, _Mapping]] = ..., period: _Optional[_Union[IncomeReport.Period, _Mapping]] = ..., generation_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., account_number: _Optional[str] = ..., disclaimers: _Optional[_Iterable[_Union[_disclaimer_pb2.Disclaimer, _Mapping]]] = ..., client_address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., client_name: _Optional[str] = ..., copyright: _Optional[str] = ...) -> None: ...
