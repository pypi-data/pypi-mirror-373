"""
Configuration management for zmp-knowledge-store-mcp-server

Handles environment variables and application settings
"""

import os

# Load environment variables early to ensure they're available for configuration
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


class Config:
    """Configuration management for the knowledge store"""

    # Server configuration
    SERVER_NAME = "zmp-knowledge-store-mcp-server"
    SERVER_VERSION = "1.0.0"
    SERVER_HOST = os.getenv("HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("PORT", "5371"))

    CLUSTER_MODE = os.getenv("ZMP_CLUSTER_MODE", "true").lower() == "true"

    # Qdrant configuration
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT_RAW = os.getenv("QDRANT_PORT", "6333")
    # Handle case where QDRANT_PORT might be a full URL like "tcp://172.20.231.180:6333"
    if "://" in QDRANT_PORT_RAW:
        # Extract port from URL like "tcp://172.20.231.180:6333"
        QDRANT_PORT = int(QDRANT_PORT_RAW.split(":")[-1])
    else:
        QDRANT_PORT = int(QDRANT_PORT_RAW)
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_URL = os.getenv("QDRANT_URL", f"http://{QDRANT_HOST}:{QDRANT_PORT}")

    # Collection configuration
    DOCUMENT_COLLECTION = os.getenv("DOCUMENT_COLLECTION", "solution-docs")
    CHAT_HISTORY_COLLECTION = os.getenv("CHAT_HISTORY_COLLECTION", "chat-history")

    COLLECTION = DOCUMENT_COLLECTION  # For backward compatibility

    # Supported values
    SOLUTIONS = ["zcp", "amdp", "apim"]

    # Search configuration
    DEFAULT_RESULTS = 5
    MAX_RESULTS = 20

    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    # S3 configuration
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "zmp-ai-knowledge-store")

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        # No required configuration validation needed currently
        return True

    @classmethod
    def get_server_config(cls) -> dict:
        """Get server configuration"""
        return {
            "name": cls.SERVER_NAME,
            "version": cls.SERVER_VERSION,
            "host": cls.SERVER_HOST,
            "port": cls.SERVER_PORT,
        }

    @classmethod
    def get_s3_config(cls) -> dict:
        """Get S3 configuration"""
        return {
            "aws_access_key_id": cls.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": cls.AWS_SECRET_ACCESS_KEY,
            "region_name": cls.AWS_REGION,
            "bucket_name": cls.S3_BUCKET_NAME,
        }

    @classmethod
    def is_solution_valid(cls, solution: str) -> bool:
        """Check if solution is valid"""
        return solution.lower() in cls.SOLUTIONS
