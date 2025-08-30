"""
Enhanced Memory Manager for Smriti Memory with modular architecture.

This enhanced version provides:
- Pluggable embedding providers (OpenAI, HuggingFace, Cohere, Gemini, Custom)
- Multiple vector database backends (Pinecone, Qdrant, ChromaDB, FAISS)
- Improved CRUD operations with DELETE functionality
- Advanced memory operations and intelligent curation
- Performance optimizations and caching
"""

import uuid
import logging
import time
import asyncio
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import asdict

from .config import MemoryConfig, EmbeddingProviderConfig, VectorStoreConfig
from .embeddings import EmbeddingManager, EmbeddingConfig
from .vector_stores import VectorStoreManager, VectorDBConfig, MemoryRecord
from .llm import LLMManager
from .exceptions import MemoryError, ValidationError, SmritiError

logger = logging.getLogger(__name__)


class EnhancedMemoryManager:
    """Enhanced Memory Manager with modular architecture and advanced features."""
    
    def __init__(self, config: Optional[MemoryConfig] = None):
        """Initialize the enhanced memory manager."""
        self.config = config or MemoryConfig()
        
        # Initialize modular components
        self._initialize_components()
        
        # Initialize performance features
        self._memory_cache = {} if self.config.cache_enabled else None
        self._last_summarization = {}
        self._memory_stats = {}
        
        if self.config.enable_logging:
            logging.basicConfig(level=getattr(logging, self.config.log_level))
        
        logger.info("Enhanced Memory Manager initialized with modular architecture")
    
    def _initialize_components(self):
        """Initialize the modular components (embedding, vector store, LLM)."""
        try:
            # Initialize embedding manager
            embedding_config = EmbeddingConfig(
                provider=self.config.embedding_config.provider,
                model_name=self.config.embedding_config.model_name,
                api_key=self.config.embedding_config.api_key,
                model_kwargs=self.config.embedding_config.model_kwargs,
                cache_embeddings=self.config.embedding_config.cache_embeddings,
                batch_size=self.config.embedding_config.batch_size,
                max_retries=self.config.embedding_config.max_retries,
                timeout=self.config.embedding_config.timeout
            )
            self.embedding_manager = EmbeddingManager(embedding_config)
            
            # Initialize vector store manager
            vector_config = VectorDBConfig(
                provider=self.config.vector_store_config.provider,
                embedding_dimension=self.embedding_manager.get_embedding_dimension(),
                similarity_metric=self.config.vector_store_config.similarity_metric,
                api_key=self.config.vector_store_config.api_key,
                environment=self.config.vector_store_config.environment,
                host=self.config.vector_store_config.host,
                port=self.config.vector_store_config.port,
                collection_name=self.config.vector_store_config.collection_name,
                batch_size=self.config.vector_store_config.batch_size,
                timeout=self.config.vector_store_config.timeout,
                max_retries=self.config.vector_store_config.max_retries,
                storage_path=self.config.vector_store_config.storage_path,
                provider_kwargs=self.config.vector_store_config.provider_kwargs
            )
            self.vector_store = VectorStoreManager(vector_config)
            
            # Initialize LLM manager (keeping existing implementation for now)
            self.llm = LLMManager(self.config)
            
            logger.info(f"Components initialized: {embedding_config.provider} embeddings, {vector_config.provider} vector store")
            
        except Exception as e:
            error_msg = f"Failed to initialize components: {str(e)}"
            logger.error(error_msg)
            raise MemoryError(error_msg)
    
    def add_memory(self, user_id: str, chat_thread: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add memory based on chat thread with enhanced processing.
        
        Args:
            user_id: The user identifier
            chat_thread: List of chat messages with user/ai content
            
        Returns:
            Dict containing the result of the memory operation
        """
        try:
            # Validate inputs
            self._validate_inputs(user_id, chat_thread)
            
            # Ensure index exists
            index_name = self._get_index_name(user_id)
            self.vector_store.create_index(index_name)
            
            # Extract user text for search
            user_text = self._extract_user_text(chat_thread)
            if not user_text:
                return {
                    "success": True,
                    "memory": [],
                    "action": "ignored",
                    "reason": "No user text found in chat thread"
                }
            
            # Search for existing memories
            existing_memories = self.search_memories(user_id, user_text, top_k=5)
            
            # Use LLM to decide memory action
            decision = self.llm.decide_memory_action(user_id, chat_thread, existing_memories)
            
            if not decision.get("memory", False):
                return {
                    "success": True,
                    "memory": [],
                    "action": "ignored",
                    "reason": "LLM decided no memory needed"
                }
            
            # Process memory data
            memory_data = decision.get("memory_data", [])
            if not memory_data:
                return {
                    "success": True,
                    "memory": [],
                    "action": "ignored",
                    "reason": "No memory data in decision"
                }
            
            # Process memories with enhanced operations
            result = self._process_memory_operations(user_id, memory_data, decision.get("type_of_memory", "user_understanding"))
            
            # Update statistics
            self._update_memory_stats(user_id, result)
            
            # Check if summarization is needed
            if self.config.enable_memory_summarization:
                self._check_summarization_needed(user_id)
            
            logger.info(f"Memory operation completed for user {user_id}: {result['action']}")
            return result
            
        except Exception as e:
            error_msg = f"Failed to add memory for user {user_id}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "memory": [],
                "action": "error"
            }
    
    def _process_memory_operations(self, user_id: str, memory_data: List[Dict[str, Any]], memory_type: str) -> Dict[str, Any]:
        """Process memory operations (ADD, UPDATE, DELETE) with enhanced logic."""
        index_name = self._get_index_name(user_id)
        namespace = self._get_namespace(memory_type)
        
        added_count = 0
        updated_count = 0
        deleted_count = 0
        memory_records = []
        
        for memory_item in memory_data:
            try:
                text = memory_item.get("text", "")
                update_id = memory_item.get("update_id")
                
                if not text:
                    continue
                
                # Generate embedding for the memory
                embedding = self.embedding_manager.embed_text(text)
                
                if update_id:
                    # UPDATE operation: delete old memory and add new one
                    deleted = self.vector_store.delete_memories(index_name, memory_ids=[update_id])
                    if deleted > 0:
                        deleted_count += deleted
                    
                    # Add the updated memory
                    memory_record = MemoryRecord(
                        id=str(uuid.uuid4()),
                        text=text,
                        embedding=embedding,
                        metadata={
                            "user_id": user_id,
                            "timestamp": datetime.now().isoformat(),
                            "type": memory_type,
                            "updated_from": update_id
                        },
                        namespace=namespace
                    )
                    memory_records.append(memory_record)
                    updated_count += 1
                else:
                    # ADD operation: add new memory
                    memory_record = MemoryRecord(
                        id=str(uuid.uuid4()),
                        text=text,
                        embedding=embedding,
                        metadata={
                            "user_id": user_id,
                            "timestamp": datetime.now().isoformat(),
                            "type": memory_type
                        },
                        namespace=namespace
                    )
                    memory_records.append(memory_record)
                    added_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to process memory item: {str(e)}")
                continue
        
        # Batch upsert all new/updated memories
        if memory_records:
            storage_result = self.vector_store.upsert_memories(index_name, memory_records)
        else:
            storage_result = {"success": True, "count": 0}
        
        # Clear cache for this user
        if self._memory_cache and user_id in self._memory_cache:
            del self._memory_cache[user_id]
        
        # Determine primary action
        if updated_count > 0:
            action = "updated"
        elif added_count > 0:
            action = "added"
        elif deleted_count > 0:
            action = "deleted"
        else:
            action = "no_change"
        
        return {
            "success": True,
            "memory": [asdict(record) for record in memory_records],
            "action": action,
            "namespace": namespace,
            "added_count": added_count,
            "updated_count": updated_count,
            "deleted_count": deleted_count,
            "total_count": len(memory_records),
            "storage_result": storage_result
        }
    
    def search_memories(
        self, 
        user_id: str, 
        query: str,
        namespace: Optional[str] = None,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        include_scores: bool = True
    ) -> Dict[str, Any]:
        """
        Enhanced search for memories with caching and advanced filtering.
        
        Args:
            user_id: User identifier
            query: Search query
            namespace: Optional namespace to search in
            top_k: Number of results to return
            filters: Additional filters to apply
            include_scores: Whether to include similarity scores
            
        Returns:
            Dict containing search results
        """
        try:
            self._validate_user_id(user_id)
            self._validate_query(query)
            
            top_k = top_k or self.config.max_search_results
            namespace = namespace or self.config.default_namespace
            
            # Check cache first
            cache_key = f"{user_id}:{query}:{namespace}:{top_k}"
            if self._memory_cache and cache_key in self._memory_cache:
                cached_result = self._memory_cache[cache_key]
                if time.time() - cached_result["timestamp"] < 300:  # 5 minute cache
                    logger.debug(f"Returning cached search result for user {user_id}")
                    return cached_result["result"]
            
            index_name = self._get_index_name(user_id)
            
            # Check if index exists
            if not self.vector_store.index_exists(index_name):
                return {
                    "success": True,
                    "results": [],
                    "query": query,
                    "namespace": namespace,
                    "count": 0
                }
            
            # Generate query embedding
            query_embedding = self.embedding_manager.embed_text(query)
            
            # Search vector store
            memory_records = self.vector_store.search_memories(
                index_name=index_name,
                query_embedding=query_embedding,
                top_k=top_k,
                namespace=namespace,
                filters=filters
            )
            
            # Filter by similarity threshold
            filtered_records = []
            for record in memory_records:
                if record.score and record.score >= self.config.similarity_threshold:
                    filtered_records.append(record)
            
            # Format results
            results = []
            for record in filtered_records:
                result_item = {
                    "id": record.id,
                    "text": record.text,
                    "metadata": record.metadata,
                    "namespace": record.namespace
                }
                if include_scores:
                    result_item["score"] = record.score
                results.append(result_item)
            
            search_result = {
                "success": True,
                "results": results,
                "query": query,
                "namespace": namespace,
                "count": len(results),
                "total_found": len(memory_records),
                "filtered_by_threshold": len(memory_records) - len(filtered_records)
            }
            
            # Cache the result
            if self._memory_cache:
                self._memory_cache[cache_key] = {
                    "result": search_result,
                    "timestamp": time.time()
                }
            
            logger.info(f"Found {len(results)} memories for user {user_id} query: '{query[:50]}...'")
            return search_result
            
        except Exception as e:
            error_msg = f"Failed to search memories for user {user_id}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "results": [],
                "query": query,
                "count": 0
            }
    
    def delete_memories(
        self,
        user_id: str,
        memory_ids: Optional[List[str]] = None,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        confirm_deletion: bool = False
    ) -> Dict[str, Any]:
        """
        Delete memories with multiple deletion modes.
        
        Args:
            user_id: User identifier
            memory_ids: Specific memory IDs to delete
            namespace: Delete all memories in namespace
            filters: Delete memories matching filters
            confirm_deletion: Safety flag to confirm deletion
            
        Returns:
            Dict containing deletion results
        """
        try:
            self._validate_user_id(user_id)
            
            if not confirm_deletion:
                raise ValidationError("confirm_deletion must be True to proceed with deletion")
            
            if not any([memory_ids, namespace, filters]):
                raise ValidationError("Must specify memory_ids, namespace, or filters for deletion")
            
            index_name = self._get_index_name(user_id)
            
            # Check if index exists
            if not self.vector_store.index_exists(index_name):
                return {
                    "success": True,
                    "deleted_count": 0,
                    "message": "No memories found for user"
                }
            
            # Perform deletion
            deleted_count = self.vector_store.delete_memories(
                index_name=index_name,
                memory_ids=memory_ids,
                namespace=namespace,
                filters=filters
            )
            
            # Clear cache for this user
            if self._memory_cache:
                keys_to_remove = [key for key in self._memory_cache.keys() if key.startswith(f"{user_id}:")]
                for key in keys_to_remove:
                    del self._memory_cache[key]
            
            # Update statistics
            if user_id in self._memory_stats:
                self._memory_stats[user_id]["deleted_count"] = self._memory_stats[user_id].get("deleted_count", 0) + deleted_count
            
            logger.info(f"Deleted {deleted_count} memories for user {user_id}")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "deletion_type": "by_ids" if memory_ids else "by_namespace" if namespace else "by_filters",
                "user_id": user_id
            }
            
        except Exception as e:
            error_msg = f"Failed to delete memories for user {user_id}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "deleted_count": 0
            }
    
    def delete_user_memories(self, user_id: str, confirm_deletion: bool = False) -> Dict[str, Any]:
        """
        Delete all memories for a user.
        
        Args:
            user_id: User identifier
            confirm_deletion: Safety flag to confirm deletion
            
        Returns:
            Dict containing deletion results
        """
        try:
            self._validate_user_id(user_id)
            
            if not confirm_deletion:
                raise ValidationError("confirm_deletion must be True to proceed with deletion")
            
            index_name = self._get_index_name(user_id)
            
            # Delete the entire index for this user
            deleted = self.vector_store.delete_index(index_name)
            
            # Clear cache and stats for this user
            if self._memory_cache:
                keys_to_remove = [key for key in self._memory_cache.keys() if key.startswith(f"{user_id}:")]
                for key in keys_to_remove:
                    del self._memory_cache[key]
            
            if user_id in self._memory_stats:
                del self._memory_stats[user_id]
            
            if user_id in self._last_summarization:
                del self._last_summarization[user_id]
            
            logger.info(f"Deleted all memories for user {user_id}")
            
            return {
                "success": True,
                "deleted": deleted,
                "user_id": user_id,
                "message": "All memories deleted for user"
            }
            
        except Exception as e:
            error_msg = f"Failed to delete all memories for user {user_id}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "deleted": False
            }
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics about a user's memories.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict containing user memory statistics
        """
        try:
            self._validate_user_id(user_id)
            
            index_name = self._get_index_name(user_id)
            
            # Get vector store statistics
            if self.vector_store.index_exists(index_name):
                vector_stats = self.vector_store.get_stats(index_name)
            else:
                vector_stats = {"total_vector_count": 0}
            
            # Get cached statistics
            user_stats = self._memory_stats.get(user_id, {})
            
            # Search for recent memories to get namespace breakdown
            namespace_stats = {}
            for namespace in ["user_understanding", "facts", "preferences"]:
                search_result = self.search_memories(user_id, "", namespace=namespace, top_k=1000)
                namespace_stats[namespace] = search_result.get("count", 0)
            
            return {
                "success": True,
                "user_id": user_id,
                "total_memories": vector_stats.get("total_vector_count", 0),
                "namespace_breakdown": namespace_stats,
                "embedding_dimension": vector_stats.get("dimension", 0),
                "vector_store_provider": self.config.vector_store_config.provider,
                "embedding_provider": self.config.embedding_config.provider,
                "cache_enabled": self.config.cache_enabled,
                "last_activity": user_stats.get("last_activity"),
                "total_added": user_stats.get("added_count", 0),
                "total_updated": user_stats.get("updated_count", 0),
                "total_deleted": user_stats.get("deleted_count", 0),
                "last_summarization": self._last_summarization.get(user_id)
            }
            
        except Exception as e:
            error_msg = f"Failed to get stats for user {user_id}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "user_id": user_id
            }
    
    def chat_with_memory(
        self, 
        user_id: str, 
        query: str,
        add_to_memory: bool = True,
        namespace: Optional[str] = None,
        context_limit: int = 5
    ) -> Dict[str, Any]:
        """
        Enhanced chat with memory context including performance optimizations.
        
        Args:
            user_id: The user identifier
            query: User's query
            add_to_memory: Whether to add the interaction to memory
            namespace: Namespace to search for context
            context_limit: Maximum number of context memories to use
            
        Returns:
            Dict containing the response and memory context
        """
        try:
            self._validate_user_id(user_id)
            self._validate_query(query)
            
            # Search for relevant memories
            memory_context = self.search_memories(
                user_id=user_id, 
                query=query,
                namespace=namespace,
                top_k=context_limit
            )
            
            # Generate response using context
            if memory_context.get("success") and memory_context.get("results"):
                context_text = self._format_memory_context(memory_context["results"])
                response = self.llm.generate_response_with_context(query, {"context": context_text})
            else:
                response = self.llm.ask_llm(query)
            
            # Add to memory if requested
            memory_result = None
            if add_to_memory:
                chat_thread = [{"user": query, "ai": response}]
                memory_result = self.add_memory(user_id, chat_thread)
            
            logger.info(f"Chat response generated for user {user_id}")
            
            return {
                "success": True,
                "response": response,
                "memory_context": memory_context,
                "memory_result": memory_result,
                "context_used": len(memory_context.get("results", [])),
                "user_id": user_id
            }
            
        except Exception as e:
            error_msg = f"Failed to generate chat response for user {user_id}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "response": None,
                "user_id": user_id
            }
    
    def clear_cache(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Clear memory cache for a specific user or all users."""
        try:
            if not self._memory_cache:
                return {"success": True, "message": "Cache not enabled"}
            
            if user_id:
                keys_to_remove = [key for key in self._memory_cache.keys() if key.startswith(f"{user_id}:")]
                for key in keys_to_remove:
                    del self._memory_cache[key]
                message = f"Cache cleared for user {user_id}"
            else:
                self._memory_cache.clear()
                message = "Cache cleared for all users"
            
            # Also clear embedding cache
            self.embedding_manager.clear_cache()
            
            logger.info(message)
            return {"success": True, "message": message}
            
        except Exception as e:
            error_msg = f"Failed to clear cache: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics and health information."""
        try:
            total_users = len(self._memory_stats)
            total_cache_entries = len(self._memory_cache) if self._memory_cache else 0
            
            # Get embedding provider info
            embedding_dimension = self.embedding_manager.get_embedding_dimension()
            
            return {
                "success": True,
                "system_info": {
                    "embedding_provider": self.config.embedding_config.provider,
                    "embedding_model": self.config.embedding_config.model_name,
                    "embedding_dimension": embedding_dimension,
                    "vector_store_provider": self.config.vector_store_config.provider,
                    "llm_provider": self.config.llm_config.provider,
                    "llm_model": self.config.llm_config.model_name
                },
                "performance": {
                    "cache_enabled": self.config.cache_enabled,
                    "cache_entries": total_cache_entries,
                    "async_operations": self.config.enable_async_operations,
                    "batch_processing": self.config.batch_processing
                },
                "features": {
                    "graph_memory": self.config.enable_graph_memory,
                    "memory_summarization": self.config.enable_memory_summarization,
                    "memory_clustering": self.config.enable_memory_clustering
                },
                "usage": {
                    "total_users": total_users,
                    "memory_stats_tracked": len(self._memory_stats)
                }
            }
            
        except Exception as e:
            error_msg = f"Failed to get system stats: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    # Helper methods
    def _get_index_name(self, user_id: str) -> str:
        """Generate index name for user."""
        # Use custom index name from config if specified, otherwise auto-generate
        if self.config.vector_store_config and self.config.vector_store_config.custom_index_name:
            return self.config.vector_store_config.custom_index_name
        return f"smriti-{user_id.lower().replace('_', '-')}"
    
    def _get_namespace(self, memory_type: str) -> str:
        """Get namespace for memory operations."""
        # Use default namespace from config if specified, otherwise use memory_type
        if self.config.vector_store_config and self.config.vector_store_config.default_namespace:
            return self.config.vector_store_config.default_namespace
        return memory_type
    
    def _validate_inputs(self, user_id: str, chat_thread: List[Dict[str, Any]]) -> None:
        """Validate input parameters."""
        self._validate_user_id(user_id)
        
        if not chat_thread or not isinstance(chat_thread, list):
            raise ValidationError("Chat thread must be a non-empty list")
        
        for i, message in enumerate(chat_thread):
            if not isinstance(message, dict):
                raise ValidationError(f"Message {i} must be a dictionary")
    
    def _validate_user_id(self, user_id: str) -> None:
        """Validate user ID."""
        if not user_id or not isinstance(user_id, str) or not user_id.strip():
            raise ValidationError("User ID must be a non-empty string")
    
    def _validate_query(self, query: str) -> None:
        """Validate search query."""
        if not query or not isinstance(query, str) or not query.strip():
            raise ValidationError("Query must be a non-empty string")
    
    def _extract_user_text(self, chat_thread: List[Dict[str, Any]]) -> str:
        """Extract user text from chat thread."""
        user_messages = []
        for message in chat_thread:
            if "user" in message and message["user"]:
                user_messages.append(str(message["user"]))
        
        return " ".join(user_messages).strip()
    
    def _format_memory_context(self, memories: List[Dict[str, Any]]) -> str:
        """Format memories into context text."""
        if not memories:
            return ""
        
        context_parts = []
        for memory in memories:
            text = memory.get("text", "")
            score = memory.get("score", 0)
            if text:
                context_parts.append(f"[Score: {score:.2f}] {text}")
        
        return "\n".join(context_parts)
    
    def _update_memory_stats(self, user_id: str, result: Dict[str, Any]) -> None:
        """Update memory statistics for user."""
        if user_id not in self._memory_stats:
            self._memory_stats[user_id] = {
                "added_count": 0,
                "updated_count": 0,
                "deleted_count": 0,
                "last_activity": None
            }
        
        stats = self._memory_stats[user_id]
        stats["added_count"] += result.get("added_count", 0)
        stats["updated_count"] += result.get("updated_count", 0)
        stats["deleted_count"] += result.get("deleted_count", 0)
        stats["last_activity"] = datetime.now().isoformat()
    
    def _check_summarization_needed(self, user_id: str) -> None:
        """Check if memory summarization is needed for user."""
        if not self.config.enable_memory_summarization:
            return
        
        stats = self._memory_stats.get(user_id, {})
        total_memories = stats.get("added_count", 0) + stats.get("updated_count", 0)
        
        last_summarization = self._last_summarization.get(user_id, 0)
        
        if total_memories - last_summarization >= self.config.summarization_interval:
            # TODO: Implement memory summarization logic
            logger.info(f"Memory summarization needed for user {user_id}")
            self._last_summarization[user_id] = total_memories 