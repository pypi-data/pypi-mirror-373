import datetime

from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from meshtrade.reporting.income_report.v1 import income_report_pb2 as _income_report_pb2
from meshtrade.iam.role.v1 import role_pb2 as _role_pb2
from meshtrade.option.v1 import method_type_pb2 as _method_type_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetIncomeReportRequest(_message.Message):
    __slots__ = ("account_num", "to")
    ACCOUNT_NUM_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    account_num: str
    to: _timestamp_pb2.Timestamp
    def __init__(self, account_num: _Optional[str] = ..., to: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., **kwargs) -> None: ...

class GetExcelIncomeReportRequest(_message.Message):
    __slots__ = ("account_num", "to")
    ACCOUNT_NUM_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    account_num: str
    to: _timestamp_pb2.Timestamp
    def __init__(self, account_num: _Optional[str] = ..., to: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., **kwargs) -> None: ...

class GetExcelIncomeReportResponse(_message.Message):
    __slots__ = ("excel_base64",)
    EXCEL_BASE64_FIELD_NUMBER: _ClassVar[int]
    excel_base64: str
    def __init__(self, excel_base64: _Optional[str] = ...) -> None: ...
