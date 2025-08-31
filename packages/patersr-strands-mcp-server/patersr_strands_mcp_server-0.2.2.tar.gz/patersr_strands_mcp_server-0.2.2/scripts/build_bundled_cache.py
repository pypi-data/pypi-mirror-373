#!/usr/bin/env python3
"""Script to build bundled cache for the MCP server package."""

import asyncio
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from strands_mcp.services.documentation_service import DocumentationService
from strands_mcp.models.documentation import DocumentIndex


async def build_bundled_cache(force: bool = False):
    """Build bundled cache from latest documentation.
    
    Args:
        force: If True, rebuild cache even if it exists and is recent
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("Building bundled cache from latest Strands documentation")
    
    # Define bundled cache directory
    bundled_cache_dir = Path(__file__).parent.parent / "src" / "strands_mcp" / "data" / "cache"
    bundled_cache_file = bundled_cache_dir / "index.json"
    
    # Check if we need to rebuild
    if not force and bundled_cache_file.exists():
        try:
            existing_index = DocumentIndex.load_from_file(str(bundled_cache_file))
            # If cache is less than 7 days old, skip rebuild
            age_days = (datetime.now(timezone.utc) - existing_index.last_updated).days
            if age_days < 7:
                logger.info(f"Bundled cache is {age_days} days old, skipping rebuild (use --force to override)")
                return True
        except Exception as e:
            logger.warning(f"Error reading existing cache, will rebuild: {e}")
    
    # Create documentation service
    doc_service = DocumentationService()
    
    try:
        # Fetch latest documentation
        logger.info("Fetching latest documentation from GitHub")
        chunks = await doc_service.fetch_latest_docs()
        
        if not chunks:
            logger.error("No documentation chunks fetched")
            return False
        
        logger.info(f"Fetched {len(chunks)} documentation chunks")
        
        # Create bundled cache directory
        bundled_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create index for bundled cache
        index = DocumentIndex(
            version="1.0",
            last_updated=datetime.now(timezone.utc),
            chunks=chunks,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Save bundled cache
        index.save_to_file(str(bundled_cache_file))
        
        logger.info(f"Bundled cache saved to {bundled_cache_file}")
        logger.info(f"Cache contains {len(chunks)} chunks")
        logger.info(f"Cache size: {bundled_cache_file.stat().st_size / 1024 / 1024:.2f} MB")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to build bundled cache: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        await doc_service.close()


def main():
    """Main entry point with argument parsing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build bundled cache for Strands MCP server")
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force rebuild even if cache exists and is recent"
    )
    
    args = parser.parse_args()
    
    success = asyncio.run(build_bundled_cache(force=args.force))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()