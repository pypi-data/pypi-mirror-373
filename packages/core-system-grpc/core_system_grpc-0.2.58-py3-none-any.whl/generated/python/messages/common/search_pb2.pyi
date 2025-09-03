from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SortDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SORT_DIRECTION_UNSPECIFIED: _ClassVar[SortDirection]
    SORT_DIRECTION_ASC: _ClassVar[SortDirection]
    SORT_DIRECTION_DESC: _ClassVar[SortDirection]
SORT_DIRECTION_UNSPECIFIED: SortDirection
SORT_DIRECTION_ASC: SortDirection
SORT_DIRECTION_DESC: SortDirection

class SearchRequest(_message.Message):
    __slots__ = ("search_keyword",)
    SEARCH_KEYWORD_FIELD_NUMBER: _ClassVar[int]
    search_keyword: str
    def __init__(self, search_keyword: _Optional[str] = ...) -> None: ...

class SortRequest(_message.Message):
    __slots__ = ("sort_field", "sort_direction")
    SORT_FIELD_FIELD_NUMBER: _ClassVar[int]
    SORT_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    sort_field: str
    sort_direction: SortDirection
    def __init__(self, sort_field: _Optional[str] = ..., sort_direction: _Optional[_Union[SortDirection, str]] = ...) -> None: ...
