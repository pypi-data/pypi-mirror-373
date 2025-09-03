from buf.validate import validate_pb2 as _validate_pb2
from meshtrade.iam.role.v1 import role_pb2 as _role_pb2
from meshtrade.iam.user.v1 import user_pb2 as _user_pb2
from meshtrade.option.v1 import method_type_pb2 as _method_type_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AssignRoleToUserRequest(_message.Message):
    __slots__ = ("email", "group", "role")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    email: str
    group: str
    role: _role_pb2.Role
    def __init__(self, email: _Optional[str] = ..., group: _Optional[str] = ..., role: _Optional[_Union[_role_pb2.Role, str]] = ...) -> None: ...
