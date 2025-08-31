#!/usr/bin/env python3
"""Demonstration of fast startup functionality."""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from strands_mcp.server import StrandsMCPServer


async def demo_fast_startup():
    """Demonstrate fast startup functionality."""
    print("=== Fast Startup Demo ===\n")
    
    # Setup logging to see what's happening
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("1. Creating MCP Server...")
    server = StrandsMCPServer()
    
    print("\n2. Testing fast startup (should complete in < 5 seconds)...")
    start_time = time.time()
    
    try:
        # This should complete quickly by loading existing cache/index
        await server._ensure_services_initialized()
        
        end_time = time.time()
        startup_time = end_time - start_time
        
        print(f"✅ Startup completed in {startup_time:.2f} seconds")
        
        if startup_time < 5.0:
            print("✅ Meets 5-second startup requirement!")
        else:
            print("❌ Exceeds 5-second startup requirement")
        
        print(f"✅ Services initialized: {server._services_initialized}")
        print(f"✅ Background task created: {server._background_update_task is not None}")
        
        # Check if search service is ready
        if hasattr(server._search_service, 'get_index_stats'):
            try:
                stats = server._search_service.get_index_stats()
                print(f"✅ Search index status: {stats.get('status', 'unknown')}")
                if stats.get('status') == 'loaded':
                    print(f"   - Total chunks: {stats.get('total_chunks', 0)}")
                    print(f"   - Unique documents: {stats.get('unique_documents', 0)}")
            except Exception as e:
                print(f"ℹ️  Search index not yet available: {e}")
        
        print("\n3. Testing cache hierarchy...")
        cached_docs = await server._get_cached_docs_with_hierarchy()
        if cached_docs:
            print(f"✅ Found {len(cached_docs)} cached documents")
        else:
            print("ℹ️  No cached documents found (will be updated in background)")
        
        print("\n4. Simulating background update check...")
        should_update = server._should_check_for_updates()
        print(f"ℹ️  Should check for updates: {should_update}")
        
        print("\n5. Cleaning up...")
        await server._cleanup_services()
        print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(demo_fast_startup())