import logging
from typing import List, Optional, Tuple
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    PointStruct,
    SparseVector,
    VectorParams,
    Distance,
    SparseVectorParams,
    QueryRequest,  # Use QueryRequest instead of SearchRequest
)
from .utils import prepare_metadata, KEYWORD_EXTRACTORS, create_document_id
import torch
import numpy as np
from zmp_knowledge_store.config import Config
from sklearn.cluster import DBSCAN

logger = logging.getLogger(__name__)


def reciprocal_rank_fusion(
    dense_scores: dict, sparse_scores: dict, k: int = 60
) -> dict:
    """
    Manual implementation of Reciprocal Rank Fusion (RRF).

    Args:
        dense_scores: Dictionary of {doc_id: score} for dense search results
        sparse_scores: Dictionary of {doc_id: score} for sparse search results
        k: Constant for RRF (default 60)

    Returns:
        Dictionary of {doc_id: fused_score} sorted by score descending
    """
    # Get all unique document IDs
    all_docs = set(dense_scores.keys()) | set(sparse_scores.keys())

    # Create rank dictionaries (1-based ranking)
    dense_ranks = {
        doc_id: rank
        for rank, doc_id in enumerate(
            sorted(dense_scores.keys(), key=lambda x: dense_scores[x], reverse=True), 1
        )
    }
    sparse_ranks = {
        doc_id: rank
        for rank, doc_id in enumerate(
            sorted(sparse_scores.keys(), key=lambda x: sparse_scores[x], reverse=True),
            1,
        )
    }

    # Calculate RRF scores
    fused_scores = {}
    for doc_id in all_docs:
        dense_rank = dense_ranks.get(doc_id, float("inf"))
        sparse_rank = sparse_ranks.get(doc_id, float("inf"))

        # RRF formula: 1 / (k + rank)
        rrf_score = (1 / (k + dense_rank)) + (1 / (k + sparse_rank))
        fused_scores[doc_id] = rrf_score

    return fused_scores


class QdrantAdapter:
    """
    Qdrant adapter for chatbot knowledge base with hybrid (dense + sparse) support.
    Metadata is prepared using consistent logic for document processing.
    """

    def __init__(self):
        self.client: Optional[AsyncQdrantClient] = None
        self.collection_name = Config.DOCUMENT_COLLECTION

    async def ainit(self) -> None:
        """Asynchronously initializes the Qdrant client."""
        await self._ainitialize_client()

    async def _acreate_collection_if_not_exists(
        self, collection_name, vectors_config, sparse_vectors_config=None
    ) -> None:
        """Creates the specified collection if it doesn't already exist, with given vector configs."""
        if not self.client:
            logger.error("Qdrant client not initialized. Cannot create collection.")
            return
        try:
            collections = (await self.client.get_collections()).collections
            if collection_name not in [c.name for c in collections]:
                logger.info(f"Collection '{collection_name}' not found. Creating...")
                await self.client.recreate_collection(
                    collection_name=collection_name,
                    vectors_config=vectors_config,
                    sparse_vectors_config=sparse_vectors_config,
                )
                logger.info(f"✅ Collection '{collection_name}' created.")
            else:
                logger.info(f"✅ Collection '{collection_name}' already exists.")
        except Exception as e:
            logger.error(
                f"❌ Failed to create or check collection '{collection_name}': {e}"
            )

    async def _ainitialize_client(self) -> None:
        """Initializes the Qdrant client and ensures the collection exists."""
        try:
            self.client = AsyncQdrantClient(
                host=Config.QDRANT_HOST,
                port=Config.QDRANT_PORT,
                api_key=Config.QDRANT_API_KEY,
                https=False,
            )
            logger.info("✅ Qdrant async client initialized.")
            await self._acreate_collection_if_not_exists(
                collection_name=self.collection_name,
                vectors_config={
                    "dense": VectorParams(size=768, distance=Distance.COSINE)
                },
                sparse_vectors_config={"sparse": SparseVectorParams()},
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize Qdrant async client: {e}")
            self.client = None

    async def ensure_chat_history_collection_exists(self) -> None:
        """Ensure the chat history collection exists with dense and sparse vectors."""
        if not self.client:
            await self._ainitialize_client()
        await self._acreate_collection_if_not_exists(
            collection_name=Config.CHAT_HISTORY_COLLECTION,
            vectors_config={"dense": VectorParams(size=768, distance=Distance.COSINE)},
            sparse_vectors_config={"sparse": SparseVectorParams()},
        )

    async def ensure_collection_exists(self, collection_name: str) -> None:
        """
        Ensure the specified collection exists. If not, create it using template configs
        from an existing collection or fallback to default configs.

        Args:
            collection_name: Name of the collection to ensure exists
        """
        if not self.client:
            await self._ainitialize_client()

        try:
            # Check if collection already exists
            collections = (await self.client.get_collections()).collections
            if collection_name in [c.name for c in collections]:
                logger.info(f"✅ Collection '{collection_name}' already exists.")
                return

            logger.info(
                f"Collection '{collection_name}' not found. Creating with template configs..."
            )

            # Get template configs from existing collection or use defaults
            template_vectors_config = None
            template_sparse_vectors_config = None

            # Try to get configs from default collection first
            if self.collection_name in [c.name for c in collections]:
                try:
                    collection_info = await self.client.get_collection(
                        self.collection_name
                    )
                    template_vectors_config = collection_info.config.params.vectors
                    template_sparse_vectors_config = (
                        collection_info.config.params.sparse_vectors
                    )
                    logger.info(
                        f"Using vector configs from template collection '{self.collection_name}'"
                    )
                except Exception as e:
                    logger.warning(
                        f"Could not get configs from '{self.collection_name}': {e}"
                    )

            # If no template found, try any existing collection
            if template_vectors_config is None and collections:
                for collection_desc in collections:
                    try:
                        collection_info = await self.client.get_collection(
                            collection_desc.name
                        )
                        if collection_info.config.params.vectors:
                            template_vectors_config = (
                                collection_info.config.params.vectors
                            )
                            template_sparse_vectors_config = (
                                collection_info.config.params.sparse_vectors
                            )
                            logger.info(
                                f"Using vector configs from template collection '{collection_desc.name}'"
                            )
                            break
                    except Exception as e:
                        logger.warning(
                            f"Could not get configs from '{collection_desc.name}': {e}"
                        )
                        continue

            # Fallback to hardcoded default configs if no template found
            if template_vectors_config is None:
                template_vectors_config = {
                    "dense": VectorParams(size=768, distance=Distance.COSINE)
                }
                template_sparse_vectors_config = {"sparse": SparseVectorParams()}
                logger.info("Using hardcoded default vector configs")

            # Create the collection with template configs
            await self._acreate_collection_if_not_exists(
                collection_name=collection_name,
                vectors_config=template_vectors_config,
                sparse_vectors_config=template_sparse_vectors_config,
            )

        except Exception as e:
            logger.error(
                f"❌ Failed to ensure collection '{collection_name}' exists: {e}"
            )
            raise

    async def log_chat_history(
        self,
        query,
        response,
        timestamp,
        user_id=None,
        user_name=None,
        thread_id=None,
        dense_vector=None,
        sparse_vector=None,
        doc_urls=None,
        citation_map=None,
    ) -> str:
        """Insert a chat history record into the chat history collection with dense and sparse vectors, using a deterministic hash for deduplication."""
        await self.ensure_chat_history_collection_exists()
        payload = {
            "query": query,
            "response": response,
            "timestamp": timestamp,
        }
        if user_id is not None:
            payload["user_id"] = user_id
        if user_name is not None:
            payload["user_name"] = user_name
        if thread_id is not None:
            payload["thread_id"] = thread_id
        if doc_urls is not None:
            payload["doc_urls"] = doc_urls
        if citation_map is not None:
            payload["citation_map"] = citation_map
        # Prepare vector dict as in ingest_document
        vector_dict = {"dense": dense_vector}
        # --- Consistent sparse vector handling ---
        if sparse_vector is not None:
            from qdrant_client.models import SparseVector

            if isinstance(sparse_vector, dict):
                indices = list(sparse_vector.keys())
                values = list(sparse_vector.values())
                sparse_vector = SparseVector(indices=indices, values=values)
            if (
                getattr(sparse_vector, "indices", None)
                and len(sparse_vector.indices) > 0
            ):
                vector_dict["sparse"] = sparse_vector
        # --- Deterministic ID for deduplication ---
        from zmp_knowledge_store.utils import create_document_id

        # Build a minimal metadata dict for hashing
        hash_metadata = {"query": query}
        if user_id is not None:
            hash_metadata["user_id"] = user_id
        if thread_id is not None:
            hash_metadata["thread_id"] = thread_id
        point_id = create_document_id("chat_history", hash_metadata)
        await self.client.upsert(
            collection_name=Config.CHAT_HISTORY_COLLECTION,
            points=[
                PointStruct(
                    id=point_id,
                    payload=payload,
                    vector=vector_dict,
                )
            ],
        )
        logger.info(f"✅ Logged chat history: {point_id}")
        return point_id

    async def ingest_document(
        self,
        content: str,
        page_title: str = None,
        solution: str = "zmp",
        page_no: int = None,
        chunk_order: int = None,
        doc_url: str = "",
        manual_keywords: list = None,
        embedded_images: list = None,
        assets_s3_keys: list = None,
        chunk_type: str = "single",
        dense_vector: list = None,
        sparse_vector: dict = None,
        created_at: str = None,
        updated_at: str = None,
        original_created_at: str = None,
        collection_name: str = None,
    ) -> str:
        """
        Ingest a single document with both dense and sparse vectors.
        Metadata is prepared using the shared prepare_metadata utility.

        Args:
            collection_name: Collection to ingest into. If None, uses default collection.
        """
        # Determine which collection to use
        target_collection = collection_name if collection_name else self.collection_name

        # Ensure the target collection exists (and create if needed)
        if collection_name:  # Only validate custom collections
            await self.ensure_collection_exists(collection_name)

        # Convert sparse_vector to Qdrant SparseVector if needed
        if sparse_vector is not None:
            if isinstance(sparse_vector, dict):
                indices = list(sparse_vector.keys())
                values = list(sparse_vector.values())
                sparse_vector = SparseVector(indices=indices, values=values)
            elif isinstance(sparse_vector, torch.Tensor):
                nonzero = sparse_vector.nonzero(as_tuple=True)[0]
                values = sparse_vector[nonzero]
                indices = nonzero.tolist()
                values = values.tolist()
                sparse_vector = SparseVector(indices=indices, values=values)
        # Build vector dict for Qdrant
        vector_dict = {"dense": dense_vector}
        if sparse_vector is not None and getattr(sparse_vector, "indices", None):
            if len(sparse_vector.indices) > 0:
                vector_dict["sparse"] = sparse_vector
        metadata_for_hash = prepare_metadata(
            solution=solution,
            page_title=page_title,
            page_no=page_no,
            chunk_order=chunk_order,
            content=content,
            doc_url=doc_url,
            manual_keywords=manual_keywords,
            embedded_images=embedded_images,
            assets_s3_keys=assets_s3_keys,
            chunk_type=chunk_type,
            created_at=None,
            updated_at=None,
            keyword_extractors=KEYWORD_EXTRACTORS,
        )
        import json as _json

        logger.info(f"[DEBUG][Qdrant] create_document_id content: {repr(content)}")
        logger.info(
            f"[DEBUG][Qdrant] create_document_id metadata: {_json.dumps(metadata_for_hash, sort_keys=True, ensure_ascii=False)}"
        )
        doc_id = create_document_id(content, metadata_for_hash)

        # The payload for Qdrant should include the content.
        payload = metadata_for_hash.copy()
        payload["content"] = content

        # Preserve original created_at if document exists
        existing = await self.client.retrieve(
            collection_name=target_collection, ids=[doc_id], with_payload=True
        )
        if existing and existing[0].payload and existing[0].payload.get("created_at"):
            created_at_to_use = existing[0].payload["created_at"]
        else:
            created_at_to_use = created_at
        payload["created_at"] = created_at_to_use
        payload["updated_at"] = updated_at

        # Add warning if sparse vector is missing or empty
        if (
            sparse_vector is None
            or not getattr(sparse_vector, "indices", None)
            or len(sparse_vector.indices) == 0
        ):
            logger.warning(
                f"[QdrantAdapter] No sparse vector for doc_id {doc_id} (content length: {len(content)})"
            )

        try:
            await self.client.upsert(
                collection_name=target_collection,
                points=[
                    PointStruct(
                        id=doc_id,
                        payload=payload,
                        vector=vector_dict,
                    )
                ],
            )
            logger.info(f"✅ Ingested doc_id: {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"❌ Failed to ingest doc_id {doc_id}: {e}")
            raise

    @staticmethod
    def _dbsf_normalize(scores_dict) -> dict:
        """
        Normalize a dict of {doc_id: score} using DBSF (min-max with 3 std from mean).
        """
        if not scores_dict:
            return {}
        values = np.array(list(scores_dict.values()))
        # if values.size == 0:
        #     return {k: 0.0 for k in scores_dict}
        mean = values.mean()
        std = values.std()
        lower = max(values.min(), mean - 3 * std)
        upper = min(values.max(), mean + 3 * std)
        if upper == lower:
            return {k: 0.0 for k in scores_dict}
        return {k: (v - lower) / (upper - lower) for k, v in scores_dict.items()}

    async def query(
        self,
        dense_vector: List[float],
        sparse_vector: dict,
        limit: int = 5,
        collection_name: str = None,
    ) -> list:
        """
        Performs a hybrid search in the specified Qdrant collection using search_batch API and fuses results with DBSF normalization + Ranx RRF.
        Returns a list of fused results (dicts with id, score, payload).

        Args:
            dense_vector: Dense vector for search
            sparse_vector: Sparse vector dict with indices and values
            limit: Number of results to return
            collection_name: Collection to search in. If None, uses default collection.
        """
        if not self.client:
            await self._ainitialize_client()

        # Determine which collection to use
        target_collection = collection_name if collection_name else self.collection_name

        # Ensure the target collection exists (and create if needed)
        if collection_name:  # Only validate custom collections
            await self.ensure_collection_exists(collection_name)

        try:
            # Prepare the sparse vector object
            sparse_vec = SparseVector(
                indices=sparse_vector["indices"],
                values=sparse_vector["values"],
            )

            # Prepare the batch query requests (use QueryRequest, not SearchRequest)
            requests = [
                QueryRequest(
                    query=dense_vector,
                    using="dense",  # Specify the vector name for dense
                    limit=limit,
                    with_payload=True,  # Ensure payload is returned
                ),
                QueryRequest(
                    query=sparse_vec,
                    using="sparse",  # Specify the vector name for sparse
                    limit=limit,
                    with_payload=True,  # Ensure payload is returned
                ),
            ]

            # Perform the batch query using query_batch_points (not search_batch)
            results = await self.client.query_batch_points(
                collection_name=target_collection, requests=requests
            )

            # Each result is a QueryResponse object with a .points attribute
            dense_hits = results[0].points
            sparse_hits = results[1].points

            # Convert Qdrant hits to dict for normalization
            def hits_to_scores_dict(hits):
                return {str(hit.id): float(hit.score) for hit in hits}

            dense_scores = self._dbsf_normalize(hits_to_scores_dict(dense_hits))
            sparse_scores = self._dbsf_normalize(hits_to_scores_dict(sparse_hits))

            # Fuse using manual RRF (Reciprocal Rank Fusion)
            fused_scores = reciprocal_rank_fusion(dense_scores, sparse_scores)

            # Build a lookup for payloads by doc_id for efficient access
            payload_lookup = {str(h.id): h.payload for h in dense_hits + sparse_hits}

            # Get fused results sorted by score descending
            fused_results = [
                {"id": doc_id, "score": score, "payload": payload_lookup.get(doc_id)}
                for doc_id, score in fused_scores.items()
            ]
            fused_results.sort(key=lambda x: x["score"], reverse=True)
            return fused_results[:limit]

        except Exception as e:
            logger.error(f"❌ Hybrid search or fusion failed: {e}")

            return []

    async def search_chat_history(
        self,
        query: str,
        user_id: str = None,
        n_results: int = 5,
        dense_vector=None,
        sparse_vector=None,
    ) -> list:
        """Hybrid search for chat history records using provided dense+sparse vectors and optional user_id filter.

        Returns search results with payload containing all chat history fields:
        - query, response, timestamp, user_id, thread_id
        - doc_urls: list of document URLs referenced in the response
        - citation_map: dictionary mapping document IDs to citation information
        """
        # Build filter for user_id if provided
        filter_ = None
        if user_id:
            from qdrant_client.http.models import Filter, FieldCondition, MatchValue

            filter_ = Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
            )

        # Prepare the sparse vector object
        # from qdrant_client.models import SparseVector
        sparse_vec = (
            SparseVector(
                indices=sparse_vector["indices"],
                values=sparse_vector["values"],
            )
            if sparse_vector and sparse_vector.get("indices")
            else None
        )

        # Prepare the batch query requests (use QueryRequest, not SearchRequest)
        # from qdrant_client.models import QueryRequest
        requests = [
            QueryRequest(
                query=dense_vector,
                using="dense",
                limit=n_results,
                with_payload=True,
                filter=filter_,
            ),
        ]
        if sparse_vec:
            requests.append(
                QueryRequest(
                    query=sparse_vec,
                    using="sparse",
                    limit=n_results,
                    with_payload=True,
                    filter=filter_,
                )
            )

        # Perform the batch query using query_batch_points
        results = await self.client.query_batch_points(
            collection_name=Config.CHAT_HISTORY_COLLECTION, requests=requests
        )

        # Each result is a QueryResponse object with a .points attribute
        dense_hits = results[0].points
        sparse_hits = results[1].points if len(results) > 1 else []

        # Convert Qdrant hits to dict for normalization
        def hits_to_scores_dict(hits):
            return {str(hit.id): float(hit.score) for hit in hits}

        dense_scores = self._dbsf_normalize(hits_to_scores_dict(dense_hits))
        sparse_scores = self._dbsf_normalize(hits_to_scores_dict(sparse_hits))

        # Fuse using manual RRF (Reciprocal Rank Fusion)
        fused_scores = reciprocal_rank_fusion(dense_scores, sparse_scores)

        # Build a lookup for payloads by doc_id for efficient access
        payload_lookup = {str(h.id): h.payload for h in dense_hits + sparse_hits}

        # Get fused results sorted by score descending
        fused_results = [
            {"id": doc_id, "score": score, "payload": payload_lookup.get(doc_id)}
            for doc_id, score in fused_scores.items()
        ]
        fused_results.sort(key=lambda x: x["score"], reverse=True)
        # --- Cluster results by score and only return those in the same cluster as the top result ---
        if fused_results:
            try:
                scores = np.array([[r["score"]] for r in fused_results])
                # eps can be tuned; 0.05 is a reasonable starting point for normalized scores
                clustering = DBSCAN(eps=0.01, min_samples=1).fit(scores)
                labels = clustering.labels_
                top_label = labels[0]
                clustered_results = [
                    r for r, label in zip(fused_results, labels) if label == top_label
                ]
                filtered_out = [
                    r for r, label in zip(fused_results, labels) if label != top_label
                ]
                if filtered_out:
                    logger.info(
                        f"[Clustering] Filtered out {len(filtered_out)} results for query: {query}"
                    )
                    for r in filtered_out:
                        logger.info(
                            f"[Clustering][Filtered] Score: {r['score']:.4f}, Payload: {r['payload']}"
                        )
                # Always return at least the top result
                if not clustered_results:
                    clustered_results = fused_results[:1]
                # Log cluster label for every result
                for r, label in zip(fused_results, labels):
                    logger.info(
                        f"[Clustering][Label] Score: {r['score']:.4f}, Label: {label}, Payload: {r['payload']}"
                    )
                # Return clustered results directly (semantic similarity filtering removed due to circular import)
                return clustered_results[:n_results]
            except Exception as e:
                logger.warning(
                    f"Clustering or semantic similarity filtering failed, falling back to top result only: {e}"
                )
                return fused_results[:1]
        else:
            return []

    async def get_all_document_ids(
        self, collection_name: str = "solution-docs"
    ) -> List[str]:
        if not self.client:
            await self._ainitialize_client()

        try:
            # Scroll API might need to be paginated for very large collections
            points, _ = await self.client.scroll(
                collection_name=collection_name, limit=1000
            )
            return [str(point.id) for point in points]
        except Exception as e:
            logger.error(f"❌ Failed to get all document IDs: {e}")
            return []

    async def list_threads(self, user_id: str = None) -> List[Tuple[str, str]]:
        """
        Retrieve list of unique thread_ids and their titles for a given user from chat history collection.

        Args:
            user_id: User ID to filter threads for. If None, returns all threads.

        Returns:
            List of tuples: [(thread_id, thread_title), ...]
        """
        if not self.client:
            await self._ainitialize_client()

        await self.ensure_chat_history_collection_exists()

        try:
            # Build filter for user_id if provided
            filter_ = None
            if user_id:
                from qdrant_client.http.models import Filter, FieldCondition, MatchValue

                filter_ = Filter(
                    must=[
                        FieldCondition(key="user_id", match=MatchValue(value=user_id))
                    ]
                )

            # Get all records from chat history collection
            # For large collections, you might need pagination
            points, _ = await self.client.scroll(
                collection_name=Config.CHAT_HISTORY_COLLECTION,
                scroll_filter=filter_,
                limit=1000,
                with_payload=True,
            )

            # Extract unique thread_ids and create thread titles
            threads = {}
            for point in points:
                payload = point.payload
                thread_id = payload.get("thread_id")

                if thread_id:
                    # Extract thread title from thread_id
                    # Pattern: thread_{title}_{hash} -> extract {title}
                    thread_title = self._extract_thread_title(thread_id)
                    threads[thread_id] = thread_title

            # Convert to list of tuples and sort by thread_id for consistent ordering
            thread_list = [(thread_id, title) for thread_id, title in threads.items()]
            thread_list.sort(key=lambda x: x[0])

            logger.info(
                f"✅ Found {len(thread_list)} unique threads for user_id: {user_id}"
            )
            return thread_list

        except Exception as e:
            logger.error(f"❌ Failed to list threads for user_id {user_id}: {e}")
            return []

    def _extract_thread_title(self, thread_id: str) -> str:
        """
        Extract thread title from thread_id.

        Pattern: thread_{title}_{hash} -> extract {title}
        Example: "thread_amdp_definition_9101" -> "amdp_definition"

        Args:
            thread_id: The thread ID string

        Returns:
            Extracted thread title or original thread_id if pattern doesn't match
        """
        import re

        # Pattern to match thread_{title}_{hash}
        pattern = r"^thread_(.+?)_\d+$"
        match = re.match(pattern, thread_id)

        if match:
            return match.group(1)
        else:
            # If pattern doesn't match, return the original thread_id
            logger.warning(f"Thread ID doesn't match expected pattern: {thread_id}")
            return thread_id

    async def get_thread(self, user_id: str, thread_id: str) -> list:
        """
        Retrieve all chat records for a specific user_id and thread_id from chat history collection.

        Args:
            user_id: User ID to filter for
            thread_id: Specific thread ID to retrieve records for

        Returns:
            List of dictionaries with chat record details:
            [{"thread_id": str, "thread_title": str, "query": str, "response": str,
              "timestamp": str, "doc_urls": list, "citation_map": dict}, ...]
        """
        if not self.client:
            await self._ainitialize_client()

        await self.ensure_chat_history_collection_exists()

        try:
            # Build filter for both user_id and thread_id
            from qdrant_client.http.models import Filter, FieldCondition, MatchValue

            conditions = []
            if user_id:
                conditions.append(
                    FieldCondition(key="user_id", match=MatchValue(value=user_id))
                )
            if thread_id:
                conditions.append(
                    FieldCondition(key="thread_id", match=MatchValue(value=thread_id))
                )

            filter_ = Filter(must=conditions) if conditions else None

            # Get all records matching the filter
            points, _ = await self.client.scroll(
                collection_name=Config.CHAT_HISTORY_COLLECTION,
                scroll_filter=filter_,
                limit=1000,  # Should be sufficient for a single thread
                with_payload=True,
            )

            # Process results and extract chat record details
            chat_records = []
            for point in points:
                payload = point.payload

                # Extract thread title from thread_id
                thread_title = self._extract_thread_title(payload.get("thread_id", ""))

                record = {
                    "thread_id": payload.get("thread_id"),
                    "thread_title": thread_title,
                    "query": payload.get("query"),
                    "response": payload.get("response"),
                    "timestamp": payload.get("timestamp"),
                    "doc_urls": payload.get("doc_urls", []),
                    "citation_map": payload.get("citation_map", {}),
                }
                chat_records.append(record)

            # Sort by timestamp if available (newest first for conversation order)
            chat_records.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            logger.info(
                f"✅ Found {len(chat_records)} chat records in thread {thread_id} for user_id: {user_id}"
            )
            return chat_records

        except Exception as e:
            logger.error(
                f"❌ Failed to get thread for user_id {user_id}, thread_id {thread_id}: {e}"
            )
            return []
