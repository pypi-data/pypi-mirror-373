#!/usr/bin/env python3
"""
Demo script for SearchService functionality.

This script demonstrates how to use the SearchService to perform semantic search
over indexed documentation.
"""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from strands_mcp.models.documentation import SearchQuery
from strands_mcp.services.indexing_service import DocumentIndexingService
from strands_mcp.services.search_service import SearchService


async def main():
    """Run the search service demo."""
    print("🔍 SearchService Demo")
    print("=" * 50)
    
    # Create temporary directory for this demo
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temporary directory: {temp_dir}")
        
        # Initialize services
        indexing_service = DocumentIndexingService(
            model_name="all-MiniLM-L6-v2",
            index_dir=temp_dir,
            chunk_size=300,
            chunk_overlap=50
        )
        
        search_service = SearchService(
            model_name="all-MiniLM-L6-v2",
            index_dir=temp_dir,
            max_snippet_length=200
        )
        
        print("\n📚 Creating sample documentation...")
        
        # Sample documentation content
        now = datetime.now()
        documents = [
            (
                """# Getting Started with Strands SDK

The Strands Agent SDK is a powerful framework for building intelligent agents. 
This guide will help you get started quickly.

## Installation

Install the Strands SDK using pip:

```bash
pip install strands-sdk
```

## Quick Start

Here's a simple example to create your first agent:

```python
from strands import Agent

agent = Agent(name="my-agent")
agent.run()
```

## Key Features

- Multi-agent orchestration
- Built-in observability
- AWS integration
- Scalable deployment options
""",
                "Getting Started Guide",
                "https://github.com/strands-agents/docs/getting-started.md",
                "/docs/getting-started.md",
                now
            ),
            (
                """# Multi-Agent Patterns

The Strands SDK supports various multi-agent patterns for complex workflows.

## Hierarchical Agents

Create hierarchical agent structures where parent agents coordinate child agents:

```python
from strands import HierarchicalAgent

parent = HierarchicalAgent(name="coordinator")
child1 = Agent(name="worker-1")
child2 = Agent(name="worker-2")

parent.add_child(child1)
parent.add_child(child2)
```

## Pipeline Patterns

Chain agents together in processing pipelines:

```python
from strands import Pipeline

pipeline = Pipeline()
pipeline.add_stage(preprocessing_agent)
pipeline.add_stage(analysis_agent)
pipeline.add_stage(output_agent)
```

## Event-Driven Architecture

Use event-driven patterns for reactive agent systems:

```python
from strands import EventBus

bus = EventBus()
agent.subscribe(bus, "data_received")
```
""",
                "Multi-Agent Patterns",
                "https://github.com/strands-agents/docs/multi-agent.md",
                "/docs/multi-agent.md",
                now
            ),
            (
                """# Observability and Monitoring

The Strands SDK provides comprehensive observability features for monitoring agent performance.

## Metrics Collection

Enable automatic metrics collection:

```python
from strands import Agent, MetricsCollector

agent = Agent(name="monitored-agent")
collector = MetricsCollector()
agent.add_observer(collector)
```

## Logging

Configure structured logging:

```python
import logging
from strands.logging import configure_logging

configure_logging(level=logging.INFO, format="json")
```

## Tracing

Enable distributed tracing for multi-agent systems:

```python
from strands.tracing import enable_tracing

enable_tracing(service_name="my-agent-system")
```

## Performance Monitoring

Monitor agent performance metrics:

- Response time
- Throughput
- Error rates
- Resource utilization
""",
                "Observability Guide",
                "https://github.com/strands-agents/docs/observability.md",
                "/docs/observability.md",
                now
            ),
            (
                """# Deployment Options

Deploy your Strands agents to various environments.

## Local Development

Run agents locally for development:

```bash
strands run --config local.yaml
```

## Docker Deployment

Deploy using Docker containers:

```dockerfile
FROM python:3.11
COPY . /app
WORKDIR /app
RUN pip install strands-sdk
CMD ["strands", "run"]
```

## AWS Deployment

Deploy to AWS using various services:

### Lambda Functions

Deploy agents as AWS Lambda functions:

```python
from strands.aws import LambdaDeployment

deployment = LambdaDeployment(
    function_name="my-agent",
    runtime="python3.11"
)
deployment.deploy()
```

### ECS/Fargate

Deploy using Amazon ECS:

```yaml
version: '3'
services:
  agent:
    image: my-agent:latest
    environment:
      - STRANDS_CONFIG=production
```

## Kubernetes

Deploy to Kubernetes clusters:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: strands-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: strands-agent
  template:
    metadata:
      labels:
        app: strands-agent
    spec:
      containers:
      - name: agent
        image: my-agent:latest
```
""",
                "Deployment Guide",
                "https://github.com/strands-agents/docs/deployment.md",
                "/docs/deployment.md",
                now
            )
        ]
        
        print(f"📝 Indexing {len(documents)} documents...")
        
        # Index the documents
        document_index = await indexing_service.index_documents(documents)
        faiss_index = indexing_service.build_faiss_index(document_index)
        
        # Save the indexes
        indexing_service.save_index(document_index, faiss_index)
        
        print(f"✅ Created index with {len(document_index.chunks)} chunks")
        
        # Load index in search service
        print("\n🔄 Loading search index...")
        loaded = await search_service.load_index()
        
        if not loaded:
            print("❌ Failed to load search index")
            return
        
        print("✅ Search index loaded successfully")
        
        # Display index statistics
        stats = search_service.get_index_stats()
        print(f"\n📊 Index Statistics:")
        print(f"   • Total chunks: {stats['total_chunks']}")
        print(f"   • Unique documents: {stats['unique_documents']}")
        print(f"   • Unique sections: {stats['unique_sections']}")
        print(f"   • Embedding model: {stats['embedding_model']}")
        
        # Demo queries
        demo_queries = [
            "How do I install and get started with Strands?",
            "Multi-agent patterns and hierarchical agents",
            "Observability metrics and monitoring",
            "Deploy to AWS Lambda functions",
            "Docker container deployment",
            "Event-driven architecture patterns"
        ]
        
        print(f"\n🔍 Running {len(demo_queries)} demo searches...")
        print("=" * 50)
        
        for i, query_text in enumerate(demo_queries, 1):
            print(f"\n🔎 Query {i}: {query_text}")
            print("-" * 40)
            
            # Create search query
            query = SearchQuery(
                query=query_text,
                limit=3,
                min_score=0.1
            )
            
            # Perform search
            results = await search_service.semantic_search(query)
            
            if not results:
                print("   No results found")
                continue
            
            # Display results
            for j, result in enumerate(results, 1):
                print(f"   {j}. {result.title} ({result.section})")
                print(f"      Score: {result.relevance_score:.3f}")
                print(f"      Snippet: {result.snippet}")
                print(f"      URL: {result.source_url}")
                if j < len(results):
                    print()
        
        # Demo similar document search
        print(f"\n🔗 Finding similar documents...")
        print("-" * 40)
        
        # Get the first chunk ID for similarity search
        first_chunk = document_index.chunks[0]
        print(f"Reference document: {first_chunk.title} ({first_chunk.section})")
        
        similar_docs = await search_service.get_similar_documents(
            first_chunk.id, 
            limit=3
        )
        
        if similar_docs:
            print("Similar documents:")
            for i, doc in enumerate(similar_docs, 1):
                print(f"   {i}. {doc.title} ({doc.section})")
                print(f"      Score: {doc.relevance_score:.3f}")
                print(f"      Snippet: {doc.snippet[:100]}...")
        else:
            print("No similar documents found")
        
        print(f"\n✨ Demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())