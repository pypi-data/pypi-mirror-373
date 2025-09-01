import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from .keyword_extractor import KeywordExtractor
import uuid
import json
from docling_core.types.doc.document import DoclingDocument
from docling_core.types.doc.document import DocTagsDocument
from PIL import Image
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)

logger = logging.getLogger(__name__)

# Shared keyword extractor registry
KEYWORD_EXTRACTORS = {
    "zcp": KeywordExtractor("zcp"),
    "amdp": KeywordExtractor("amdp"),
    "apim": KeywordExtractor("apim"),
    "general": KeywordExtractor(),
}


def extract_keywords_auto(
    content: str,
    solution: str,
    keyword_extractors: Dict[str, KeywordExtractor] = None,
) -> List[str]:
    """Automatically extract keywords using the appropriate extractor."""
    if keyword_extractors is None:
        keyword_extractors = KEYWORD_EXTRACTORS
    try:
        extractor = keyword_extractors.get(
            (solution or "").lower(), keyword_extractors["general"]
        )
        keywords = extractor.extract_keywords(content)
        logger.info(f"Extracted {len(keywords)} keywords for {solution}: {keywords}")
        return keywords
    except Exception as e:
        logger.warning(f"Keyword extraction failed for {solution}: {e}")
        return []


def prepare_metadata(
    solution=None,
    page_title=None,
    page_no=None,
    chunk_order=None,
    content=None,
    doc_url=None,
    manual_keywords=None,
    embedded_images=None,
    assets_s3_keys=None,
    chunk_type=None,
    created_at=None,
    updated_at=None,
    keyword_extractors=None,
) -> Dict[str, Any]:
    """Prepare comprehensive metadata with auto keyword extraction and optional structured OCR/image data and S3 URLs. Requires solution as a positional argument. Excludes doctags_raw and doctags_markdown."""
    # If manual_keywords are provided, they are considered definitive.
    if manual_keywords is not None:
        auto_keywords = []
    else:
        # Special handling for frontmatter: only extract keywords from title
        if chunk_type in ("frontmatter", "front_matter"):
            title_for_keywords = page_title or ""
            auto_keywords = extract_keywords_auto(
                title_for_keywords, solution, keyword_extractors
            )
        else:
            auto_keywords = extract_keywords_auto(content, solution, keyword_extractors)

    # Combine manual and auto keywords
    all_keywords = list(set((manual_keywords or []) + auto_keywords))
    # Sort all_keywords for deterministic order
    all_keywords = sorted(all_keywords)
    # If keywords is a list, convert to comma-separated string
    if isinstance(all_keywords, list):
        keywords_value = ", ".join(str(x) for x in all_keywords)
    else:
        keywords_value = str(all_keywords)
    now = datetime.now(timezone.utc).isoformat()
    # Sort assets_s3_keys and embedded_images if present
    if assets_s3_keys and isinstance(assets_s3_keys, list):
        assets_s3_keys = sorted(assets_s3_keys)
    if embedded_images and isinstance(embedded_images, list):
        embedded_images = sorted(embedded_images)
    # Sort manual_keywords if present
    if manual_keywords and isinstance(manual_keywords, list):
        manual_keywords = sorted(manual_keywords)
    metadata = {
        "solution": solution,
        "page_title": page_title,
        "page_no": page_no,
        "chunk_order": chunk_order,
        "content": content,
        "doc_url": doc_url,
        "manual_keywords": manual_keywords,
        "embedded_images": embedded_images,
        "chunk_type": chunk_type,
        "created_at": created_at or now,
        "updated_at": updated_at or now,
        "keywords": keywords_value,
        "content_length": len(content) if content else 0,
        "word_count": len(content.split()) if content else 0,
        "keyword_count": len(all_keywords) if isinstance(all_keywords, list) else 1,
    }
    # Only include assets_s3_keys if provided
    if assets_s3_keys:
        metadata["assets_s3_keys"] = assets_s3_keys
    # Remove None values
    metadata = {k: v for k, v in metadata.items() if v is not None}
    # Remove keys with None, empty string, or empty list values
    for k in list(metadata.keys()):
        if (
            metadata[k] is None
            or (isinstance(metadata[k], str) and metadata[k].strip() == "")
            or (isinstance(metadata[k], list) and len(metadata[k]) == 0)
        ):
            logger.info(
                f"Removing metadata field '{k}' because it is None, empty string, or empty list."
            )
            del metadata[k]
    # Convert all list-type metadata fields to comma-delimited strings (after sorting above)
    for k, v in list(metadata.items()):
        if isinstance(v, list):
            logger.info(
                f"Converting metadata field '{k}' from list to comma-delimited string: {v}"
            )
            metadata[k] = ", ".join(str(x) for x in v)
    # Move 'solution' to the top of the dict
    if "solution" in metadata:
        solution_value = metadata.pop("solution")
        metadata = {"solution": solution_value, **metadata}
    return metadata


def create_document_id(content: str, metadata: dict) -> str:
    """
    Creates a deterministic UUIDv5 document ID from content and metadata.
    Excludes created_at and updated_at from the hash.
    For chat history deduplication, pass content='chat_history' and metadata={'query': ..., 'user_id': ... (optional)}.
    """
    m = metadata.copy()
    m.pop("created_at", None)
    m.pop("updated_at", None)

    # Use a specific namespace for our document IDs
    namespace = uuid.UUID("3c1a8459-2713-4e4f-8f8b-1e2b3c4d5e6f")

    # Serialize content and metadata to a stable string
    # Use repr() for content to handle all characters, and sort keys in metadata
    data_string = repr(content) + json.dumps(m, sort_keys=True, ensure_ascii=False)

    # Generate UUIDv5
    doc_id = uuid.uuid5(namespace, data_string)
    return str(doc_id)


def export_markdown(doctags_markup, images) -> str:
    """
    Parse DocTags markup and export as Markdown using DocTagsDocument and export_to_markdown().
    Args:
        doctags_markup (str): The raw doctags XML/markup string.
        images (list): List of PIL.Image.Image objects corresponding to pages.
    Returns:
        str: Markdown representation of the document.
    """

    logger = logging.getLogger("zmp-knowledge-store")
    if DocTagsDocument is None:
        raise ImportError(
            "DocTagsDocument is not available. Please install docling_core."
        )
    logger.info(f"[ExportMarkdown] DocTags markup (full): {doctags_markup}")
    for idx, img in enumerate(images):
        logger.info(f"[ExportMarkdown] Image {idx}: type={type(img)}")
        try:
            if isinstance(img, Image.Image):
                logger.info(
                    f"[ExportMarkdown] Image {idx}: size={img.size}, mode={img.mode}"
                )
        except ImportError:
            pass
    try:
        doctags_doc = create_doctags_document(doctags_markup, images)

        docling_doc = DoclingDocument(name="ExportedDocument")
        doc = docling_doc.load_from_doctags(doctags_doc)
        md = doc.export_to_markdown()
        logger.info(f"[ExportMarkdown] Markdown output length: {len(md)}")
        return md
    except Exception as e:
        logger.error(f"create_doctags_document failed: {e}")
        logger.error(f"Full doctags_markup: {doctags_markup}")
        raise


def create_doctags_document(doctags_markup, images) -> DocTagsDocument:
    """
    Centralized wrapper for DocTagsDocument.from_doctags_and_image_pairs.
    Handles logging and error handling.
    """

    import logging

    logger = logging.getLogger("zmp-knowledge-store")
    try:
        doc = DocTagsDocument.from_doctags_and_image_pairs([doctags_markup], images)
        logger.info("[DocTags] Successfully created DocTagsDocument.")
        return doc
    except Exception as e:
        logger.error(f"DocTagsDocument.from_doctags_and_image_pairs failed: {e}")
        logger.error(f"Full doctags_markup: {doctags_markup}")
        raise


def download_image_from_s3(s3_client, bucket_name, s3_key, local_path) -> bool:
    """
    Download an image from S3 to a local file using the given S3 key.
    Args:
        s3_client: boto3 S3 client
        bucket_name: S3 bucket name
        s3_key: S3 object key (e.g., 'assets/image.png')
        local_path: Path to save the downloaded image
    Returns:
        True if download succeeds, False otherwise
    """
    try:
        s3_client.download_file(bucket_name, s3_key, local_path)
        logging.info(
            f"Downloaded image from S3: s3://{bucket_name}/{s3_key} -> {local_path}"
        )
        return True
    except Exception as e:
        logging.error(
            f"Failed to download image from S3: s3://{bucket_name}/{s3_key} -> {local_path}: {e}"
        )
        return False


# =====================
# Chunking Utilities
# =====================
def chunk_documents_character(docs, chunk_size: int, chunk_overlap: int) -> List[Any]:
    """
    Split documents into chunks using CharacterTextSplitter.
    This is the default splitter for current ingestion.
    """
    if chunk_overlap >= chunk_size:
        raise ValueError("Chunk overlap must be smaller than chunk size.")
    splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(docs)


def chunk_documents_recursive(docs, chunk_size: int, chunk_overlap: int) -> List[Any]:
    """
    Split documents into chunks using RecursiveCharacterTextSplitter.
    Use this for future graph DB ingestion or more robust chunking.
    """
    if chunk_overlap >= chunk_size:
        raise ValueError("Chunk overlap must be smaller than chunk size.")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(docs)
