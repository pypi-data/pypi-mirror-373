#!/usr/bin/env python3
"""
Demonstration of the document indexing and embedding system.

This script shows how to use the DocumentIndexingService to:
1. Index documents with embeddings
2. Build a FAISS vector index
3. Save and load indexes
4. Perform incremental updates
"""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path

# Add the src directory to the path so we can import our modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from strands_mcp.services.indexing_service import DocumentIndexingService


async def main():
    """Demonstrate the indexing service functionality."""
    print("🚀 Document Indexing and Embedding System Demo")
    print("=" * 50)
    
    # Create a temporary directory for this demo
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temporary directory: {temp_dir}")
        
        # Initialize the indexing service
        print("\n1️⃣ Initializing DocumentIndexingService...")
        service = DocumentIndexingService(
            model_name="all-MiniLM-L6-v2",
            index_dir=temp_dir,
            chunk_size=300,  # Smaller chunks for demo
            chunk_overlap=50
        )
        print(f"   ✅ Service initialized with model: {service.model_name}")
        
        # Sample documents to index
        sample_docs = [
            (
                """# Strands Agent SDK

## Introduction

The Strands Agent SDK is a powerful framework for building AI agents that can interact with various services and APIs. It provides a comprehensive set of tools and utilities to create sophisticated agent-based applications.

## Key Features

- **Multi-Agent Support**: Create and coordinate multiple agents
- **Tool Integration**: Easy integration with external APIs and services  
- **Workflow Management**: Define complex workflows and orchestration
- **Observability**: Built-in monitoring and logging capabilities

## Getting Started

To get started with Strands, install the SDK and configure your environment:

```bash
pip install strands-sdk
```

Then create your first agent:

```python
from strands import Agent

agent = Agent("my-first-agent")
agent.run()
```
""",
                "Strands SDK Documentation",
                "https://github.com/strands-agents/docs/blob/main/sdk.md",
                "/docs/sdk.md",
                datetime(2024, 1, 1, 12, 0, 0)
            ),
            (
                """# Multi-Agent Patterns

## Overview

Multi-agent systems in Strands allow you to create complex workflows by coordinating multiple specialized agents. Each agent can have its own role and capabilities.

## Common Patterns

### Sequential Execution

Agents execute one after another in a predefined order:

```python
from strands import SequentialWorkflow

workflow = SequentialWorkflow()
workflow.add_agent(research_agent)
workflow.add_agent(analysis_agent)
workflow.add_agent(report_agent)
```

### Parallel Execution

Multiple agents work simultaneously:

```python
from strands import ParallelWorkflow

workflow = ParallelWorkflow()
workflow.add_agent(data_collector_1)
workflow.add_agent(data_collector_2)
```

### Hierarchical Coordination

A supervisor agent coordinates worker agents:

```python
from strands import HierarchicalWorkflow

supervisor = SupervisorAgent()
workers = [WorkerAgent(f"worker-{i}") for i in range(3)]

workflow = HierarchicalWorkflow(supervisor, workers)
```

## Best Practices

- Keep agent responsibilities focused and well-defined
- Use proper error handling and recovery mechanisms
- Monitor agent performance and resource usage
- Implement proper communication protocols between agents
""",
                "Multi-Agent Patterns Guide",
                "https://github.com/strands-agents/docs/blob/main/multi-agent.md",
                "/docs/multi-agent.md",
                datetime(2024, 1, 2, 12, 0, 0)
            )
        ]
        
        # Index the documents
        print("\n2️⃣ Indexing documents...")
        print(f"   📄 Processing {len(sample_docs)} documents...")
        
        document_index = await service.index_documents(sample_docs)
        
        print(f"   ✅ Created index with {len(document_index.chunks)} chunks")
        print(f"   📊 Index version: {document_index.version}")
        print(f"   🤖 Embedding model: {document_index.embedding_model}")
        
        # Show some chunk details
        print("\n   📋 Sample chunks:")
        for i, chunk in enumerate(document_index.chunks[:3]):
            print(f"      {i+1}. Section: '{chunk.section}' (ID: {chunk.id[:12]}...)")
            print(f"         Content preview: {chunk.content[:80]}...")
            print(f"         Embedding dimension: {len(chunk.embedding) if chunk.embedding else 0}")
        
        # Build FAISS index
        print("\n3️⃣ Building FAISS vector index...")
        faiss_index = service.build_faiss_index(document_index)
        print(f"   ✅ FAISS index created with {faiss_index.ntotal} vectors")
        print(f"   📐 Vector dimension: {faiss_index.d}")
        
        # Save indexes to disk
        print("\n4️⃣ Saving indexes to disk...")
        service.save_index(document_index, faiss_index)
        
        # List created files
        index_dir = Path(temp_dir)
        index_files = list(index_dir.glob("*"))
        print(f"   ✅ Saved {len(index_files)} files:")
        for file in sorted(index_files):
            size_kb = file.stat().st_size / 1024
            print(f"      📄 {file.name} ({size_kb:.1f} KB)")
        
        # Load indexes back
        print("\n5️⃣ Loading indexes from disk...")
        loaded_doc_index, loaded_faiss_index = service.load_latest_index()
        
        if loaded_doc_index and loaded_faiss_index:
            print(f"   ✅ Loaded document index with {len(loaded_doc_index.chunks)} chunks")
            print(f"   ✅ Loaded FAISS index with {loaded_faiss_index.ntotal} vectors")
        else:
            print("   ❌ Failed to load indexes")
            return
        
        # Demonstrate incremental indexing
        print("\n6️⃣ Demonstrating incremental indexing...")
        
        new_doc = [
            (
                """# Deployment Guide

## Overview

This guide covers deploying Strands applications to production environments. Choose the deployment method that best fits your infrastructure and requirements.

## AWS Lambda Deployment

Deploy your agents as serverless functions:

```python
from strands.deployment import LambdaDeployer

deployer = LambdaDeployer()
deployer.deploy(agent, function_name="my-agent")
```

## Container Deployment

Use Docker containers for more control:

```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install strands-sdk
CMD ["python", "main.py"]
```

## Monitoring and Observability

Set up monitoring for your deployed agents:

- CloudWatch integration for AWS deployments
- Custom metrics and dashboards
- Error tracking and alerting
- Performance monitoring
""",
                "Deployment Guide",
                "https://github.com/strands-agents/docs/blob/main/deployment.md",
                "/docs/deployment.md",
                datetime(2024, 1, 3, 12, 0, 0)
            )
        ]
        
        print(f"   📄 Adding 1 new document...")
        updated_index = await service.update_index_incremental(new_doc, loaded_doc_index)
        
        print(f"   ✅ Updated index now has {len(updated_index.chunks)} chunks")
        print(f"   📈 Added {len(updated_index.chunks) - len(loaded_doc_index.chunks)} new chunks")
        print(f"   🆕 New version: {updated_index.version}")
        
        # Build updated FAISS index
        updated_faiss_index = service.build_faiss_index(updated_index)
        print(f"   ✅ Updated FAISS index with {updated_faiss_index.ntotal} vectors")
        
        # Show final statistics
        print("\n📊 Final Statistics:")
        print(f"   📚 Total documents processed: {len(sample_docs) + len(new_doc)}")
        print(f"   🧩 Total chunks created: {len(updated_index.chunks)}")
        print(f"   🎯 Vector dimension: {updated_faiss_index.d}")
        print(f"   💾 Index version: {updated_index.version}")
        
        # Show section distribution
        sections = {}
        for chunk in updated_index.chunks:
            sections[chunk.section] = sections.get(chunk.section, 0) + 1
        
        print(f"\n   📋 Chunks by section:")
        for section, count in sorted(sections.items()):
            print(f"      • {section}: {count} chunks")
        
        print("\n🎉 Demo completed successfully!")
        print("\nThe indexing service provides:")
        print("  ✅ Automatic document chunking with configurable size and overlap")
        print("  ✅ Section-aware chunking based on markdown headers")
        print("  ✅ High-quality embeddings using sentence-transformers")
        print("  ✅ Efficient FAISS vector indexing for fast similarity search")
        print("  ✅ Persistent storage with version tracking")
        print("  ✅ Incremental updates for new documents")
        print("  ✅ Comprehensive error handling and validation")


if __name__ == "__main__":
    asyncio.run(main())