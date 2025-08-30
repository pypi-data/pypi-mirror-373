"""
Main Memory Manager for Smriti Memory with backward compatibility.

This version provides backward compatibility while leveraging enhanced features
when modular configurations are available.
"""

import uuid
import logging
from typing import List, Dict, Any, Optional
from .config import MemoryConfig
from .vector_db import VectorDBManager
from .llm import LLMManager
from .exceptions import MemoryError, ValidationError, SmritiError

# Import enhanced components when available
try:
    from .enhanced_memory_manager import EnhancedMemoryManager
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False

logger = logging.getLogger(__name__)


class MemoryManager:
    """Main memory manager that orchestrates all memory operations with backward compatibility."""
    
    def __init__(self, config: Optional[MemoryConfig] = None):
        """Initialize the memory manager."""
        self.config = config or MemoryConfig()
        
        # Determine whether to use enhanced or legacy mode
        self._use_enhanced = self._should_use_enhanced()
        
        if self._use_enhanced and ENHANCED_AVAILABLE:
            logger.info("Using enhanced memory manager with modular architecture")
            self._enhanced_manager = EnhancedMemoryManager(self.config)
        else:
            logger.info("Using legacy memory manager")
            self.vector_db = VectorDBManager(self.config)
            self.llm = LLMManager(self.config)
            self._enhanced_manager = None
        
        if self.config.enable_logging:
            logging.basicConfig(level=getattr(logging, self.config.log_level))
    
    def _should_use_enhanced(self) -> bool:
        """Determine if enhanced mode should be used based on configuration."""
        # Use enhanced mode if any modular configs are specified
        return any([
            self.config.embedding_config is not None,
            self.config.vector_store_config is not None,
            self.config.llm_config is not None,
            self.config.enable_graph_memory,
            self.config.enable_memory_summarization
        ])
    
    def add_memory(self, user_id: str, chat_thread: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add memory based on chat thread.
        
        Args:
            user_id: The user identifier
            chat_thread: List of chat messages with user/ai content
            
        Returns:
            Dict containing the result of the memory operation
        """
        # Delegate to enhanced manager if available
        if self._enhanced_manager:
            return self._enhanced_manager.add_memory(user_id, chat_thread)
        
        # Legacy implementation
        try:
            # Validate inputs
            self._validate_inputs(user_id, chat_thread)
            
            # Ensure index exists
            self.vector_db.create_index(user_id)
            
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
            search_result = self.vector_db.search_memories(user_id, user_text)
            
            # Use LLM to decide memory action
            decision = self.llm.decide_memory_action(user_id, chat_thread, search_result)
            
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
            
            # Format memories for storage
            formatted_memories = self._format_memories_for_storage(memory_data)
            
            # Store memories (namespace parameter is ignored, we use user_id for namespace)
            storage_result = self.vector_db.add_memories(user_id, formatted_memories, "")
            
            logger.info(f"Successfully added {len(formatted_memories)} memories for user {user_id}")
            
            return {
                "success": True,
                "memory": formatted_memories,
                "action": "added",
                "count": len(formatted_memories),
                "storage_result": storage_result
            }
            
        except Exception as e:
            error_msg = f"Failed to add memory for user {user_id}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "memory": []
            }
    
    def search_memories(
        self, 
        user_id: str, 
        query: str, 
        namespace: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search for relevant memories.
        
        Args:
            user_id: The user identifier
            query: Search query
            namespace: Optional namespace to search in
            top_k: Number of results to return
            
        Returns:
            Dict containing search results
        """
        # Delegate to enhanced manager if available
        if self._enhanced_manager:
            return self._enhanced_manager.search_memories(user_id, query, namespace, top_k)
        
        # Legacy implementation
        try:
            self._validate_user_id(user_id)
            self._validate_query(query)
            
            result = self.vector_db.search_memories(user_id, query, namespace, top_k)
            
            logger.info(f"Memory search completed for user {user_id}: {result.get('count', 0)} results")
            return result
            
        except Exception as e:
            error_msg = f"Failed to search memories for user {user_id}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "results": []
            }
    
    def chat_with_memory(
        self, 
        user_id: str, 
        query: str,
        add_to_memory: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a chat response using memory context.
        
        Args:
            user_id: The user identifier
            query: User's query
            add_to_memory: Whether to add the interaction to memory
            
        Returns:
            Dict containing the response and memory context
        """
        # Delegate to enhanced manager if available
        if self._enhanced_manager:
            return self._enhanced_manager.chat_with_memory(user_id, query, add_to_memory)
        
        # Legacy implementation
        try:
            self._validate_user_id(user_id)
            self._validate_query(query)
            
            # Search for relevant memories
            memory_context = self.search_memories(user_id, query)
            
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
                "memory_result": memory_result
            }
            
        except Exception as e:
            error_msg = f"Failed to generate chat response for user {user_id}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "response": None
            }
    
    def delete_user_memories(self, user_id: str, confirm_deletion: bool = False) -> Dict[str, Any]:
        """
        Delete all memories for a user.
        
        Args:
            user_id: The user identifier
            confirm_deletion: Safety flag to confirm deletion (enhanced mode only)
            
        Returns:
            Dict containing the result of the deletion
        """
        # Delegate to enhanced manager if available
        if self._enhanced_manager:
            return self._enhanced_manager.delete_user_memories(user_id, confirm_deletion)
        
        # Legacy implementation
        try:
            self._validate_user_id(user_id)
            
            result = self.vector_db.delete_user_memories(user_id)
            
            logger.info(f"Deleted all memories for user {user_id}")
            return result
            
        except Exception as e:
            error_msg = f"Failed to delete memories for user {user_id}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics about a user's memories.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Dict containing user memory statistics
        """
        try:
            self._validate_user_id(user_id)
            
            stats = self.vector_db.get_index_stats(user_id)
            
            logger.info(f"Retrieved stats for user {user_id}")
            return stats
            
        except Exception as e:
            error_msg = f"Failed to get stats for user {user_id}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def _validate_inputs(self, user_id: str, chat_thread: List[Dict[str, Any]]) -> None:
        """Validate input parameters."""
        self._validate_user_id(user_id)
        
        if not isinstance(chat_thread, list):
            raise ValidationError("Chat thread must be a list")
        
        if not chat_thread:
            raise ValidationError("Chat thread cannot be empty")
        
        for message in chat_thread:
            if not isinstance(message, dict):
                raise ValidationError("Each chat message must be a dictionary")
            
            if "user" not in message and "ai" not in message:
                raise ValidationError("Each chat message must contain 'user' or 'ai' field")
    
    def _validate_user_id(self, user_id: str) -> None:
        """Validate user ID."""
        if not user_id or not isinstance(user_id, str):
            raise ValidationError("User ID must be a non-empty string")
    
    def _validate_query(self, query: str) -> None:
        """Validate query."""
        if not query or not isinstance(query, str):
            raise ValidationError("Query must be a non-empty string")
    
    def _extract_user_text(self, chat_thread: List[Dict[str, Any]]) -> str:
        """Extract user text from chat thread."""
        user_messages = []
        for message in chat_thread:
            if "user" in message:
                user_messages.append(str(message["user"]))
        
        return " ".join(user_messages)
    
    def _format_memories_for_storage(self, memory_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format memory data for storage in vector database."""
        formatted_memories = []
        
        for item in memory_data:
            # Generate ID for new memories
            record_id = item.get("update_id") or str(uuid.uuid4())
            
            formatted_memories.append({
                "_id": record_id,
                "chunk_text": item["text"],
                "category": item.get("category", "general")
            })
        
        return formatted_memories
    
    def _format_memory_context(self, memories: List[Dict[str, Any]]) -> str:
        """Format memory results into context string."""
        if not memories:
            return ""
        
        context_parts = []
        for memory in memories:
            context_parts.append(f"- {memory.get('text', '')}")
        
        return "\n".join(context_parts)
    
    # Enhanced methods (available only in enhanced mode)
    
    def delete_memories(
        self,
        user_id: str,
        memory_ids: Optional[List[str]] = None,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        confirm_deletion: bool = False
    ) -> Dict[str, Any]:
        """
        Delete specific memories (Enhanced mode only).
        
        Args:
            user_id: User identifier
            memory_ids: Specific memory IDs to delete
            namespace: Delete all memories in namespace
            filters: Delete memories matching filters
            confirm_deletion: Safety flag to confirm deletion
            
        Returns:
            Dict containing deletion results
        """
        if self._enhanced_manager:
            return self._enhanced_manager.delete_memories(
                user_id, memory_ids, namespace, filters, confirm_deletion
            )
        else:
            return {
                "success": False,
                "error": "Enhanced memory operations require modular configuration",
                "deleted_count": 0
            }
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics about a user's memories.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict containing user memory statistics
        """
        if self._enhanced_manager:
            return self._enhanced_manager.get_user_stats(user_id)
        else:
            # Legacy basic stats
            try:
                self._validate_user_id(user_id)
                stats = self.vector_db.get_user_stats(user_id)
                return {
                    "success": True,
                    "user_id": user_id,
                    "legacy_mode": True,
                    **stats
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "user_id": user_id
                }
    
    def clear_cache(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Clear memory cache (Enhanced mode only)."""
        if self._enhanced_manager:
            return self._enhanced_manager.clear_cache(user_id)
        else:
            return {
                "success": True,
                "message": "Cache operations not available in legacy mode"
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics and health information."""
        if self._enhanced_manager:
            return self._enhanced_manager.get_system_stats()
        else:
            return {
                "success": True,
                "mode": "legacy",
                "features": {
                    "modular_architecture": False,
                    "multiple_vector_stores": False,
                    "multiple_embedding_providers": False,
                    "enhanced_crud": False,
                    "caching": False
                }
            }
    
    def switch_embedding_provider(self, provider: str, model_name: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Switch embedding provider at runtime (Enhanced mode only).
        
        Args:
            provider: New embedding provider ('openai', 'huggingface', 'cohere', 'gemini')
            model_name: Model name for the provider
            api_key: API key if required
            
        Returns:
            Dict containing switch results
        """
        if self._enhanced_manager:
            try:
                self.config.update_embedding_provider(provider, model_name, api_key)
                self._enhanced_manager._initialize_components()
                return {
                    "success": True,
                    "message": f"Switched to {provider} embedding provider",
                    "provider": provider,
                    "model": model_name
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to switch embedding provider: {str(e)}"
                }
        else:
            return {
                "success": False,
                "error": "Provider switching requires enhanced mode with modular configuration"
            }
    
    def switch_vector_store(self, provider: str, **kwargs) -> Dict[str, Any]:
        """
        Switch vector store provider at runtime (Enhanced mode only).
        
        Args:
            provider: New vector store provider ('pinecone', 'qdrant', 'chroma', 'faiss')
            **kwargs: Provider-specific configuration options
            
        Returns:
            Dict containing switch results
        """
        if self._enhanced_manager:
            try:
                self.config.update_vector_store_provider(provider, **kwargs)
                self._enhanced_manager._initialize_components()
                return {
                    "success": True,
                    "message": f"Switched to {provider} vector store",
                    "provider": provider
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to switch vector store: {str(e)}"
                }
        else:
            return {
                "success": False,
                "error": "Provider switching requires enhanced mode with modular configuration"
            } 