"""
Memory Service gRPC Client

A Python client library for the Memory Service gRPC API.
"""

from .rag_service_pb2 import *
from .rag_service_pb2_grpc import *

__version__ = "0.1.0"
__all__ = [
    "RagServiceStub",
    "ProcessDocumentRequest",
    "ProcessDocumentResponse", 
    "QueryKnowledgeRequest",
    "QueryKnowledgeResponse",
    "DocumentStatusRequest",
    "DocumentStatusResponse",
    "HelloWorldRequest",
    "HelloWorldResponse",
    "ChunkingConfig",
    "QueryConfig",
    "ProcessingStatus",
    "ProcessingStats",
    "RetrievedChunk",
    "QueryStats",
]
