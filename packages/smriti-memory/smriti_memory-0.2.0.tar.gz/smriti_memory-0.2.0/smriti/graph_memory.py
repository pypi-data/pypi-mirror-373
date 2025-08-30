"""
Graph-based Memory System for Advanced AI Memory Management

This module implements a sophisticated graph-based memory system that:
- Extracts entities and relationships from text
- Builds knowledge graphs from memories
- Enables graph traversal for enhanced retrieval
- Supports temporal relationships and fact validity
- Provides memory consolidation and deduplication
"""

import json
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import networkx as nx
from collections import defaultdict
import re

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


@dataclass
class Entity:
    """Represents an extracted entity with metadata"""
    id: str
    text: str
    type: str  # PERSON, ORGANIZATION, LOCATION, EVENT, CONCEPT, etc.
    confidence: float
    start_pos: int
    end_pos: int
    canonical_form: str  # Normalized form
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.canonical_form:
            self.canonical_form = self.text.lower().strip()


@dataclass
class Relationship:
    """Represents a relationship between entities"""
    id: str
    source_entity: str  # Entity ID
    target_entity: str  # Entity ID
    relation_type: str  # KNOWS, WORKS_AT, LOCATED_IN, CAUSES, etc.
    confidence: float
    evidence_text: str  # Text supporting this relationship
    temporal_validity: Optional[Tuple[datetime, datetime]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class GraphMemory:
    """Represents a memory with extracted graph information"""
    memory_id: str
    content: str
    entities: List[Entity]
    relationships: List[Relationship]
    embedding: Optional[List[float]] = None
    timestamp: datetime = None
    user_id: Optional[str] = None
    memory_type: str = "user_message"
    consolidation_score: float = 0.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class EntityExtractor(ABC):
    """Abstract base class for entity extraction"""
    
    @abstractmethod
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities from text"""
        pass


class SpacyEntityExtractor(EntityExtractor):
    """Entity extractor using spaCy NLP"""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        if not SPACY_AVAILABLE:
            raise ImportError("spaCy is required for SpacyEntityExtractor")
        
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            # Fallback to blank model with basic components
            self.nlp = spacy.blank("en")
            # Add basic pipeline components
            self.nlp.add_pipe("sentencizer")
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities using spaCy"""
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entity = Entity(
                id=str(uuid.uuid4()),
                text=ent.text,
                type=ent.label_,
                confidence=0.9,  # spaCy doesn't provide confidence scores by default
                start_pos=ent.start_char,
                end_pos=ent.end_char,
                canonical_form=ent.text.lower().strip()
            )
            entities.append(entity)
        
        return entities


class TransformersEntityExtractor(EntityExtractor):
    """Entity extractor using Transformers NER models"""
    
    def __init__(self, model_name: str = "dbmdz/bert-large-cased-finetuned-conll03-english"):
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers is required for TransformersEntityExtractor")
        
        self.ner_pipeline = pipeline("ner", 
                                   model=model_name, 
                                   tokenizer=model_name,
                                   aggregation_strategy="simple")
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities using Transformers"""
        results = self.ner_pipeline(text)
        entities = []
        
        for result in results:
            entity = Entity(
                id=str(uuid.uuid4()),
                text=result['word'],
                type=result['entity_group'],
                confidence=result['score'],
                start_pos=result['start'],
                end_pos=result['end'],
                canonical_form=result['word'].lower().strip()
            )
            entities.append(entity)
        
        return entities


class RuleBasedEntityExtractor(EntityExtractor):
    """Simple rule-based entity extractor as fallback"""
    
    def __init__(self):
        # Simple patterns for common entity types
        self.patterns = {
            'EMAIL': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'PHONE': re.compile(r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s?\d{3}-\d{4}\b'),
            'URL': re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            'DATE': re.compile(r'\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{4}-\d{2}-\d{2}\b'),
            'MONEY': re.compile(r'\$\d+(?:,\d{3})*(?:\.\d{2})?'),
        }
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities using simple regex patterns"""
        entities = []
        
        for entity_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                entity = Entity(
                    id=str(uuid.uuid4()),
                    text=match.group(),
                    type=entity_type,
                    confidence=0.8,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    canonical_form=match.group().lower().strip()
                )
                entities.append(entity)
        
        return entities


class RelationshipExtractor:
    """Extracts relationships between entities"""
    
    def __init__(self):
        # Simple relationship patterns
        self.relation_patterns = [
            (r'(\w+)\s+works?\s+(?:at|for)\s+(\w+)', 'WORKS_AT'),
            (r'(\w+)\s+(?:is|are)\s+(?:from|in)\s+(\w+)', 'LOCATED_IN'),
            (r'(\w+)\s+(?:knows?|met)\s+(\w+)', 'KNOWS'),
            (r'(\w+)\s+(?:owns?|has)\s+(\w+)', 'OWNS'),
            (r'(\w+)\s+(?:causes?|leads?\s+to)\s+(\w+)', 'CAUSES'),
            (r'(\w+)\s+(?:happened|occurred)\s+(?:in|at)\s+(\w+)', 'OCCURRED_AT'),
        ]
    
    def extract_relationships(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """Extract relationships from text and entities"""
        relationships = []
        
        # Create entity lookup by text
        entity_lookup = {ent.text.lower(): ent for ent in entities}
        
        # Pattern-based relationship extraction
        for pattern, relation_type in self.relation_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                source_text = match.group(1).lower()
                target_text = match.group(2).lower()
                
                if source_text in entity_lookup and target_text in entity_lookup:
                    relationship = Relationship(
                        id=str(uuid.uuid4()),
                        source_entity=entity_lookup[source_text].id,
                        target_entity=entity_lookup[target_text].id,
                        relation_type=relation_type,
                        confidence=0.7,
                        evidence_text=match.group(0)
                    )
                    relationships.append(relationship)
        
        # Co-occurrence based relationships (entities mentioned together)
        for i, ent1 in enumerate(entities):
            for ent2 in entities[i+1:]:
                # If entities are close together, create a general relationship
                distance = abs(ent1.start_pos - ent2.start_pos)
                if distance < 100:  # Within 100 characters
                    relationship = Relationship(
                        id=str(uuid.uuid4()),
                        source_entity=ent1.id,
                        target_entity=ent2.id,
                        relation_type='MENTIONED_WITH',
                        confidence=0.5,
                        evidence_text=text[min(ent1.start_pos, ent2.start_pos):max(ent1.end_pos, ent2.end_pos)]
                    )
                    relationships.append(relationship)
        
        return relationships


class KnowledgeGraph:
    """Manages the knowledge graph of entities and relationships"""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.entities: Dict[str, Entity] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.entity_to_canonical: Dict[str, str] = {}  # Maps text to canonical entity ID
    
    def add_entity(self, entity: Entity) -> str:
        """Add entity to graph with deduplication"""
        # Check for existing canonical form
        canonical_id = self.entity_to_canonical.get(entity.canonical_form)
        
        if canonical_id:
            # Update existing entity with new information
            existing_entity = self.entities[canonical_id]
            existing_entity.confidence = max(existing_entity.confidence, entity.confidence)
            existing_entity.metadata.update(entity.metadata)
            return canonical_id
        else:
            # Add new entity
            self.entities[entity.id] = entity
            self.entity_to_canonical[entity.canonical_form] = entity.id
            self.graph.add_node(entity.id, 
                              type=entity.type,
                              text=entity.text,
                              confidence=entity.confidence,
                              canonical_form=entity.canonical_form)
            return entity.id
    
    def add_relationship(self, relationship: Relationship):
        """Add relationship to graph"""
        self.relationships[relationship.id] = relationship
        self.graph.add_edge(
            relationship.source_entity,
            relationship.target_entity,
            key=relationship.id,
            relation_type=relationship.relation_type,
            confidence=relationship.confidence,
            evidence=relationship.evidence_text
        )
    
    def add_memory(self, graph_memory: GraphMemory):
        """Add a complete memory with entities and relationships"""
        # Add entities
        entity_id_mapping = {}
        for entity in graph_memory.entities:
            actual_id = self.add_entity(entity)
            entity_id_mapping[entity.id] = actual_id
        
        # Add relationships with updated entity IDs
        for relationship in graph_memory.relationships:
            # Update entity IDs to canonical ones
            relationship.source_entity = entity_id_mapping.get(
                relationship.source_entity, relationship.source_entity)
            relationship.target_entity = entity_id_mapping.get(
                relationship.target_entity, relationship.target_entity)
            
            self.add_relationship(relationship)
    
    def find_related_entities(self, entity_id: str, max_distance: int = 2) -> Set[str]:
        """Find entities related to given entity within max_distance"""
        if entity_id not in self.graph:
            return set()
        
        related = set()
        for distance in range(1, max_distance + 1):
            # Find all nodes at this distance
            nodes_at_distance = set()
            for node in related if distance > 1 else [entity_id]:
                neighbors = set(self.graph.successors(node)) | set(self.graph.predecessors(node))
                nodes_at_distance.update(neighbors)
            
            related.update(nodes_at_distance)
        
        return related - {entity_id}  # Remove the original entity
    
    def get_relationship_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """Find shortest path between two entities"""
        try:
            return nx.shortest_path(self.graph.to_undirected(), source_id, target_id)
        except nx.NetworkXNoPath:
            return None
    
    def get_entity_subgraph(self, entity_ids: List[str], include_neighbors: bool = True) -> nx.MultiDiGraph:
        """Get subgraph containing specified entities and optionally their neighbors"""
        nodes_to_include = set(entity_ids)
        
        if include_neighbors:
            for entity_id in entity_ids:
                if entity_id in self.graph:
                    neighbors = set(self.graph.successors(entity_id)) | set(self.graph.predecessors(entity_id))
                    nodes_to_include.update(neighbors)
        
        return self.graph.subgraph(nodes_to_include)
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        return {
            'num_entities': len(self.entities),
            'num_relationships': len(self.relationships),
            'num_edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'is_connected': nx.is_connected(self.graph.to_undirected()),
            'num_connected_components': nx.number_connected_components(self.graph.to_undirected()),
            'average_clustering': nx.average_clustering(self.graph.to_undirected()) if self.graph.number_of_nodes() > 0 else 0
        }


class GraphMemoryManager:
    """Advanced memory manager with graph-based capabilities"""
    
    def __init__(self, entity_extractor: Optional[EntityExtractor] = None):
        self.knowledge_graph = KnowledgeGraph()
        self.memories: Dict[str, GraphMemory] = {}
        
        # Initialize entity extractor with fallback chain
        if entity_extractor:
            self.entity_extractor = entity_extractor
        else:
            self.entity_extractor = self._initialize_entity_extractor()
        
        self.relationship_extractor = RelationshipExtractor()
    
    def _initialize_entity_extractor(self) -> EntityExtractor:
        """Initialize entity extractor with best available option"""
        try:
            if SPACY_AVAILABLE:
                return SpacyEntityExtractor()
        except Exception:
            pass
        
        try:
            if TRANSFORMERS_AVAILABLE:
                return TransformersEntityExtractor()
        except Exception:
            pass
        
        # Fallback to rule-based extractor
        return RuleBasedEntityExtractor()
    
    def add_memory(self, content: str, user_id: Optional[str] = None, 
                   memory_type: str = "user_message", 
                   embedding: Optional[List[float]] = None) -> GraphMemory:
        """Add memory with graph extraction"""
        
        # Extract entities
        entities = self.entity_extractor.extract_entities(content)
        
        # Extract relationships
        relationships = self.relationship_extractor.extract_relationships(content, entities)
        
        # Create graph memory
        graph_memory = GraphMemory(
            memory_id=str(uuid.uuid4()),
            content=content,
            entities=entities,
            relationships=relationships,
            embedding=embedding,
            user_id=user_id,
            memory_type=memory_type
        )
        
        # Add to knowledge graph
        self.knowledge_graph.add_memory(graph_memory)
        
        # Store memory
        self.memories[graph_memory.memory_id] = graph_memory
        
        return graph_memory
    
    def get_related_memories(self, query: str, max_memories: int = 10) -> List[GraphMemory]:
        """Get memories related to query using graph traversal"""
        
        # Extract entities from query
        query_entities = self.entity_extractor.extract_entities(query)
        
        related_memory_ids = set()
        
        for query_entity in query_entities:
            # Find canonical entity ID
            canonical_id = self.knowledge_graph.entity_to_canonical.get(
                query_entity.canonical_form)
            
            if canonical_id:
                # Find related entities
                related_entity_ids = self.knowledge_graph.find_related_entities(canonical_id)
                
                # Find memories containing these entities
                for memory in self.memories.values():
                    memory_entity_ids = {self.knowledge_graph.entity_to_canonical.get(
                        ent.canonical_form) for ent in memory.entities}
                    
                    if canonical_id in memory_entity_ids or memory_entity_ids & related_entity_ids:
                        related_memory_ids.add(memory.memory_id)
        
        # Return related memories sorted by relevance
        related_memories = [self.memories[mid] for mid in related_memory_ids if mid in self.memories]
        return related_memories[:max_memories]
    
    def consolidate_memories(self, similarity_threshold: float = 0.8) -> int:
        """Consolidate similar memories to reduce redundancy"""
        consolidated_count = 0
        memories_to_remove = set()
        
        memory_list = list(self.memories.values())
        
        for i, memory1 in enumerate(memory_list):
            if memory1.memory_id in memories_to_remove:
                continue
                
            for memory2 in memory_list[i+1:]:
                if memory2.memory_id in memories_to_remove:
                    continue
                
                # Calculate similarity based on shared entities
                entities1 = {ent.canonical_form for ent in memory1.entities}
                entities2 = {ent.canonical_form for ent in memory2.entities}
                
                if entities1 and entities2:
                    similarity = len(entities1 & entities2) / len(entities1 | entities2)
                    
                    if similarity >= similarity_threshold:
                        # Merge memories - keep the more recent one
                        if memory1.timestamp >= memory2.timestamp:
                            # Update memory1 with additional information from memory2
                            memory1.content += f"\n[Consolidated]: {memory2.content}"
                            memories_to_remove.add(memory2.memory_id)
                        else:
                            # Update memory2 with additional information from memory1
                            memory2.content += f"\n[Consolidated]: {memory1.content}"
                            memories_to_remove.add(memory1.memory_id)
                            break
                        
                        consolidated_count += 1
        
        # Remove consolidated memories
        for memory_id in memories_to_remove:
            if memory_id in self.memories:
                del self.memories[memory_id]
        
        return consolidated_count
    
    def get_memory_insights(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get insights about the user's memory graph"""
        user_memories = [m for m in self.memories.values() 
                        if user_id is None or m.user_id == user_id]
        
        if not user_memories:
            return {"message": "No memories found"}
        
        # Collect all entities from user memories
        all_entities = []
        for memory in user_memories:
            all_entities.extend(memory.entities)
        
        # Entity type distribution
        entity_types = defaultdict(int)
        for entity in all_entities:
            entity_types[entity.type] += 1
        
        # Most frequent entities
        entity_frequency = defaultdict(int)
        for entity in all_entities:
            entity_frequency[entity.canonical_form] += 1
        
        top_entities = sorted(entity_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Graph statistics
        graph_stats = self.knowledge_graph.get_graph_statistics()
        
        return {
            "total_memories": len(user_memories),
            "total_entities": len(all_entities),
            "unique_entities": len(set(ent.canonical_form for ent in all_entities)),
            "entity_types": dict(entity_types),
            "top_entities": top_entities,
            "graph_statistics": graph_stats,
            "memory_timespan": {
                "earliest": min(m.timestamp for m in user_memories).isoformat(),
                "latest": max(m.timestamp for m in user_memories).isoformat()
            }
        }
    
    def export_graph(self, format: str = "json") -> str:
        """Export knowledge graph in specified format"""
        if format == "json":
            graph_data = {
                "entities": [asdict(entity) for entity in self.knowledge_graph.entities.values()],
                "relationships": [asdict(rel) for rel in self.knowledge_graph.relationships.values()],
                "graph_stats": self.knowledge_graph.get_graph_statistics()
            }
            return json.dumps(graph_data, default=str, indent=2)
        
        elif format == "gexf":
            try:
                import networkx as nx
                return '\n'.join(nx.generate_gexf(self.knowledge_graph.graph))
            except ImportError:
                raise ImportError("NetworkX is required for GEXF export")
        
        else:
            raise ValueError(f"Unsupported format: {format}") 