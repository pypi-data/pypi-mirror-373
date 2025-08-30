"""
Vector database abstraction layer for Smriti Memory.

This module provides a unified interface for different vector database providers,
allowing easy switching between Pinecone, Qdrant, Weaviate, Chroma, FAISS, and SQLite.
"""

import logging
import os
import pickle
import sqlite3
import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
import numpy as np
import json

# Optional imports for different vector databases
try:
    from pinecone import (
        Pinecone,
        ServerlessSpec,
        CloudProvider,
        AwsRegion,
        VectorType
    )
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

try:
    import qdrant_client
    from qdrant_client.http.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from .exceptions import VectorDBError, ConfigurationError

logger = logging.getLogger(__name__)


@dataclass
class VectorDBConfig:
    """Configuration for vector database."""
    provider: str  # 'pinecone', 'qdrant', 'weaviate', 'chroma', 'faiss', 'sqlite'
    
    # Common settings
    embedding_dimension: int = 768
    similarity_metric: str = "cosine"  # 'cosine', 'euclidean', 'dot_product'
    
    # Provider-specific settings
    api_key: Optional[str] = None
    environment: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    collection_name: str = "smriti_memories"
    
    # Performance settings
    batch_size: int = 100
    timeout: int = 30
    max_retries: int = 3
    
    # Local storage settings (for FAISS, SQLite)
    storage_path: str = "./smriti_data"
    
    # Additional provider-specific parameters
    provider_kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryRecord:
    """Represents a memory record in the vector database."""
    id: str
    text: str
    embedding: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    namespace: Optional[str] = None
    score: Optional[float] = None  # Similarity score from search


class BaseVectorStore(ABC):
    """Abstract base class for vector database providers."""
    
    def __init__(self, config: VectorDBConfig):
        self.config = config
        self.embedding_dimension = config.embedding_dimension
    
    @abstractmethod
    def create_index(self, index_name: str) -> bool:
        """Create an index/collection."""
        pass
    
    @abstractmethod
    def delete_index(self, index_name: str) -> bool:
        """Delete an index/collection."""
        pass
    
    @abstractmethod
    def index_exists(self, index_name: str) -> bool:
        """Check if index/collection exists."""
        pass
    
    @abstractmethod
    def upsert_memories(self, index_name: str, memories: List[MemoryRecord]) -> Dict[str, Any]:
        """Insert or update memory records."""
        pass
    
    @abstractmethod
    def search_memories(
        self, 
        index_name: str, 
        query_embedding: List[float],
        top_k: int = 10,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[MemoryRecord]:
        """Search for similar memories."""
        pass
    
    @abstractmethod
    def delete_memories(
        self, 
        index_name: str,
        memory_ids: Optional[List[str]] = None,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Delete memories by IDs, namespace, or filters."""
        pass
    
    @abstractmethod
    def get_stats(self, index_name: str) -> Dict[str, Any]:
        """Get statistics about the index."""
        pass


class PineconeVectorStore(BaseVectorStore):
    """Pinecone vector database implementation."""
    
    def __init__(self, config: VectorDBConfig):
        if not PINECONE_AVAILABLE:
            raise VectorDBError("Pinecone package not available. Install with: pip install pinecone")
        
        super().__init__(config)
        api_key = config.api_key or os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ConfigurationError("Pinecone API key is required")
        
        self.client = Pinecone(api_key=api_key)
        self.environment = config.environment or "us-east-1"
    
    def create_index(self, index_name: str) -> bool:
        """Create a Pinecone index."""
        try:
            if not self.client.has_index(index_name):
                # Use the new Pinecone API format with spec parameter for region
                self.client.create_index(
                    name=index_name,
                    dimension=self.embedding_dimension,
                    spec=ServerlessSpec(
                        cloud=CloudProvider.AWS,
                        region=AwsRegion.US_EAST_1
                    ),
                    vector_type=VectorType.DENSE
                )
                logger.info(f"Created Pinecone index: {index_name}")
                return True
            return False
        except Exception as e:
            raise VectorDBError(f"Failed to create Pinecone index {index_name}: {str(e)}")
    
    def delete_index(self, index_name: str) -> bool:
        """Delete a Pinecone index."""
        try:
            if self.client.has_index(index_name):
                self.client.delete_index(index_name)
                logger.info(f"Deleted Pinecone index: {index_name}")
                return True
            return False
        except Exception as e:
            raise VectorDBError(f"Failed to delete Pinecone index {index_name}: {str(e)}")
    
    def index_exists(self, index_name: str) -> bool:
        """Check if Pinecone index exists."""
        try:
            return self.client.has_index(index_name)
        except Exception as e:
            raise VectorDBError(f"Failed to check Pinecone index {index_name}: {str(e)}")
    
    def upsert_memories(self, index_name: str, memories: List[MemoryRecord]) -> Dict[str, Any]:
        """Insert or update memories in Pinecone."""
        try:
            index = self.client.Index(index_name)
            
            # Convert to Pinecone format using the new API
            vectors = []
            for memory in memories:
                vector_data = (
                    memory.id,
                    memory.embedding,
                    {
                        "text": memory.text,
                        **memory.metadata
                    }
                )
                vectors.append(vector_data)
            
            # Upsert in batches
            batch_size = self.config.batch_size
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                namespace = memories[0].namespace if memories else None
                index.upsert(
                    vectors=batch,
                    namespace=namespace
                )
            
            logger.info(f"Upserted {len(memories)} memories to Pinecone index {index_name}")
            return {"success": True, "count": len(memories)}
            
        except Exception as e:
            raise VectorDBError(f"Failed to upsert memories to Pinecone: {str(e)}")
    
    def search_memories(
        self, 
        index_name: str, 
        query_embedding: List[float],
        top_k: int = 10,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[MemoryRecord]:
        """Search for similar memories in Pinecone."""
        try:
            index = self.client.Index(index_name)
            
            result = index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                filter=filters,
                include_metadata=True
            )
            
            memories = []
            for match in result.matches:
                metadata = match.metadata or {}
                text = metadata.pop("text", "")
                
                memory = MemoryRecord(
                    id=match.id,
                    text=text,
                    embedding=[],  # Don't return embedding for search results
                    metadata=metadata,
                    namespace=namespace,
                    score=match.score
                )
                memories.append(memory)
            
            logger.info(f"Found {len(memories)} memories in Pinecone search")
            return memories
            
        except Exception as e:
            raise VectorDBError(f"Failed to search Pinecone: {str(e)}")
    
    def delete_memories(
        self, 
        index_name: str,
        memory_ids: Optional[List[str]] = None,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Delete memories from Pinecone."""
        try:
            index = self.client.Index(index_name)
            
            if memory_ids:
                index.delete(ids=memory_ids, namespace=namespace)
                return len(memory_ids)
            elif filters:
                index.delete(filter=filters, namespace=namespace)
                return -1  # Unknown count for filter-based deletion
            elif namespace:
                index.delete(delete_all=True, namespace=namespace)
                return -1  # Unknown count for namespace deletion
            else:
                raise VectorDBError("Must specify memory_ids, namespace, or filters for deletion")
                
        except Exception as e:
            raise VectorDBError(f"Failed to delete memories from Pinecone: {str(e)}")
    
    def get_stats(self, index_name: str) -> Dict[str, Any]:
        """Get Pinecone index statistics."""
        try:
            index = self.client.Index(index_name)
            stats = index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "namespaces": stats.namespaces
            }
        except Exception as e:
            raise VectorDBError(f"Failed to get Pinecone stats: {str(e)}")


class QdrantVectorStore(BaseVectorStore):
    """Qdrant vector database implementation."""
    
    def __init__(self, config: VectorDBConfig):
        if not QDRANT_AVAILABLE:
            raise VectorDBError("Qdrant package not available. Install with: pip install qdrant-client")
        
        super().__init__(config)
        
        # Determine connection method
        if config.host:
            self.client = qdrant_client.QdrantClient(
                host=config.host,
                port=config.port or 6333,
                api_key=config.api_key
            )
        else:
            # Use local/in-memory Qdrant
            self.client = qdrant_client.QdrantClient(":memory:")
        
        # Map similarity metrics
        self.distance_map = {
            "cosine": Distance.COSINE,
            "euclidean": Distance.EUCLID,
            "dot_product": Distance.DOT
        }
    
    def create_index(self, index_name: str) -> bool:
        """Create a Qdrant collection."""
        try:
            if not self.client.collection_exists(index_name):
                self.client.create_collection(
                    collection_name=index_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=self.distance_map.get(self.config.similarity_metric, Distance.COSINE)
                    )
                )
                logger.info(f"Created Qdrant collection: {index_name}")
                return True
            return False
        except Exception as e:
            raise VectorDBError(f"Failed to create Qdrant collection {index_name}: {str(e)}")
    
    def delete_index(self, index_name: str) -> bool:
        """Delete a Qdrant collection."""
        try:
            if self.client.collection_exists(index_name):
                self.client.delete_collection(index_name)
                logger.info(f"Deleted Qdrant collection: {index_name}")
                return True
            return False
        except Exception as e:
            raise VectorDBError(f"Failed to delete Qdrant collection {index_name}: {str(e)}")
    
    def index_exists(self, index_name: str) -> bool:
        """Check if Qdrant collection exists."""
        try:
            return self.client.collection_exists(index_name)
        except Exception as e:
            raise VectorDBError(f"Failed to check Qdrant collection {index_name}: {str(e)}")
    
    def upsert_memories(self, index_name: str, memories: List[MemoryRecord]) -> Dict[str, Any]:
        """Insert or update memories in Qdrant."""
        try:
            points = []
            for memory in memories:
                payload = {
                    "text": memory.text,
                    "namespace": memory.namespace,
                    **memory.metadata
                }
                
                point = PointStruct(
                    id=memory.id,
                    vector=memory.embedding,
                    payload=payload
                )
                points.append(point)
            
            # Upsert in batches
            batch_size = self.config.batch_size
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=index_name,
                    points=batch
                )
            
            logger.info(f"Upserted {len(memories)} memories to Qdrant collection {index_name}")
            return {"success": True, "count": len(memories)}
            
        except Exception as e:
            raise VectorDBError(f"Failed to upsert memories to Qdrant: {str(e)}")
    
    def search_memories(
        self, 
        index_name: str, 
        query_embedding: List[float],
        top_k: int = 10,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[MemoryRecord]:
        """Search for similar memories in Qdrant."""
        try:
            # Build filter
            query_filter = {}
            if namespace:
                query_filter["namespace"] = {"$eq": namespace}
            if filters:
                query_filter.update(filters)
            
            result = self.client.search(
                collection_name=index_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=query_filter if query_filter else None
            )
            
            memories = []
            for hit in result:
                payload = hit.payload
                text = payload.pop("text", "")
                namespace = payload.pop("namespace", None)
                
                memory = MemoryRecord(
                    id=str(hit.id),
                    text=text,
                    embedding=[],  # Don't return embedding for search results
                    metadata=payload,
                    namespace=namespace,
                    score=hit.score
                )
                memories.append(memory)
            
            logger.info(f"Found {len(memories)} memories in Qdrant search")
            return memories
            
        except Exception as e:
            raise VectorDBError(f"Failed to search Qdrant: {str(e)}")
    
    def delete_memories(
        self, 
        index_name: str,
        memory_ids: Optional[List[str]] = None,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Delete memories from Qdrant."""
        try:
            if memory_ids:
                self.client.delete(
                    collection_name=index_name,
                    points_selector=memory_ids
                )
                return len(memory_ids)
            else:
                # Build filter for deletion
                delete_filter = {}
                if namespace:
                    delete_filter["namespace"] = {"$eq": namespace}
                if filters:
                    delete_filter.update(filters)
                
                if delete_filter:
                    result = self.client.delete(
                        collection_name=index_name,
                        points_selector=qdrant_client.models.FilterSelector(
                            filter=qdrant_client.models.Filter(**delete_filter)
                        )
                    )
                    return -1  # Unknown count
                else:
                    raise VectorDBError("Must specify memory_ids, namespace, or filters for deletion")
                    
        except Exception as e:
            raise VectorDBError(f"Failed to delete memories from Qdrant: {str(e)}")
    
    def get_stats(self, index_name: str) -> Dict[str, Any]:
        """Get Qdrant collection statistics."""
        try:
            info = self.client.get_collection(index_name)
            return {
                "total_vector_count": info.points_count,
                "dimension": info.config.params.vectors.size,
                "distance_metric": info.config.params.vectors.distance.name
            }
        except Exception as e:
            raise VectorDBError(f"Failed to get Qdrant stats: {str(e)}")


class ChromaVectorStore(BaseVectorStore):
    """ChromaDB vector database implementation."""
    
    def __init__(self, config: VectorDBConfig):
        if not CHROMADB_AVAILABLE:
            raise VectorDBError("ChromaDB package not available. Install with: pip install chromadb")
        
        super().__init__(config)
        
        # Initialize ChromaDB client
        if config.host:
            self.client = chromadb.HttpClient(
                host=config.host,
                port=config.port or 8000
            )
        else:
            # Use persistent local client
            persist_directory = os.path.join(config.storage_path, "chroma")
            os.makedirs(persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=persist_directory)
    
    def create_index(self, index_name: str) -> bool:
        """Create a ChromaDB collection."""
        try:
            # ChromaDB creates collections automatically, but we can check if it exists
            try:
                self.client.get_collection(index_name)
                return False  # Already exists
            except:
                # Collection doesn't exist, it will be created on first insert
                logger.info(f"ChromaDB collection {index_name} will be created on first insert")
                return True
        except Exception as e:
            raise VectorDBError(f"Failed to create ChromaDB collection {index_name}: {str(e)}")
    
    def delete_index(self, index_name: str) -> bool:
        """Delete a ChromaDB collection."""
        try:
            self.client.delete_collection(index_name)
            logger.info(f"Deleted ChromaDB collection: {index_name}")
            return True
        except Exception as e:
            if "does not exist" in str(e).lower():
                return False
            raise VectorDBError(f"Failed to delete ChromaDB collection {index_name}: {str(e)}")
    
    def index_exists(self, index_name: str) -> bool:
        """Check if ChromaDB collection exists."""
        try:
            self.client.get_collection(index_name)
            return True
        except:
            return False
    
    def upsert_memories(self, index_name: str, memories: List[MemoryRecord]) -> Dict[str, Any]:
        """Insert or update memories in ChromaDB."""
        try:
            # Get or create collection
            collection = self.client.get_or_create_collection(
                name=index_name,
                metadata={"embedding_dimension": self.embedding_dimension}
            )
            
            # Prepare data
            ids = [memory.id for memory in memories]
            embeddings = [memory.embedding for memory in memories]
            documents = [memory.text for memory in memories]
            metadatas = []
            
            for memory in memories:
                metadata = {
                    "namespace": memory.namespace or "default",
                    **memory.metadata
                }
                metadatas.append(metadata)
            
            # Upsert to ChromaDB
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Upserted {len(memories)} memories to ChromaDB collection {index_name}")
            return {"success": True, "count": len(memories)}
            
        except Exception as e:
            raise VectorDBError(f"Failed to upsert memories to ChromaDB: {str(e)}")
    
    def search_memories(
        self, 
        index_name: str, 
        query_embedding: List[float],
        top_k: int = 10,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[MemoryRecord]:
        """Search for similar memories in ChromaDB."""
        try:
            collection = self.client.get_collection(index_name)
            
            # Build where clause
            where_clause = {}
            if namespace:
                where_clause["namespace"] = {"$eq": namespace}
            if filters:
                where_clause.update(filters)
            
            result = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause if where_clause else None,
                include=["documents", "metadatas", "distances"]
            )
            
            memories = []
            if result["ids"] and result["ids"][0]:
                for i in range(len(result["ids"][0])):
                    metadata = result["metadatas"][0][i] if result["metadatas"] else {}
                    namespace = metadata.pop("namespace", None)
                    
                    # Convert distance to similarity score (ChromaDB returns distances)
                    distance = result["distances"][0][i] if result["distances"] else 0
                    score = 1.0 / (1.0 + distance)  # Convert distance to similarity
                    
                    memory = MemoryRecord(
                        id=result["ids"][0][i],
                        text=result["documents"][0][i] if result["documents"] else "",
                        embedding=[],  # Don't return embedding for search results
                        metadata=metadata,
                        namespace=namespace,
                        score=score
                    )
                    memories.append(memory)
            
            logger.info(f"Found {len(memories)} memories in ChromaDB search")
            return memories
            
        except Exception as e:
            raise VectorDBError(f"Failed to search ChromaDB: {str(e)}")
    
    def delete_memories(
        self, 
        index_name: str,
        memory_ids: Optional[List[str]] = None,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Delete memories from ChromaDB."""
        try:
            collection = self.client.get_collection(index_name)
            
            if memory_ids:
                collection.delete(ids=memory_ids)
                return len(memory_ids)
            else:
                # Build where clause for deletion
                where_clause = {}
                if namespace:
                    where_clause["namespace"] = {"$eq": namespace}
                if filters:
                    where_clause.update(filters)
                
                if where_clause:
                    collection.delete(where=where_clause)
                    return -1  # Unknown count
                else:
                    raise VectorDBError("Must specify memory_ids, namespace, or filters for deletion")
                    
        except Exception as e:
            raise VectorDBError(f"Failed to delete memories from ChromaDB: {str(e)}")
    
    def get_stats(self, index_name: str) -> Dict[str, Any]:
        """Get ChromaDB collection statistics."""
        try:
            collection = self.client.get_collection(index_name)
            count = collection.count()
            metadata = collection.metadata or {}
            
            return {
                "total_vector_count": count,
                "dimension": metadata.get("embedding_dimension", self.embedding_dimension),
                "metadata": metadata
            }
        except Exception as e:
            raise VectorDBError(f"Failed to get ChromaDB stats: {str(e)}")


class FAISSVectorStore(BaseVectorStore):
    """FAISS vector database implementation with SQLite metadata storage."""
    
    def __init__(self, config: VectorDBConfig):
        if not FAISS_AVAILABLE:
            raise VectorDBError("FAISS package not available. Install with: pip install faiss-cpu")
        
        super().__init__(config)
        self.storage_path = config.storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Map similarity metrics to FAISS index types
        self.metric_map = {
            "cosine": faiss.METRIC_INNER_PRODUCT,  # Normalized vectors for cosine
            "euclidean": faiss.METRIC_L2,
            "dot_product": faiss.METRIC_INNER_PRODUCT
        }
    
    def _get_index_path(self, index_name: str) -> str:
        """Get file path for FAISS index."""
        return os.path.join(self.storage_path, f"{index_name}.faiss")
    
    def _get_metadata_db_path(self, index_name: str) -> str:
        """Get file path for metadata SQLite database."""
        return os.path.join(self.storage_path, f"{index_name}_metadata.db")
    
    def create_index(self, index_name: str) -> bool:
        """Create a FAISS index with SQLite metadata storage."""
        try:
            index_path = self._get_index_path(index_name)
            metadata_path = self._get_metadata_db_path(index_name)
            
            if os.path.exists(index_path):
                return False  # Already exists
            
            # Create FAISS index
            metric = self.metric_map.get(self.config.similarity_metric, faiss.METRIC_INNER_PRODUCT)
            index = faiss.IndexFlatIP(self.embedding_dimension) if metric == faiss.METRIC_INNER_PRODUCT else faiss.IndexFlatL2(self.embedding_dimension)
            
            # Save index
            faiss.write_index(index, index_path)
            
            # Create metadata database
            conn = sqlite3.connect(metadata_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE metadata (
                    id TEXT PRIMARY KEY,
                    text TEXT,
                    namespace TEXT,
                    metadata TEXT,
                    vector_id INTEGER
                )
            ''')
            conn.commit()
            conn.close()
            
            logger.info(f"Created FAISS index: {index_name}")
            return True
            
        except Exception as e:
            raise VectorDBError(f"Failed to create FAISS index {index_name}: {str(e)}")
    
    def delete_index(self, index_name: str) -> bool:
        """Delete a FAISS index."""
        try:
            index_path = self._get_index_path(index_name)
            metadata_path = self._get_metadata_db_path(index_name)
            
            deleted = False
            if os.path.exists(index_path):
                os.remove(index_path)
                deleted = True
            
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
                deleted = True
            
            if deleted:
                logger.info(f"Deleted FAISS index: {index_name}")
            
            return deleted
            
        except Exception as e:
            raise VectorDBError(f"Failed to delete FAISS index {index_name}: {str(e)}")
    
    def index_exists(self, index_name: str) -> bool:
        """Check if FAISS index exists."""
        index_path = self._get_index_path(index_name)
        return os.path.exists(index_path)
    
    def upsert_memories(self, index_name: str, memories: List[MemoryRecord]) -> Dict[str, Any]:
        """Insert or update memories in FAISS."""
        try:
            index_path = self._get_index_path(index_name)
            metadata_path = self._get_metadata_db_path(index_name)
            
            # Load FAISS index
            index = faiss.read_index(index_path)
            
            # Connect to metadata database
            conn = sqlite3.connect(metadata_path)
            cursor = conn.cursor()
            
            # Prepare vectors and metadata
            vectors = np.array([memory.embedding for memory in memories], dtype=np.float32)
            
            # Normalize vectors for cosine similarity
            if self.config.similarity_metric == "cosine":
                faiss.normalize_L2(vectors)
            
            # Add vectors to FAISS index
            start_id = index.ntotal
            index.add(vectors)
            
            # Store metadata in SQLite
            for i, memory in enumerate(memories):
                vector_id = start_id + i
                metadata_json = json.dumps(memory.metadata)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO metadata 
                    (id, text, namespace, metadata, vector_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (memory.id, memory.text, memory.namespace, metadata_json, vector_id))
            
            # Save index and commit metadata
            faiss.write_index(index, index_path)
            conn.commit()
            conn.close()
            
            logger.info(f"Upserted {len(memories)} memories to FAISS index {index_name}")
            return {"success": True, "count": len(memories)}
            
        except Exception as e:
            raise VectorDBError(f"Failed to upsert memories to FAISS: {str(e)}")
    
    def search_memories(
        self, 
        index_name: str, 
        query_embedding: List[float],
        top_k: int = 10,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[MemoryRecord]:
        """Search for similar memories in FAISS."""
        try:
            index_path = self._get_index_path(index_name)
            metadata_path = self._get_metadata_db_path(index_name)
            
            # Load FAISS index
            index = faiss.read_index(index_path)
            
            # Prepare query vector
            query_vector = np.array([query_embedding], dtype=np.float32)
            if self.config.similarity_metric == "cosine":
                faiss.normalize_L2(query_vector)
            
            # Search FAISS index
            scores, vector_ids = index.search(query_vector, top_k)
            
            # Connect to metadata database
            conn = sqlite3.connect(metadata_path)
            cursor = conn.cursor()
            
            memories = []
            for i, vector_id in enumerate(vector_ids[0]):
                if vector_id == -1:  # FAISS returns -1 for empty results
                    continue
                
                # Get metadata from SQLite
                where_clause = "vector_id = ?"
                params = [int(vector_id)]
                
                if namespace:
                    where_clause += " AND namespace = ?"
                    params.append(namespace)
                
                cursor.execute(f"SELECT id, text, namespace, metadata FROM metadata WHERE {where_clause}", params)
                result = cursor.fetchone()
                
                if result:
                    memory_id, text, ns, metadata_json = result
                    metadata = json.loads(metadata_json) if metadata_json else {}
                    
                    # Apply additional filters
                    if filters:
                        match = True
                        for key, value in filters.items():
                            if key not in metadata or metadata[key] != value:
                                match = False
                                break
                        if not match:
                            continue
                    
                    memory = MemoryRecord(
                        id=memory_id,
                        text=text,
                        embedding=[],  # Don't return embedding for search results
                        metadata=metadata,
                        namespace=ns,
                        score=float(scores[0][i])
                    )
                    memories.append(memory)
            
            conn.close()
            
            logger.info(f"Found {len(memories)} memories in FAISS search")
            return memories
            
        except Exception as e:
            raise VectorDBError(f"Failed to search FAISS: {str(e)}")
    
    def delete_memories(
        self, 
        index_name: str,
        memory_ids: Optional[List[str]] = None,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Delete memories from FAISS (removes from metadata, marks vectors as deleted)."""
        try:
            metadata_path = self._get_metadata_db_path(index_name)
            
            # Connect to metadata database
            conn = sqlite3.connect(metadata_path)
            cursor = conn.cursor()
            
            # Build delete query
            if memory_ids:
                placeholders = ",".join(["?" for _ in memory_ids])
                cursor.execute(f"DELETE FROM metadata WHERE id IN ({placeholders})", memory_ids)
                deleted_count = cursor.rowcount
            else:
                where_conditions = []
                params = []
                
                if namespace:
                    where_conditions.append("namespace = ?")
                    params.append(namespace)
                
                if filters:
                    for key, value in filters.items():
                        where_conditions.append("json_extract(metadata, ?) = ?")
                        params.extend([f"$.{key}", value])
                
                if where_conditions:
                    where_clause = " AND ".join(where_conditions)
                    cursor.execute(f"DELETE FROM metadata WHERE {where_clause}", params)
                    deleted_count = cursor.rowcount
                else:
                    raise VectorDBError("Must specify memory_ids, namespace, or filters for deletion")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Deleted {deleted_count} memories from FAISS metadata")
            return deleted_count
            
        except Exception as e:
            raise VectorDBError(f"Failed to delete memories from FAISS: {str(e)}")
    
    def get_stats(self, index_name: str) -> Dict[str, Any]:
        """Get FAISS index statistics."""
        try:
            index_path = self._get_index_path(index_name)
            metadata_path = self._get_metadata_db_path(index_name)
            
            # Load FAISS index
            index = faiss.read_index(index_path)
            
            # Connect to metadata database
            conn = sqlite3.connect(metadata_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM metadata")
            metadata_count = cursor.fetchone()[0]
            conn.close()
            
            return {
                "total_vector_count": index.ntotal,
                "metadata_count": metadata_count,
                "dimension": index.d,
                "metric": self.config.similarity_metric
            }
            
        except Exception as e:
            raise VectorDBError(f"Failed to get FAISS stats: {str(e)}")


class VectorStoreManager:
    """Main manager for vector database operations with support for multiple providers."""
    
    def __init__(self, config: VectorDBConfig):
        self.config = config
        self.store = self._create_store()
    
    def _create_store(self) -> BaseVectorStore:
        """Create the appropriate vector store provider."""
        provider = self.config.provider.lower()
        
        if provider == "pinecone":
            return PineconeVectorStore(self.config)
        elif provider == "qdrant":
            return QdrantVectorStore(self.config)
        elif provider == "chroma":
            return ChromaVectorStore(self.config)
        elif provider == "faiss":
            return FAISSVectorStore(self.config)
        elif provider == "sqlite":
            # SQLite is similar to FAISS but simpler - we could implement it
            raise VectorDBError("SQLite vector store not yet implemented")
        elif provider == "weaviate":
            # Placeholder for Weaviate implementation
            raise VectorDBError("Weaviate vector store not yet implemented")
        else:
            raise VectorDBError(f"Unknown vector store provider: {provider}")
    
    def create_index(self, index_name: str) -> bool:
        """Create an index/collection."""
        return self.store.create_index(index_name)
    
    def delete_index(self, index_name: str) -> bool:
        """Delete an index/collection."""
        return self.store.delete_index(index_name)
    
    def index_exists(self, index_name: str) -> bool:
        """Check if index/collection exists."""
        return self.store.index_exists(index_name)
    
    def upsert_memories(self, index_name: str, memories: List[MemoryRecord]) -> Dict[str, Any]:
        """Insert or update memory records."""
        if not memories:
            return {"success": True, "count": 0}
        return self.store.upsert_memories(index_name, memories)
    
    def search_memories(
        self, 
        index_name: str, 
        query_embedding: List[float],
        top_k: int = 10,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[MemoryRecord]:
        """Search for similar memories."""
        return self.store.search_memories(index_name, query_embedding, top_k, namespace, filters)
    
    def delete_memories(
        self, 
        index_name: str,
        memory_ids: Optional[List[str]] = None,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Delete memories by IDs, namespace, or filters."""
        return self.store.delete_memories(index_name, memory_ids, namespace, filters)
    
    def get_stats(self, index_name: str) -> Dict[str, Any]:
        """Get statistics about the index."""
        return self.store.get_stats(index_name)


# Helper functions for easy usage
def create_pinecone_store(
    api_key: Optional[str] = None,
    environment: str = "us-east-1",
    embedding_dimension: int = 768
) -> VectorStoreManager:
    """Create a Pinecone vector store manager."""
    config = VectorDBConfig(
        provider="pinecone",
        api_key=api_key,
        environment=environment,
        embedding_dimension=embedding_dimension
    )
    return VectorStoreManager(config)

def create_qdrant_store(
    host: Optional[str] = None,
    port: int = 6333,
    api_key: Optional[str] = None,
    embedding_dimension: int = 768
) -> VectorStoreManager:
    """Create a Qdrant vector store manager."""
    config = VectorDBConfig(
        provider="qdrant",
        host=host,
        port=port,
        api_key=api_key,
        embedding_dimension=embedding_dimension
    )
    return VectorStoreManager(config)

def create_chroma_store(
    storage_path: str = "./smriti_data",
    host: Optional[str] = None,
    port: int = 8000,
    embedding_dimension: int = 768
) -> VectorStoreManager:
    """Create a ChromaDB vector store manager."""
    config = VectorDBConfig(
        provider="chroma",
        storage_path=storage_path,
        host=host,
        port=port,
        embedding_dimension=embedding_dimension
    )
    return VectorStoreManager(config)

def create_faiss_store(
    storage_path: str = "./smriti_data",
    embedding_dimension: int = 768,
    similarity_metric: str = "cosine"
) -> VectorStoreManager:
    """Create a FAISS vector store manager."""
    config = VectorDBConfig(
        provider="faiss",
        storage_path=storage_path,
        embedding_dimension=embedding_dimension,
        similarity_metric=similarity_metric
    )
    return VectorStoreManager(config) 