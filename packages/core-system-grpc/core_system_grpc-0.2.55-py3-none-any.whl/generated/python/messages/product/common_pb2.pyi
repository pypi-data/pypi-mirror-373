from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Product(_message.Message):
    __slots__ = ("id", "shop_id", "product_name")
    ID_FIELD_NUMBER: _ClassVar[int]
    SHOP_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    id: int
    shop_id: int
    product_name: str
    def __init__(self, id: _Optional[int] = ..., shop_id: _Optional[int] = ..., product_name: _Optional[str] = ...) -> None: ...
