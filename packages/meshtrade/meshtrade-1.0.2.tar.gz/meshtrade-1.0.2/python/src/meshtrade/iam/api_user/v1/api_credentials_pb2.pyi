from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class APICredentials(_message.Message):
    __slots__ = ("api_key", "group")
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    api_key: str
    group: str
    def __init__(self, api_key: _Optional[str] = ..., group: _Optional[str] = ...) -> None: ...
