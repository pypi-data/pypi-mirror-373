from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Role(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROLE_UNSPECIFIED: _ClassVar[Role]
    ROLE_WALLET_ADMIN: _ClassVar[Role]
    ROLE_WALLET_VIEWER: _ClassVar[Role]
    ROLE_COMPLIANCE_ADMIN: _ClassVar[Role]
    ROLE_COMPLIANCE_VIEWER: _ClassVar[Role]
    ROLE_IAM_ADMIN: _ClassVar[Role]
    ROLE_IAM_VIEWER: _ClassVar[Role]
    ROLE_ISSUANCE_HUB_ADMIN: _ClassVar[Role]
    ROLE_ISSUANCE_HUB_VIEWER: _ClassVar[Role]
    ROLE_TRADING_ADMIN: _ClassVar[Role]
    ROLE_TRADING_VIEWER: _ClassVar[Role]
    ROLE_REPORT_ADMIN: _ClassVar[Role]
    ROLE_REPORT_VIEWER: _ClassVar[Role]
ROLE_UNSPECIFIED: Role
ROLE_WALLET_ADMIN: Role
ROLE_WALLET_VIEWER: Role
ROLE_COMPLIANCE_ADMIN: Role
ROLE_COMPLIANCE_VIEWER: Role
ROLE_IAM_ADMIN: Role
ROLE_IAM_VIEWER: Role
ROLE_ISSUANCE_HUB_ADMIN: Role
ROLE_ISSUANCE_HUB_VIEWER: Role
ROLE_TRADING_ADMIN: Role
ROLE_TRADING_VIEWER: Role
ROLE_REPORT_ADMIN: Role
ROLE_REPORT_VIEWER: Role
STANDARD_ROLES_FIELD_NUMBER: _ClassVar[int]
standard_roles: _descriptor.FieldDescriptor
ROLES_FIELD_NUMBER: _ClassVar[int]
roles: _descriptor.FieldDescriptor

class RoleList(_message.Message):
    __slots__ = ("roles",)
    ROLES_FIELD_NUMBER: _ClassVar[int]
    roles: _containers.RepeatedScalarFieldContainer[Role]
    def __init__(self, roles: _Optional[_Iterable[_Union[Role, str]]] = ...) -> None: ...
