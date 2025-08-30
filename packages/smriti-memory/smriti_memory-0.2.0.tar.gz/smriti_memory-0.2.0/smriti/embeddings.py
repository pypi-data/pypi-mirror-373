"""
Embedding abstraction layer for Smriti Memory.

This module provides a unified interface for different embedding providers,
allowing easy switching between OpenAI, HuggingFace, Cohere, Gemini, and custom models.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import numpy as np

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from .exceptions import EmbeddingError, ConfigurationError

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingConfig:
    """Configuration for embedding models."""
    provider: str  # 'openai', 'huggingface', 'cohere', 'gemini', 'custom'
    model_name: str
    api_key: Optional[str] = None
    model_kwargs: Optional[Dict[str, Any]] = None
    cache_embeddings: bool = True
    batch_size: int = 32
    max_retries: int = 3
    timeout: int = 30


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.cache = {} if config.cache_embeddings else None
        
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings efficiently."""
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        pass
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return f"{self.config.provider}:{self.config.model_name}:{hash(text)}"
    
    def _get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding if available."""
        if not self.cache:
            return None
        key = self._get_cache_key(text)
        return self.cache.get(key)
    
    def _cache_embedding(self, text: str, embedding: List[float]) -> None:
        """Cache embedding."""
        if not self.cache:
            return
        key = self._get_cache_key(text)
        self.cache[key] = embedding


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI embedding provider."""
    
    def __init__(self, config: EmbeddingConfig):
        if not OPENAI_AVAILABLE:
            raise EmbeddingError("OpenAI package not available. Install with: pip install openai")
        
        super().__init__(config)
        self.client = openai.OpenAI(
            api_key=config.api_key or os.getenv("OPENAI_API_KEY")
        )
        self._dimension = None
        
        if not self.client.api_key:
            raise ConfigurationError("OpenAI API key is required")
    
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        cached = self._get_cached_embedding(text)
        if cached:
            return cached
        
        try:
            response = self.client.embeddings.create(
                model=self.config.model_name,
                input=text
            )
            embedding = response.data[0].embedding
            self._cache_embedding(text, embedding)
            return embedding
        except Exception as e:
            raise EmbeddingError(f"OpenAI embedding failed: {str(e)}")
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings efficiently."""
        if not texts:
            return []
        
        # Check cache first
        embeddings = []
        uncached_indices = []
        uncached_texts = []
        
        for i, text in enumerate(texts):
            cached = self._get_cached_embedding(text)
            if cached:
                embeddings.append(cached)
            else:
                embeddings.append(None)
                uncached_indices.append(i)
                uncached_texts.append(text)
        
        # Process uncached texts in batches
        if uncached_texts:
            try:
                batch_size = min(self.config.batch_size, len(uncached_texts))
                for i in range(0, len(uncached_texts), batch_size):
                    batch = uncached_texts[i:i + batch_size]
                    response = self.client.embeddings.create(
                        model=self.config.model_name,
                        input=batch
                    )
                    
                    for j, embedding_data in enumerate(response.data):
                        original_idx = uncached_indices[i + j]
                        embedding = embedding_data.embedding
                        embeddings[original_idx] = embedding
                        self._cache_embedding(texts[original_idx], embedding)
                        
            except Exception as e:
                raise EmbeddingError(f"OpenAI batch embedding failed: {str(e)}")
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        if self._dimension is None:
            # Get dimension by embedding a test string
            test_embedding = self.embed_text("test")
            self._dimension = len(test_embedding)
        return self._dimension


class HuggingFaceEmbeddingProvider(BaseEmbeddingProvider):
    """HuggingFace embedding provider using SentenceTransformers."""
    
    def __init__(self, config: EmbeddingConfig):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise EmbeddingError("SentenceTransformers package not available. Install with: pip install sentence-transformers")
        
        super().__init__(config)
        
        try:
            model_kwargs = config.model_kwargs or {}
            self.model = SentenceTransformer(config.model_name, **model_kwargs)
        except Exception as e:
            raise EmbeddingError(f"Failed to load HuggingFace model {config.model_name}: {str(e)}")
    
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        cached = self._get_cached_embedding(text)
        if cached:
            return cached
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            embedding_list = embedding.tolist()
            self._cache_embedding(text, embedding_list)
            return embedding_list
        except Exception as e:
            raise EmbeddingError(f"HuggingFace embedding failed: {str(e)}")
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings efficiently."""
        if not texts:
            return []
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True, batch_size=self.config.batch_size)
            embedding_lists = embeddings.tolist()
            
            # Cache embeddings
            for text, embedding in zip(texts, embedding_lists):
                self._cache_embedding(text, embedding)
            
            return embedding_lists
        except Exception as e:
            raise EmbeddingError(f"HuggingFace batch embedding failed: {str(e)}")
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.model.get_sentence_embedding_dimension()


class CohereEmbeddingProvider(BaseEmbeddingProvider):
    """Cohere embedding provider."""
    
    def __init__(self, config: EmbeddingConfig):
        if not COHERE_AVAILABLE:
            raise EmbeddingError("Cohere package not available. Install with: pip install cohere")
        
        super().__init__(config)
        api_key = config.api_key or os.getenv("COHERE_API_KEY")
        if not api_key:
            raise ConfigurationError("Cohere API key is required")
        
        self.client = cohere.Client(api_key)
        self._dimension = None
    
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        cached = self._get_cached_embedding(text)
        if cached:
            return cached
        
        try:
            response = self.client.embed(
                texts=[text],
                model=self.config.model_name
            )
            embedding = response.embeddings[0]
            self._cache_embedding(text, embedding)
            return embedding
        except Exception as e:
            raise EmbeddingError(f"Cohere embedding failed: {str(e)}")
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings efficiently."""
        if not texts:
            return []
        
        try:
            # Process in batches
            all_embeddings = []
            batch_size = min(self.config.batch_size, len(texts))
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = self.client.embed(
                    texts=batch,
                    model=self.config.model_name
                )
                batch_embeddings = response.embeddings
                all_embeddings.extend(batch_embeddings)
                
                # Cache embeddings
                for text, embedding in zip(batch, batch_embeddings):
                    self._cache_embedding(text, embedding)
            
            return all_embeddings
        except Exception as e:
            raise EmbeddingError(f"Cohere batch embedding failed: {str(e)}")
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        if self._dimension is None:
            # Get dimension by embedding a test string
            test_embedding = self.embed_text("test")
            self._dimension = len(test_embedding)
        return self._dimension


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """Google Gemini embedding provider."""
    
    def __init__(self, config: EmbeddingConfig):
        if not GEMINI_AVAILABLE:
            raise EmbeddingError("Gemini package not available. Install with: pip install langchain-google-genai")
        
        super().__init__(config)
        api_key = config.api_key or os.getenv("GEMINI_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ConfigurationError("Gemini API key is required")
        
        try:
            self.model = GoogleGenerativeAIEmbeddings(
                model=config.model_name,
                google_api_key=api_key
            )
        except Exception as e:
            raise EmbeddingError(f"Failed to initialize Gemini model: {str(e)}")
        
        self._dimension = None
    
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        cached = self._get_cached_embedding(text)
        if cached:
            return cached
        
        try:
            embedding = self.model.embed_query(text)
            self._cache_embedding(text, embedding)
            return embedding
        except Exception as e:
            raise EmbeddingError(f"Gemini embedding failed: {str(e)}")
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings efficiently."""
        if not texts:
            return []
        
        try:
            embeddings = self.model.embed_documents(texts)
            
            # Cache embeddings
            for text, embedding in zip(texts, embeddings):
                self._cache_embedding(text, embedding)
            
            return embeddings
        except Exception as e:
            raise EmbeddingError(f"Gemini batch embedding failed: {str(e)}")
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        if self._dimension is None:
            # Get dimension by embedding a test string
            test_embedding = self.embed_text("test")
            self._dimension = len(test_embedding)
        return self._dimension


class CustomEmbeddingProvider(BaseEmbeddingProvider):
    """Custom embedding provider for user-defined models."""
    
    def __init__(self, config: EmbeddingConfig, custom_embedder):
        super().__init__(config)
        self.custom_embedder = custom_embedder
        
        # Validate custom embedder has required methods
        if not hasattr(custom_embedder, 'embed'):
            raise EmbeddingError("Custom embedder must have an 'embed' method")
        
        self._dimension = None
    
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        cached = self._get_cached_embedding(text)
        if cached:
            return cached
        
        try:
            embedding = self.custom_embedder.embed(text)
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
            self._cache_embedding(text, embedding)
            return embedding
        except Exception as e:
            raise EmbeddingError(f"Custom embedding failed: {str(e)}")
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings efficiently."""
        if not texts:
            return []
        
        try:
            # Check if custom embedder supports batch processing
            if hasattr(self.custom_embedder, 'embed_batch'):
                embeddings = self.custom_embedder.embed_batch(texts)
            else:
                # Fall back to individual embedding
                embeddings = [self.embed_text(text) for text in texts]
            
            # Ensure embeddings are lists, not numpy arrays
            if embeddings and isinstance(embeddings[0], np.ndarray):
                embeddings = [emb.tolist() for emb in embeddings]
            
            return embeddings
        except Exception as e:
            raise EmbeddingError(f"Custom batch embedding failed: {str(e)}")
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        if self._dimension is None:
            # Get dimension by embedding a test string
            test_embedding = self.embed_text("test")
            self._dimension = len(test_embedding)
        return self._dimension


class EmbeddingManager:
    """Main manager for embedding operations with support for multiple providers."""
    
    def __init__(self, config: EmbeddingConfig, custom_embedder=None):
        self.config = config
        self.provider = self._create_provider(custom_embedder)
    
    def _create_provider(self, custom_embedder=None) -> BaseEmbeddingProvider:
        """Create the appropriate embedding provider."""
        provider = self.config.provider.lower()
        
        if provider == "openai":
            return OpenAIEmbeddingProvider(self.config)
        elif provider == "huggingface":
            return HuggingFaceEmbeddingProvider(self.config)
        elif provider == "cohere":
            return CohereEmbeddingProvider(self.config)
        elif provider == "gemini":
            return GeminiEmbeddingProvider(self.config)
        elif provider == "custom":
            if custom_embedder is None:
                raise EmbeddingError("Custom embedder must be provided for custom provider")
            return CustomEmbeddingProvider(self.config, custom_embedder)
        else:
            raise EmbeddingError(f"Unknown embedding provider: {provider}")
    
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        if not text or not text.strip():
            raise EmbeddingError("Text cannot be empty")
        
        try:
            return self.provider.embed_text(text.strip())
        except Exception as e:
            logger.error(f"Embedding failed for text: {text[:100]}...")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings efficiently."""
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [text.strip() for text in texts if text and text.strip()]
        if not valid_texts:
            raise EmbeddingError("No valid texts to embed")
        
        try:
            return self.provider.embed_batch(valid_texts)
        except Exception as e:
            logger.error(f"Batch embedding failed for {len(texts)} texts")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.provider.get_embedding_dimension()
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        if self.provider.cache:
            self.provider.cache.clear()
            logger.info("Embedding cache cleared")


# Helper functions for easy usage
def create_openai_embedder(model_name: str = "text-embedding-3-small", api_key: Optional[str] = None) -> EmbeddingManager:
    """Create an OpenAI embedding manager."""
    config = EmbeddingConfig(provider="openai", model_name=model_name, api_key=api_key)
    return EmbeddingManager(config)

def create_huggingface_embedder(model_name: str = "all-MiniLM-L6-v2") -> EmbeddingManager:
    """Create a HuggingFace embedding manager."""
    config = EmbeddingConfig(provider="huggingface", model_name=model_name)
    return EmbeddingManager(config)

def create_cohere_embedder(model_name: str = "embed-english-v2.0", api_key: Optional[str] = None) -> EmbeddingManager:
    """Create a Cohere embedding manager."""
    config = EmbeddingConfig(provider="cohere", model_name=model_name, api_key=api_key)
    return EmbeddingManager(config)

def create_gemini_embedder(model_name: str = "models/embedding-001", api_key: Optional[str] = None) -> EmbeddingManager:
    """Create a Gemini embedding manager."""
    config = EmbeddingConfig(provider="gemini", model_name=model_name, api_key=api_key)
    return EmbeddingManager(config) 