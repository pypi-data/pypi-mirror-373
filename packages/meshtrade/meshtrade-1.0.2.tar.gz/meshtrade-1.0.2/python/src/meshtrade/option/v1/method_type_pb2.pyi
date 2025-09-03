from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class MethodType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    METHOD_TYPE_UNSPECIFIED: _ClassVar[MethodType]
    METHOD_TYPE_READ: _ClassVar[MethodType]
    METHOD_TYPE_WRITE: _ClassVar[MethodType]
METHOD_TYPE_UNSPECIFIED: MethodType
METHOD_TYPE_READ: MethodType
METHOD_TYPE_WRITE: MethodType
METHOD_TYPE_FIELD_NUMBER: _ClassVar[int]
method_type: _descriptor.FieldDescriptor
