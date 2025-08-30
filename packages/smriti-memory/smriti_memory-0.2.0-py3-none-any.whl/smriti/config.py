"""
Configuration management for Smriti Memory.
"""

import os
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, field
from .exceptions import ConfigurationError


@dataclass 
class EmbeddingProviderConfig:
    """Configuration for embedding providers."""
    provider: str = "gemini"  # 'openai', 'huggingface', 'cohere', 'gemini', 'custom'
    model_name: str = "models/embedding-001"
    api_key: Optional[str] = None
    model_kwargs: Optional[Dict[str, Any]] = None
    cache_embeddings: bool = True
    batch_size: int = 32
    max_retries: int = 3
    timeout: int = 30


@dataclass
class VectorStoreConfig:
    """Configuration for vector database providers."""
    provider: str = "pinecone"  # 'pinecone', 'qdrant', 'weaviate', 'chroma', 'faiss', 'sqlite'
    
    # Common settings
    embedding_dimension: int = 768
    similarity_metric: str = "cosine"  # 'cosine', 'euclidean', 'dot_product'
    
    # Provider-specific settings
    api_key: Optional[str] = None
    environment: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    collection_name: str = "smriti_memories"
    
    # Index and Namespace Configuration
    custom_index_name: Optional[str] = None  # Custom index name (if not specified, auto-generated)
    default_namespace: str = "user_understanding"  # Default namespace for memories
    
    # Performance settings
    batch_size: int = 100
    timeout: int = 30
    max_retries: int = 3
    
    # Local storage settings (for FAISS, SQLite)
    storage_path: str = "./smriti_data"
    
    # Additional provider-specific parameters
    provider_kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMProviderConfig:
    """Configuration for LLM providers."""
    provider: str = "groq"  # 'groq', 'openai', 'anthropic', 'huggingface', 'custom'
    model_name: str = "llama-3.1-8b-instant"
    api_key: Optional[str] = None
    temperature: float = 0.3
    max_tokens: Optional[int] = None
    timeout: int = 30
    max_retries: int = 3
    provider_kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryConfig:
    """Enhanced configuration for the Smriti Memory system with modular architecture."""
    
    # Modular provider configurations
    embedding_config: Optional[EmbeddingProviderConfig] = None
    vector_store_config: Optional[VectorStoreConfig] = None
    llm_config: Optional[LLMProviderConfig] = None
    
    # Backward compatibility - Legacy configurations
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "us-east-1"
    pinecone_cloud: str = "aws"
    groq_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    llm_model: str = "llama-3.1-8b-instant"
    llm_temperature: float = 0.3
    embedding_model: str = "models/embedding-001"
    
    # Memory Configuration
    default_namespace: str = "user_understanding"
    max_memory_length: int = 1000
    similarity_threshold: float = 0.7
    max_search_results: int = 10
    
    # Advanced Memory Features
    enable_graph_memory: bool = False
    enable_memory_summarization: bool = False
    summarization_interval: int = 100  # Number of memories before summarization
    memory_retention_days: int = 365
    enable_memory_clustering: bool = False
    
    # Performance Configuration
    enable_async_operations: bool = True
    batch_processing: bool = True
    cache_enabled: bool = True
    cache_size: int = 1000
    
    # System Configuration
    enable_logging: bool = True
    log_level: str = "INFO"
    debug_mode: bool = False
    
    def __post_init__(self):
        """Initialize configuration with environment variables and validation."""
        self._load_from_env()
        self._create_default_configs()
        self._validate_config()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Load legacy environment variables for backward compatibility
        if not self.pinecone_api_key:
            self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        
        if not self.groq_api_key:
            self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not self.gemini_api_key:
            self.gemini_api_key = os.getenv("GEMINI_KEY")
        
        # Load environment variables for specific provider configs
        openai_key = os.getenv("OPENAI_API_KEY")
        cohere_key = os.getenv("COHERE_API_KEY")
        qdrant_host = os.getenv("QDRANT_HOST")
        qdrant_port = os.getenv("QDRANT_PORT")
        chroma_host = os.getenv("CHROMA_HOST")
        
        # Store for use in default config creation
        self._env_vars = {
            "openai_key": openai_key,
            "cohere_key": cohere_key,
            "qdrant_host": qdrant_host,
            "qdrant_port": int(qdrant_port) if qdrant_port else None,
            "chroma_host": chroma_host
        }
    
    def _create_default_configs(self):
        """Create default configurations for providers if not specified."""
        # Create default embedding config if not provided
        if self.embedding_config is None:
            self.embedding_config = EmbeddingProviderConfig(
                provider="gemini",
                model_name=self.embedding_model,
                api_key=self.gemini_api_key
            )
        
        # Create default vector store config if not provided  
        if self.vector_store_config is None:
            self.vector_store_config = VectorStoreConfig(
                provider="pinecone",
                api_key=self.pinecone_api_key,
                environment=self.pinecone_environment
            )
        
        # Create default LLM config if not provided
        if self.llm_config is None:
            self.llm_config = LLMProviderConfig(
                provider="groq",
                model_name=self.llm_model,
                api_key=self.groq_api_key,
                temperature=self.llm_temperature
            )
    
    def _validate_config(self):
        """Validate the configuration."""
        # Validate embedding configuration
        if self.embedding_config:
            if not self.embedding_config.provider:
                raise ConfigurationError("Embedding provider must be specified")
            
            if self.embedding_config.provider in ["openai", "cohere", "gemini"] and not self.embedding_config.api_key:
                raise ConfigurationError(f"API key required for {self.embedding_config.provider} embedding provider")
        
        # Validate vector store configuration
        if self.vector_store_config:
            if not self.vector_store_config.provider:
                raise ConfigurationError("Vector store provider must be specified")
                
            if self.vector_store_config.provider == "pinecone" and not self.vector_store_config.api_key:
                raise ConfigurationError("Pinecone API key is required")
                
            if self.vector_store_config.embedding_dimension <= 0:
                raise ConfigurationError("Embedding dimension must be positive")
        
        # Validate LLM configuration
        if self.llm_config:
            if not self.llm_config.provider:
                raise ConfigurationError("LLM provider must be specified")
                
            if self.llm_config.provider in ["groq", "openai", "anthropic"] and not self.llm_config.api_key:
                raise ConfigurationError(f"API key required for {self.llm_config.provider} LLM provider")
                
            if not 0.0 <= self.llm_config.temperature <= 2.0:
                raise ConfigurationError("LLM temperature must be between 0.0 and 2.0")
        
        # Validate legacy configuration for backward compatibility
        if not any([self.pinecone_api_key, self.groq_api_key, self.gemini_api_key]):
            # Check if modular configs have the required keys
            has_embedding_key = self.embedding_config and self.embedding_config.api_key
            has_vector_key = self.vector_store_config and self.vector_store_config.api_key  
            has_llm_key = self.llm_config and self.llm_config.api_key
            
            if not any([has_embedding_key, has_vector_key, has_llm_key]):
                raise ConfigurationError(
                    "At least one API key must be provided. "
                    "Please configure provider API keys or set legacy environment variables."
                )
        
        # Validate similarity threshold
        if not 0.0 <= self.similarity_threshold <= 1.0:
            raise ConfigurationError("Similarity threshold must be between 0.0 and 1.0")
        
        # Validate search results limit
        if self.max_search_results <= 0:
            raise ConfigurationError("Max search results must be positive")
        
        # Validate advanced features
        if self.summarization_interval <= 0:
            raise ConfigurationError("Summarization interval must be positive")
        
        if self.memory_retention_days <= 0:
            raise ConfigurationError("Memory retention days must be positive")
        
        if self.cache_size <= 0:
            raise ConfigurationError("Cache size must be positive")
    
    def get_embedding_config(self) -> EmbeddingProviderConfig:
        """Get the embedding configuration."""
        return self.embedding_config
    
    def get_vector_store_config(self) -> VectorStoreConfig:
        """Get the vector store configuration."""
        return self.vector_store_config
    
    def get_llm_config(self) -> LLMProviderConfig:
        """Get the LLM configuration."""
        return self.llm_config
    
    def update_embedding_provider(self, provider: str, model_name: str, api_key: Optional[str] = None):
        """Update embedding provider configuration."""
        self.embedding_config.provider = provider
        self.embedding_config.model_name = model_name
        if api_key:
            self.embedding_config.api_key = api_key
    
    def update_vector_store_provider(self, provider: str, **kwargs):
        """Update vector store provider configuration."""
        self.vector_store_config.provider = provider
        for key, value in kwargs.items():
            if hasattr(self.vector_store_config, key):
                setattr(self.vector_store_config, key, value)
    
    def update_llm_provider(self, provider: str, model_name: str, api_key: Optional[str] = None, **kwargs):
        """Update LLM provider configuration."""
        self.llm_config.provider = provider
        self.llm_config.model_name = model_name
        if api_key:
            self.llm_config.api_key = api_key
        for key, value in kwargs.items():
            if hasattr(self.llm_config, key):
                setattr(self.llm_config, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "pinecone_api_key": self.pinecone_api_key,
            "pinecone_environment": self.pinecone_environment,
            "pinecone_cloud": self.pinecone_cloud,
            "groq_api_key": self.groq_api_key,
            "gemini_api_key": self.gemini_api_key,
            "llm_model": self.llm_model,
            "llm_temperature": self.llm_temperature,
            "default_namespace": self.default_namespace,
            "max_memory_length": self.max_memory_length,
            "similarity_threshold": self.similarity_threshold,
            "max_search_results": self.max_search_results,
            "embedding_model": self.embedding_model,
            "enable_logging": self.enable_logging,
            "log_level": self.log_level,
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "MemoryConfig":
        """Create configuration from dictionary."""
        return cls(**config_dict)


# Helper functions for creating specific configurations
def create_openai_config(
    openai_api_key: str,
    embedding_model: str = "text-embedding-3-small",
    llm_model: str = "gpt-4",
    vector_store: str = "pinecone",
    **kwargs
) -> MemoryConfig:
    """Create a configuration using OpenAI for embeddings and LLM."""
    embedding_config = EmbeddingProviderConfig(
        provider="openai",
        model_name=embedding_model,
        api_key=openai_api_key
    )
    
    llm_config = LLMProviderConfig(
        provider="openai", 
        model_name=llm_model,
        api_key=openai_api_key
    )
    
    vector_config = VectorStoreConfig(
        provider=vector_store,
        **kwargs
    )
    
    return MemoryConfig(
        embedding_config=embedding_config,
        llm_config=llm_config,
        vector_store_config=vector_config
    )


def create_local_config(
    storage_path: str = "./smriti_data",
    embedding_model: str = "all-MiniLM-L6-v2",
    vector_store: str = "faiss"
) -> MemoryConfig:
    """Create a configuration for local deployment using HuggingFace and FAISS."""
    embedding_config = EmbeddingProviderConfig(
        provider="huggingface",
        model_name=embedding_model
    )
    
    vector_config = VectorStoreConfig(
        provider=vector_store,
        storage_path=storage_path
    )
    
    # Note: For local config, you'd still need an LLM provider
    llm_config = LLMProviderConfig(
        provider="groq",  # Could be swapped for local LLM
        model_name="llama-3.1-8b-instant"
    )
    
    return MemoryConfig(
        embedding_config=embedding_config,
        vector_store_config=vector_config,
        llm_config=llm_config
    )


def create_cloud_config(
    providers: Dict[str, Dict[str, Any]]
) -> MemoryConfig:
    """Create a cloud configuration with custom provider settings.
    
    Args:
        providers: Dict with 'embedding', 'vector_store', 'llm' keys containing provider configs
    """
    embedding_config = EmbeddingProviderConfig(**providers.get("embedding", {}))
    vector_config = VectorStoreConfig(**providers.get("vector_store", {}))
    llm_config = LLMProviderConfig(**providers.get("llm", {}))
    
    return MemoryConfig(
        embedding_config=embedding_config,
        vector_store_config=vector_config,
        llm_config=llm_config
    ) 