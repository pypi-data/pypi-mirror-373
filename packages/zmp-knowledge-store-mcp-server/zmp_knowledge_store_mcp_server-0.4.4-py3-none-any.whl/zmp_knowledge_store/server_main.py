#!/usr/bin/env python3
"""
ZMP Knowledge Store MCP Server

Following the standard FastMCP pattern from the Medium article
"""

import asyncio
import logging
from datetime import datetime, timezone
import json

# Add FastAPI for health check endpoint
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

# Import FastMCP
from fastmcp import FastMCP, Context

# from mcp.server.fastmcp import FastMCP
from zmp_knowledge_store.knowledge_store import ZmpKnowledgeStore
from zmp_knowledge_store.config import Config

# Load environment variables first
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Configure logging for all package modules
logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
logger = logging.getLogger("zmp-knowledge-store")

# Ensure all zmp_knowledge_store module loggers are visible
package_logger = logging.getLogger("zmp_knowledge_store")
package_logger.setLevel(logging.INFO)


# Create the FastMCP server with standard variable name
mcp = FastMCP(
    name="zmp-knowledge-store",
    instructions="""
               This server provides ZMP knowledge store tools.
               Call ingest_documents() to ingest documents into the knowledge store.
               Call search_knowledge() to search the knowledge store for relevant information.
               Call log_chat_history() to log user conversations with responses.
               Call search_chat_history() to search through chat history records.
               Call list_threads() to get all thread IDs and titles for a specific user.
               Call get_thread() to get all chat records for a specific user and thread.
            """,
)

# Add /healthz endpoint to the main FastMCP app (on port 5371)
if hasattr(mcp, "app") and isinstance(mcp.app, FastAPI):

    @mcp.app.get("/healthz")
    def healthz() -> PlainTextResponse:
        return PlainTextResponse("ok", status_code=200)


# Global knowledge store - initialize at module level for mcp dev
knowledge_store = None


async def get_knowledge_store() -> ZmpKnowledgeStore:
    """Initialize and return knowledge store"""
    global knowledge_store
    if knowledge_store is None:
        logger.info("🔧 Creating ZmpKnowledgeStore instance...")
        knowledge_store = ZmpKnowledgeStore()

    # Always ensure async initialization is run
    if not getattr(knowledge_store, "initialized", False):
        logger.info("🔌 Initializing Knowledge Store (async)...")
        await knowledge_store.initialize()

        logger.info("✅ Knowledge store initialized successfully (async)")

    return knowledge_store


@mcp.tool()
async def ingest_documents(
    documents: list, solution: str = None, collection: str = None, ctx: Context = None
) -> dict:
    """
    Ingest documents into the ZMP knowledge store.

    Args:
        documents: List of documents to ingest
        solution: Solution identifier (optional)
        collection: Target collection name. If not provided, uses default collection.
                   If collection doesn't exist, it will be created with same vector configs as existing collections.
        ctx: MCP context (internal use)
    """
    # logger.info(f"[REQUEST] ingest_documents input: {json.dumps({'documents': documents, 'solution': solution}, ensure_ascii=False, indent=2)}")
    ingest_timestamp = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    try:
        if not documents:
            result = {
                "success": False,
                "error": "No documents provided for ingestion",
                "results": [],
            }
            if ctx:
                await ctx.error("No documents provided for ingestion")
            return result

        # Validate collection parameter
        if collection is not None:
            if not collection or not collection.strip():
                result = {
                    "success": False,
                    "error": "Collection name cannot be empty",
                    "results": [],
                }
                if ctx:
                    await ctx.error("Collection name cannot be empty")
                return result
        ks = await get_knowledge_store()
        results = []
        ingest_results = await ks.ingest_documents(
            documents,
            ingest_timestamp=ingest_timestamp,
            solution=solution,
            collection=collection,
        )
        results = ingest_results.get("results", [])
        response = {"success": True, "results": results}
        if "total_page_count" in ingest_results:
            response["total_page_count"] = ingest_results["total_page_count"]
        logger.info(
            f"##### Ingest Document Job completed with {len(results)} results successfully! #####"
        )
        return response
    except Exception as e:
        if ctx:
            await ctx.error(f"💥 Document ingestion failed: {e}")
        logger.error(f"##### Ingest Document Job failed: {e} #####")
        return {"success": False, "error": f"Ingestion failed: {str(e)}", "results": []}


@mcp.tool()
async def search_knowledge(
    query: str, n_results: int = 5, collection: str = None, ctx: Context = None
) -> dict:
    """
    Search the ZMP knowledge store for relevant information.

    Args:
        query: Search query string
        n_results: Number of results to return (1-20, default: 5)
        collection: Target collection name. If not provided, uses default collection.
                   If collection doesn't exist, it will be created with same vector configs as existing collections.
        ctx: MCP context (internal use)
    """
    logger.info(
        f"[REQUEST] search_knowledge input: {json.dumps({'query': query, 'n_results': n_results}, ensure_ascii=False, indent=2)}"
    )
    try:
        if not query or not query.strip():
            result = {
                "success": False,
                "error": "Empty search query provided",
                "query": query,
                "results": [],
            }
            if ctx:
                await ctx.error("Empty search query provided")
            return result

        # Validate collection parameter
        if collection is not None:
            if not collection or not collection.strip():
                result = {
                    "success": False,
                    "error": "Collection name cannot be empty",
                    "query": query,
                    "results": [],
                }
                if ctx:
                    await ctx.error("Collection name cannot be empty")
                return result
        n_results = max(1, min(n_results, 20))
        ks = await get_knowledge_store()
        search_results = await ks.search_knowledge(
            query, n_results, collection=collection
        )

        if "error" in search_results:
            error_message = search_results.get(
                "error", "Search failed without a specific message."
            )
            result = {
                "success": False,
                "error": error_message,
                "query": query,
                "results": [],
            }
            if ctx:
                await ctx.error(error_message)
            return result

        results = search_results.get("results", [])
        return {"query": query, "results": results}
    except Exception as e:
        if ctx:
            await ctx.error(f"💥 Knowledge search failed: {e}")
        return {
            "success": False,
            "error": f"Search failed: {str(e)}",
            "query": query,
            "results": [],
        }


@mcp.tool()
async def log_chat_history(
    query: str,
    response: str,
    user_id: str = None,
    user_name: str = None,
    thread_id: str = None,
    doc_urls: list = None,
    citation_map: dict = None,
    ctx: Context = None,
) -> dict:
    """
    Log a user query and response pair to the chat_history collection in Qdrant.

    Args:
        query: The user's query
        response: The system's response
        user_id: Optional user identifier
        user_name: Optional user name/display name
        thread_id: Optional session identifier
        doc_urls: Optional list of document URLs referenced in the response
        citation_map: Optional dictionary mapping document IDs to citation information
    """
    logger.info(
        f"[REQUEST] log_chat_history input: {{'query': {query}, 'response': {response}, 'user_id': {user_id}, 'user_name': {user_name}, 'thread_id': {thread_id}, 'doc_urls': {doc_urls}, 'citation_map': {citation_map}}}"
    )
    try:
        if not query or not response:
            result = {
                "success": False,
                "error": "Both query and response are required",
                "query": query,
                "response": response,
            }
            if ctx:
                await ctx.error("Both query and response are required")
            return result
        timestamp = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        ks = await get_knowledge_store()
        record_id = await ks.log_chat_history(
            query,
            response,
            timestamp,
            user_id,
            user_name,
            thread_id,
            doc_urls,
            citation_map,
        )
        logger.info(f"✅ Chat history logged: {record_id}")
        return {"success": True, "id": record_id}
    except Exception as e:
        if ctx:
            await ctx.error(f"💥 Chat history logging failed: {e}")
        logger.error(f"##### Chat history logging failed: {e} #####")
        return {"success": False, "error": f"Chat history logging failed: {str(e)}"}


@mcp.tool()
async def search_chat_history(
    query: str, user_id: str = None, n_results: int = 5, ctx: Context = None
) -> dict:
    """
    Hybrid search for chat history records using dense+sparse vectors and optional user_id filter.

    Returns search results that include all fields from log_chat_history:
    - query, response, timestamp, user_id, thread_id
    - doc_urls: list of document URLs referenced in the response
    - citation_map: dictionary mapping document IDs to citation information
    """
    logger.info(
        f"[REQUEST] search_chat_history input: {{'query': {query}, 'user_id': {user_id}, 'n_results': {n_results}}}"
    )
    try:
        if not query or not query.strip():
            result = {
                "success": False,
                "error": "Empty search query provided",
                "query": query,
                "results": [],
            }
            if ctx:
                await ctx.error("Empty search query provided")
            return result
        n_results = max(1, min(n_results, 20))
        ks = await get_knowledge_store()
        search_results = await ks.search_chat_history(query, user_id, n_results)
        return {"query": query, "user_id": user_id, "results": search_results}
    except Exception as e:
        if ctx:
            await ctx.error(f"💥 Chat history search failed: {e}")
        return {
            "success": False,
            "error": f"Chat history search failed: {str(e)}",
            "query": query,
            "results": [],
        }


@mcp.tool()
async def list_threads(user_id: str, ctx: Context = None) -> dict:
    """
    List all unique thread IDs and their titles for a given user from chat history.

    Args:
        user_id: User ID to filter threads for
        ctx: MCP context (internal use)

    Returns:
        List of dictionaries with thread information:
        [{"thread_id": str, "thread_title": str}, ...]
    """
    logger.info(f"[REQUEST] list_threads input: {{'user_id': {user_id}}}")
    try:
        if not user_id or not user_id.strip():
            result = {
                "success": False,
                "error": "User ID is required",
                "threads": [],
            }
            if ctx:
                await ctx.error("User ID is required")
            return result

        ks = await get_knowledge_store()
        thread_tuples = await ks.list_threads(user_id)

        # Convert tuples to dictionaries for better JSON structure
        threads = [
            {"thread_id": thread_id, "thread_title": thread_title}
            for thread_id, thread_title in thread_tuples
        ]

        logger.info(f"✅ Found {len(threads)} threads for user_id: {user_id}")
        return {"user_id": user_id, "threads": threads}
    except Exception as e:
        if ctx:
            await ctx.error(f"💥 Thread listing failed: {e}")
        logger.error(f"##### Thread listing failed: {e} #####")
        return {
            "success": False,
            "error": f"Thread listing failed: {str(e)}",
            "user_id": user_id,
            "threads": [],
        }


@mcp.tool()
async def get_thread(user_id: str, thread_id: str, ctx: Context = None) -> dict:
    """
    Retrieve all chat records for a specific user_id and thread_id from chat history.

    Args:
        user_id: User ID to filter for
        thread_id: Specific thread ID to retrieve records for
        ctx: MCP context (internal use)

    Returns:
        List of dictionaries with chat record details:
        [{"thread_id": str, "thread_title": str, "query": str, "response": str,
          "timestamp": str, "doc_urls": list, "citation_map": dict}, ...]
    """
    logger.info(
        f"[REQUEST] get_thread input: {{'user_id': {user_id}, 'thread_id': {thread_id}}}"
    )
    try:
        if not user_id or not user_id.strip():
            result = {
                "success": False,
                "error": "User ID is required",
                "records": [],
            }
            if ctx:
                await ctx.error("User ID is required")
            return result

        if not thread_id or not thread_id.strip():
            result = {
                "success": False,
                "error": "Thread ID is required",
                "records": [],
            }
            if ctx:
                await ctx.error("Thread ID is required")
            return result

        ks = await get_knowledge_store()
        chat_records = await ks.get_thread(user_id, thread_id)

        logger.info(
            f"✅ Found {len(chat_records)} chat records in thread {thread_id} for user_id: {user_id}"
        )
        return {"user_id": user_id, "thread_id": thread_id, "records": chat_records}
    except Exception as e:
        if ctx:
            await ctx.error(f"💥 Get thread failed: {e}")
        logger.error(f"##### Get thread failed: {e} #####")
        return {
            "success": False,
            "error": f"Get thread failed: {str(e)}",
            "user_id": user_id,
            "thread_id": thread_id,
            "records": [],
        }


# Main execution
async def main() -> None:
    """Initializes the knowledge store and runs the MCP server."""
    logger.info("🚀 Starting ZMP Knowledge Store MCP Server...")
    logger.info(
        "📋 Available tools: ingest_documents, search_knowledge, log_chat_history, search_chat_history, list_threads, get_thread"
    )
    logger.info(
        f"⚙️  Configuration: {Config.SERVER_HOST}:{Config.SERVER_PORT} (for reference)"
    )

    # Initialize knowledge store at startup
    logger.info("🔄 Initializing knowledge store...")
    await get_knowledge_store()
    logger.info("✅ Knowledge store initialized successfully.")

    # The `run_async` method should be used within an async context.
    await mcp.run_async(
        transport="streamable-http",
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        log_level=Config.LOG_LEVEL,
    )


if __name__ == "__main__":
    asyncio.run(main())
