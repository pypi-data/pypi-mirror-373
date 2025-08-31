"""
Embedder systems for AIFlow Vector Database Integration.

Provides text-to-vector embedding capabilities using various providers.
"""

import asyncio
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class BaseEmbedder(ABC):
    """Abstract base class for text embedders."""
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key
        self.dimension = None  # Will be set by specific implementations
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of text strings."""
        pass
    
    def get_dimension(self) -> Optional[int]:
        """Get the embedding dimension."""
        return self.dimension
    
    def get_info(self) -> Dict[str, Any]:
        """Get embedder information."""
        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "provider": self.__class__.__name__
        }


class OpenAIEmbedder(BaseEmbedder):
    """OpenAI embeddings provider."""
    
    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        api_key: Optional[str] = None
    ):
        super().__init__(model_name, api_key or os.getenv("OPENAI_API_KEY"))
        
        # Set dimensions based on model
        model_dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        self.dimension = model_dimensions.get(model_name, 1536)
        
        self._client = None
    
    def _get_client(self):
        """Get OpenAI client."""
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("OpenAI library not installed. Run: pip install openai")
        return self._client
    
    async def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        try:
            client = self._get_client()
            response = client.embeddings.create(
                model=self.model_name,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error embedding text with OpenAI: {e}")
            raise
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of text strings."""
        try:
            client = self._get_client()
            response = client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Error embedding batch with OpenAI: {e}")
            raise


class CohereEmbedder(BaseEmbedder):
    """Cohere embeddings provider."""
    
    def __init__(
        self,
        model_name: str = "embed-english-v3.0",
        api_key: Optional[str] = None
    ):
        super().__init__(model_name, api_key or os.getenv("COHERE_API_KEY"))
        
        # Set dimensions based on model
        model_dimensions = {
            "embed-english-v3.0": 1024,
            "embed-multilingual-v3.0": 1024,
            "embed-english-light-v3.0": 384,
            "embed-multilingual-light-v3.0": 384
        }
        self.dimension = model_dimensions.get(model_name, 1024)
        
        self._client = None
    
    def _get_client(self):
        """Get Cohere client."""
        if self._client is None:
            try:
                import cohere
                self._client = cohere.Client(api_key=self.api_key)
            except ImportError:
                raise ImportError("Cohere library not installed. Run: pip install cohere")
        return self._client
    
    async def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        try:
            client = self._get_client()
            response = client.embed(
                texts=[text],
                model=self.model_name,
                input_type="search_document"
            )
            return response.embeddings[0]
        except Exception as e:
            logger.error(f"Error embedding text with Cohere: {e}")
            raise
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of text strings."""
        try:
            client = self._get_client()
            response = client.embed(
                texts=texts,
                model=self.model_name,
                input_type="search_document"
            )
            return response.embeddings
        except Exception as e:
            logger.error(f"Error embedding batch with Cohere: {e}")
            raise


class HuggingFaceEmbedder(BaseEmbedder):
    """Hugging Face embeddings provider."""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        api_key: Optional[str] = None
    ):
        super().__init__(model_name, api_key)
        
        # Common model dimensions
        model_dimensions = {
            "sentence-transformers/all-MiniLM-L6-v2": 384,
            "sentence-transformers/all-mpnet-base-v2": 768,
            "sentence-transformers/all-distilroberta-v1": 768
        }
        self.dimension = model_dimensions.get(model_name, 384)
        
        self._model = None
        self._tokenizer = None
    
    def _load_model(self):
        """Load Hugging Face model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError(
                    "Sentence Transformers library not installed. "
                    "Run: pip install sentence-transformers"
                )
    
    async def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        try:
            self._load_model()
            embedding = self._model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error embedding text with Hugging Face: {e}")
            raise
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of text strings."""
        try:
            self._load_model()
            embeddings = self._model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error embedding batch with Hugging Face: {e}")
            raise


class EmbedderManager:
    """Manager for multiple embedders."""
    
    def __init__(self):
        self.embedders: Dict[str, BaseEmbedder] = {}
        self.default_embedder: Optional[str] = None
    
    def add_embedder(self, name: str, embedder: BaseEmbedder, set_as_default: bool = False):
        """Add an embedder."""
        self.embedders[name] = embedder
        if set_as_default or self.default_embedder is None:
            self.default_embedder = name
    
    def get_embedder(self, name: Optional[str] = None) -> Optional[BaseEmbedder]:
        """Get an embedder by name or default."""
        if name is None:
            name = self.default_embedder
        return self.embedders.get(name)
    
    def list_embedders(self) -> List[str]:
        """List available embedders."""
        return list(self.embedders.keys())
    
    async def embed_text(self, text: str, embedder_name: Optional[str] = None) -> List[float]:
        """Embed text using specified or default embedder."""
        embedder = self.get_embedder(embedder_name)
        if embedder is None:
            raise ValueError(f"Embedder not found: {embedder_name}")
        return await embedder.embed_text(text)
    
    async def embed_batch(
        self,
        texts: List[str],
        embedder_name: Optional[str] = None
    ) -> List[List[float]]:
        """Embed batch using specified or default embedder."""
        embedder = self.get_embedder(embedder_name)
        if embedder is None:
            raise ValueError(f"Embedder not found: {embedder_name}")
        return await embedder.embed_batch(texts)
    
    def get_dimension(self, embedder_name: Optional[str] = None) -> Optional[int]:
        """Get embedding dimension for specified or default embedder."""
        embedder = self.get_embedder(embedder_name)
        if embedder is None:
            return None
        return embedder.get_dimension()
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all embedders."""
        return {
            "embedders": {name: embedder.get_info() for name, embedder in self.embedders.items()},
            "default_embedder": self.default_embedder,
            "total_embedders": len(self.embedders)
        }


# Factory functions for easy embedder creation
def create_openai_embedder(
    model_name: str = "text-embedding-3-small",
    api_key: Optional[str] = None
) -> OpenAIEmbedder:
    """Create OpenAI embedder."""
    return OpenAIEmbedder(model_name, api_key)


def create_cohere_embedder(
    model_name: str = "embed-english-v3.0",
    api_key: Optional[str] = None
) -> CohereEmbedder:
    """Create Cohere embedder."""
    return CohereEmbedder(model_name, api_key)


def create_huggingface_embedder(
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
) -> HuggingFaceEmbedder:
    """Create Hugging Face embedder."""
    return HuggingFaceEmbedder(model_name)


def create_default_embedder_manager() -> EmbedderManager:
    """Create embedder manager with common embedders."""
    manager = EmbedderManager()
    
    # Try to add OpenAI embedder if API key is available
    if os.getenv("OPENAI_API_KEY"):
        try:
            openai_embedder = create_openai_embedder()
            manager.add_embedder("openai", openai_embedder, set_as_default=True)
        except Exception as e:
            logger.warning(f"Could not create OpenAI embedder: {e}")
    
    # Try to add Cohere embedder if API key is available
    if os.getenv("COHERE_API_KEY"):
        try:
            cohere_embedder = create_cohere_embedder()
            manager.add_embedder("cohere", cohere_embedder)
        except Exception as e:
            logger.warning(f"Could not create Cohere embedder: {e}")
    
    # Add Hugging Face embedder as fallback
    try:
        hf_embedder = create_huggingface_embedder()
        manager.add_embedder("huggingface", hf_embedder, set_as_default=(manager.default_embedder is None))
    except Exception as e:
        logger.warning(f"Could not create Hugging Face embedder: {e}")
    
    return manager


class SimpleEmbedder(BaseEmbedder):
    """Simple embedder for testing and basic functionality."""

    def __init__(self, dimension: int = 384):
        super().__init__("simple_embedder")
        self.dimension = dimension

    async def embed_text(self, text: str) -> List[float]:
        """Create simple hash-based embedding."""
        # Simple hash-based embedding for testing
        import hashlib

        # Create deterministic embedding based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()

        # Convert hash to numbers and normalize
        embedding = []
        for i in range(0, min(len(text_hash), self.dimension * 2), 2):
            hex_pair = text_hash[i:i+2]
            value = int(hex_pair, 16) / 255.0  # Normalize to 0-1
            embedding.append(value)

        # Pad or truncate to desired dimension
        while len(embedding) < self.dimension:
            embedding.append(0.0)

        return embedding[:self.dimension]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        return [await self.embed_text(text) for text in texts]

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension


def create_default_embedder() -> BaseEmbedder:
    """Create default embedder based on available dependencies."""
    # Try OpenAI first
    if os.getenv("OPENAI_API_KEY"):
        try:
            return OpenAIEmbedder()
        except ImportError:
            pass

    # Try Cohere
    if os.getenv("COHERE_API_KEY"):
        try:
            return CohereEmbedder()
        except ImportError:
            pass

    # Try HuggingFace
    try:
        return HuggingFaceEmbedder()
    except ImportError:
        pass

    # Fallback to simple embedder
    logger.warning("No advanced embedder dependencies available, using simple embedder")
    return SimpleEmbedder()
