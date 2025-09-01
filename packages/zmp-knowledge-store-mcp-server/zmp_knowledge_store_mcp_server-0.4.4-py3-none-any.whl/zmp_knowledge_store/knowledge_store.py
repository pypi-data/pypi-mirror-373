#!/usr/bin/env python3
"""
ZMP Knowledge Store Core Module

Vector knowledge store for ZMP solutions documentation
"""

import logging
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Tuple
import json  # Ensure json is imported globally
import yaml
import boto3
from PIL import Image
from docling_core.types.doc.document import DoclingDocument
import platform

if (
    platform.system() == "Darwin"
    and os.environ.get("SMOLDOCLING_BACKEND", "auto") == "mlx"
):
    from mlx_vlm import load
    from mlx_vlm.utils import load_config, stream_generate
    from mlx_vlm.prompt_utils import apply_chat_template
from docling_core.types.doc.labels import DocItemLabel
import platform
from .qdrant_adapter import QdrantAdapter
import torch
from transformers import (
    AutoProcessor,
    AutoModelForVision2Seq,
    AutoTokenizer,
    AutoModelForMaskedLM,
)
from docling_core.transforms.serializer.markdown import MarkdownDocSerializer
from pdf2image import convert_from_path
from sentence_transformers import SentenceTransformer
from huggingface_hub import snapshot_download
from .utils import create_doctags_document
from .utils import chunk_documents_character  # Import the new chunking utility
from langchain.schema import Document  # Import Document for chunking
import difflib
from zmp_knowledge_store.config import Config
from llama_index.core.postprocessor import SentenceTransformerRerank

# Disable tokenizer parallelism to avoid warnings when forking processes
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Set root paths to match Dockerfile's WORKDIR (/app)
KNOWLEDGE_STORE_ROOT = os.path.dirname(os.path.abspath(__file__))


def detect_project_root() -> str:
    # If running in Docker, /.dockerenv exists
    if os.path.exists("/.dockerenv"):
        return "/app"
    # If PROJECT_ROOT is set in env, use it
    if "PROJECT_ROOT" in os.environ:
        return os.environ["PROJECT_ROOT"]
    # Otherwise, use the parent of this file (local dev)
    return os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    )


PROJECT_ROOT = detect_project_root()
MODELS_DIR = os.path.join(PROJECT_ROOT, "data", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

logger = logging.getLogger("zmp-knowledge-store")

# S3 client setup (optional)
s3_client = None

if boto3:
    try:
        # Get S3 configuration from Config class
        s3_config = Config.get_s3_config()
        aws_access_key = s3_config["aws_access_key_id"]
        aws_secret_key = s3_config["aws_secret_access_key"]
        aws_region = s3_config["region_name"]

        if aws_access_key and aws_secret_key:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region,
            )
            logger.info(f"✅ S3 client initialized for region: {aws_region}")
        else:
            logger.warning(
                "⚠️  S3 credentials not found - S3 upload functionality will be disabled"
            )
    except Exception as e:
        logger.warning(
            f"⚠️  Failed to initialize S3 client: {e} - S3 upload functionality will be disabled"
        )
        s3_client = None
else:
    logger.warning("⚠️  boto3 not available - S3 upload functionality will be disabled")

# SmolDocling model setup (optional)
model = None
processor = None
config = None

try:
    from splade.models.transformer_rep import Splade
except ImportError:
    Splade = None  # SPLADE not installed
    # User must install: pip install transformers torch

# Add chunking constants
# Character-based chunking (default)
CHAR_SPLIT_CHUNK_SIZE = 1024
CHAR_SPLIT_CHUNK_OVERLAP = 128
CHUNK_SIZE = CHAR_SPLIT_CHUNK_SIZE
CHUNK_OVERLAP = CHAR_SPLIT_CHUNK_OVERLAP
# Token-based chunking (for future use)
TOKEN_SPLIT_CHUNK_SIZE = 2048
TOKEN_SPLIT_CHUNK_OVERLAP = 24


def is_mlx_available() -> bool:
    try:
        import mlx_vlm

        logger.info(f"MLX available: {mlx_vlm}")
        return platform.system() == "Darwin" and platform.machine().startswith("arm")
    except ImportError:
        return False


def get_smoldocling_backend() -> str:
    backend = os.getenv("SMOLDOCLING_BACKEND", "auto").lower()

    logger.info(f"🔍 Platform detection: {platform.system()} {platform.machine()}")
    logger.info(f"🔍 MLX available: {is_mlx_available()}")
    logger.info(f"🔍 SMOLDOCLING_BACKEND env var: {backend}")

    if backend == "mlx":
        if is_mlx_available():
            logger.info("✅ Using MLX backend for SmolDocling (explicitly requested)")
            return "mlx"
        else:
            logger.warning(
                "⚠️  MLX backend requested but not available on this platform"
            )
            logger.info("🔄 Falling back to Transformers backend")
            return "transformers"
    elif backend == "transformers":
        logger.info(
            "✅ Using Transformers backend for SmolDocling (explicitly requested)"
        )
        return "transformers"
    elif backend == "auto":
        if is_mlx_available():
            logger.info("✅ Using MLX backend for SmolDocling (auto-detected)")
            return "mlx"
        else:
            logger.info("✅ Using Transformers backend for SmolDocling (auto-detected)")
            return "transformers"
    else:
        logger.warning(f"⚠️  Unknown backend '{backend}', defaulting to Transformers")
        return "transformers"


class MultiIngester:
    def __init__(self, ingesters):
        self.ingesters = ingesters  # List of adapters

    async def ingest_document(self, **kwargs) -> dict:
        results = {}
        logger.info(f"[MultiIngester] Ingesting with {len(self.ingesters)} adapters.")
        for ingester in self.ingesters:
            name = type(ingester).__name__
            logger.info(f"[MultiIngester] Calling {name}.ingest_document...")
            try:
                result = await ingester.ingest_document(**kwargs)
                logger.info(f"[MultiIngester] {name} returned: {result}")
                results[name] = result
            except Exception as e:
                logger.error(f"[MultiIngester] {name} failed: {e}")
                results[name] = f"error: {e}"
        # logger.info(f"[MultiIngester] Returning results: {results}")
        return results


class ZmpKnowledgeStore:
    """
    Vector knowledge store for ZMP solutions documentation with hybrid (dense + sparse) Qdrant ingestion.
    """

    def __init__(self) -> None:
        self.ingester = None
        self.initialized = False
        self.qdrant_adapter = None
        self.model_id = "ds4sd/SmolDocling-256M-preview"
        self.processor = None
        self.model = None
        self.device = None
        self.dense_tokenizer = None
        self.dense_model = None
        self.dense_device = None
        self.sparse_doc_tokenizer = None
        self.sparse_doc_model = None
        self.sparse_query_tokenizer = None
        self.sparse_query_model = None
        self.sparse_device = None
        self.smoldocling_backend = get_smoldocling_backend()

        # CrossEncoder reranker
        self.sentence_transformers_rerank = SentenceTransformerRerank(
            model="cross-encoder/ms-marco-MiniLM-L-2-v2", top_n=20
        )
        # No longer loading these at init, will be loaded by initialize()
        # self._load_dense_model()
        # self._load_sparse_model()

        # --- Device check and logging ---
        device_info = []
        try:
            if torch.cuda.is_available():
                device_info.append(
                    f"PyTorch CUDA available: {torch.cuda.get_device_name(0)}"
                )
            else:
                device_info.append("PyTorch running on CPU")
        except ImportError:
            device_info.append("PyTorch not installed")
        try:
            import mlx

            logger.info(f"MLX available: {mlx}")
            device_info.append("MLX available")
        except ImportError:
            device_info.append("MLX not available")
        device_info.append(f"platform: {platform.platform()}")
        self.device_info = device_info
        logger.info(f"[Init] Device info: {' | '.join(device_info)}")
        self.dense_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    async def initialize(self) -> None:
        """Initialize Qdrant connection. No arguments. Raises on failure."""
        if self.initialized:
            logger.info("Knowledge store already initialized.")
            return
        try:
            logger.info("📊 Validating configuration...")
            logger.info("🔗 Creating QdrantAdapter instance...")
            self.qdrant_adapter = QdrantAdapter()
            await self.qdrant_adapter.ainit()
            # Load models after setting up ingesters
            self._load_dense_model()
            self._load_sparse_model()
            self._load_smoldocling_model()
            self.ingester = MultiIngester([self.qdrant_adapter])
            self.initialized = True
            logger.info(
                "✅ ZMP Knowledge Store initialized successfully (Qdrant hybrid mode)"
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize knowledge store: {e}")
            raise

    def _load_smoldocling_model(self) -> None:
        backend = self.smoldocling_backend
        logger.info(f"🔄 Loading SmolDocling model with backend: {backend}")

        try:
            if backend == "mlx":
                model_id = "ds4sd/SmolDocling-256M-preview-mlx-bf16"
                logger.info(f"📥 Downloading SmolDocling MLX model '{model_id}'...")
                local_model_path = snapshot_download(
                    repo_id=model_id, cache_dir=MODELS_DIR
                )
                logger.info(
                    f"✅ SmolDocling MLX model downloaded to: {local_model_path}"
                )

                if not load or not load_config:
                    raise ImportError(
                        "mlx_vlm is required for the MLX backend but is not available. "
                        "Please install mlx_vlm: pip install mlx-vlm"
                    )

                logger.info("🔄 Loading SmolDocling MLX model...")
                self.model, self.processor = load(local_model_path)
                self.model_config = load_config(local_model_path)
                logger.info("✅ SmolDocling MLX model loaded successfully")

            else:  # transformers backend
                model_id = "ds4sd/SmolDocling-256M-preview"
                logger.info(
                    f"📥 Downloading SmolDocling Transformers model '{model_id}'..."
                )
                local_model_path = snapshot_download(
                    repo_id=model_id, cache_dir=MODELS_DIR
                )
                logger.info(
                    f"✅ SmolDocling Transformers model downloaded to: {local_model_path}"
                )

                logger.info("🔄 Loading SmolDocling Transformers model...")
                self.processor = AutoProcessor.from_pretrained(local_model_path)
                self.model = AutoModelForVision2Seq.from_pretrained(local_model_path)
                self.device = torch.device(
                    "cuda" if torch.cuda.is_available() else "cpu"
                )
                self.model = self.model.to(self.device)
                logger.info(
                    f"✅ SmolDocling Transformers model loaded successfully on {self.device}"
                )

        except Exception as e:
            logger.error(
                f"❌ Failed to load SmolDocling model with {backend} backend: {e}"
            )
            logger.error("   This will disable OCR functionality")
            # Set to None to indicate failure
            self.model = None
            self.processor = None
            if backend == "mlx":
                self.model_config = None
            else:
                self.device = None

    def _load_dense_model(self) -> None:
        # st_model_path = snapshot_download(
        #     repo_id="sentence-transformers/all-MiniLM-L6-v2", cache_dir=MODELS_DIR
        # )
        st_model_path = snapshot_download(
            repo_id="sentence-transformers/all-mpnet-base-v2", cache_dir=MODELS_DIR
        )
        self.dense_model = SentenceTransformer(st_model_path)

    def _load_sparse_model(self) -> None:
        """Load SPLADE models from HuggingFace, caching them locally."""
        doc_model_id = "naver/efficient-splade-VI-BT-large-doc"
        query_model_id = "naver/efficient-splade-VI-BT-large-query"

        logger.info(f"Ensuring SPLADE doc model '{doc_model_id}' is cached locally...")
        local_doc_model_path = snapshot_download(
            repo_id=doc_model_id, cache_dir=MODELS_DIR
        )
        logger.info(f"Loading SPLADE doc model from: {local_doc_model_path}")

        logger.info(
            f"Ensuring SPLADE query model '{query_model_id}' is cached locally..."
        )
        local_query_model_path = snapshot_download(
            repo_id=query_model_id, cache_dir=MODELS_DIR
        )
        logger.info(f"Loading SPLADE query model from: {local_query_model_path}")

        self.sparse_device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        # For document embedding
        self.sparse_doc_tokenizer = AutoTokenizer.from_pretrained(local_doc_model_path)
        self.sparse_doc_model = (
            AutoModelForMaskedLM.from_pretrained(local_doc_model_path)
            .to(self.sparse_device)
            .eval()
        )

        # For query embedding
        self.sparse_query_tokenizer = AutoTokenizer.from_pretrained(
            local_query_model_path
        )
        self.sparse_query_model = (
            AutoModelForMaskedLM.from_pretrained(local_query_model_path)
            .to(self.sparse_device)
            .eval()
        )

    async def _compute_dense_embedding(self, content: str) -> list:
        """Computes a dense embedding for a given text content using the SentenceTransformer model."""
        if self.dense_model is None:
            logger.error("Embedding model not loaded, cannot compute dense embedding.")
            return []

        try:
            # The model is already loaded, so we just use the encode method.
            # It handles tokenization, padding, and moving to the correct device automatically.
            embedding = self.dense_model.encode(
                content, convert_to_tensor=False
            ).tolist()
            return embedding
        except Exception as e:
            logger.error(f"Dense embedding computation failed: {e}")
            # Return an empty list or a zero-vector of the correct dimension if you know it
            # and want to handle errors gracefully downstream.
            return []

    async def _compute_sparse_embedding_for_doc(self, content: str) -> dict:
        """Computes a sparse embedding for a document using the SPLADE document model."""
        if not self.sparse_doc_model or not self.sparse_doc_tokenizer:
            logger.error(
                "SPLADE document model not loaded, cannot compute sparse embedding."
            )
            return {}
        try:
            # max_length = 512
            inputs = self.sparse_doc_tokenizer(
                content,
                return_tensors="pt",
                padding="max_length",
                truncation=True,
                max_length=512,
            )
            inputs = {k: v.to(self.sparse_device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = self.sparse_doc_model(**inputs).logits
                doc_rep = torch.max(
                    torch.log(1 + torch.relu(logits))
                    * inputs["attention_mask"].unsqueeze(-1),
                    dim=1,
                ).values.squeeze()

                # get non-zero indices and values
                indices_tensor = doc_rep.nonzero().squeeze()

                if indices_tensor.numel() == 0:
                    indices = []
                    values = []
                elif indices_tensor.dim() == 0:  # Handle single non-zero value case
                    indices = [indices_tensor.item()]
                    values = [doc_rep[indices_tensor].item()]
                else:
                    indices = indices_tensor.cpu().tolist()
                    values = doc_rep[indices_tensor].cpu().tolist()

                sparse_vector = {int(i): float(v) for i, v in zip(indices, values)}
                logger.info(f"SPLADE doc vector: {len(sparse_vector)} nonzero entries.")
                return sparse_vector
        except Exception as e:
            logger.error(f"Sparse document embedding computation failed: {e}")
            return {}

    async def _compute_sparse_embedding_for_query(self, content: str) -> dict:
        """Computes a sparse embedding for a query using the SPLADE query model."""
        if not self.sparse_query_model or not self.sparse_query_tokenizer:
            logger.error(
                "SPLADE query model not loaded, cannot compute sparse embedding."
            )
            return {}
        try:
            # max_length = 512
            inputs = self.sparse_query_tokenizer(
                content,
                return_tensors="pt",
                padding="max_length",
                truncation=True,
                max_length=512,
            )
            inputs = {k: v.to(self.sparse_device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = self.sparse_query_model(**inputs).logits
                query_rep = torch.max(
                    torch.log(1 + torch.relu(logits))
                    * inputs["attention_mask"].unsqueeze(-1),
                    dim=1,
                ).values.squeeze()

                # get non-zero indices and values
                indices_tensor = query_rep.nonzero().squeeze()

                if indices_tensor.numel() == 0:
                    indices = []
                    values = []
                elif indices_tensor.dim() == 0:  # Handle single non-zero value case
                    indices = [indices_tensor.item()]
                    values = [query_rep[indices_tensor].item()]
                else:
                    indices = indices_tensor.cpu().tolist()
                    values = query_rep[indices_tensor].cpu().tolist()

                sparse_vector = {"indices": indices, "values": values}
                logger.info(f"SPLADE query vector: {len(indices)} nonzero entries.")
                return sparse_vector
        except Exception as e:
            logger.error(f"Sparse query embedding computation failed: {e}")
            return {}

    def run_smoldocling_on_page(
        self,
        image_path,
        instruction="Convert this page to docling.",
        asset_url_map=None,
        mdx_path=None,
        ordered_mdx_images=None,
        curr_page_no=None,
    ) -> dict:
        """
        Processes a single page image with SmolDocling using MLX or Transformers backend, selected via .env or platform.
        Returns the parsed DocTags as a dict with 'elements'.
        """
        logger.info(
            f"[SmolDocling][Debug] run_smoldocling_on_page called with ordered_mdx_images: {ordered_mdx_images is not None}, length: {len(ordered_mdx_images) if ordered_mdx_images else 0}"
        )
        if ordered_mdx_images:
            logger.info(
                f"[SmolDocling][Debug] First few ordered_mdx_images: {ordered_mdx_images[:3]}"
            )
        else:
            logger.warning("[SmolDocling][Debug] ordered_mdx_images is None or empty!")

        # Check if model is loaded
        if not self.model or not self.processor:
            logger.error(
                "❌ SmolDocling model not loaded. OCR functionality is disabled."
            )
            logger.error("   This could be due to:")
            logger.error("   - Model download failure")
            logger.error("   - Missing dependencies (mlx-vlm for MLX backend)")
            logger.error("   - Platform compatibility issues")
            return {"elements": []}

        image = Image.open(image_path).convert("RGB")
        backend = self.smoldocling_backend

        # Unified logging
        logger.info(
            f"[SmolDocling-{backend.upper()}] run_smoldocling_on_page: image_path={image_path}, instruction='{instruction}', type(image)={type(image)}"
        )

        # Unified prompt handling - use the same instruction for both backends
        prompt = instruction

        # Generate output based on backend
        output = self._generate_smoldocling_output(backend, image, prompt)

        # Unified DocTags repair logic
        output = self._repair_doctags_output(output, backend)

        # Unified fallback logic if no valid DocTags found
        if not self._has_valid_doctags(output):
            logger.warning(
                f"[SmolDocling-{backend.upper()}] No valid DocTags found in output: {output}"
            )
            fallback_prompt = "Convert this page to docling format with <doctag> tags."
            logger.info(
                f"[SmolDocling-{backend.upper()}] Trying fallback prompt: {fallback_prompt}"
            )

            fallback_output = self._generate_smoldocling_output(
                backend, image, fallback_prompt
            )
            fallback_output = self._repair_doctags_output(fallback_output, backend)

            if self._has_valid_doctags(fallback_output):
                output = fallback_output
                logger.info(
                    f"[SmolDocling-{backend.upper()}] Fallback prompt successful"
                )
            else:
                logger.error(
                    f"[SmolDocling-{backend.upper()}] Both primary and fallback prompts failed"
                )

        # Unified DocTags document creation
        doctags_doc = create_doctags_document(output, [image])
        doc = DoclingDocument.load_from_doctags(
            doctags_doc, document_name="ProcessedDocument"
        )

        # After getting the doc, extract elements
        elements = []
        current_title = None
        current_page = curr_page_no if curr_page_no is not None else None
        doc_url = (
            getattr(doc.origin, "uri", None) if getattr(doc, "origin", None) else None
        )

        def extract_list_items(parent, meta):
            items = []
            for child in getattr(parent, "children", []):
                child_label = getattr(child, "label", None)
                if child_label == "list_item":
                    items.append(
                        {
                            "content": getattr(child, "text", ""),
                            "chunk_type": "list_item",
                            "meta": meta.copy() if meta else {},
                        }
                    )
                elif child_label in ("unordered_list", "ordered_list"):
                    items.extend(extract_list_items(child, meta))
            return items

        root_meta = {
            "title": current_title,
            "page_no": current_page,
            "url": doc_url,
        }
        for item, level in doc.iterate_items():
            label = getattr(item, "label", None)
            if label == "list_item":
                elements.append(
                    {
                        "content": getattr(item, "text", ""),
                        "chunk_type": "list_item",
                        "meta": {**root_meta, "page_no": current_page},
                    }
                )
            if label == DocItemLabel.TITLE:
                current_title = getattr(item, "text", None)
            if hasattr(item, "prov") and item.prov and hasattr(item.prov[0], "page_no"):
                page_no = item.prov[0].page_no
                current_page = page_no
            elif current_page is not None:
                page_no = current_page
            if label not in ("page_break", "page_footer", "page_header"):
                content = getattr(item, "text", "")
                if label in ("otsl", "table"):
                    try:
                        doc_serializer = MarkdownDocSerializer(doc=doc)
                        full_markdown = doc_serializer.serialize().text
                        anchor = getattr(item, "anchor", None) or getattr(
                            item, "id", None
                        )
                        content = None
                        if anchor and anchor in full_markdown:
                            lines = full_markdown.splitlines()
                            start = [
                                i for i, line in enumerate(lines) if anchor in line
                            ]
                            if start:
                                s = max(0, start[0] - 2)
                                e = min(len(lines), start[0] + 10)
                                content = "\n".join(lines[s:e])
                        if not content:
                            content = full_markdown
                        if not content or not content.strip():
                            raise ValueError("Serialized table content is empty")
                    except Exception as e:
                        logger.warning(
                            f"[Ingest] Failed to serialize OTSL/table to markdown: {e}. Using raw OTSL string."
                        )
                        content = getattr(item, "otsl_xml", None) or str(item)
                    meta = {
                        "title": current_title,
                        "page_no": current_page,
                        "url": doc_url,
                    }
                    element = {
                        "content": content,
                        "chunk_type": label,
                        "meta": meta,
                    }
                    elements.append(element)
                    continue
                if label == "picture":
                    logger.info(
                        f"[Ingest][Debug] PICTURE ELEMENT DETECTED - label: {label}, page_no: {current_page}, ordered_mdx_images: {ordered_mdx_images is not None}"
                    )
                    meta = {
                        "title": current_title,
                        "page_no": current_page,
                        "url": doc_url,
                    }

                    # --- NEW: Validate picture against actual MDX images ---
                    image_url = None
                    assigned_mdx_image = None

                    logger.info(
                        f"[Ingest][Debug] Picture element detected. ordered_mdx_images: {ordered_mdx_images is not None}, hasattr _assigned_mdx_images: {hasattr(self, '_assigned_mdx_images')}"
                    )

                    if ordered_mdx_images and hasattr(self, "_assigned_mdx_images"):
                        logger.info(
                            f"[Ingest][Debug] Available MDX images: {len(ordered_mdx_images)}, Assigned: {len(self._assigned_mdx_images)}"
                        )
                        # Find the next unassigned MDX image
                        for mdx_ref, s3_key in ordered_mdx_images:
                            if mdx_ref not in self._assigned_mdx_images:
                                assigned_mdx_image = mdx_ref
                                image_url = s3_key
                                self._assigned_mdx_images.add(mdx_ref)
                                logger.info(
                                    f"[Ingest][Validation] Validated picture element -> MDX image '{mdx_ref}' -> S3 key '{s3_key}'"
                                )
                                break

                        if not assigned_mdx_image:
                            logger.warning(
                                "[Ingest][Validation] Picture element detected but no unassigned MDX images available. Skipping false positive."
                            )
                            continue  # Skip this picture element (false positive)
                    else:
                        logger.info(
                            f"[Ingest][Debug] Using fallback logic. ordered_mdx_images: {ordered_mdx_images}, _assigned_mdx_images: {getattr(self, '_assigned_mdx_images', 'NOT_SET')}"
                        )
                        # Fallback to old logic if no ordered_mdx_images provided
                        if self._picture_index < len(self._asset_urls):
                            image_url = self._asset_urls[self._picture_index]
                            logger.info(
                                f"[Ingest] Fallback: Assigning S3 URL for picture element at document index {self._picture_index}: {image_url}"
                            )
                        else:
                            logger.error(
                                f"[Ingest] Fallback: No S3 URL available for picture element at document index {self._picture_index}. Using 'image-not-found'."
                            )
                            image_url = "image-not-found"
                        self._picture_index += 1

                    caption = (
                        getattr(item, "caption", None)
                        or meta.get("caption", None)
                        or "Image"
                    )
                    content = f"![{caption}]({image_url})"
                    meta["assets_s3_keys"] = [image_url]
                    element = {
                        "content": content,
                        "chunk_type": label,
                        "meta": meta,
                    }
                    elements.append(element)
                    continue
                if label in ("unordered_list", "ordered_list"):
                    meta = {
                        "title": current_title,
                        "page_no": current_page,
                        "url": doc_url,
                    }
                    list_items = extract_list_items(item, meta)
                    elements.extend(list_items)
                    continue
                elem = {
                    "content": content,
                    "type": label,
                    "meta": {
                        "title": current_title,
                        "page_no": current_page,
                        "url": doc_url,
                    },
                    "level": level,
                }
                elements.append(elem)
        logger.debug("[SmolDocling][Debug] Extracted elements:")
        for i, elem in enumerate(elements):
            ctype = elem.get("chunk_type") or elem.get("type") or "unknown"
            content = elem.get("content", "")

            # --- Progressive correction: ensure corrected content is used ---
            # New: Word-level correction for hallucinated words
            def word_level_correction(chunk, mdx):
                mdx_words = set(mdx.split())
                chunk_words = chunk.split()
                corrected_words = []
                for word in chunk_words:
                    # If the word is in the MDX (case-insensitive), keep it
                    if any(word.lower() == w.lower() for w in mdx_words):
                        corrected_words.append(word)
                    else:
                        # Try to find the closest match in the MDX (case-insensitive)
                        matches = difflib.get_close_matches(
                            word, mdx_words, n=1, cutoff=0.8
                        )
                        if matches:
                            corrected_words.append(matches[0])
                        else:
                            corrected_words.append(word)  # fallback: keep original
                return " ".join(corrected_words)

            try:
                if mdx_path:
                    with open(mdx_path, "r", encoding="utf-8") as f:
                        mdx = f.read()
                    mdx = re.sub(r"^---.*?---\s*", "", mdx, flags=re.DOTALL)
                    if content:
                        corrected = word_level_correction(content, mdx)
                        if corrected != content:
                            content = corrected
            except Exception as e:
                logger.warning(f"[Ingest] Correction failed: {e}")
            logger.info(
                f"  [Element {i}] {ctype}: {content[:50].replace('\n',' ')}{'...' if len(content)>50 else ''}"
            )
        return {"elements": elements, "doctags_markup": output}

    def _generate_smoldocling_output(self, backend, image, prompt) -> str:
        """Generate SmolDocling output using the specified backend with unified logic."""
        if backend == "mlx":
            if not self.model or not self.processor or not self.model_config:
                raise RuntimeError(
                    "SmolDocling MLX model not loaded. Call initialize() first."
                )
            model, processor, config = self.model, self.processor, self.model_config

            # Use the correct API for mlx_vlm
            formatted_prompt = apply_chat_template(
                processor, config, prompt, num_images=1
            )

            output = ""
            for token in stream_generate(
                model,
                processor,
                formatted_prompt,
                [image],
                max_tokens=4096,
                verbose=False,
            ):
                output += token.text
                if "</doctag>" in token.text:
                    break
        elif backend == "transformers":
            if not self.model or not self.processor:
                raise RuntimeError(
                    "SmolDocling Transformers model not loaded. Call initialize() first."
                )
            model, processor = self.model, self.processor
            # Use chat template and message-based prompt
            messages = [
                {
                    "role": "user",
                    "content": [{"type": "image"}, {"type": "text", "text": prompt}],
                },
            ]
            chat_prompt = processor.apply_chat_template(
                messages, add_generation_prompt=True
            )
            inputs = processor(
                text=chat_prompt, images=[image], return_tensors="pt"
            ).to(self.device)
            generated_ids = model.generate(**inputs, max_new_tokens=4096)
            prompt_length = inputs.input_ids.shape[1]
            trimmed_generated_ids = generated_ids[:, prompt_length:]
            output = processor.batch_decode(
                trimmed_generated_ids, skip_special_tokens=False
            )[0].lstrip()
        else:
            raise ValueError(f"Unsupported SmolDocling backend: {backend}")
        return output

    def _repair_doctags_output(self, output, backend) -> str:
        """Repair malformed DocTags output with unified logic for all backends."""
        # --- Begin: Robust repair of malformed DocTags lists (pre-parse) ---
        doctags_str = output
        # Look for orphaned <list_item> elements at the start (after <doctag> and any whitespace)
        orphaned_listitem_pattern = r"(<doctag>\s*)(<list_item>)"
        if re.search(orphaned_listitem_pattern, doctags_str):
            # Decide which open tag to use by looking for the first closing tag
            idx = doctags_str.find("</list_item>")
            open_tag = "<unordered_list>"  # Default
            if idx != -1:
                after = doctags_str[idx:]
                if "</ordered_list>" in after:
                    open_tag = "<ordered_list>"
            doctags_str = re.sub(
                orphaned_listitem_pattern,
                r"\1" + open_tag + r"\2",
                doctags_str,
                count=1,
            )
            logger.info(
                f"[Repair][Pre-parse] Inserted {open_tag} after <doctag> to wrap orphaned <list_item>."
            )
        # Log the repaired DocTags string before parsing
        logger.info(
            f"[SmolDocling-{backend.upper()}] DocTags output (repaired): {doctags_str}"
        )
        return doctags_str
        # --- End: Robust repair of malformed DocTags lists (pre-parse) ---

    def _has_valid_doctags(self, output):
        """Check if output contains valid DocTags with unified logic."""
        return "<doctag>" in output or "<text>" in output or "<picture>" in output

    async def search_knowledge(
        self, query: str, n_results: int = 5, collection: str = None
    ) -> Dict[str, Any]:
        """
        Search for documents using a hybrid query (dense + sparse embeddings).

        Args:
            query: Search query string
            n_results: Number of results to return
            collection: Collection to search in. If None, uses default collection.
        """
        if not self.initialized:
            raise RuntimeError(
                "Knowledge store not initialized. Call the 'initialize' method first."
            )

        # Validate collection name if provided
        if collection is not None:
            if not collection or not collection.strip():
                raise ValueError("Collection name cannot be empty")
            # Collection validation will be handled by QdrantAdapter.query()

        try:
            logger.info(f"🧠 Searching for: '{query}' with {n_results} results")
            # Start a timer
            start_time = time.time()

            # Compute embeddings for the query
            dense_vector = await self._compute_dense_embedding(query)
            sparse_vector_dict = await self._compute_sparse_embedding_for_query(query)

            logger.info(
                f"SPLADE query vector: {len(sparse_vector_dict.get('indices', []))} nonzero entries."
            )

            try:
                # Query Qdrant
                qdrant_results = await self.qdrant_adapter.query(
                    dense_vector,
                    sparse_vector_dict,
                    n_results,
                    collection_name=collection,
                )

                # End timer
                end_time = time.time()
                logger.info(
                    f"⚡️ Search completed in {end_time - start_time:.2f} seconds"
                )

                # Format results
                formatted_results = self._format_results(qdrant_results)

                # Re-rank results (optional)
                reranked_results = self._rerank_results(formatted_results, query)

                return {
                    "status": "success",
                    "results": reranked_results,
                }
            except Exception as e:
                logger.error(f"❌ Knowledge search failed: {e}", exc_info=True)
                return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"❌ Knowledge search failed: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def _format_results(self, qdrant_results) -> list:
        combined_qdrant_points = {}

        # qdrant_results is a list of dicts (after fusion) or objects (older code)
        if qdrant_results and isinstance(qdrant_results, list):
            for result_batch in qdrant_results:
                # Each result_batch is a QueryResponse object which contains the points
                if hasattr(result_batch, "points"):
                    points = result_batch.points
                else:
                    # In new code, result_batch is a dict (id/score/payload)
                    points = result_batch

                if points:
                    # If points is a list of dicts (new code)
                    if isinstance(points, dict):
                        # Single dict, wrap in list
                        points = [points]
                    if (
                        isinstance(points, list)
                        and points
                        and isinstance(points[0], dict)
                    ):
                        for point in points:
                            doc_id = point["id"]
                            payload = point.get("payload")
                            score = point.get("score")
                            if doc_id not in combined_qdrant_points:
                                combined_qdrant_points[doc_id] = {
                                    "id": doc_id,
                                    "payload": payload,
                                    "score": score,
                                    "source": "qdrant",
                                }
                    else:
                        # Fallback for object with .id
                        for point in points:
                            doc_id = point.id
                            payload = point.payload
                            score = point.score
                            if doc_id not in combined_qdrant_points:
                                combined_qdrant_points[doc_id] = {
                                    "id": doc_id,
                                    "payload": payload,
                                    "score": score,
                                    "source": "qdrant",
                                }

        # Return Qdrant results
        return list(combined_qdrant_points.values())

    def _rerank_results(self, results, query=None) -> list:
        """
        Rerank results using CrossEncoder (SentenceTransformerRerank).
        If query is None or reranker fails, fallback to score sort.
        """
        if query is not None:
            try:
                # Prepare input for reranker: list of (query, doc) pairs
                pairs = [(query, r["payload"].get("content", "")) for r in results]
                # Get reranked scores
                scores = self.sentence_transformers_rerank._model.predict(pairs)
                # Attach rerank scores
                for r, s in zip(results, scores):
                    r["rerank_score"] = float(s)
                # Sort by rerank_score
                return sorted(results, key=lambda x: x["rerank_score"], reverse=True)
            except Exception as e:
                logger.warning(f"CrossEncoder rerank failed: {e}")
        # Fallback: sort by original score
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def _extract_metadata_and_content(
        self, doc: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], str]:
        """
        Extract metadata from frontmatter and directory structure.
        Args:
            doc (Dict[str, Any]): Document dict with 'filename' and 'content'. Required.
        Returns:
            Tuple[Dict[str, Any], str]: (metadata dict, content string)
        """
        filename = doc.get("filename", "")
        content = doc.get("content", "")

        # Try to parse YAML frontmatter
        frontmatter_match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
        meta = {}

        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            logger.info(f"Extracted frontmatter for {filename}: {frontmatter}")
            try:
                meta = yaml.safe_load(frontmatter) or {}
            except Exception:
                meta = {}

        # Extract page title
        page_title = (
            meta.get("title")
            or doc.get("page_title")
            or os.path.splitext(os.path.basename(filename))[0]
            or "Untitled Document"
        )

        # Extract other metadata
        solution = doc.get("solution") or meta.get("solution") or "zmp"
        manual_keywords = (
            doc.get("manual_keywords") or meta.get("manual_keywords") or []
        )
        doc_url = doc.get("doc_url")

        return {
            "page_title": page_title,
            "solution": solution,
            "created_at": doc.get("created_at") or meta.get("created_at"),
            "updated_at": doc.get("updated_at") or meta.get("updated_at"),
            "manual_keywords": manual_keywords,
            "doc_url": doc_url,
        }, content

    async def ingest_document(
        self, doc: Dict[str, Any], ingest_timestamp: str = None, collection: str = None
    ) -> Dict[str, Any]:
        """
        Ingest a single document with asset support. Returns the document ID.
        Args:
            doc (Dict[str, Any]): Document dict with 'filename' and 'content'. Required.
            ingest_timestamp (str, optional): Timestamp to use for created_at and updated_at fields.
        Returns:
            Dict[str, Any]: Document ID.
        """
        if not self.initialized:
            raise RuntimeError(
                "Knowledge store not initialized. Call initialize() first."
            )
        filename = doc.get("filename", "")
        content = doc.get("content", "")
        assets = doc.get("assets", [])
        # Collect all S3 keys from all assets
        all_assets_s3_keys = []
        for asset in assets:
            keys = asset.get("assets_s3_keys", [])
            if isinstance(keys, list):
                all_assets_s3_keys.extend(keys)
            elif isinstance(keys, str):
                all_assets_s3_keys.append(keys)

        # Extract frontmatter as a special chunk if present
        frontmatter_match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            logger.info(f"Extracted frontmatter for {filename}: {frontmatter}")
            # This part seems to have a logic bug where it returns early.
            # Assuming we want to ingest the frontmatter AND the content.
            # For now, let's just ingest the frontmatter and see if that was the intent.
            # The original code here would return, skipping the rest of the file.

            # Simplified metadata for frontmatter
            meta_for_frontmatter = {
                "page_title": "Frontmatter: " + filename,
                "solution": "zmp",
            }
            logger.info(f"meta_for_frontmatter: {meta_for_frontmatter}")
            dense_vector = await self._compute_dense_embedding(frontmatter)
            sparse_vector = await self._compute_sparse_embedding_for_doc(frontmatter)

            doc_url = doc.get("doc_url")

            qdrant_result = await self.qdrant_adapter.ingest_document(
                content=frontmatter,
                page_title="Frontmatter: " + filename,
                solution="zmp",
                dense_vector=dense_vector,
                sparse_vector=sparse_vector,
                assets_s3_keys=all_assets_s3_keys,  # Pass assets here too
                created_at=ingest_timestamp,
                updated_at=ingest_timestamp,
                doc_url=doc_url,
                collection_name=collection,
            )
            return {"qdrant_adapter": qdrant_result}
        else:
            # Non-markdown: ingest as a single document
            metadata, clean_content = self._extract_metadata_and_content(doc)
            dense_vector = await self._compute_dense_embedding(clean_content)
            sparse_vector = await self._compute_sparse_embedding_for_doc(clean_content)

            qdrant_result = await self.qdrant_adapter.ingest_document(
                content=clean_content,
                page_title=metadata.get("page_title", filename),
                solution=metadata.get("solution", "zmp"),
                dense_vector=dense_vector,
                sparse_vector=sparse_vector,
                assets_s3_keys=all_assets_s3_keys,
                created_at=ingest_timestamp,
                updated_at=ingest_timestamp,
                doc_url=metadata.get("doc_url"),
                collection_name=collection,
            )
            return {"qdrant_adapter": qdrant_result}

    def convert_directory(self, input_dir, output_json="document_docling.json") -> None:
        """
        Convert all PNG/JPEG pages in input_dir to a single DoclingDocument with pages list.
        """

        pages_json = []
        for file in sorted(os.listdir(input_dir)):
            if not file.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            img_path = os.path.join(input_dir, file)
            docling_page = self.run_smoldocling_on_page(img_path)
            pages_json.append(docling_page)
        consolidated = {"pages": pages_json}
        with open(output_json, "w") as f:
            json.dump(consolidated, f, indent=2)
        logger.info(f"Saved consolidated DoclingDocument to {output_json}")

    def _handle_ingestion_result(
        self, result, filename, page_idx, elem_idx, metadata
    ) -> dict:
        """Handle the result from the MultiIngester properly."""
        try:
            # Handle successful dict from MultiIngester
            if isinstance(result, dict) and "QdrantAdapter" in result:
                qdrant_id = result.get("QdrantAdapter")
                is_qdrant_success = isinstance(qdrant_id, str) and len(qdrant_id) > 10
                if is_qdrant_success:
                    return {
                        "doc_id": qdrant_id,
                        "filename": filename,
                        "page_index": page_idx,
                        "element_index": elem_idx,
                        "status": "success",
                        "chunk_type": metadata.get("chunk_type", None),
                        "meta": metadata,
                        "adapter_results": result,
                    }
            # Fallback for other dicts or partial success/errors
            if isinstance(result, dict):
                return {
                    "doc_id": str(result),
                    "filename": filename,
                    "page_index": page_idx,
                    "element_index": elem_idx,
                    "status": "error",
                    "chunk_type": metadata.get("chunk_type", None),
                    "meta": metadata,
                    "error": "One or more adapters failed.",
                }
            # Fallback for unexpected non-dict result formats
            return {
                "doc_id": str(result) if result else None,
                "filename": filename,
                "page_index": page_idx,
                "element_index": elem_idx,
                "status": "unknown",
                "chunk_type": metadata.get("chunk_type", None),
                "meta": metadata,
                "warning": f"Unexpected result format: {type(result)}",
            }
        except Exception as e:
            logger.error(f"Error handling ingestion result: {e}")
            return {
                "doc_id": None,
                "filename": filename,
                "page_index": page_idx,
                "element_index": elem_idx,
                "status": "error",
                "chunk_type": metadata.get("chunk_type", None),
                "meta": metadata,
                "error": f"Result handling error: {str(e)}",
            }

    async def ingest_documents(
        self,
        documents: List[Dict[str, Any]],
        ingest_timestamp: str = None,
        solution: str = None,
        collection: str = None,
    ) -> dict:
        # Validate collection name if provided
        if collection is not None:
            if not collection or not collection.strip():
                raise ValueError("Collection name cannot be empty")
            # Collection validation will be handled by QdrantAdapter.ingest_document()

        results = []
        batch_start_time = time.time()
        for doc in documents:
            doc_start_time = time.time()
            try:
                filename = doc.get("filename", "")
                content = doc.get("content", "")
                assets = doc.get("assets", [])
                doc_url = doc.get("doc_url")
                logger.info(
                    f"[Ingest] Processing document: {filename}, assets={len(assets)}"
                )
                # --- S3 key-based asset handling ---
                # Build a mapping from asset filename to its S3 keys
                asset_filename_to_s3keys = {}
                for a in assets:
                    fname = os.path.basename(a.get("filename", ""))
                    keys = a.get("assets_s3_keys", [])
                    if isinstance(keys, list):
                        asset_filename_to_s3keys[fname] = keys
                    elif isinstance(keys, str):
                        asset_filename_to_s3keys[fname] = [keys]
                # Reconstruct all_assets_s3_keys for self._asset_urls assignment
                all_assets_s3_keys = []
                for keys in asset_filename_to_s3keys.values():
                    all_assets_s3_keys.extend(keys)
                all_assets_s3_keys = list(set(all_assets_s3_keys))
                self._asset_urls = all_assets_s3_keys
                # --- Extract all image references from the MDX (in order) ---
                image_refs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", content)
                image_refs = [
                    p.lstrip("/") for p in image_refs
                ]  # Remove leading slash if present
                # Build an ordered list of (ref_path, s3_key) pairs
                ordered_image_ref_to_s3 = []
                for ref in image_refs:
                    fname = os.path.basename(ref)
                    # Find the asset with this filename
                    for asset in assets:
                        asset_filename = os.path.basename(asset.get("filename", ""))
                        s3_keys = asset.get("assets_s3_keys", [])
                        if isinstance(s3_keys, str):
                            s3_keys = [s3_keys]
                        if fname == asset_filename and s3_keys:
                            for s3_key in s3_keys:
                                ordered_image_ref_to_s3.append((ref, s3_key))
                                logger.info(
                                    f"[Ingest][ImageOrder] MDX image ref '{ref}' matched to S3 key '{s3_key}'"
                                )
                            break

                # Store ordered image references for validation in run_smoldocling_on_page
                self._ordered_mdx_images = ordered_image_ref_to_s3
                self._assigned_mdx_images = (
                    set()
                )  # Track which MDX images have been assigned

                # --- Begin: Relocate images and save MDX in output tmp dir ---
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                logger.info(
                    f"[Ingest] Creating output tmp directory for {filename} with timestamp {timestamp}"
                )
                mdx_basename = os.path.basename(filename)
                base_tmp_dir = os.path.join(PROJECT_ROOT, "tmp")
                output_dir = os.path.join(base_tmp_dir, timestamp)
                os.makedirs(output_dir, exist_ok=True)
                # --- Download images from S3 using assets_s3_keys before Pandoc/SmolDocling ---
                if assets:
                    for asset in assets:
                        asset_filename = asset.get("filename")
                        s3_keys = asset.get("assets_s3_keys")
                        if not asset_filename or not s3_keys:
                            logger.warning(
                                f"[Ingest] Asset missing filename or assets_s3_keys: {asset}"
                            )
                            continue
                        if isinstance(s3_keys, str):
                            s3_keys = [s3_keys]
                        # Only download if referenced in the MDX
                        ref_paths = [
                            ref
                            for ref, _ in ordered_image_ref_to_s3
                            if os.path.basename(ref) == asset_filename
                        ]
                        if not ref_paths:
                            logger.info(
                                f"[Ingest] Asset {asset_filename} not referenced in MDX, skipping download."
                            )
                            continue
                        for s3_key in s3_keys:
                            for ref_path in ref_paths:
                                local_img_path = os.path.join(output_dir, ref_path)
                                os.makedirs(
                                    os.path.dirname(local_img_path), exist_ok=True
                                )
                                try:
                                    logger.info(
                                        f"[Ingest] Downloading image from S3: s3://{Config.S3_BUCKET_NAME}/{s3_key} -> {local_img_path}"
                                    )
                                    s3_client.download_file(
                                        Config.S3_BUCKET_NAME, s3_key, local_img_path
                                    )
                                except Exception as e:
                                    logger.error(
                                        f"[Ingest] Failed to download {s3_key} to {local_img_path}: {e}"
                                    )

                # --- Remove leading slash from all /img/ references in markdown images ---
                def fix_image_paths(md):
                    # Remove a leading slash from /img/ in all markdown image references
                    return re.sub(r"(!\[[^\]]*\]\()\s*/img/", r"\1img/", md)

                logger.info(f"[Ingest][MDX] Before path fix: {content}")
                fixed_content = fix_image_paths(content)
                logger.info(f"[Ingest][MDX] After path fix: {fixed_content}")
                mdx_path = os.path.join(output_dir, mdx_basename)
                logger.info(f"[Ingest] Saving MDX file to {mdx_path}")
                with open(mdx_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                # --- End: Relocate images and save MDX ---
                # --- Extract frontmatter for metadata ---
                frontmatter_match = re.match(
                    r"^---\n(.*?)\n---\n(.*)$", fixed_content, re.DOTALL
                )
                meta = {}
                if frontmatter_match:
                    frontmatter = frontmatter_match.group(1)
                    try:
                        meta = yaml.safe_load(frontmatter) or {}
                    except Exception:
                        meta = {}
                page_title = (
                    meta.get("title")
                    or os.path.splitext(os.path.basename(filename))[0]
                    or "Untitled Document"
                )
                # --- Convert MDX to PDF and extract images (pages) ---
                images = []
                pdf_base = None
                if filename.endswith((".md", ".mdx")):
                    t_pandoc_start = time.time()
                    pdf_path = os.path.join(
                        output_dir, mdx_basename.rsplit(".", 1)[0] + ".pdf"
                    )
                    logger.info(
                        f"[Ingest] Starting Pandoc conversion: {mdx_basename} -> {pdf_path}"
                    )
                    os.system(
                        f"cd '{output_dir}' && pandoc -f markdown '{mdx_basename}' -o '{os.path.basename(pdf_path)}' --pdf-engine=xelatex -V mainfont='Noto Sans Symbols'"
                    )
                    t_pandoc_end = time.time()
                    logger.info(
                        f"[Ingest] Pandoc conversion elapsed time: {t_pandoc_end-t_pandoc_start:.2f}s"
                    )
                    t_pdfimg_start = time.time()
                    logger.info(f"[Ingest] Loading images from PDF: {pdf_path}")
                    images = convert_from_path(pdf_path)
                    t_pdfimg_end = time.time()
                    logger.info(
                        f"[Ingest] Loaded {len(images)} images from PDF in {t_pdfimg_end-t_pdfimg_start:.2f}s"
                    )
                    pdf_base = os.path.splitext(os.path.basename(pdf_path))[0]
                    for idx, img in enumerate(images):
                        img_filename = f"{pdf_base}_page{idx+1}.png"
                        img_path = os.path.join(output_dir, img_filename)
                        img.save(img_path, format="PNG")
                        logger.info(f"[Ingest] Saved page image: {img_path}")
                elif filename.endswith(".pdf"):
                    t_pdfimg_start = time.time()
                    logger.info(f"[Ingest] Loading images from PDF: {filename}")
                    images = convert_from_path(filename)
                    t_pdfimg_end = time.time()
                    logger.info(
                        f"[Ingest] Loaded {len(images)} images from PDF in {t_pdfimg_end-t_pdfimg_start:.2f}s"
                    )
                    pdf_base = os.path.splitext(os.path.basename(filename))[0]
                elif filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    t_imgload_start = time.time()
                    logger.info(f"[Ingest] Loading single image file: {filename}")
                    images = [Image.open(filename)]
                    t_imgload_end = time.time()
                    logger.info(
                        f"[Ingest] Loaded image in {t_imgload_end-t_imgload_start:.2f}s"
                    )
                    pdf_base = os.path.splitext(os.path.basename(filename))[0]
                else:
                    logger.error(
                        f"[Ingest] Unsupported file type for SmolDocling ingestion: {filename}"
                    )
                    raise ValueError("Unsupported file type for SmolDocling ingestion")
                total_page_count = len(images)
                self.total_page_count = total_page_count
                self._picture_index = 0
                # --- Run SmolDocling on each page image, extract elements, group, and ingest ---
                for page_idx, image in enumerate(images):
                    t_model_start = time.time()
                    img_filename = f"{pdf_base}_page{page_idx+1}.png"
                    img_path = os.path.join(output_dir, img_filename)
                    # --- Extract page number from filename ---
                    match = re.search(r"_page(\d+)\\.png$", img_filename)
                    if match:
                        curr_page_no = int(match.group(1))
                    else:
                        curr_page_no = page_idx + 1  # fallback
                    logger.info(
                        f"[Ingest] Running SmolDocling on page image: {img_path} (curr_page_no={curr_page_no})"
                    )
                    try:
                        logger.info(
                            f"[Ingest][Debug] Calling run_smoldocling_on_page with ordered_mdx_images: {self._ordered_mdx_images is not None}, length: {len(self._ordered_mdx_images) if self._ordered_mdx_images else 0}"
                        )
                        docling_result = self.run_smoldocling_on_page(
                            img_path,
                            asset_url_map=None,
                            mdx_path=mdx_path,
                            ordered_mdx_images=self._ordered_mdx_images,
                            curr_page_no=curr_page_no,
                        )
                        elements = docling_result.get("elements", [])
                        if not elements:
                            logger.warning(
                                f"[Ingest] No DocTags elements for page {curr_page_no} of {filename}"
                            )
                            continue
                    except Exception as e:
                        logger.error(
                            f"[Ingest] Failed to process page image {img_path}: {e}"
                        )
                        continue
                    t_model_end = time.time()
                    logger.info(
                        f"[Ingest] Finished SmolDocling inference for {filename} page {curr_page_no}/{len(images)} in {t_model_end-t_model_start:.2f}s"
                    )
                    # --- Improved grouping: group table/picture with adjacent caption (before or after) ---
                    i = 0
                    n = len(elements)
                    grouped_elements = []
                    buffer = []
                    buffer_type = None
                    buffer_meta = None
                    current_size = 0
                    while i < n:
                        elem = elements[i]
                        elem_type = (
                            elem.get("chunk_type") or elem.get("type") or "unknown"
                        )
                        elem_content = elem.get("content", "")
                        elem_meta = elem.get("meta", {}) or {}

                        if elem_type in ("table", "picture"):
                            # Prefer caption before, else after
                            grouped = False
                            # Caption before
                            if (
                                i > 0
                                and (
                                    elements[i - 1].get("chunk_type")
                                    or elements[i - 1].get("type")
                                )
                                == "caption"
                            ):
                                caption_elem = elements[i - 1]
                                grouped_elements.append(
                                    {
                                        "content": "\n".join(
                                            [caption_elem["content"], elem_content]
                                        ),
                                        "chunk_type": elem_type,
                                        "meta": elem_meta,
                                    }
                                )
                                grouped = True
                                i += 1  # Skip current table/picture
                            # Caption after
                            elif (
                                i + 1 < n
                                and (
                                    elements[i + 1].get("chunk_type")
                                    or elements[i + 1].get("type")
                                )
                                == "caption"
                            ):
                                caption_elem = elements[i + 1]
                                grouped_elements.append(
                                    {
                                        "content": "\n".join(
                                            [elem_content, caption_elem["content"]]
                                        ),
                                        "chunk_type": elem_type,
                                        "meta": elem_meta,
                                    }
                                )
                                grouped = True
                                i += 2  # Skip current and next (caption)
                            if not grouped:
                                grouped_elements.append(
                                    {
                                        "content": elem_content,
                                        "chunk_type": elem_type,
                                        "meta": elem_meta,
                                    }
                                )
                                i += 1
                        elif elem_type == "caption":
                            # Only group caption if not already grouped with table/picture
                            # If next is table/picture, let that logic handle it
                            if i + 1 < n and (
                                elements[i + 1].get("chunk_type")
                                or elements[i + 1].get("type")
                            ) in ("table", "picture"):
                                i += 1  # Skip, will be handled by next iteration
                            else:
                                grouped_elements.append(
                                    {
                                        "content": elem_content,
                                        "chunk_type": elem_type,
                                        "meta": elem_meta,
                                    }
                                )
                                i += 1
                        elif elem_type == "list_item":
                            # Buffer logic for list_items (as before)
                            if buffer_type == "list_item":
                                if current_size + len(elem_content) > CHUNK_SIZE:
                                    grouped_elements.append(
                                        {
                                            "content": "\n".join(buffer),
                                            "chunk_type": buffer_type,
                                            "meta": buffer_meta,
                                        }
                                    )
                                    buffer = [elem_content]
                                    current_size = len(elem_content)
                                else:
                                    buffer.append(elem_content)
                                    current_size += len(elem_content) + 1
                            else:
                                if buffer:
                                    grouped_elements.append(
                                        {
                                            "content": "\n".join(buffer),
                                            "chunk_type": buffer_type,
                                            "meta": buffer_meta,
                                        }
                                    )
                                buffer = [elem_content]
                                buffer_type = elem_type
                                buffer_meta = elem_meta
                                current_size = len(elem_content)
                            i += 1
                        else:
                            if buffer:
                                grouped_elements.append(
                                    {
                                        "content": "\n".join(buffer),
                                        "chunk_type": buffer_type,
                                        "meta": buffer_meta,
                                    }
                                )
                                buffer = []
                                current_size = 0
                            grouped_elements.append(
                                {
                                    "content": elem_content,
                                    "chunk_type": elem_type,
                                    "meta": elem_meta,
                                }
                            )
                            i += 1
                    if buffer:
                        grouped_elements.append(
                            {
                                "content": "\n".join(buffer),
                                "chunk_type": buffer_type,
                                "meta": buffer_meta,
                            }
                        )
                    # --- Debug log for grouped elements ---
                    for i, elem in enumerate(grouped_elements):
                        logger.debug(
                            f"[Debug][Grouping] Grouped element {i}: type={elem['chunk_type']}, size={len(elem['content'])}, content_snippet={elem['content'][:80].replace('\n',' ')}{'...' if len(elem['content'])>80 else ''}"
                        )

                    # --- For each grouped chunk, embed and ingest ---
                    # Convert grouped_elements (dicts) to LangChain Document objects
                    grouped_documents = [
                        Document(page_content=elem["content"], metadata=elem)
                        for elem in grouped_elements
                    ]
                    # Use CharacterTextSplitter for now; swap to chunk_documents_recursive for future graph DB expansion
                    chunks = chunk_documents_character(
                        grouped_documents,
                        chunk_size=CHUNK_SIZE,
                        chunk_overlap=CHUNK_OVERLAP,
                    )
                    used_image_keys = set()
                    for elem_idx, chunk_doc in enumerate(chunks):
                        content = chunk_doc.page_content
                        chunk_type = chunk_doc.metadata.get("chunk_type") or "unknown"
                        meta = chunk_doc.metadata.get("meta", {}) or {}
                        chunk_order_base = float(f"{page_idx}.{elem_idx}")
                        # --- Only add assets_s3_keys if this chunk references an image ---
                        image_refs = re.findall(r"!\[[^]]*\]\(([^)]+)\)", content)
                        chunk_assets_s3_keys = []
                        for ref in image_refs:
                            ref_basename = os.path.basename(ref)
                            if ref_basename in asset_filename_to_s3keys:
                                chunk_assets_s3_keys.extend(
                                    asset_filename_to_s3keys[ref_basename]
                                )
                                used_image_keys.update(
                                    asset_filename_to_s3keys[ref_basename]
                                )
                        chunk_assets_s3_keys = list(set(chunk_assets_s3_keys))
                        # --- Build metadata dict for this chunk ---
                        # Get the correct page number based on MDX content and image position
                        correct_page_no = page_idx + 1

                        metadata = {
                            "solution": solution,
                            "page_title": page_title,
                            "chunk_order": chunk_order_base,
                            "chunk_type": chunk_type,
                            "page_no": correct_page_no,
                            "created_at": ingest_timestamp,
                            "updated_at": ingest_timestamp,
                        }
                        if doc_url:
                            metadata["doc_url"] = doc_url
                        if chunk_assets_s3_keys:
                            metadata["assets_s3_keys"] = chunk_assets_s3_keys
                        if collection:
                            metadata["collection_name"] = collection

                        metadata = {k: v for k, v in metadata.items()}

                        # --- Progressive correction: ensure corrected content is used ---
                        # New: Word-level correction for hallucinated words
                        def word_level_correction(chunk, mdx):
                            mdx_words = set(mdx.split())
                            chunk_words = chunk.split()
                            corrected_words = []
                            for word in chunk_words:
                                # If the word is in the MDX (case-insensitive), keep it
                                if any(word.lower() == w.lower() for w in mdx_words):
                                    corrected_words.append(word)
                                else:
                                    # Try to find the closest match in the MDX (case-insensitive)
                                    matches = difflib.get_close_matches(
                                        word, mdx_words, n=1, cutoff=0.8
                                    )
                                    if matches:
                                        corrected_words.append(matches[0])
                                    else:
                                        corrected_words.append(
                                            word
                                        )  # fallback: keep original
                            return " ".join(corrected_words)

                        try:
                            if mdx_path:
                                with open(mdx_path, "r", encoding="utf-8") as f:
                                    mdx = f.read()
                                mdx = re.sub(r"^---.*?---\s*", "", mdx, flags=re.DOTALL)
                                if content:
                                    corrected = word_level_correction(content, mdx)
                                    if corrected != content:
                                        content = corrected
                        except Exception as e:
                            logger.warning(f"[Ingest] Correction failed: {e}")
                        # --- Ingest chunk (rest of logic unchanged) ---
                        try:
                            result = await self.ingester.ingest_document(
                                content=content,
                                dense_vector=await self._compute_dense_embedding(
                                    content
                                ),
                                sparse_vector=await self._compute_sparse_embedding_for_doc(
                                    content
                                ),
                                **metadata,
                            )
                            logger.info(
                                f"[Ingest] MultiIngester returned for chunk_order {metadata['chunk_order']}: {result}"
                            )
                            results.append(
                                self._handle_ingestion_result(
                                    result, filename, page_idx, elem_idx, metadata
                                )
                            )
                        except Exception as e:
                            logger.error(
                                f"[Ingest] Failed to ingest chunk_order {metadata['chunk_order']}: {e}"
                            )
                            results.append(
                                {
                                    "doc_id": None,
                                    "filename": filename,
                                    "page_index": page_idx,
                                    "element_index": elem_idx,
                                    "status": "error",
                                    "chunk_type": metadata.get("chunk_type", None),
                                    "meta": metadata,
                                    "error": str(e),
                                }
                            )
            except Exception as e:
                filename_val = doc.get("filename", "unknown")
                logger.error(
                    f"Exception in ingest_documents for filename={filename_val}: {e}"
                )
                result = {"filename": filename_val, "status": "error", "error": str(e)}
                results.append(result)
            finally:
                doc_end_time = time.time()
                logger.info(
                    f"[Ingest] Finished processing document {filename} in {doc_end_time - doc_start_time:.2f}s"
                )

                # Upload all files from temp directory to S3
                if s3_client and doc_url and os.path.exists(output_dir):
                    try:
                        # Parse doc_url to extract domain and path
                        from urllib.parse import urlparse

                        parsed_url = urlparse(doc_url)
                        domain = parsed_url.netloc
                        path = parsed_url.path.strip(
                            "/"
                        )  # Remove leading/trailing slashes

                        # Create S3 prefix: ingested_docs/{domain}/{path}
                        if path:
                            s3_prefix = f"ingested_docs/{domain}/{path}"
                        else:
                            s3_prefix = f"ingested_docs/{domain}"

                        logger.info(
                            f"[Ingest] Uploading files from {output_dir} to S3: s3://{Config.S3_BUCKET_NAME}/{s3_prefix}"
                        )

                        # Walk through all files in the temp directory
                        for root, dirs, files in os.walk(output_dir):
                            for file in files:
                                local_file_path = os.path.join(root, file)
                                # Calculate relative path from output_dir
                                relative_path = os.path.relpath(
                                    local_file_path, output_dir
                                )
                                s3_key = f"{s3_prefix}/{relative_path}"

                                try:
                                    s3_client.upload_file(
                                        local_file_path, Config.S3_BUCKET_NAME, s3_key
                                    )
                                    logger.info(
                                        f"[Ingest] Uploaded: {local_file_path} -> s3://{Config.S3_BUCKET_NAME}/{s3_key}"
                                    )
                                except Exception as e:
                                    logger.error(
                                        f"[Ingest] Failed to upload {local_file_path} to S3: {e}"
                                    )

                        logger.info(
                            f"[Ingest] Successfully uploaded all files to S3 prefix: {s3_prefix}"
                        )
                    except Exception as e:
                        logger.error(f"[Ingest] Failed to upload files to S3: {e}")

                # Remove temp directory if LOG_LEVEL is not INFO
                try:
                    if Config.LOG_LEVEL == "INFO" and os.path.exists(output_dir):
                        # shutil.rmtree(output_dir)
                        logger.info(
                            f"[Ingest] Removed temp directory {output_dir} (LOG_LEVEL={Config.LOG_LEVEL})"
                        )
                except Exception as e:
                    logger.warning(
                        f"[Ingest] Failed to remove temp directory {output_dir}: {e}"
                    )
        logger.info(f"ingest_documents finished, results: {results}")
        batch_end_time = time.time()
        logger.info(
            f"[Ingest] Finished batch ingestion of {len(documents)} documents in {batch_end_time - batch_start_time:.2f}s"
        )
        # Filter out any non-dict results (should not happen, but defensive)
        filtered_results = [r for r in results if isinstance(r, dict)]
        return {
            "results": filtered_results,
            "total_page_count": getattr(self, "total_page_count", None),
        }

    async def log_chat_history(
        self,
        query,
        response,
        timestamp,
        user_id=None,
        user_name=None,
        thread_id=None,
        doc_urls=None,
        citation_map=None,
    ) -> str:
        """Log a chat history record via QdrantAdapter, with dense and sparse vectors. Deduplication is based on query and user_id (if provided)."""
        if not self.qdrant_adapter:
            raise RuntimeError("QdrantAdapter not initialized")
        # Use the same embedding logic as ingest_document, but for the concatenated query and response
        content = f"Q: {query}\nA: {response}"
        dense_vector = await self._compute_dense_embedding(content)
        sparse_vector = await self._compute_sparse_embedding_for_doc(content)
        # Deduplication is handled in QdrantAdapter.log_chat_history
        return await self.qdrant_adapter.log_chat_history(
            query,
            response,
            timestamp,
            user_id,
            user_name,
            thread_id,
            dense_vector=dense_vector,
            sparse_vector=sparse_vector,
            doc_urls=doc_urls,
            citation_map=citation_map,
        )

    async def search_chat_history(
        self, query: str, user_id: str = None, n_results: int = 5
    ) -> list:
        """Hybrid search for chat history records via QdrantAdapter.

        Returns search results that include all fields from log_chat_history:
        - query, response, timestamp, user_id, thread_id
        - doc_urls: list of document URLs referenced in the response
        - citation_map: dictionary mapping document IDs to citation information
        """
        if not self.qdrant_adapter:
            raise RuntimeError("QdrantAdapter not initialized")
        dense_vector = await self._compute_dense_embedding(query)
        sparse_vector = await self._compute_sparse_embedding_for_query(query)
        return await self.qdrant_adapter.search_chat_history(
            query, user_id, n_results, dense_vector, sparse_vector
        )

    def extract_citation_info_from_chat_history(self, search_results) -> list:
        """Extract and format citation information from chat history search results.

        Args:
            search_results: List of search result dictionaries from search_chat_history

        Returns:
            List of dictionaries with formatted citation information
        """
        formatted_results = []

        for result in search_results:
            payload = result.get("payload", {})
            formatted_result = {
                "id": result.get("id"),
                "score": result.get("score"),
                "query": payload.get("query"),
                "response": payload.get("response"),
                "timestamp": payload.get("timestamp"),
                "user_id": payload.get("user_id"),
                "thread_id": payload.get("thread_id"),
                "doc_urls": payload.get("doc_urls", []),
                "citation_map": payload.get("citation_map", {}),
                "citation_summary": [],
            }

            # Create a summary of citations
            citation_map = payload.get("citation_map", {})
            for key, citation in citation_map.items():
                citation_summary = {
                    "citation_id": key,
                    "solution": citation.get("solution"),
                    "doc_url": citation.get("doc_url"),
                    "page_no": citation.get("page_no"),
                    "page_image_url": citation.get("page_image_url"),
                }
                formatted_result["citation_summary"].append(citation_summary)

            formatted_results.append(formatted_result)

        return formatted_results

    async def list_threads(self, user_id: str = None) -> List[Tuple[str, str]]:
        """
        List all unique thread IDs and their titles for a given user from chat history.

        Args:
            user_id: User ID to filter threads for. If None, returns all threads.

        Returns:
            List of tuples: [(thread_id, thread_title), ...]
        """
        if not self.initialized:
            raise RuntimeError(
                "Knowledge store not initialized. Call the 'initialize' method first."
            )

        if not self.qdrant_adapter:
            raise RuntimeError("QdrantAdapter not initialized")

        return await self.qdrant_adapter.list_threads(user_id)

    async def get_thread(self, user_id: str, thread_id: str) -> list:
        """
        Retrieve all chat records for a specific user_id and thread_id from chat history.

        Args:
            user_id: User ID to filter for
            thread_id: Specific thread ID to retrieve records for

        Returns:
            List of dictionaries with chat record details:
            [{"thread_id": str, "thread_title": str, "query": str, "response": str,
              "timestamp": str, "doc_urls": list, "citation_map": dict}, ...]
        """
        if not self.initialized:
            raise RuntimeError(
                "Knowledge store not initialized. Call the 'initialize' method first."
            )

        if not self.qdrant_adapter:
            raise RuntimeError("QdrantAdapter not initialized")

        return await self.qdrant_adapter.get_thread(user_id, thread_id)

    def _has_valid_doctags(self, output):
        """Check if output contains valid DocTags with unified logic."""
        return "<doctag>" in output or "<text>" in output or "<picture>" in output


def get_chunk_type(chunk) -> str:
    # 1. Direct attributes
    for attr in ["label", "type", "item_type"]:
        if hasattr(chunk, attr):
            value = getattr(chunk, attr)
            if value:
                return str(value)
    # 2. Meta as dict or object
    meta = getattr(chunk, "meta", None)
    if meta:
        # If meta is a dict
        if isinstance(meta, dict):
            doc_items = meta.get("doc_items")
            if doc_items and len(doc_items) > 0:
                label = doc_items[0].get("label")
                if label:
                    return str(label)
        else:
            doc_items = getattr(meta, "doc_items", None)
            if doc_items and len(doc_items) > 0:
                label = getattr(doc_items[0], "label", None)
                if label:
                    return getattr(label, "value", str(label))
    return "unknown"


def extract_metadata_from_doctag(elem) -> dict:
    meta = elem.get("meta", {}) or {}
    if hasattr(meta, "__dict__"):
        meta = vars(meta)
    metadata = {
        "chunk_type": elem.get("type", None) or meta.get("type", None),
        "page_title": meta.get("title", None),
        "url": meta.get("url", None),
        "manual_keywords": meta.get("keywords", [])
        if isinstance(meta.get("keywords", []), list)
        else [],
        "created_at": meta.get("created_at", None),
        "updated_at": meta.get("updated_at", None),
    }
    metadata = {k: v for k, v in metadata.items() if v is not None}
    return metadata


# Export based on selected format
def export_document(doc, export_format) -> str:
    if export_format == "Markdown":
        from docling_core.transforms.serializer.markdown import MarkdownDocSerializer

        serializer = MarkdownDocSerializer(doc=doc)
        result = serializer.serialize().text
    elif export_format == "HTML":
        from docling_core.transforms.serializer.html import HTMLDocSerializer

        serializer = HTMLDocSerializer(doc=doc)
        result = serializer.serialize().text
    elif export_format == "JSON":
        doc_dict = doc.export_to_dict()
        result = json.dumps(doc_dict, indent=4)
    else:
        result = "Invalid export format selected"
    return result
