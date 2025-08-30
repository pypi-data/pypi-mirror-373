"""
Hybrid Retrieval System for Enhanced Memory Search

This module implements sophisticated retrieval strategies that combine:
- Vector-based semantic search
- Graph-based entity traversal
- Temporal awareness and fact validity
- Multi-modal retrieval capabilities
- Advanced scoring and ranking algorithms
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import json
import math

from .graph_memory import GraphMemoryManager, GraphMemory, Entity, Relationship
from .vector_stores import VectorStoreManager, MemoryRecord
from .embeddings import EmbeddingManager


@dataclass
class RetrievalResult:
    """Represents a single retrieval result with scoring details"""
    memory: GraphMemory
    vector_score: float
    graph_score: float
    temporal_score: float
    final_score: float
    explanation: str
    related_entities: List[str]
    retrieval_path: List[str]


@dataclass
class HybridQuery:
    """Represents a hybrid query with multiple retrieval strategies"""
    text: str
    vector_weight: float = 0.4
    graph_weight: float = 0.4
    temporal_weight: float = 0.2
    max_results: int = 10
    include_related: bool = True
    temporal_decay_days: float = 30.0
    user_id: Optional[str] = None
    entity_boost: Dict[str, float] = None  # Boost specific entity types
    
    def __post_init__(self):
        if self.entity_boost is None:
            self.entity_boost = {}


class AdvancedScorer:
    """Advanced scoring algorithms for memory retrieval"""
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        vec1, vec2 = np.array(vec1), np.array(vec2)
        dot_product = np.dot(vec1, vec2)
        norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)
        
        return dot_product / norm_product if norm_product != 0 else 0.0
    
    @staticmethod
    def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
        """Calculate Jaccard similarity between two sets"""
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union
    
    @staticmethod
    def temporal_decay_score(memory_time: datetime, current_time: datetime, 
                           decay_days: float) -> float:
        """Calculate temporal decay score"""
        time_diff = (current_time - memory_time).total_seconds()
        days_diff = time_diff / (24 * 60 * 60)
        
        # Exponential decay: score = e^(-days_diff / decay_days)
        return math.exp(-days_diff / decay_days) if decay_days > 0 else 1.0
    
    @staticmethod
    def entity_frequency_score(entities: List[Entity], boost_factors: Dict[str, float]) -> float:
        """Calculate score based on entity frequency and boosting"""
        if not entities:
            return 0.0
        
        total_score = 0.0
        for entity in entities:
            base_score = entity.confidence
            boost = boost_factors.get(entity.type, 1.0)
            total_score += base_score * boost
        
        return total_score / len(entities)  # Average score
    
    @staticmethod
    def graph_centrality_score(entity_ids: List[str], graph_manager) -> float:
        """Calculate score based on entity centrality in the graph"""
        if not entity_ids:
            return 0.0
        
        graph = graph_manager.knowledge_graph.graph
        total_centrality = 0.0
        valid_entities = 0
        
        for entity_id in entity_ids:
            if entity_id in graph:
                # Use degree centrality as a simple measure
                centrality = graph.degree(entity_id)
                total_centrality += centrality
                valid_entities += 1
        
        return total_centrality / valid_entities if valid_entities > 0 else 0.0


class BiTemporalMemory:
    """Handles bi-temporal facts with transaction and valid time"""
    
    def __init__(self):
        self.facts: Dict[str, Dict[str, Any]] = {}  # fact_id -> fact_data
        self.temporal_index: Dict[str, List[str]] = defaultdict(list)  # entity_id -> fact_ids
    
    def add_fact(self, fact_id: str, subject: str, predicate: str, object_val: Any,
                 valid_from: datetime, valid_to: Optional[datetime] = None,
                 transaction_time: Optional[datetime] = None):
        """Add a bi-temporal fact"""
        if transaction_time is None:
            transaction_time = datetime.utcnow()
        
        fact = {
            'id': fact_id,
            'subject': subject,
            'predicate': predicate,
            'object': object_val,
            'valid_from': valid_from,
            'valid_to': valid_to,
            'transaction_time': transaction_time,
            'active': True
        }
        
        self.facts[fact_id] = fact
        self.temporal_index[subject].append(fact_id)
    
    def get_facts_at_time(self, entity_id: str, query_time: datetime) -> List[Dict[str, Any]]:
        """Get facts valid at a specific time"""
        valid_facts = []
        
        for fact_id in self.temporal_index.get(entity_id, []):
            fact = self.facts[fact_id]
            
            if not fact['active']:
                continue
            
            # Check if fact is valid at query_time
            valid_from = fact['valid_from']
            valid_to = fact['valid_to']
            
            if valid_from <= query_time and (valid_to is None or query_time <= valid_to):
                valid_facts.append(fact)
        
        return valid_facts
    
    def invalidate_fact(self, fact_id: str, invalidation_time: Optional[datetime] = None):
        """Mark a fact as invalid (soft delete)"""
        if fact_id in self.facts:
            if invalidation_time is None:
                invalidation_time = datetime.utcnow()
            
            self.facts[fact_id]['valid_to'] = invalidation_time
            self.facts[fact_id]['active'] = False


class HybridRetriever:
    """Advanced hybrid retrieval engine"""
    
    def __init__(self, 
                 vector_store_manager: VectorStoreManager,
                 graph_memory_manager: GraphMemoryManager,
                 embedding_manager: EmbeddingManager):
        self.vector_store = vector_store_manager
        self.graph_manager = graph_memory_manager
        self.embedding_manager = embedding_manager
        self.scorer = AdvancedScorer()
        self.bitemporal_memory = BiTemporalMemory()
        
        # Cache for embeddings
        self.embedding_cache: Dict[str, List[float]] = {}
    
    def retrieve(self, query: HybridQuery) -> List[RetrievalResult]:
        """Perform hybrid retrieval combining multiple strategies"""
        
        # Step 1: Get query embedding
        query_embedding = self._get_query_embedding(query.text)
        
        # Step 2: Vector-based retrieval
        vector_results = self._vector_retrieval(query_embedding, query)
        
        # Step 3: Graph-based retrieval
        graph_results = self._graph_retrieval(query)
        
        # Step 4: Combine and score results
        combined_results = self._combine_results(vector_results, graph_results, query)
        
        # Step 5: Apply temporal scoring
        final_results = self._apply_temporal_scoring(combined_results, query)
        
        # Step 6: Sort and limit results
        final_results.sort(key=lambda x: x.final_score, reverse=True)
        
        return final_results[:query.max_results]
    
    def _get_query_embedding(self, query_text: str) -> List[float]:
        """Get or compute query embedding with caching"""
        cache_key = f"query:{hash(query_text)}"
        
        if cache_key not in self.embedding_cache:
            embedding = self.embedding_manager.get_embedding(query_text)
            self.embedding_cache[cache_key] = embedding
        
        return self.embedding_cache[cache_key]
    
    def _vector_retrieval(self, query_embedding: List[float], 
                         query: HybridQuery) -> Dict[str, Tuple[float, MemoryRecord]]:
        """Perform vector-based semantic search"""
        vector_results = {}
        
        try:
            # Search in vector store
            search_results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=query.max_results * 2,  # Get more results for better fusion
                namespace=query.user_id,
                filter_dict={}
            )
            
            for result in search_results:
                memory_id = result.metadata.get('memory_id', result.id)
                vector_results[memory_id] = (result.score, result)
        
        except Exception as e:
            print(f"Vector retrieval error: {e}")
        
        return vector_results
    
    def _graph_retrieval(self, query: HybridQuery) -> Dict[str, Tuple[float, GraphMemory]]:
        """Perform graph-based entity traversal search"""
        graph_results = {}
        
        try:
            # Get related memories through graph traversal
            related_memories = self.graph_manager.get_related_memories(
                query.text, max_memories=query.max_results * 2
            )
            
            for memory in related_memories:
                # Calculate graph-based score
                graph_score = self._calculate_graph_score(memory, query)
                graph_results[memory.memory_id] = (graph_score, memory)
        
        except Exception as e:
            print(f"Graph retrieval error: {e}")
        
        return graph_results
    
    def _calculate_graph_score(self, memory: GraphMemory, query: HybridQuery) -> float:
        """Calculate graph-based relevance score"""
        # Extract entities from query
        query_entities = self.graph_manager.entity_extractor.extract_entities(query.text)
        query_entity_forms = {ent.canonical_form for ent in query_entities}
        
        # Get memory entities
        memory_entity_forms = {ent.canonical_form for ent in memory.entities}
        
        # Base score: entity overlap
        overlap_score = self.scorer.jaccard_similarity(query_entity_forms, memory_entity_forms)
        
        # Entity frequency and boosting
        frequency_score = self.scorer.entity_frequency_score(memory.entities, query.entity_boost)
        
        # Graph centrality score
        memory_entity_ids = [
            self.graph_manager.knowledge_graph.entity_to_canonical.get(ent.canonical_form)
            for ent in memory.entities
        ]
        memory_entity_ids = [eid for eid in memory_entity_ids if eid is not None]
        centrality_score = self.scorer.graph_centrality_score(memory_entity_ids, self.graph_manager)
        
        # Combine scores
        final_score = (overlap_score * 0.5 + 
                      frequency_score * 0.3 + 
                      centrality_score * 0.2)
        
        return min(final_score, 1.0)  # Cap at 1.0
    
    def _combine_results(self, vector_results: Dict, graph_results: Dict, 
                        query: HybridQuery) -> List[RetrievalResult]:
        """Combine vector and graph results with weighted scoring"""
        all_memory_ids = set(vector_results.keys()) | set(graph_results.keys())
        combined_results = []
        
        for memory_id in all_memory_ids:
            # Get vector score and data
            vector_score = 0.0
            memory_data = None
            
            if memory_id in vector_results:
                vector_score, vector_record = vector_results[memory_id]
                # Try to get corresponding graph memory
                if memory_id in self.graph_manager.memories:
                    memory_data = self.graph_manager.memories[memory_id]
                else:
                    # Create minimal graph memory from vector record
                    memory_data = self._create_minimal_graph_memory(vector_record)
            
            # Get graph score
            graph_score = 0.0
            if memory_id in graph_results:
                graph_score, graph_memory = graph_results[memory_id]
                if memory_data is None:
                    memory_data = graph_memory
            
            if memory_data is None:
                continue
            
            # Calculate combined score
            combined_score = (vector_score * query.vector_weight + 
                            graph_score * query.graph_weight)
            
            # Create retrieval result
            result = RetrievalResult(
                memory=memory_data,
                vector_score=vector_score,
                graph_score=graph_score,
                temporal_score=0.0,  # Will be calculated later
                final_score=combined_score,
                explanation=f"Vector: {vector_score:.3f}, Graph: {graph_score:.3f}",
                related_entities=[ent.canonical_form for ent in memory_data.entities],
                retrieval_path=[]
            )
            
            combined_results.append(result)
        
        return combined_results
    
    def _create_minimal_graph_memory(self, vector_record: MemoryRecord) -> GraphMemory:
        """Create a minimal graph memory from vector record"""
        from datetime import datetime
        
        return GraphMemory(
            memory_id=vector_record.id,
            content=vector_record.content,
            entities=[],  # No entities extracted yet
            relationships=[],
            embedding=vector_record.vector,
            timestamp=datetime.utcnow(),
            user_id=vector_record.metadata.get('user_id'),
            memory_type=vector_record.metadata.get('memory_type', 'unknown')
        )
    
    def _apply_temporal_scoring(self, results: List[RetrievalResult], 
                               query: HybridQuery) -> List[RetrievalResult]:
        """Apply temporal decay scoring to results"""
        current_time = datetime.utcnow()
        
        for result in results:
            # Calculate temporal score
            temporal_score = self.scorer.temporal_decay_score(
                result.memory.timestamp,
                current_time,
                query.temporal_decay_days
            )
            
            result.temporal_score = temporal_score
            
            # Update final score with temporal component
            result.final_score = (
                result.vector_score * query.vector_weight +
                result.graph_score * query.graph_weight +
                temporal_score * query.temporal_weight
            )
            
            # Update explanation
            result.explanation += f", Temporal: {temporal_score:.3f}"
        
        return results
    
    def retrieve_with_explanation(self, query: HybridQuery) -> Dict[str, Any]:
        """Retrieve with detailed explanation of scoring"""
        results = self.retrieve(query)
        
        explanation = {
            "query": query.text,
            "weights": {
                "vector": query.vector_weight,
                "graph": query.graph_weight,
                "temporal": query.temporal_weight
            },
            "total_results": len(results),
            "results": []
        }
        
        for i, result in enumerate(results):
            explanation["results"].append({
                "rank": i + 1,
                "memory_id": result.memory.memory_id,
                "content_preview": result.memory.content[:100] + "..." if len(result.memory.content) > 100 else result.memory.content,
                "scores": {
                    "vector": result.vector_score,
                    "graph": result.graph_score,
                    "temporal": result.temporal_score,
                    "final": result.final_score
                },
                "entities": result.related_entities,
                "explanation": result.explanation
            })
        
        return explanation
    
    def batch_retrieve(self, queries: List[HybridQuery]) -> List[List[RetrievalResult]]:
        """Perform batch retrieval for multiple queries"""
        results = []
        
        for query in queries:
            query_results = self.retrieve(query)
            results.append(query_results)
        
        return results
    
    def get_retrieval_analytics(self, query_history: List[HybridQuery]) -> Dict[str, Any]:
        """Analyze retrieval patterns and performance"""
        if not query_history:
            return {"message": "No query history available"}
        
        # Analyze query patterns
        total_queries = len(query_history)
        avg_max_results = sum(q.max_results for q in query_history) / total_queries
        
        # Weight usage analysis
        avg_vector_weight = sum(q.vector_weight for q in query_history) / total_queries
        avg_graph_weight = sum(q.graph_weight for q in query_history) / total_queries
        avg_temporal_weight = sum(q.temporal_weight for q in query_history) / total_queries
        
        # Entity boost analysis
        entity_boosts = defaultdict(list)
        for query in query_history:
            for entity_type, boost in query.entity_boost.items():
                entity_boosts[entity_type].append(boost)
        
        avg_entity_boosts = {
            entity_type: sum(boosts) / len(boosts)
            for entity_type, boosts in entity_boosts.items()
        }
        
        return {
            "total_queries": total_queries,
            "average_max_results": avg_max_results,
            "average_weights": {
                "vector": avg_vector_weight,
                "graph": avg_graph_weight,
                "temporal": avg_temporal_weight
            },
            "entity_boost_usage": avg_entity_boosts,
            "temporal_decay_usage": {
                "min_days": min(q.temporal_decay_days for q in query_history),
                "max_days": max(q.temporal_decay_days for q in query_history),
                "avg_days": sum(q.temporal_decay_days for q in query_history) / total_queries
            }
        }


class ConversationalRetrieval:
    """Handles conversational context and follow-up queries"""
    
    def __init__(self, hybrid_retriever: HybridRetriever):
        self.retriever = hybrid_retriever
        self.conversation_history: List[Dict[str, Any]] = []
        self.context_entities: Set[str] = set()
    
    def conversational_retrieve(self, query: str, context_window: int = 5) -> List[RetrievalResult]:
        """Retrieve with conversational context awareness"""
        # Build hybrid query with context
        hybrid_query = HybridQuery(
            text=query,
            entity_boost=self._get_context_entity_boosts(),
            max_results=10
        )
        
        # Perform retrieval
        results = self.retriever.retrieve(hybrid_query)
        
        # Update conversation history
        self._update_conversation_context(query, results)
        
        # Keep only recent context
        if len(self.conversation_history) > context_window:
            self.conversation_history = self.conversation_history[-context_window:]
        
        return results
    
    def _get_context_entity_boosts(self) -> Dict[str, float]:
        """Calculate entity boosts based on conversation context"""
        boosts = defaultdict(float)
        
        # Boost entities mentioned in recent conversation
        for entry in self.conversation_history[-3:]:  # Last 3 exchanges
            for entity in entry.get('entities', []):
                boosts[entity] += 0.2
        
        return dict(boosts)
    
    def _update_conversation_context(self, query: str, results: List[RetrievalResult]):
        """Update conversation context with new query and results"""
        # Extract entities from query
        query_entities = self.retriever.graph_manager.entity_extractor.extract_entities(query)
        
        # Collect entities from results
        result_entities = set()
        for result in results:
            result_entities.update(result.related_entities)
        
        # Update context
        conversation_entry = {
            "query": query,
            "timestamp": datetime.utcnow(),
            "entities": [ent.canonical_form for ent in query_entities],
            "result_entities": list(result_entities)
        }
        
        self.conversation_history.append(conversation_entry)
        
        # Update context entities
        self.context_entities.update(ent.canonical_form for ent in query_entities)
        self.context_entities.update(result_entities)
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of conversation context"""
        return {
            "conversation_length": len(self.conversation_history),
            "context_entities": list(self.context_entities),
            "recent_queries": [entry["query"] for entry in self.conversation_history[-5:]],
            "entity_frequency": self._get_entity_frequency()
        }
    
    def _get_entity_frequency(self) -> Dict[str, int]:
        """Get frequency of entities in conversation"""
        frequency = defaultdict(int)
        
        for entry in self.conversation_history:
            for entity in entry.get('entities', []):
                frequency[entity] += 1
            for entity in entry.get('result_entities', []):
                frequency[entity] += 1
        
        return dict(frequency) 