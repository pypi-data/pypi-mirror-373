"""
Reranking system for AIFlow Vector Database Integration.

Provides reranking capabilities to improve search result quality and relevance.
"""

import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import logging

from .base import SearchResult

logger = logging.getLogger(__name__)


class BaseReranker(ABC):
    """Abstract base class for rerankers."""
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key
    
    @abstractmethod
    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: Optional[int] = None
    ) -> List[SearchResult]:
        """Rerank search results based on relevance to query."""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get reranker information."""
        return {
            "model_name": self.model_name,
            "provider": self.__class__.__name__
        }


class CohereReranker(BaseReranker):
    """Cohere reranking implementation."""
    
    def __init__(
        self,
        model_name: str = "rerank-english-v3.0",
        api_key: Optional[str] = None
    ):
        super().__init__(model_name, api_key or os.getenv("COHERE_API_KEY"))
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
    
    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: Optional[int] = None
    ) -> List[SearchResult]:
        """Rerank search results using Cohere reranker."""
        if not results:
            return results
        
        try:
            client = self._get_client()
            
            # Prepare documents for reranking
            documents = [result.content for result in results]
            
            # Call Cohere rerank API
            response = client.rerank(
                model=self.model_name,
                query=query,
                documents=documents,
                top_k=top_k or len(results)
            )
            
            # Reorder results based on reranking scores
            reranked_results = []
            for result in response.results:
                original_result = results[result.index]
                
                # Update score with reranking score
                original_result.score = result.relevance_score
                original_result.metadata["original_score"] = original_result.metadata.get("score", 0)
                original_result.metadata["rerank_score"] = result.relevance_score
                original_result.metadata["reranked"] = True
                
                reranked_results.append(original_result)
            
            logger.info(f"Reranked {len(results)} results, returned top {len(reranked_results)}")
            return reranked_results
            
        except Exception as e:
            logger.error(f"Error reranking with Cohere: {e}")
            # Return original results if reranking fails
            return results


class HuggingFaceReranker(BaseReranker):
    """Hugging Face reranking implementation."""
    
    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        api_key: Optional[str] = None
    ):
        super().__init__(model_name, api_key)
        self._model = None
    
    def _load_model(self):
        """Load Hugging Face cross-encoder model."""
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(self.model_name)
            except ImportError:
                raise ImportError(
                    "Sentence Transformers library not installed. "
                    "Run: pip install sentence-transformers"
                )
    
    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: Optional[int] = None
    ) -> List[SearchResult]:
        """Rerank search results using Hugging Face cross-encoder."""
        if not results:
            return results
        
        try:
            self._load_model()
            
            # Prepare query-document pairs
            pairs = [(query, result.content) for result in results]
            
            # Get relevance scores
            scores = self._model.predict(pairs)
            
            # Combine results with new scores
            scored_results = []
            for i, result in enumerate(results):
                result.metadata["original_score"] = result.score
                result.metadata["rerank_score"] = float(scores[i])
                result.metadata["reranked"] = True
                result.score = float(scores[i])
                scored_results.append((result, float(scores[i])))
            
            # Sort by reranking score
            scored_results.sort(key=lambda x: x[1], reverse=True)
            
            # Return top_k results
            top_k = top_k or len(results)
            reranked_results = [result for result, _ in scored_results[:top_k]]
            
            logger.info(f"Reranked {len(results)} results, returned top {len(reranked_results)}")
            return reranked_results
            
        except Exception as e:
            logger.error(f"Error reranking with Hugging Face: {e}")
            # Return original results if reranking fails
            return results


class SimpleReranker(BaseReranker):
    """Simple rule-based reranker."""
    
    def __init__(self):
        super().__init__("simple_reranker")
    
    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: Optional[int] = None
    ) -> List[SearchResult]:
        """Rerank using simple text matching and length heuristics."""
        if not results:
            return results
        
        try:
            query_terms = set(query.lower().split())
            
            # Calculate enhanced relevance scores
            for result in results:
                content_lower = result.content.lower()
                content_terms = set(content_lower.split())
                
                # Term overlap score
                overlap = len(query_terms.intersection(content_terms))
                overlap_score = overlap / len(query_terms) if query_terms else 0
                
                # Exact phrase matching bonus
                phrase_bonus = 1.2 if query.lower() in content_lower else 1.0
                
                # Length penalty for very short or very long content
                content_length = len(result.content)
                if content_length < 50:
                    length_penalty = 0.8
                elif content_length > 2000:
                    length_penalty = 0.9
                else:
                    length_penalty = 1.0
                
                # Position bonus for early matches
                position_bonus = 1.0
                first_match_pos = content_lower.find(query.lower())
                if first_match_pos != -1:
                    # Earlier matches get higher bonus
                    position_bonus = 1.1 if first_match_pos < 100 else 1.05
                
                # Combine scores
                original_score = result.score
                enhanced_score = (
                    original_score * 0.6 +  # Original vector similarity
                    overlap_score * 0.3 +   # Term overlap
                    0.1                     # Base score
                ) * phrase_bonus * length_penalty * position_bonus
                
                # Update result
                result.metadata["original_score"] = original_score
                result.metadata["overlap_score"] = overlap_score
                result.metadata["phrase_bonus"] = phrase_bonus
                result.metadata["length_penalty"] = length_penalty
                result.metadata["position_bonus"] = position_bonus
                result.metadata["rerank_score"] = enhanced_score
                result.metadata["reranked"] = True
                result.score = enhanced_score
            
            # Sort by enhanced score
            results.sort(key=lambda x: x.score, reverse=True)
            
            # Return top_k results
            top_k = top_k or len(results)
            reranked_results = results[:top_k]
            
            logger.info(f"Simple reranked {len(results)} results, returned top {len(reranked_results)}")
            return reranked_results
            
        except Exception as e:
            logger.error(f"Error in simple reranking: {e}")
            return results


class HybridReranker(BaseReranker):
    """Hybrid reranker that combines multiple reranking strategies."""
    
    def __init__(self, rerankers: List[BaseReranker], weights: Optional[List[float]] = None):
        super().__init__("hybrid_reranker")
        self.rerankers = rerankers
        self.weights = weights or [1.0 / len(rerankers)] * len(rerankers)
        
        if len(self.weights) != len(self.rerankers):
            raise ValueError("Number of weights must match number of rerankers")
    
    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: Optional[int] = None
    ) -> List[SearchResult]:
        """Rerank using multiple strategies and combine scores."""
        if not results:
            return results
        
        try:
            # Get reranking results from all rerankers
            all_reranked = []
            for reranker in self.rerankers:
                reranked = await reranker.rerank(query, results.copy(), top_k)
                all_reranked.append(reranked)
            
            # Combine scores using weighted average
            result_scores = {}
            for i, reranked_results in enumerate(all_reranked):
                weight = self.weights[i]
                for result in reranked_results:
                    if result.id not in result_scores:
                        result_scores[result.id] = {"result": result, "scores": [], "weights": []}
                    result_scores[result.id]["scores"].append(result.score)
                    result_scores[result.id]["weights"].append(weight)
            
            # Calculate final weighted scores
            final_results = []
            for result_data in result_scores.values():
                scores = result_data["scores"]
                weights = result_data["weights"]
                
                # Weighted average
                final_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
                
                result = result_data["result"]
                result.metadata["hybrid_scores"] = scores
                result.metadata["hybrid_weights"] = weights
                result.metadata["final_score"] = final_score
                result.metadata["reranked"] = True
                result.score = final_score
                
                final_results.append(result)
            
            # Sort by final score
            final_results.sort(key=lambda x: x.score, reverse=True)
            
            # Return top_k results
            top_k = top_k or len(final_results)
            hybrid_results = final_results[:top_k]
            
            logger.info(f"Hybrid reranked {len(results)} results using {len(self.rerankers)} rerankers")
            return hybrid_results
            
        except Exception as e:
            logger.error(f"Error in hybrid reranking: {e}")
            return results


class RerankerManager:
    """Manager for multiple rerankers."""
    
    def __init__(self):
        self.rerankers: Dict[str, BaseReranker] = {}
        self.default_reranker: Optional[str] = None
    
    def add_reranker(self, name: str, reranker: BaseReranker, set_as_default: bool = False):
        """Add a reranker."""
        self.rerankers[name] = reranker
        if set_as_default or self.default_reranker is None:
            self.default_reranker = name
    
    def get_reranker(self, name: Optional[str] = None) -> Optional[BaseReranker]:
        """Get a reranker by name or default."""
        if name is None:
            name = self.default_reranker
        return self.rerankers.get(name)
    
    def list_rerankers(self) -> List[str]:
        """List available rerankers."""
        return list(self.rerankers.keys())
    
    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        reranker_name: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> List[SearchResult]:
        """Rerank using specified or default reranker."""
        reranker = self.get_reranker(reranker_name)
        if reranker is None:
            logger.warning(f"Reranker not found: {reranker_name}, returning original results")
            return results
        
        return await reranker.rerank(query, results, top_k)
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all rerankers."""
        return {
            "rerankers": {name: reranker.get_info() for name, reranker in self.rerankers.items()},
            "default_reranker": self.default_reranker,
            "total_rerankers": len(self.rerankers)
        }


# Factory functions for easy reranker creation
def create_cohere_reranker(
    model_name: str = "rerank-english-v3.0",
    api_key: Optional[str] = None
) -> CohereReranker:
    """Create Cohere reranker."""
    return CohereReranker(model_name, api_key)


def create_huggingface_reranker(
    model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
) -> HuggingFaceReranker:
    """Create Hugging Face reranker."""
    return HuggingFaceReranker(model_name)


def create_simple_reranker() -> SimpleReranker:
    """Create simple rule-based reranker."""
    return SimpleReranker()


def create_default_reranker_manager() -> RerankerManager:
    """Create reranker manager with common rerankers."""
    manager = RerankerManager()
    
    # Add simple reranker as fallback
    simple_reranker = create_simple_reranker()
    manager.add_reranker("simple", simple_reranker, set_as_default=True)
    
    # Try to add Cohere reranker if API key is available
    if os.getenv("COHERE_API_KEY"):
        try:
            cohere_reranker = create_cohere_reranker()
            manager.add_reranker("cohere", cohere_reranker, set_as_default=True)
        except Exception as e:
            logger.warning(f"Could not create Cohere reranker: {e}")
    
    # Try to add Hugging Face reranker
    try:
        hf_reranker = create_huggingface_reranker()
        manager.add_reranker("huggingface", hf_reranker)
    except Exception as e:
        logger.warning(f"Could not create Hugging Face reranker: {e}")
    
    return manager
