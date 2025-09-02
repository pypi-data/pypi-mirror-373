#!/usr/bin/env python3
"""
Command-line interface for Memory Service client.
"""

import argparse
import json
import sys
from typing import Dict, Any

from .client import MemoryServiceClient


def process_document_cmd(args) -> None:
    """Process document command."""
    with MemoryServiceClient(args.server) as client:
        metadata = {}
        if args.metadata:
            try:
                metadata = json.loads(args.metadata)
            except json.JSONDecodeError:
                print("Error: Invalid JSON in metadata", file=sys.stderr)
                sys.exit(1)
        
        response = client.process_document(
            document_id=args.document_id,
            content=args.content,
            title=args.title or "",
            source_url=args.source_url or "",
            metadata=metadata,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            chunking_strategy=args.strategy
        )
        
        print(f"Status: {response.status}")
        print(f"Message: {response.message}")
        if response.stats:
            print(f"Chunks: {response.stats.total_chunks}")
            print(f"Processing time: {response.stats.processing_time_seconds:.2f}s")


def query_knowledge_cmd(args) -> None:
    """Query knowledge command."""
    with MemoryServiceClient(args.server) as client:
        response = client.query_knowledge(
            query=args.query,
            top_k=args.top_k,
            similarity_threshold=args.threshold,
            include_metadata=args.include_metadata,
            use_reranking=args.use_reranking,
            llm_model=args.llm_model,
            max_tokens=args.max_tokens
        )
        
        print(f"Answer: {response.answer}")
        print(f"Retrieved {len(response.chunks)} chunks:")
        for i, chunk in enumerate(response.chunks):
            print(f"  {i+1}. {chunk.content[:100]}... (score: {chunk.similarity_score:.3f})")


def document_status_cmd(args) -> None:
    """Document status command."""
    with MemoryServiceClient(args.server) as client:
        response = client.get_document_status(args.document_id)
        print(f"Document ID: {response.document_id}")
        print(f"Status: {response.status}")
        print(f"Message: {response.message}")


def hello_world_cmd(args) -> None:
    """Hello world command."""
    with MemoryServiceClient(args.server) as client:
        response = client.hello_world(args.name)
        print(response.message)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Memory Service Client CLI")
    parser.add_argument("--server", default="localhost:50051", help="Server address")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Process document command
    process_parser = subparsers.add_parser("process", help="Process a document")
    process_parser.add_argument("document_id", help="Document ID")
    process_parser.add_argument("content", help="Document content")
    process_parser.add_argument("--title", help="Document title")
    process_parser.add_argument("--source-url", help="Source URL")
    process_parser.add_argument("--metadata", help="Metadata as JSON string")
    process_parser.add_argument("--chunk-size", type=int, default=1000, help="Chunk size")
    process_parser.add_argument("--chunk-overlap", type=int, default=100, help="Chunk overlap")
    process_parser.add_argument("--strategy", default="sentence", help="Chunking strategy")
    process_parser.set_defaults(func=process_document_cmd)
    
    # Query knowledge command
    query_parser = subparsers.add_parser("query", help="Query knowledge base")
    query_parser.add_argument("query", help="Query text")
    query_parser.add_argument("--top-k", type=int, default=5, help="Number of results")
    query_parser.add_argument("--threshold", type=float, default=0.7, help="Similarity threshold")
    query_parser.add_argument("--include-metadata", action="store_true", help="Include metadata")
    query_parser.add_argument("--use-reranking", action="store_true", help="Use reranking")
    query_parser.add_argument("--llm-model", default="gpt-3.5-turbo", help="LLM model")
    query_parser.add_argument("--max-tokens", type=int, default=1000, help="Max tokens")
    query_parser.set_defaults(func=query_knowledge_cmd)
    
    # Document status command
    status_parser = subparsers.add_parser("status", help="Get document status")
    status_parser.add_argument("document_id", help="Document ID")
    status_parser.set_defaults(func=document_status_cmd)
    
    # Hello world command
    hello_parser = subparsers.add_parser("hello", help="Test connection")
    hello_parser.add_argument("--name", default="World", help="Name to greet")
    hello_parser.set_defaults(func=hello_world_cmd)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
