"""
Framework adapters for Smriti Memory.

This module provides adapters for popular AI frameworks like LangChain and LlamaIndex,
enabling seamless integration of Smriti Memory as a drop-in replacement for their
built-in memory systems.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod

# Optional imports for different frameworks
try:
    from langchain.memory.chat_memory import BaseChatMemory
    from langchain.schema import BaseMessage, HumanMessage, AIMessage
    from langchain.memory.utils import get_prompt_input_key
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Create placeholder classes
    class BaseChatMemory:
        pass
    class BaseMessage:
        pass

try:
    from llama_index.core.memory import BaseMemory as LlamaBaseMemory
    from llama_index.core.llms.types import ChatMessage, MessageRole
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    LLAMAINDEX_AVAILABLE = False
    # Create placeholder classes
    class LlamaBaseMemory:
        pass
    class ChatMessage:
        pass
    class MessageRole:
        pass

from .memory_manager import MemoryManager
from .config import MemoryConfig
from .exceptions import SmritiError

logger = logging.getLogger(__name__)


class SmritiLangChainMemory(BaseChatMemory):
    """LangChain adapter for Smriti Memory."""
    
    def __init__(
        self,
        user_id: str,
        memory_manager: Optional[MemoryManager] = None,
        config: Optional[MemoryConfig] = None,
        human_prefix: str = "Human",
        ai_prefix: str = "AI",
        memory_key: str = "history",
        return_messages: bool = False,
        input_key: Optional[str] = None,
        output_key: Optional[str] = None,
        max_context_memories: int = 10,
        **kwargs
    ):
        """Initialize Smriti LangChain memory adapter.
        
        Args:
            user_id: Unique identifier for the user/conversation
            memory_manager: Smriti MemoryManager instance (optional)
            config: Smriti configuration (optional)
            human_prefix: Prefix for human messages
            ai_prefix: Prefix for AI messages
            memory_key: Key to store memory in prompt variables
            return_messages: Whether to return messages or formatted string
            input_key: Key for input in the prompt template
            output_key: Key for output in the prompt template
            max_context_memories: Maximum number of context memories to retrieve
            **kwargs: Additional arguments passed to BaseChatMemory
        """
        if not LANGCHAIN_AVAILABLE:
            raise SmritiError("LangChain is not available. Install with: pip install langchain")
        
        super().__init__(
            return_messages=return_messages,
            input_key=input_key,
            output_key=output_key,
            **kwargs
        )
        
        self.user_id = user_id
        self.memory_manager = memory_manager or MemoryManager(config)
        self.human_prefix = human_prefix
        self.ai_prefix = ai_prefix
        self.memory_key = memory_key
        self.max_context_memories = max_context_memories
        
        logger.info(f"Initialized Smriti LangChain memory for user {user_id}")
    
    @property
    def memory_variables(self) -> List[str]:
        """Return memory variables that this memory class will use."""
        return [self.memory_key]
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load memory variables from Smriti Memory."""
        try:
            # Get the input text for context retrieval
            prompt_input_key = self.input_key or get_prompt_input_key(inputs, self.memory_variables)
            input_text = inputs.get(prompt_input_key, "")
            
            if input_text:
                # Search for relevant memories
                search_result = self.memory_manager.search_memories(
                    user_id=self.user_id,
                    query=input_text,
                    top_k=self.max_context_memories
                )
                
                memories = search_result.get("results", [])
            else:
                memories = []
            
            if self.return_messages:
                # Return as LangChain message objects
                messages = []
                for memory in memories:
                    text = memory.get("text", "")
                    # Try to parse if it contains both human and AI parts
                    if " AI: " in text:
                        parts = text.split(" AI: ", 1)
                        if len(parts) == 2:
                            human_part = parts[0].replace(f"{self.human_prefix}: ", "")
                            ai_part = parts[1]
                            messages.append(HumanMessage(content=human_part))
                            messages.append(AIMessage(content=ai_part))
                    else:
                        # Treat as human message
                        content = text.replace(f"{self.human_prefix}: ", "")
                        messages.append(HumanMessage(content=content))
                
                return {self.memory_key: messages}
            else:
                # Return as formatted string
                if memories:
                    context_lines = []
                    for memory in memories:
                        text = memory.get("text", "")
                        score = memory.get("score", 0)
                        context_lines.append(f"[Relevance: {score:.2f}] {text}")
                    
                    memory_string = "\n".join(context_lines)
                else:
                    memory_string = ""
                
                return {self.memory_key: memory_string}
                
        except Exception as e:
            logger.error(f"Failed to load memory variables: {str(e)}")
            return {self.memory_key: [] if self.return_messages else ""}
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save the context from this conversation to Smriti Memory."""
        try:
            # Get input and output keys
            prompt_input_key = self.input_key or get_prompt_input_key(inputs, self.memory_variables)
            output_key = self.output_key or list(outputs.keys())[0]
            
            # Extract input and output text
            input_text = inputs.get(prompt_input_key, "")
            output_text = outputs.get(output_key, "")
            
            if input_text or output_text:
                # Create chat thread for Smriti
                chat_thread = []
                if input_text:
                    chat_thread.append({"user": input_text})
                if output_text:
                    chat_thread.append({"ai": output_text})
                
                # Save to Smriti Memory
                result = self.memory_manager.add_memory(self.user_id, chat_thread)
                
                if result.get("success"):
                    logger.debug(f"Saved conversation to Smriti memory: {result.get('action', 'unknown')}")
                else:
                    logger.warning(f"Failed to save to Smriti memory: {result.get('error', 'unknown error')}")
                    
        except Exception as e:
            logger.error(f"Failed to save context to Smriti memory: {str(e)}")
    
    def clear(self) -> None:
        """Clear the memory for this user."""
        try:
            result = self.memory_manager.delete_user_memories(self.user_id, confirm_deletion=True)
            if result.get("success"):
                logger.info(f"Cleared Smriti memory for user {self.user_id}")
            else:
                logger.warning(f"Failed to clear Smriti memory: {result.get('error', 'unknown error')}")
        except Exception as e:
            logger.error(f"Failed to clear Smriti memory: {str(e)}")


class SmritiLlamaIndexMemory(LlamaBaseMemory):
    """LlamaIndex adapter for Smriti Memory."""
    
    def __init__(
        self,
        user_id: str,
        memory_manager: Optional[MemoryManager] = None,
        config: Optional[MemoryConfig] = None,
        max_context_memories: int = 10,
        **kwargs
    ):
        """Initialize Smriti LlamaIndex memory adapter.
        
        Args:
            user_id: Unique identifier for the user/conversation
            memory_manager: Smriti MemoryManager instance (optional)
            config: Smriti configuration (optional)
            max_context_memories: Maximum number of context memories to retrieve
            **kwargs: Additional arguments
        """
        if not LLAMAINDEX_AVAILABLE:
            raise SmritiError("LlamaIndex is not available. Install with: pip install llama-index")
        
        super().__init__(**kwargs)
        
        self.user_id = user_id
        self.memory_manager = memory_manager or MemoryManager(config)
        self.max_context_memories = max_context_memories
        
        logger.info(f"Initialized Smriti LlamaIndex memory for user {user_id}")
    
    def get_all(self) -> List[ChatMessage]:
        """Get all chat messages from memory."""
        try:
            # For LlamaIndex, we'll return recent memories as chat messages
            search_result = self.memory_manager.search_memories(
                user_id=self.user_id,
                query="",  # Empty query to get recent memories
                top_k=self.max_context_memories
            )
            
            messages = []
            for memory in search_result.get("results", []):
                text = memory.get("text", "")
                
                # Try to parse if it contains both user and assistant parts
                if " AI: " in text:
                    parts = text.split(" AI: ", 1)
                    if len(parts) == 2:
                        user_part = parts[0].replace("Human: ", "")
                        ai_part = parts[1]
                        messages.append(ChatMessage(role=MessageRole.USER, content=user_part))
                        messages.append(ChatMessage(role=MessageRole.ASSISTANT, content=ai_part))
                else:
                    # Treat as user message
                    content = text.replace("Human: ", "")
                    messages.append(ChatMessage(role=MessageRole.USER, content=content))
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get all messages: {str(e)}")
            return []
    
    def get_relevant(self, query: str, **kwargs) -> List[ChatMessage]:
        """Get relevant chat messages based on query."""
        try:
            search_result = self.memory_manager.search_memories(
                user_id=self.user_id,
                query=query,
                top_k=self.max_context_memories
            )
            
            messages = []
            for memory in search_result.get("results", []):
                text = memory.get("text", "")
                
                # Convert to ChatMessage format
                if " AI: " in text:
                    parts = text.split(" AI: ", 1)
                    if len(parts) == 2:
                        user_part = parts[0].replace("Human: ", "")
                        ai_part = parts[1]
                        messages.append(ChatMessage(role=MessageRole.USER, content=user_part))
                        messages.append(ChatMessage(role=MessageRole.ASSISTANT, content=ai_part))
                else:
                    content = text.replace("Human: ", "")
                    messages.append(ChatMessage(role=MessageRole.USER, content=content))
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get relevant messages: {str(e)}")
            return []
    
    def put(self, message: ChatMessage) -> None:
        """Store a chat message in memory."""
        try:
            # Convert ChatMessage to Smriti format
            content = message.content
            role = message.role
            
            if role == MessageRole.USER:
                chat_thread = [{"user": content}]
            elif role == MessageRole.ASSISTANT:
                chat_thread = [{"ai": content}]
            else:
                # For other roles, treat as user message
                chat_thread = [{"user": content}]
            
            # Save to Smriti Memory
            result = self.memory_manager.add_memory(self.user_id, chat_thread)
            
            if result.get("success"):
                logger.debug(f"Saved message to Smriti memory: {result.get('action', 'unknown')}")
            else:
                logger.warning(f"Failed to save to Smriti memory: {result.get('error', 'unknown error')}")
                
        except Exception as e:
            logger.error(f"Failed to put message to Smriti memory: {str(e)}")
    
    def reset(self) -> None:
        """Clear all messages from memory."""
        try:
            result = self.memory_manager.delete_user_memories(self.user_id, confirm_deletion=True)
            if result.get("success"):
                logger.info(f"Reset Smriti memory for user {self.user_id}")
            else:
                logger.warning(f"Failed to reset Smriti memory: {result.get('error', 'unknown error')}")
        except Exception as e:
            logger.error(f"Failed to reset Smriti memory: {str(e)}")


class SmritiMemoryBuffer:
    """Universal memory buffer that works with multiple frameworks."""
    
    def __init__(
        self,
        user_id: str,
        memory_manager: Optional[MemoryManager] = None,
        config: Optional[MemoryConfig] = None,
        max_context_length: int = 5000,
        **kwargs
    ):
        """Initialize universal Smriti memory buffer.
        
        Args:
            user_id: Unique identifier for the user/conversation
            memory_manager: Smriti MemoryManager instance (optional)
            config: Smriti configuration (optional)
            max_context_length: Maximum context length in characters
            **kwargs: Additional arguments
        """
        self.user_id = user_id
        self.memory_manager = memory_manager or MemoryManager(config)
        self.max_context_length = max_context_length
        
        logger.info(f"Initialized universal Smriti memory buffer for user {user_id}")
    
    def add_message(self, content: str, role: str = "user") -> Dict[str, Any]:
        """Add a message to memory."""
        try:
            if role.lower() in ["user", "human"]:
                chat_thread = [{"user": content}]
            elif role.lower() in ["assistant", "ai", "bot"]:
                chat_thread = [{"ai": content}]
            else:
                chat_thread = [{"user": content}]  # Default to user
            
            return self.memory_manager.add_memory(self.user_id, chat_thread)
            
        except Exception as e:
            logger.error(f"Failed to add message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def add_exchange(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        """Add a complete user-AI exchange to memory."""
        try:
            chat_thread = [
                {"user": user_message},
                {"ai": ai_response}
            ]
            return self.memory_manager.add_memory(self.user_id, chat_thread)
            
        except Exception as e:
            logger.error(f"Failed to add exchange: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_context(self, query: str = "", max_memories: int = 10) -> str:
        """Get formatted context for the current query."""
        try:
            search_result = self.memory_manager.search_memories(
                user_id=self.user_id,
                query=query,
                top_k=max_memories
            )
            
            memories = search_result.get("results", [])
            if not memories:
                return ""
            
            # Format as context string with length limit
            context_parts = []
            total_length = 0
            
            for memory in memories:
                text = memory.get("text", "")
                score = memory.get("score", 0)
                formatted_text = f"[Relevance: {score:.2f}] {text}"
                
                if total_length + len(formatted_text) <= self.max_context_length:
                    context_parts.append(formatted_text)
                    total_length += len(formatted_text)
                else:
                    break
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Failed to get context: {str(e)}")
            return ""
    
    def get_memories(self, query: str = "", max_memories: int = 10) -> List[Dict[str, Any]]:
        """Get raw memories for custom processing."""
        try:
            search_result = self.memory_manager.search_memories(
                user_id=self.user_id,
                query=query,
                top_k=max_memories
            )
            return search_result.get("results", [])
            
        except Exception as e:
            logger.error(f"Failed to get memories: {str(e)}")
            return []
    
    def clear_memory(self) -> Dict[str, Any]:
        """Clear all memories for this user."""
        try:
            return self.memory_manager.delete_user_memories(self.user_id, confirm_deletion=True)
        except Exception as e:
            logger.error(f"Failed to clear memory: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics for this user."""
        try:
            return self.memory_manager.get_user_stats(self.user_id)
        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {"success": False, "error": str(e)}


# Factory functions for easy creation

def create_langchain_memory(
    user_id: str,
    config: Optional[MemoryConfig] = None,
    **kwargs
) -> 'SmritiLangChainMemory':
    """Create a LangChain-compatible Smriti memory instance."""
    if not LANGCHAIN_AVAILABLE:
        raise SmritiError("LangChain is not available. Install with: pip install langchain")
    
    return SmritiLangChainMemory(user_id=user_id, config=config, **kwargs)


def create_llamaindex_memory(
    user_id: str,
    config: Optional[MemoryConfig] = None,
    **kwargs
) -> 'SmritiLlamaIndexMemory':
    """Create a LlamaIndex-compatible Smriti memory instance."""
    if not LLAMAINDEX_AVAILABLE:
        raise SmritiError("LlamaIndex is not available. Install with: pip install llama-index")
    
    return SmritiLlamaIndexMemory(user_id=user_id, config=config, **kwargs)


def create_universal_memory(
    user_id: str,
    config: Optional[MemoryConfig] = None,
    **kwargs
) -> SmritiMemoryBuffer:
    """Create a universal Smriti memory buffer."""
    return SmritiMemoryBuffer(user_id=user_id, config=config, **kwargs)


# Example usage classes for common patterns

class SmritiConversationChain:
    """Example conversation chain using Smriti memory with LangChain."""
    
    def __init__(
        self,
        user_id: str,
        llm,  # LangChain LLM instance
        config: Optional[MemoryConfig] = None,
        **kwargs
    ):
        """Initialize conversation chain with Smriti memory."""
        if not LANGCHAIN_AVAILABLE:
            raise SmritiError("LangChain is not available for ConversationChain")
        
        from langchain.chains import ConversationChain
        
        self.user_id = user_id
        self.memory = create_langchain_memory(user_id, config, **kwargs)
        self.chain = ConversationChain(
            llm=llm,
            memory=self.memory,
            verbose=kwargs.get("verbose", False)
        )
    
    def predict(self, input_text: str) -> str:
        """Generate a response using the conversation chain."""
        return self.chain.predict(input=input_text)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return self.memory.memory_manager.get_user_stats(self.user_id)


class SmritiChatEngine:
    """Example chat engine using Smriti memory with LlamaIndex."""
    
    def __init__(
        self,
        user_id: str,
        llm,  # LlamaIndex LLM instance
        config: Optional[MemoryConfig] = None,
        **kwargs
    ):
        """Initialize chat engine with Smriti memory."""
        if not LLAMAINDEX_AVAILABLE:
            raise SmritiError("LlamaIndex is not available for ChatEngine")
        
        self.user_id = user_id
        self.memory = create_llamaindex_memory(user_id, config, **kwargs)
        self.llm = llm
    
    def chat(self, message: str) -> str:
        """Chat with memory context."""
        # Get relevant context
        relevant_messages = self.memory.get_relevant(message)
        
        # Build context string
        context = ""
        if relevant_messages:
            context_parts = []
            for msg in relevant_messages[-5:]:  # Last 5 relevant messages
                context_parts.append(f"{msg.role.value}: {msg.content}")
            context = "\n".join(context_parts) + "\n\n"
        
        # Generate response
        full_prompt = f"{context}User: {message}\nAssistant:"
        response = self.llm.complete(full_prompt).text
        
        # Store the exchange
        from llama_index.core.llms.types import ChatMessage, MessageRole
        self.memory.put(ChatMessage(role=MessageRole.USER, content=message))
        self.memory.put(ChatMessage(role=MessageRole.ASSISTANT, content=response))
        
        return response
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return self.memory.memory_manager.get_user_stats(self.user_id) 