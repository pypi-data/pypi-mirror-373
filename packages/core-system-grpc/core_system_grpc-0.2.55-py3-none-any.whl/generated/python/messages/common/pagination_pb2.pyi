from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PaginationRequest(_message.Message):
    __slots__ = ("offset", "limit")
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    offset: int
    limit: int
    def __init__(self, offset: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class PaginationResponse(_message.Message):
    __slots__ = ("total_count", "offset", "limit")
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    total_count: int
    offset: int
    limit: int
    def __init__(self, total_count: _Optional[int] = ..., offset: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...
