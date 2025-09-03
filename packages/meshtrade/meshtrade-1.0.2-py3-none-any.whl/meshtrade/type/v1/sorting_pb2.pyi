from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class SortingOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SORTING_ORDER_UNSPECIFIED: _ClassVar[SortingOrder]
    SORTING_ORDER_ASC: _ClassVar[SortingOrder]
    SORTING_ORDER_DESC: _ClassVar[SortingOrder]
SORTING_ORDER_UNSPECIFIED: SortingOrder
SORTING_ORDER_ASC: SortingOrder
SORTING_ORDER_DESC: SortingOrder
