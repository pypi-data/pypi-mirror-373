"""
zmp-knowledge-store-mcp-server

Vector knowledge base management for ZMP solutions (ZCP, AMDP, APIM)
using Model Context Protocol over SSE.

This package provides:
- Document ingestion with intelligent keyword extraction
- Semantic search with metadata filtering
- MCP server with SSE transport
- Production-ready deployment configuration

Author: AI Assistant
Version: 1.0.0
License: MIT
"""

__version__ = "0.1.0"
__description__ = "ZMP Knowledge Store MCP Server"
__author__ = "Your Name or Team"
__license__ = "MIT"


# Import main classes and functions
from .keyword_extractor import KeywordExtractor
from .config import Config
from .knowledge_store import ZmpKnowledgeStore
from .qdrant_adapter import QdrantAdapter

# Define what gets imported with "from zmp_knowledge_store import *"
__all__ = [
    "ZmpKnowledgeStore",
    "KeywordExtractor",
    "Config",
    "QdrantAdapter",
]

# Package metadata
PACKAGE_INFO = {
    "name": "zmp-knowledge-store-mcp-server",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "license": __license__,
    "transport": "sse",
    "port": 20004,
    "supported_solutions": ["zcp", "amdp", "apim"],
    "mcp_tools": ["ingest_document", "search_knowledge"],
    "features": [
        "Intelligent keyword extraction",
        "Semantic vector search",
        "Rich metadata tagging",
        "Solution-specific optimization",
        "Production monitoring",
        "Health checks",
    ],
}


def get_package_info():
    """Get package information"""
    return PACKAGE_INFO.copy()


def get_version():
    """Get package version"""
    return __version__


# Module-level configuration validation
def validate_environment():
    """Validate environment configuration"""
    try:
        Config.validate()
        return True
    except Exception as e:
        print(f"❌ Environment validation failed: {e}")
        return False


# Optional: Auto-validation on import (uncomment if desired)
# if not validate_environment():
#     print("⚠️  Warning: Environment validation failed. Some features may not work correctly.")
