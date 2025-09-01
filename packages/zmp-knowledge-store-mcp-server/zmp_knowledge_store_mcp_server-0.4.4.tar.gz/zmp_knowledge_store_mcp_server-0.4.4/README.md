# ZMP Knowledge Store MCP Server

![Platform Badge](https://img.shields.io/badge/platform-zmp-red)
![Component Badge](https://img.shields.io/badge/component-knowledge_store_mcp_server-red)
![CI Badge](https://img.shields.io/badge/ci-github_action-green)
![License Badge](https://img.shields.io/badge/license-MIT-green)
![Version Badge](https://img.shields.io/badge/version-0.3.9.2-blue)

A high-performance MCP (Model Context Protocol) server for managing knowledge store content with multi-modal RAG capabilities, powered by Qdrant vector store with hybrid search, chat history logging, configurable collections, and advanced image analysis features.

**Latest Version: 0.3.9.2** - Enhanced with PyTorch security fixes, manual RRF implementation, and optimized Docker builds.

---

## Recent Updates (v0.3.9.2)

### 🔒 Security & Compatibility Fixes
- **PyTorch Security**: Upgraded to PyTorch 2.6.0+cpu to resolve CVE-2025-32434 vulnerability
- **Torchvision Compatibility**: Fixed torchvision 0.21.0+cpu compatibility with CPU-only PyTorch
- **NumPy/SciPy Stability**: Resolved compatibility issues with Python 3.12 and ML dependencies

### 🚀 Performance Improvements
- **Manual RRF Implementation**: Replaced `ranx` dependency with custom Reciprocal Rank Fusion (RRF) implementation
- **Docker Optimizations**: CPU-only PyTorch builds for faster deployment and smaller images
- **Network Resilience**: Enhanced SSL handling and timeout configurations for reliable builds

### 🐛 Bug Fixes
- **Startup Warnings**: Removed `get_collection_stats` warning for cleaner startup logs
- **Dependency Management**: Improved Poetry + pip hybrid installation strategy
- **Error Handling**: Enhanced error handling and logging throughout the application

---

## Python File Structure

```
zmp_knowledge_store/
├── __init__.py              # Package initialization & metadata
├── config.py                # Configuration management with S3 integration
├── knowledge_store.py       # Main knowledge store logic (ingestion, search, multi-modal RAG)
├── qdrant_adapter.py        # Qdrant vector DB integration with hybrid search & manual RRF
├── keyword_extractor.py     # Advanced keyword extraction
├── utils.py                 # Utility functions
├── server_main.py           # FastMCP server main entry point

tests/
├── test_client.py           # MCP client integration tests
├── test_hybrid_search.py    # Hybrid search validation
├── test_collection_*.py     # Configurable collection tests
├── test_*_chat_history.py   # Chat history logging and retrieval tests
├── enhance_pictures.py      # Image enhancement and vision model tests
├── analyze_*.py             # Image analysis and validation scripts
└── ...                      # Other tests and utilities (80+ files)

examples/
├── zcp/                     # ZCP (CloudZ Container Platform) documentation
├── amdp/                    # AMDP (Application Modernization & Development Platform) docs
├── apim/                    # APIM (API Management) documentation
└── assets/                  # Shared assets and images
```

---

## Key Features

### 1. Multi-Modal Knowledge Store (`knowledge_store.py`)
- Handles ingestion, chunking, and search for multi-modal documentation (text + images)
- Powered by Qdrant vector store with hybrid search (dense + sparse vectors)
- SmolDocling integration for document parsing and layout understanding
- Advanced image analysis with vision language model integration
- Automatic image description generation and enhancement
- Configurable collections for multi-tenant knowledge organization
- Robust metadata enrichment and error handling

### 2. Hybrid Search with Manual RRF (`qdrant_adapter.py`)
- **Custom RRF Implementation**: Manual Reciprocal Rank Fusion algorithm for optimal search results
- **Dense + Sparse Vectors**: Combines semantic similarity with keyword-based search
- **No External Dependencies**: Self-contained RRF implementation without `ranx` dependency
- **Configurable Parameters**: Adjustable RRF constant (k=60) for different use cases

### 3. Chat History Management
- Chat history logging with deduplication
- Hybrid search over chat history with clustering and semantic similarity
- User and session-based filtering
- Analytics and debugging support

### 4. Qdrant Vector Store Integration
- `qdrant_adapter.py`: Advanced Qdrant integration with hybrid search (dense + sparse vectors)
- Dynamic collection creation and management with configurable parameters
- Template-based collection creation with automatic vector configuration inheritance
- Comprehensive metadata filtering and upsert operations

### 5. Advanced Text Processing
- `keyword_extractor.py`: Multi-method keyword extraction (KeyBERT, spaCy, NLTK)
- Solution-specific optimization for ZCP, AMDP, and APIM platforms
- Adaptive keyword counts and domain vocabulary boosting

### 6. Configuration & Utilities
- `config.py`: Environment-based configuration with S3 integration
- `utils.py`: Chunking, document creation, and helper functions
- `server_main.py`: FastMCP server with tool endpoints

### 7. Enhanced Image Analysis
- Vision language model integration for automatic image description generation
- MDX image validation and enhanced asset mapping
- Automatic image enhancement during document ingestion
- SmolDocling integration for picture detection and processing
- S3 integration for image asset management

### 8. Comprehensive Testing
- 80+ test files and analysis scripts covering all functionality
- Configurable collection parameter validation
- Hybrid search and image analysis testing
- Multi-platform compatibility testing

---

## MCP Tools Implemented

| Tool Name           | Request Schema                | Response Schema                        | Description |
|---------------------|------------------------------|----------------------------------------|-------------|
| ingest_documents    | `{documents: list, solution?: str, collection?: str}`   | `{ success: bool, results: list, total_page_count?: int }`              | Ingest documents with metadata, keyword extraction, and automatic image enhancement. Supports configurable collections. |
| search_knowledge    | `{query: str, n_results?: int, collection?: str}`       | `{ query: str, results: list }`    | Hybrid search (dense + sparse) over the knowledge store. Supports configurable collections with auto-creation. |
| log_chat_history    | `{query: str, response: str, user_id?: str, session_id?: str}` | `{ success: bool, id?: str, error?: str }` | Log query/response pairs with deduplication by (query, user_id). |
| search_chat_history | `{query: str, user_id?: str, n_results?: int}` | `{ query: str, user_id?: str, results: list }` | Hybrid search over chat history with optional user filtering. |

---

## Usage Examples

```python
# Ingest documents (see examples/ for sample MDX and images)
result = await client.call_tool("ingest_documents", {
    "documents": [...],
    "solution": "zcp",
    "collection": "my-custom-collection"  # Optional: auto-creates if not exists
})

# Search knowledge
result = await client.call_tool("search_knowledge", {
    "query": "Group Management",
    "n_results": 3,
    "collection": "my-custom-collection"  # Optional: defaults to solution-docs
})

# Log chat history
result = await client.call_tool("log_chat_history", {
    "query": "What is a group?",
    "response": "A group is ...",
    "user_id": "user1"
})

# Search chat history
result = await client.call_tool("search_chat_history", {
    "query": "Delete a group",
    "n_results": 5
})
```

---

## Example Documentation Sets

- `examples/zcp/`: CloudZ Container Platform documentation with tutorials and guides
- `examples/amdp/`: Application Modernization & Development Platform documentation
- `examples/apim/`: API Management platform documentation and tutorials
- Each directory contains MDX files with embedded images and comprehensive documentation

---

---

## Document Processing Pipeline

### Supported File Types and Processing Methods

The ZMP Knowledge Store supports multiple input formats with specialized processing for each type:

#### 1. MDX Files (`.md`, `.mdx`) - Primary Format
**Pipeline**: MDX → PDF → Images → SmolDocling → Chunks → Vector Store

**Processing Steps**:
1. **Frontmatter Extraction**: YAML frontmatter parsed for metadata (title, solution, keywords)
2. **Asset Resolution**: Referenced images downloaded from S3 and mapped to local paths
3. **PDF Conversion**: Pandoc converts MDX to PDF using XeLaTeX engine with Noto Sans Symbols font
4. **Page Rendering**: PDF converted to individual PNG images using pdf2image
5. **SmolDocling Analysis**: Each page processed by vision-language model for layout understanding
6. **Element Extraction**: Text, tables, images, and structure extracted with page numbers
7. **Content Validation**: OCR output validated against original MDX for accuracy correction
8. **Chunking**: Elements grouped and split using character-based chunking (1024 chars, 128 overlap)
9. **Embedding**: Dense (all-mpnet-base-v2) + sparse (SPLADE) vectors computed
10. **Storage**: Chunks stored in Qdrant with metadata and S3 image references

**SmolDocling Backend Selection**:
- **MLX Backend** (`SMOLDOCLING_BACKEND=mlx`): Apple Silicon optimized, uses `ds4sd/SmolDocling-256M-preview-mlx-bf16`
- **Transformers Backend** (`SMOLDOCLING_BACKEND=transformers`): Cross-platform, uses `ds4sd/SmolDocling-256M-preview`
- **Auto-Detection** (`SMOLDOCLING_BACKEND=auto`): Platform-based selection (default)

#### 2. PDF Files (`.pdf`) - Direct Processing
**Pipeline**: PDF → Images → SmolDocling → Chunks → Vector Store

**Processing Steps**:
1. **Page Extraction**: PDF pages converted directly to PNG images
2. **SmolDocling Analysis**: Same vision-language processing as MDX pipeline
3. **Element Processing**: Text, tables, images extracted with page metadata
4. **Chunking & Storage**: Same as MDX pipeline without MDX validation

#### 3. Image Files (`.png`, `.jpg`, `.jpeg`) - Single Page
**Pipeline**: Image → SmolDocling → Chunks → Vector Store

**Processing Steps**:
1. **Image Loading**: Single image loaded as PIL Image object
2. **SmolDocling Processing**: Vision-language model extracts content and structure
3. **Element Extraction**: All content treated as single page (page_no=1)
4. **Chunking & Storage**: Standard pipeline for extracted elements

### Element Types and Processing

#### Text Elements
- **Types**: `text`, `paragraph`, `heading`, `title`
- **Processing**: Direct text extraction with markdown formatting preservation
- **Chunking**: Character-based splitting with semantic boundaries
- **Metadata**: Page number, chunk order, content type

#### Table Elements  
- **Type**: `table`, `otsl` (Open Table Schema Language)
- **Processing**: OTSL serialized to markdown format for better searchability
- **Fallback**: Raw OTSL XML if markdown serialization fails
- **Enhancement**: Caption grouping with adjacent caption elements

#### Image Elements
- **Type**: `picture`
- **Processing**: Mapped to S3 URLs from asset metadata
- **Validation**: MDX image references validated against detected pictures
- **Format**: Markdown image syntax `![caption](s3_url)`
- **Metadata**: S3 keys stored in `assets_s3_keys` field

#### List Elements
- **Types**: `list_item`, `unordered_list`, `ordered_list`
- **Processing**: Items grouped and buffered until size threshold
- **Chunking**: Multiple list items combined into single chunks (up to 1024 chars)
- **Structure**: Nested lists flattened with proper indentation

### Advanced Processing Features

#### Image Reference Validation
```python
# Extract ordered image references from MDX
image_refs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", content)

# Map to S3 keys and validate against SmolDocling detection
ordered_image_ref_to_s3 = []
for ref in image_refs:
    # Match with asset metadata and S3 keys
    # Track assignment to prevent false positives
```

#### Content Correction Pipeline
```python
def word_level_correction(chunk, mdx):
    """Correct OCR hallucinations using original MDX content"""
    mdx_words = set(mdx.split())
    chunk_words = chunk.split()
    corrected_words = []
    for word in chunk_words:
        # Find exact matches or closest alternatives
        if any(word.lower() == w.lower() for w in mdx_words):
            corrected_words.append(word)
        else:
            matches = difflib.get_close_matches(word, mdx_words, n=1, cutoff=0.8)
            corrected_words.append(matches[0] if matches else word)
    return " ".join(corrected_words)
```

#### Hybrid Vector Embeddings
- **Dense Vectors**: 768-dimensional using `sentence-transformers/all-mpnet-base-v2`
- **Sparse Vectors**: SPLADE-based with separate document and query models:
  - Document: `naver/efficient-splade-VI-BT-large-doc`
  - Query: `naver/efficient-splade-VI-BT-large-query`
- **Fusion**: Manual RRF (Reciprocal Rank Fusion) with k=60 constant

### Error Handling and Fallbacks

#### SmolDocling Model Loading
- **Failure Handling**: Graceful degradation with disabled OCR functionality
- **Backend Switching**: Auto-fallback from MLX to Transformers on compatibility issues
- **Retry Logic**: Multiple prompt attempts for DocTags extraction

#### Asset Management
- **S3 Download**: Automatic retry with error logging
- **Local Caching**: Images cached in timestamped temp directories
- **Cleanup**: Temp files removed after processing (configurable by LOG_LEVEL)

#### Content Validation
- **MDX Validation**: OCR output compared against source content
- **Image Mapping**: False positive detection for picture elements
- **Metadata Preservation**: Page numbers and structure maintained throughout pipeline

---

## Running the Tests

The project includes 80+ comprehensive tests and analysis scripts:

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_client.py                # MCP client integration tests
pytest tests/test_hybrid_search.py         # Hybrid search validation
pytest tests/test_collection_*.py          # Configurable collection tests
pytest tests/test_*_chat_history.py        # Chat history tests

# Run image analysis scripts
python tests/enhance_pictures.py           # Image enhancement validation
python tests/analyze_*.py                  # Various analysis scripts
```

Key test files:
- `test_client.py`: MCP client integration and tool validation
- `test_hybrid_search.py`: Qdrant hybrid search functionality
- `test_collection_*.py`: Configurable collection parameter testing
- `test_*_chat_history.py`: Chat history logging and retrieval
- `enhance_pictures.py`: Vision model and image enhancement validation
- `analyze_*.py`: Image analysis and validation scripts

---

## Configurable Collections

The MCP server supports configurable collections for multi-tenant knowledge organization:

- **Auto-Creation**: Collections are automatically created when specified if they don't exist
- **Template-Based**: New collections inherit vector configurations from existing collections
- **Backward Compatibility**: Tools work without collection parameter (defaults to "solution-docs")
- **Collection Parameter**: Optional `collection` parameter available for `ingest_documents` and `search_knowledge`

---

## Platform Compatibility & Configuration

### SmolDocling Backend Selection
Controlled by the `SMOLDOCLING_BACKEND` environment variable:
- `mlx`: MLX backend (Apple Silicon optimized)
- `transformers`: HuggingFace Transformers backend (cross-platform)
- `auto`: Auto-select based on platform (recommended)

### Vision Model Integration
- Supports vision language models for automatic image description generation
- Uses transformers library with vision models for AI-generated descriptions
- Fallback mechanisms when vision models are unavailable

### Vector Store Configuration
- Qdrant: High-performance hybrid search with dense + sparse vectors
- Dynamic collection management with configurable parameters
- Template-based collection creation and automatic configuration inheritance
- Advanced metadata filtering and semantic search capabilities

---

## Environment Configuration

Key environment variables (set in `.env` file):

```bash
# Vector Store Configuration
QDRANT_URL=http://localhost:6333
DOCUMENT_COLLECTION=solution-docs

# Model Configuration
SMOLDOCLING_BACKEND=auto  # auto, mlx, or transformers
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# S3 Configuration (for asset storage)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_bucket_name

# Server Configuration
PORT=5371
HOST=0.0.0.0
```

---

## Installation & Deployment

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd zmp-knowledge-store-mcp-server

# Install dependencies with Poetry
poetry install

# Or install with pip
pip install -e .
```

### Running the Server

```bash
# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the FastMCP server
python zmp_knowledge_store/server_main.py
```

### Docker Deployment

**Optimized Docker build with CPU-only PyTorch for faster builds and smaller images:**

```bash
# Build Docker image (optimized for production)
docker build -t zmp-knowledge-store-mcp-server .

# Run with Docker
docker run -p 5371:5371 --env-file .env zmp-knowledge-store-mcp-server

# Build and push (for CI/CD)
./k8s/build-and-push.sh
```

**Build Optimizations:**
- **CPU-only PyTorch**: PyTorch 2.6.0+cpu and torchvision 0.21.0+cpu for security and compatibility
- **Multi-stage build**: Smaller production images with optimized layers
- **SSL certificate handling**: Secure package downloads with trusted hosts
- **Network resilience**: Enhanced timeout and retry configurations
- **Manual RRF**: Self-contained hybrid search without external dependencies

**Security Features:**
- **PyTorch 2.6.0+**: Resolves CVE-2025-32434 security vulnerability
- **CPU-only builds**: Eliminates CUDA dependencies for faster, more secure deployments
- **Comprehensive error handling**: Robust error handling and logging throughout

---

## Version History

### v0.3.9.2 (Latest)
- ✅ **Security Fix**: PyTorch upgraded to 2.6.0+cpu (CVE-2025-32434)
- ✅ **Compatibility**: Torchvision 0.21.0+cpu compatibility
- ✅ **Performance**: Manual RRF implementation (no `ranx` dependency)
- ✅ **Cleanup**: Removed `get_collection_stats` warning
- ✅ **Optimization**: Enhanced Docker build with CPU-only ML stack

### v0.3.9.1
- ✅ **Security**: Initial PyTorch security vulnerability fixes
- ✅ **Compatibility**: NumPy/SciPy compatibility improvements
- ✅ **Stability**: Enhanced error handling and logging

### v0.3.0
- ✅ **Features**: Configurable collections and enhanced search
- ✅ **Performance**: Optimized hybrid search implementation

### v0.2.9
- ✅ **Foundation**: Initial release with core MCP server functionality
