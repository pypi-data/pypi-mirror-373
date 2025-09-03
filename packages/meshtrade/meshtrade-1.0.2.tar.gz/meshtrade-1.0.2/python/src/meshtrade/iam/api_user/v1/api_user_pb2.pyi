from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class APIUserState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    API_USER_STATE_UNSPECIFIED: _ClassVar[APIUserState]
    API_USER_STATE_ACTIVE: _ClassVar[APIUserState]
    API_USER_STATE_INACTIVE: _ClassVar[APIUserState]

class APIUserAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    API_USER_ACTION_UNSPECIFIED: _ClassVar[APIUserAction]
    API_USER_ACTION_ACTIVATE: _ClassVar[APIUserAction]
    API_USER_ACTION_DEACTIVATE: _ClassVar[APIUserAction]
    API_USER_ACTION_CREATE: _ClassVar[APIUserAction]
    API_USER_ACTION_UPDATE: _ClassVar[APIUserAction]
API_USER_STATE_UNSPECIFIED: APIUserState
API_USER_STATE_ACTIVE: APIUserState
API_USER_STATE_INACTIVE: APIUserState
API_USER_ACTION_UNSPECIFIED: APIUserAction
API_USER_ACTION_ACTIVATE: APIUserAction
API_USER_ACTION_DEACTIVATE: APIUserAction
API_USER_ACTION_CREATE: APIUserAction
API_USER_ACTION_UPDATE: APIUserAction

class APIUser(_message.Message):
    __slots__ = ("name", "owner", "owners", "display_name", "state", "roles", "api_key")
    NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    OWNERS_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    name: str
    owner: str
    owners: _containers.RepeatedScalarFieldContainer[str]
    display_name: str
    state: APIUserState
    roles: _containers.RepeatedScalarFieldContainer[str]
    api_key: str
    def __init__(self, name: _Optional[str] = ..., owner: _Optional[str] = ..., owners: _Optional[_Iterable[str]] = ..., display_name: _Optional[str] = ..., state: _Optional[_Union[APIUserState, str]] = ..., roles: _Optional[_Iterable[str]] = ..., api_key: _Optional[str] = ...) -> None: ...
