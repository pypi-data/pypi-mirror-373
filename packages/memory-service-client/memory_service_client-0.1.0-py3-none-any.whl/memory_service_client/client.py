"""
High-level client for Memory Service gRPC API.
"""

import grpc
from typing import Optional, List, Dict, Any

from . import rag_service_pb2_grpc as rpc
from . import rag_service_pb2 as pb


class MemoryServiceClient:
    """High-level client for Memory Service gRPC API."""
    
    def __init__(self, server_address: str = "localhost:50051"):
        """Initialize the client with server address."""
        self.server_address = server_address
        self._channel: Optional[grpc.Channel] = None
        self._stub: Optional[rpc.RagServiceStub] = None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def connect(self) -> None:
        """Connect to the gRPC server."""
        self._channel = grpc.insecure_channel(self.server_address)
        self._stub = rpc.RagServiceStub(self._channel)
    
    def close(self) -> None:
        """Close the connection to the gRPC server."""
        if self._channel:
            self._channel.close()
            self._channel = None
            self._stub = None
    
    def process_document(
        self,
        document_id: str,
        content: str,
        title: str = "",
        source_url: str = "",
        metadata: Optional[Dict[str, str]] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        chunking_strategy: str = "sentence"
    ) -> pb.ProcessDocumentResponse:
        """Process a document for RAG."""
        if not self._stub:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        chunking_config = pb.ChunkingConfig(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=chunking_strategy
        )
        
        request = pb.ProcessDocumentRequest(
            document_id=document_id,
            content=content,
            title=title,
            source_url=source_url,
            metadata=metadata or {},
            chunking_config=chunking_config
        )
        
        return self._stub.ProcessDocument(request)
    
    def query_knowledge(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        include_metadata: bool = True,
        use_reranking: bool = False,
        llm_model: str = "gpt-3.5-turbo",
        max_tokens: int = 1000
    ) -> pb.QueryKnowledgeResponse:
        """Query the knowledge base."""
        if not self._stub:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        query_config = pb.QueryConfig(
            include_metadata=include_metadata,
            use_reranking=use_reranking,
            llm_model=llm_model,
            max_tokens=max_tokens
        )
        
        request = pb.QueryKnowledgeRequest(
            query=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            config=query_config
        )
        
        return self._stub.QueryKnowledge(request)
    
    def get_document_status(self, document_id: str) -> pb.DocumentStatusResponse:
        """Get the processing status of a document."""
        if not self._stub:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        request = pb.DocumentStatusRequest(document_id=document_id)
        return self._stub.GetDocumentStatus(request)
    
    def hello_world(self, name: str = "World") -> pb.HelloWorldResponse:
        """Test connection with hello world."""
        if not self._stub:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        request = pb.HelloWorldRequest(name=name)
        return self._stub.HelloWorld(request)
