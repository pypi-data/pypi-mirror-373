from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class User(_message.Message):
    __slots__ = ("email", "roles")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    email: str
    roles: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, email: _Optional[str] = ..., roles: _Optional[_Iterable[str]] = ...) -> None: ...
