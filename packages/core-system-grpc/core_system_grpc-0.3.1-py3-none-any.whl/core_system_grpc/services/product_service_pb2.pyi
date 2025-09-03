from messages.product import request_pb2 as _request_pb2
from messages.product import response_pb2 as _response_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import service as _service
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class ProductService(_service.service): ...

class ProductService_Stub(ProductService): ...
