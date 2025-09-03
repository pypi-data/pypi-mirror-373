"""Core System gRPC Package"""

from .generated.python.services.product_service_pb2_grpc import ProductServiceStub
from .generated.python.messages.product.request_pb2 import GetProductsByShopRequest
from .generated.python.messages.common.pagination_pb2 import PaginationRequest

__version__ = "0.2.58"

__all__ = [
    "ProductServiceStub",
    "GetProductsByShopRequest",
    "PaginationRequest",
]
