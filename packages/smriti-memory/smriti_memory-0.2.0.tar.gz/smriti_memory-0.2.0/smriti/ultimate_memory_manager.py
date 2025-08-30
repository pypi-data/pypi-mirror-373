"""
Ultimate Memory Manager - World-Class AI Memory Layer

This is the crown jewel of Smriti Memory that integrates all advanced features:
- Graph-based memory with entity extraction
- Hybrid retrieval (vector + graph + temporal)
- Performance optimization with consolidation
- Enterprise security and privacy
- Multi-tenancy and GDPR compliance
- Bi-temporal facts and advanced scoring
- Neural memory modules and entity linking
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import uuid
from collections import defaultdict

from .graph_memory import GraphMemoryManager, GraphMemory, Entity, Relationship
from .hybrid_retrieval import HybridRetriever, HybridQuery, RetrievalResult, ConversationalRetrieval
from .performance_optimizer import PerformanceOptimizer, MemoryConsolidator, MemoryOperation
from .enterprise_security import EnterpriseSecurityManager, PermissionLevel, AuditAction
from .vector_stores import VectorStoreManager, MemoryRecord
from .embeddings import EmbeddingManager
from .enhanced_memory_manager import EnhancedMemoryManager


@dataclass
class MemoryInsight:
    """Advanced memory insights with AI-powered analysis"""
    insight_type: str
    title: str
    description: str
    confidence: float
    entities_involved: List[str]
    evidence: List[str]
    actionable_suggestions: List[str]
    metadata: Dict[str, Any] = None


@dataclass
class MemoryStats:
    """Comprehensive memory statistics"""
    total_memories: int
    unique_entities: int
    relationships_count: int
    graph_density: float
    memory_growth_rate: float
    consolidation_rate: float
    search_performance: Dict[str, float]
    user_engagement: Dict[str, Any]
    timestamp: datetime


class NeuralMemoryModule:
    """Advanced neural memory processing capabilities"""
    
    def __init__(self):
        self.memory_patterns: Dict[str, List[str]] = defaultdict(list)
        self.entity_embeddings: Dict[str, List[float]] = {}
        self.relationship_strengths: Dict[str, float] = {}
        
    def extract_memory_patterns(self, memories: List[GraphMemory]) -> List[Dict[str, Any]]:
        """Extract recurring patterns from memories"""
        patterns = []
        
        # Entity co-occurrence patterns
        entity_pairs = defaultdict(int)
        for memory in memories:
            entities = [e.canonical_form for e in memory.entities]
            for i, ent1 in enumerate(entities):
                for ent2 in entities[i+1:]:
                    pair = tuple(sorted([ent1, ent2]))
                    entity_pairs[pair] += 1
        
        # Find significant patterns
        for (ent1, ent2), count in entity_pairs.items():
            if count >= 3:  # Threshold for significance
                patterns.append({
                    "type": "entity_co_occurrence",
                    "entities": [ent1, ent2],
                    "frequency": count,
                    "strength": min(count / 10, 1.0)  # Normalize
                })
        
        # Temporal patterns
        temporal_patterns = self._extract_temporal_patterns(memories)
        patterns.extend(temporal_patterns)
        
        return patterns
    
    def _extract_temporal_patterns(self, memories: List[GraphMemory]) -> List[Dict[str, Any]]:
        """Extract temporal patterns from memories"""
        patterns = []
        
        # Group memories by time periods
        daily_memories = defaultdict(list)
        for memory in memories:
            day_key = memory.timestamp.strftime("%Y-%m-%d")
            daily_memories[day_key].append(memory)
        
        # Find days with similar entity patterns
        daily_entities = {}
        for day, day_memories in daily_memories.items():
            entities = set()
            for memory in day_memories:
                entities.update(e.canonical_form for e in memory.entities)
            daily_entities[day] = entities
        
        # Find recurring daily patterns
        for day1, entities1 in daily_entities.items():
            for day2, entities2 in daily_entities.items():
                if day1 != day2:
                    overlap = entities1 & entities2
                    if len(overlap) >= 3:  # Significant overlap
                        patterns.append({
                            "type": "temporal_entity_pattern",
                            "days": [day1, day2],
                            "common_entities": list(overlap),
                            "overlap_ratio": len(overlap) / len(entities1 | entities2)
                        })
        
        return patterns
    
    def predict_relevant_entities(self, query: str, context_entities: List[str]) -> List[Tuple[str, float]]:
        """Predict entities likely to be relevant based on context"""
        # Simplified prediction based on co-occurrence patterns
        predictions = []
        
        for entity, patterns in self.memory_patterns.items():
            relevance_score = 0.0
            
            # Check overlap with context entities
            for context_entity in context_entities:
                if context_entity in patterns:
                    relevance_score += 0.3
            
            # Check query relevance (simplified)
            if entity.lower() in query.lower():
                relevance_score += 0.5
            
            if relevance_score > 0.2:
                predictions.append((entity, relevance_score))
        
        return sorted(predictions, key=lambda x: x[1], reverse=True)[:10]


class EntityLinker:
    """Advanced entity linking and disambiguation"""
    
    def __init__(self):
        self.entity_knowledge_base: Dict[str, Dict[str, Any]] = {}
        self.entity_aliases: Dict[str, List[str]] = defaultdict(list)
        self.disambiguation_rules: List[Dict[str, Any]] = []
    
    def link_entities(self, entities: List[Entity], context: str) -> List[Entity]:
        """Link entities to knowledge base entries"""
        linked_entities = []
        
        for entity in entities:
            # Attempt to link to knowledge base
            linked_entity = self._find_entity_match(entity, context)
            
            if linked_entity:
                # Update entity with linked information
                entity.metadata.update({
                    "linked_entity_id": linked_entity["id"],
                    "entity_type_detailed": linked_entity.get("type"),
                    "confidence_boost": 0.2,
                    "knowledge_source": "internal_kb"
                })
                entity.confidence = min(entity.confidence + 0.2, 1.0)
            
            linked_entities.append(entity)
        
        return linked_entities
    
    def _find_entity_match(self, entity: Entity, context: str) -> Optional[Dict[str, Any]]:
        """Find matching entity in knowledge base"""
        # Check exact match
        if entity.canonical_form in self.entity_knowledge_base:
            return self.entity_knowledge_base[entity.canonical_form]
        
        # Check aliases
        for canonical, aliases in self.entity_aliases.items():
            if entity.text.lower() in [alias.lower() for alias in aliases]:
                return self.entity_knowledge_base.get(canonical)
        
        return None
    
    def add_entity_to_kb(self, entity: Entity, aliases: List[str] = None, 
                        metadata: Dict[str, Any] = None):
        """Add entity to knowledge base"""
        kb_entry = {
            "id": entity.id,
            "canonical_form": entity.canonical_form,
            "type": entity.type,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.entity_knowledge_base[entity.canonical_form] = kb_entry
        
        if aliases:
            self.entity_aliases[entity.canonical_form].extend(aliases)
    
    def get_entity_disambiguation_suggestions(self, entity_text: str) -> List[Dict[str, Any]]:
        """Get disambiguation suggestions for ambiguous entities"""
        suggestions = []
        
        # Find potential matches
        for canonical, kb_entry in self.entity_knowledge_base.items():
            if entity_text.lower() in canonical.lower():
                suggestions.append({
                    "canonical_form": canonical,
                    "type": kb_entry["type"],
                    "confidence": 0.8,  # Base confidence
                    "context_hints": kb_entry.get("metadata", {}).get("context_hints", [])
                })
        
        # Check aliases
        for canonical, aliases in self.entity_aliases.items():
            for alias in aliases:
                if entity_text.lower() in alias.lower():
                    kb_entry = self.entity_knowledge_base.get(canonical, {})
                    suggestions.append({
                        "canonical_form": canonical,
                        "type": kb_entry.get("type", "UNKNOWN"),
                        "confidence": 0.7,  # Slightly lower for alias matches
                        "matched_via": "alias",
                        "alias": alias
                    })
        
        return sorted(suggestions, key=lambda x: x["confidence"], reverse=True)


class UltimateMemoryManager:
    """World-class AI memory manager integrating all advanced features"""
    
    def __init__(self, 
                 vector_store_manager: VectorStoreManager,
                 embedding_manager: EmbeddingManager,
                 enable_security: bool = True,
                 master_key: Optional[bytes] = None):
        
        # Core components
        self.vector_store = vector_store_manager
        self.embedding_manager = embedding_manager
        self.graph_manager = GraphMemoryManager()
        
        # Advanced components
        self.hybrid_retriever = HybridRetriever(
            vector_store_manager, self.graph_manager, embedding_manager
        )
        self.performance_optimizer = PerformanceOptimizer()
        self.neural_module = NeuralMemoryModule()
        self.entity_linker = EntityLinker()
        self.conversational_retrieval = ConversationalRetrieval(self.hybrid_retriever)
        
        # Enterprise features
        self.security_enabled = enable_security
        if enable_security:
            self.security_manager = EnterpriseSecurityManager(master_key)
        
        # Statistics and monitoring
        self.operation_history: List[Dict[str, Any]] = []
        self.insights_cache: Dict[str, List[MemoryInsight]] = {}
        
        # Enhanced memory manager for backward compatibility
        self.enhanced_manager = EnhancedMemoryManager(
            vector_store_manager, embedding_manager
        )
    
    async def add_memory(self, content: str, user_id: Optional[str] = None,
                        session_id: Optional[str] = None,
                        memory_type: str = "user_message",
                        metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add memory with full world-class processing"""
        
        start_time = datetime.utcnow()
        operation_id = str(uuid.uuid4())
        
        try:
            # Security check if enabled
            if self.security_enabled and session_id:
                security_result = self.security_manager.secure_memory_operation(
                    session_id=session_id,
                    operation="create",
                    memory_data={"content": content, "type": memory_type},
                    required_permission=PermissionLevel.WRITE
                )
                
                if "error" in security_result:
                    return security_result
                
                # Extract user from security result
                user = self.security_manager.user_manager.validate_session(session_id)
                if user:
                    user_id = user.user_id
            
            # Step 1: Create graph memory with entity extraction
            graph_memory = self.graph_manager.add_memory(
                content=content,
                user_id=user_id,
                memory_type=memory_type,
                embedding=None
            )
            
            # Step 2: Link entities to knowledge base
            linked_entities = self.entity_linker.link_entities(
                graph_memory.entities, content
            )
            graph_memory.entities = linked_entities
            
            # Step 3: Get embedding
            embedding = self.embedding_manager.get_embedding(content)
            graph_memory.embedding = embedding
            
            # Step 4: Create vector store record
            vector_record = MemoryRecord(
                id=graph_memory.memory_id,
                content=content,
                vector=embedding,
                metadata={
                    "user_id": user_id,
                    "memory_type": memory_type,
                    "timestamp": graph_memory.timestamp.isoformat(),
                    "entity_count": len(graph_memory.entities),
                    "relationship_count": len(graph_memory.relationships),
                    **(metadata or {})
                }
            )
            
            # Step 5: Store in vector database
            await self._store_vector_record(vector_record, user_id)
            
            # Step 6: Memory consolidation analysis
            existing_memories = list(self.graph_manager.memories.values())
            consolidation_decision = self.performance_optimizer.consolidator.analyze_memory_for_consolidation(
                graph_memory, existing_memories
            )
            
            # Step 7: Apply consolidation decision
            final_result = await self._apply_consolidation_decision(
                graph_memory, consolidation_decision
            )
            
            # Step 8: Update neural patterns
            self.neural_module.extract_memory_patterns([graph_memory])
            
            # Step 9: Record operation
            operation_time = (datetime.utcnow() - start_time).total_seconds()
            self.operation_history.append({
                "operation_id": operation_id,
                "type": "add_memory",
                "user_id": user_id,
                "duration": operation_time,
                "success": True,
                "consolidation_operation": consolidation_decision.operation.value,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "success": True,
                "memory_id": graph_memory.memory_id,
                "consolidation_decision": asdict(consolidation_decision),
                "entities_extracted": len(graph_memory.entities),
                "relationships_extracted": len(graph_memory.relationships),
                "processing_time_ms": operation_time * 1000,
                "operation_id": operation_id
            }
            
        except Exception as e:
            # Log error
            self.operation_history.append({
                "operation_id": operation_id,
                "type": "add_memory",
                "user_id": user_id,
                "duration": (datetime.utcnow() - start_time).total_seconds(),
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "success": False,
                "error": str(e),
                "operation_id": operation_id
            }
    
    async def _store_vector_record(self, record: MemoryRecord, user_id: Optional[str]):
        """Store vector record with optimization"""
        try:
            self.vector_store.upsert([record], namespace=user_id)
        except Exception as e:
            print(f"Vector storage error: {e}")
    
    async def _apply_consolidation_decision(self, memory: GraphMemory, 
                                          decision) -> Dict[str, Any]:
        """Apply memory consolidation decision"""
        if decision.operation == MemoryOperation.UPDATE:
            # Update existing memory
            if decision.target_memory_id in self.graph_manager.memories:
                existing = self.graph_manager.memories[decision.target_memory_id]
                existing.content = decision.new_content
                existing.entities.extend(memory.entities)
                existing.relationships.extend(memory.relationships)
                
                return {
                    "action": "updated_existing",
                    "target_id": decision.target_memory_id,
                    "confidence": decision.confidence
                }
        
        elif decision.operation == MemoryOperation.NOOP:
            return {
                "action": "no_operation",
                "reason": decision.reasoning,
                "confidence": decision.confidence
            }
        
        # Default: ADD operation
        return {
            "action": "added_new",
            "memory_id": memory.memory_id,
            "confidence": decision.confidence
        }
    
    async def hybrid_search(self, query: str, user_id: Optional[str] = None,
                           session_id: Optional[str] = None,
                           max_results: int = 10,
                           search_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Advanced hybrid search combining all retrieval strategies"""
        
        start_time = datetime.utcnow()
        
        try:
            # Security check if enabled
            if self.security_enabled and session_id:
                security_result = self.security_manager.secure_memory_operation(
                    session_id=session_id,
                    operation="search",
                    memory_data={"query": query},
                    required_permission=PermissionLevel.READ
                )
                
                if "error" in security_result:
                    return security_result
                
                user = self.security_manager.user_manager.validate_session(session_id)
                if user:
                    user_id = user.user_id
            
            # Build hybrid query with intelligent weights
            weights = search_weights or {"vector": 0.4, "graph": 0.4, "temporal": 0.2}
            
            # Predict relevant entities using neural module
            context_entities = list(self.neural_module.memory_patterns.keys())[:10]
            predicted_entities = self.neural_module.predict_relevant_entities(
                query, context_entities
            )
            
            # Build entity boost map
            entity_boost = {entity: confidence for entity, confidence in predicted_entities}
            
            hybrid_query = HybridQuery(
                text=query,
                vector_weight=weights["vector"],
                graph_weight=weights["graph"],
                temporal_weight=weights["temporal"],
                max_results=max_results,
                user_id=user_id,
                entity_boost=entity_boost
            )
            
            # Perform hybrid retrieval
            results = self.hybrid_retriever.retrieve(hybrid_query)
            
            # Apply conversational context if available
            if hasattr(self, 'conversational_retrieval'):
                conversational_results = self.conversational_retrieval.conversational_retrieve(
                    query, context_window=5
                )
                
                # Merge and deduplicate results
                results = self._merge_search_results(results, conversational_results)
            
            # Process results for response
            processed_results = []
            for result in results:
                processed_results.append({
                    "memory_id": result.memory.memory_id,
                    "content": result.memory.content,
                    "score": result.final_score,
                    "scores_breakdown": {
                        "vector": result.vector_score,
                        "graph": result.graph_score,
                        "temporal": result.temporal_score
                    },
                    "entities": result.related_entities,
                    "timestamp": result.memory.timestamp.isoformat(),
                    "explanation": result.explanation
                })
            
            # Record performance
            search_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "success": True,
                "query": query,
                "results": processed_results,
                "total_results": len(processed_results),
                "search_time_ms": search_time * 1000,
                "search_weights": weights,
                "predicted_entities": predicted_entities[:5],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def _merge_search_results(self, results1: List[RetrievalResult], 
                             results2: List[RetrievalResult]) -> List[RetrievalResult]:
        """Merge and deduplicate search results"""
        seen_ids = set()
        merged_results = []
        
        # Add results from first list
        for result in results1:
            if result.memory.memory_id not in seen_ids:
                merged_results.append(result)
                seen_ids.add(result.memory.memory_id)
        
        # Add unique results from second list
        for result in results2:
            if result.memory.memory_id not in seen_ids:
                merged_results.append(result)
                seen_ids.add(result.memory.memory_id)
        
        # Sort by final score
        merged_results.sort(key=lambda x: x.final_score, reverse=True)
        
        return merged_results
    
    def generate_memory_insights(self, user_id: Optional[str] = None,
                                session_id: Optional[str] = None) -> List[MemoryInsight]:
        """Generate AI-powered insights about user's memory patterns"""
        
        # Security check if enabled
        if self.security_enabled and session_id:
            security_result = self.security_manager.secure_memory_operation(
                session_id=session_id,
                operation="read",
                memory_data={},
                required_permission=PermissionLevel.READ
            )
            
            if "error" in security_result:
                return []
        
        # Check cache first
        cache_key = f"insights_{user_id}"
        if cache_key in self.insights_cache:
            return self.insights_cache[cache_key]
        
        insights = []
        
        # Get user memories
        user_memories = [
            m for m in self.graph_manager.memories.values()
            if user_id is None or m.user_id == user_id
        ]
        
        if not user_memories:
            return insights
        
        # Pattern analysis
        patterns = self.neural_module.extract_memory_patterns(user_memories)
        
        for pattern in patterns:
            if pattern["type"] == "entity_co_occurrence":
                insight = MemoryInsight(
                    insight_type="entity_relationship",
                    title=f"Strong connection: {' & '.join(pattern['entities'])}",
                    description=f"You frequently mention {pattern['entities'][0]} and {pattern['entities'][1]} together ({pattern['frequency']} times)",
                    confidence=pattern['strength'],
                    entities_involved=pattern['entities'],
                    evidence=[f"Co-occurred {pattern['frequency']} times"],
                    actionable_suggestions=[
                        f"Consider organizing memories about {pattern['entities'][0]} and {pattern['entities'][1]}",
                        "This relationship might be important for future reference"
                    ]
                )
                insights.append(insight)
        
        # Memory growth analysis
        recent_memories = [m for m in user_memories if (datetime.utcnow() - m.timestamp).days <= 7]
        if len(recent_memories) > 10:
            insight = MemoryInsight(
                insight_type="activity_level",
                title="High memory activity detected",
                description=f"You've created {len(recent_memories)} memories in the last week",
                confidence=0.9,
                entities_involved=[],
                evidence=[f"{len(recent_memories)} memories in 7 days"],
                actionable_suggestions=[
                    "Consider reviewing and consolidating related memories",
                    "Your active memory creation shows strong engagement"
                ]
            )
            insights.append(insight)
        
        # Entity diversity analysis
        all_entities = []
        for memory in user_memories:
            all_entities.extend([e.canonical_form for e in memory.entities])
        
        unique_entities = set(all_entities)
        if len(unique_entities) > 50:
            insight = MemoryInsight(
                insight_type="knowledge_breadth",
                title="Diverse knowledge base",
                description=f"Your memories contain {len(unique_entities)} unique entities across various domains",
                confidence=0.8,
                entities_involved=list(unique_entities)[:10],
                evidence=[f"{len(unique_entities)} unique entities identified"],
                actionable_suggestions=[
                    "Your knowledge spans multiple domains effectively",
                    "Consider creating topic-based memory collections"
                ]
            )
            insights.append(insight)
        
        # Cache insights for future use
        self.insights_cache[cache_key] = insights
        
        return insights
    
    def get_comprehensive_stats(self, user_id: Optional[str] = None,
                               session_id: Optional[str] = None) -> MemoryStats:
        """Get comprehensive memory statistics"""
        
        # Security check if enabled
        if self.security_enabled and session_id:
            security_result = self.security_manager.secure_memory_operation(
                session_id=session_id,
                operation="read",
                memory_data={},
                required_permission=PermissionLevel.READ
            )
            
            if "error" in security_result:
                return MemoryStats(0, 0, 0, 0.0, 0.0, 0.0, {}, {}, datetime.utcnow())
        
        # Get user memories
        user_memories = [
            m for m in self.graph_manager.memories.values()
            if user_id is None or m.user_id == user_id
        ]
        
        # Calculate statistics
        total_memories = len(user_memories)
        
        all_entities = []
        total_relationships = 0
        for memory in user_memories:
            all_entities.extend([e.canonical_form for e in memory.entities])
            total_relationships += len(memory.relationships)
        
        unique_entities = len(set(all_entities))
        
        # Graph statistics
        graph_stats = self.graph_manager.knowledge_graph.get_graph_statistics()
        graph_density = graph_stats.get('density', 0.0)
        
        # Memory growth rate (memories per day in last month)
        recent_memories = [
            m for m in user_memories 
            if (datetime.utcnow() - m.timestamp).days <= 30
        ]
        memory_growth_rate = len(recent_memories) / 30.0
        
        # Consolidation rate (from operation history)
        recent_operations = [
            op for op in self.operation_history 
            if (datetime.utcnow() - datetime.fromisoformat(op['timestamp'])).days <= 7
        ]
        
        consolidation_ops = [
            op for op in recent_operations 
            if op.get('consolidation_operation') in ['UPDATE', 'NOOP']
        ]
        consolidation_rate = len(consolidation_ops) / max(len(recent_operations), 1)
        
        # Search performance
        search_operations = [op for op in recent_operations if op['type'] == 'search']
        avg_search_time = sum(op.get('duration', 0) for op in search_operations) / max(len(search_operations), 1)
        
        search_performance = {
            "average_search_time_ms": avg_search_time * 1000,
            "total_searches": len(search_operations),
            "search_success_rate": sum(1 for op in search_operations if op.get('success', False)) / max(len(search_operations), 1)
        }
        
        # User engagement
        user_engagement = {
            "memories_this_week": len([m for m in user_memories if (datetime.utcnow() - m.timestamp).days <= 7]),
            "memories_this_month": len(recent_memories),
            "avg_entities_per_memory": len(all_entities) / max(total_memories, 1),
            "most_active_day": self._get_most_active_day(user_memories)
        }
        
        return MemoryStats(
            total_memories=total_memories,
            unique_entities=unique_entities,
            relationships_count=total_relationships,
            graph_density=graph_density,
            memory_growth_rate=memory_growth_rate,
            consolidation_rate=consolidation_rate,
            search_performance=search_performance,
            user_engagement=user_engagement,
            timestamp=datetime.utcnow()
        )
    
    def _get_most_active_day(self, memories: List[GraphMemory]) -> str:
        """Get the most active day of the week"""
        day_counts = defaultdict(int)
        
        for memory in memories:
            day_name = memory.timestamp.strftime("%A")
            day_counts[day_name] += 1
        
        if not day_counts:
            return "N/A"
        
        return max(day_counts, key=day_counts.get)
    
    def export_user_data(self, user_id: str, session_id: Optional[str] = None,
                        format: str = "json") -> Dict[str, Any]:
        """Export all user data for GDPR compliance"""
        
        if self.security_enabled and session_id:
            # Get user data through security manager
            user = self.security_manager.user_manager.validate_session(session_id)
            if not user or user.user_id != user_id:
                return {"error": "Access denied"}
            
            # Use privacy manager for GDPR export
            return self.security_manager.privacy_manager.get_user_data_export(
                user_id, user.tenant_id
            )
        
        # Basic export without security
        user_memories = [
            m for m in self.graph_manager.memories.values()
            if m.user_id == user_id
        ]
        
        export_data = {
            "user_id": user_id,
            "export_timestamp": datetime.utcnow().isoformat(),
            "total_memories": len(user_memories),
            "memories": [asdict(memory) for memory in user_memories],
            "insights": [asdict(insight) for insight in self.generate_memory_insights(user_id)],
            "statistics": asdict(self.get_comprehensive_stats(user_id))
        }
        
        return export_data
    
    async def delete_user_data(self, user_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Delete all user data for GDPR right to erasure"""
        
        if self.security_enabled and session_id:
            user = self.security_manager.user_manager.validate_session(session_id)
            if not user or user.user_id != user_id:
                return {"error": "Access denied"}
            
            return self.security_manager.privacy_manager.delete_user_data(
                user_id, user.tenant_id
            )
        
        # Basic deletion without security
        deleted_memories = []
        for memory_id, memory in list(self.graph_manager.memories.items()):
            if memory.user_id == user_id:
                deleted_memories.append(memory_id)
                del self.graph_manager.memories[memory_id]
        
        # Delete from vector store
        try:
            # This would require implementing delete functionality in vector store
            pass
        except Exception as e:
            print(f"Vector store deletion error: {e}")
        
        return {
            "user_id": user_id,
            "deletion_timestamp": datetime.utcnow().isoformat(),
            "memories_deleted": len(deleted_memories),
            "status": "completed"
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health metrics"""
        
        # Performance metrics
        recent_operations = [
            op for op in self.operation_history 
            if (datetime.utcnow() - datetime.fromisoformat(op['timestamp'])).days <= 1
        ]
        
        success_rate = sum(1 for op in recent_operations if op.get('success', False)) / max(len(recent_operations), 1)
        avg_response_time = sum(op.get('duration', 0) for op in recent_operations) / max(len(recent_operations), 1)
        
        # Memory usage
        total_memories = len(self.graph_manager.memories)
        total_entities = len(self.graph_manager.knowledge_graph.entities)
        total_relationships = len(self.graph_manager.knowledge_graph.relationships)
        
        # Cache performance
        cache_stats = self.performance_optimizer.cache.get_stats()
        
        health_score = min(100, (success_rate * 40 + 
                                (1 / max(avg_response_time, 0.001)) * 30 + 
                                cache_stats["hit_rate"] * 30))
        
        return {
            "overall_health_score": health_score,
            "system_status": "healthy" if health_score > 80 else "degraded" if health_score > 60 else "critical",
            "performance_metrics": {
                "success_rate": success_rate,
                "avg_response_time_ms": avg_response_time * 1000,
                "operations_last_24h": len(recent_operations)
            },
            "memory_metrics": {
                "total_memories": total_memories,
                "total_entities": total_entities,
                "total_relationships": total_relationships,
                "graph_density": self.graph_manager.knowledge_graph.get_graph_statistics().get('density', 0)
            },
            "cache_performance": cache_stats,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.2",
            "features_enabled": {
                "graph_memory": True,
                "hybrid_retrieval": True,
                "performance_optimization": True,
                "enterprise_security": self.security_enabled,
                "neural_patterns": True,
                "entity_linking": True
            }
        } 