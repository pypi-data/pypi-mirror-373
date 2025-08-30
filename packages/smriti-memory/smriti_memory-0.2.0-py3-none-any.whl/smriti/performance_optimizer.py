"""
Performance Optimization Module for Smriti Memory

This module implements advanced performance optimizations including:
- Memory consolidation with ADD/UPDATE/DELETE/NOOP operations
- Advanced caching strategies
- Batch processing and async operations
- Memory deduplication and merging
- Performance monitoring and analytics
"""

import asyncio
import threading
import time
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import json
import hashlib
import numpy as np

from .graph_memory import GraphMemory, Entity, Relationship
from .vector_stores import MemoryRecord


class MemoryOperation(Enum):
    """Types of memory operations for consolidation"""
    ADD = "ADD"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    NOOP = "NO_OPERATION"


@dataclass
class ConsolidationDecision:
    """Represents a memory consolidation decision"""
    operation: MemoryOperation
    target_memory_id: Optional[str]
    new_content: Optional[str]
    confidence: float
    reasoning: str
    entities_affected: List[str]
    relationships_affected: List[str]


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring"""
    operation_name: str
    start_time: float
    end_time: float
    duration: float
    memory_usage_mb: float
    cache_hit_rate: float
    throughput_ops_per_sec: float
    error_count: int
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class AdvancedCache:
    """Advanced multi-level caching system"""
    
    def __init__(self, max_size: int = 10000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Tuple[Any, float]] = {}  # key -> (value, timestamp)
        self.access_times: Dict[str, float] = {}
        self.hit_count = 0
        self.miss_count = 0
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with TTL check"""
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                
                # Check TTL
                if time.time() - timestamp < self.ttl_seconds:
                    self.access_times[key] = time.time()
                    self.hit_count += 1
                    return value
                else:
                    # Expired
                    del self.cache[key]
                    if key in self.access_times:
                        del self.access_times[key]
            
            self.miss_count += 1
            return None
    
    def set(self, key: str, value: Any):
        """Set value in cache with eviction if needed"""
        with self.lock:
            current_time = time.time()
            
            # Add new item
            self.cache[key] = (value, current_time)
            self.access_times[key] = current_time
            
            # Evict if over max size
            if len(self.cache) > self.max_size:
                self._evict_lru()
    
    def _evict_lru(self):
        """Evict least recently used items"""
        # Sort by access time and remove oldest
        sorted_keys = sorted(self.access_times.items(), key=lambda x: x[1])
        keys_to_remove = sorted_keys[:len(sorted_keys) // 4]  # Remove 25% when full
        
        for key, _ in keys_to_remove:
            if key in self.cache:
                del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
    
    def invalidate(self, pattern: str = None):
        """Invalidate cache entries"""
        with self.lock:
            if pattern is None:
                self.cache.clear()
                self.access_times.clear()
            else:
                keys_to_remove = [k for k in self.cache.keys() if pattern in k]
                for key in keys_to_remove:
                    if key in self.cache:
                        del self.cache[key]
                    if key in self.access_times:
                        del self.access_times[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "ttl_seconds": self.ttl_seconds
        }


class MemoryConsolidator:
    """Advanced memory consolidation with intelligent operations"""
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.consolidation_history: List[ConsolidationDecision] = []
    
    def analyze_memory_for_consolidation(self, new_memory: GraphMemory, 
                                       existing_memories: List[GraphMemory]) -> ConsolidationDecision:
        """Analyze if new memory should be added, update existing, or ignored"""
        
        best_match = None
        best_similarity = 0.0
        
        # Find most similar existing memory
        for existing in existing_memories:
            similarity = self._calculate_memory_similarity(new_memory, existing)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = existing
        
        # Make consolidation decision
        if best_similarity >= self.similarity_threshold:
            if self._should_update(new_memory, best_match):
                return ConsolidationDecision(
                    operation=MemoryOperation.UPDATE,
                    target_memory_id=best_match.memory_id,
                    new_content=self._merge_memory_content(new_memory, best_match),
                    confidence=best_similarity,
                    reasoning=f"High similarity ({best_similarity:.3f}) with existing memory, updating with new information",
                    entities_affected=[e.canonical_form for e in new_memory.entities],
                    relationships_affected=[r.id for r in new_memory.relationships]
                )
            else:
                return ConsolidationDecision(
                    operation=MemoryOperation.NOOP,
                    target_memory_id=None,
                    new_content=None,
                    confidence=best_similarity,
                    reasoning=f"Similar content already exists ({best_similarity:.3f}), no action needed",
                    entities_affected=[],
                    relationships_affected=[]
                )
        else:
            return ConsolidationDecision(
                operation=MemoryOperation.ADD,
                target_memory_id=None,
                new_content=new_memory.content,
                confidence=1.0 - best_similarity,
                reasoning=f"New unique content (max similarity: {best_similarity:.3f}), adding to memory",
                entities_affected=[e.canonical_form for e in new_memory.entities],
                relationships_affected=[r.id for r in new_memory.relationships]
            )
    
    def _calculate_memory_similarity(self, memory1: GraphMemory, memory2: GraphMemory) -> float:
        """Calculate comprehensive similarity between two memories"""
        
        # Content similarity (using entity overlap as proxy)
        entities1 = {e.canonical_form for e in memory1.entities}
        entities2 = {e.canonical_form for e in memory2.entities}
        
        entity_similarity = 0.0
        if entities1 or entities2:
            intersection = len(entities1 & entities2)
            union = len(entities1 | entities2)
            entity_similarity = intersection / union if union > 0 else 0.0
        
        # Temporal similarity
        time_diff = abs((memory1.timestamp - memory2.timestamp).total_seconds())
        temporal_similarity = max(0, 1 - (time_diff / (24 * 60 * 60)))  # Decay over 24 hours
        
        # Content length similarity
        len1, len2 = len(memory1.content), len(memory2.content)
        length_similarity = min(len1, len2) / max(len1, len2) if max(len1, len2) > 0 else 1.0
        
        # Weighted combination
        final_similarity = (entity_similarity * 0.6 + 
                          temporal_similarity * 0.2 + 
                          length_similarity * 0.2)
        
        return final_similarity
    
    def _should_update(self, new_memory: GraphMemory, existing_memory: GraphMemory) -> bool:
        """Determine if existing memory should be updated with new information"""
        
        # Update if new memory has more entities
        if len(new_memory.entities) > len(existing_memory.entities):
            return True
        
        # Update if new memory is more recent
        if new_memory.timestamp > existing_memory.timestamp:
            return True
        
        # Update if new memory has higher confidence entities
        new_avg_confidence = sum(e.confidence for e in new_memory.entities) / len(new_memory.entities) if new_memory.entities else 0
        existing_avg_confidence = sum(e.confidence for e in existing_memory.entities) / len(existing_memory.entities) if existing_memory.entities else 0
        
        if new_avg_confidence > existing_avg_confidence:
            return True
        
        return False
    
    def _merge_memory_content(self, new_memory: GraphMemory, existing_memory: GraphMemory) -> str:
        """Intelligently merge content from two memories"""
        
        # Simple merge strategy - combine unique information
        base_content = existing_memory.content
        
        # Extract new entities and relationships that don't exist in base
        new_entities = {e.canonical_form for e in new_memory.entities}
        existing_entities = {e.canonical_form for e in existing_memory.entities}
        unique_entities = new_entities - existing_entities
        
        if unique_entities:
            additional_info = f"\n[Updated with new information]: {new_memory.content}"
            return base_content + additional_info
        
        return base_content
    
    def get_consolidation_stats(self) -> Dict[str, Any]:
        """Get statistics about consolidation operations"""
        if not self.consolidation_history:
            return {"message": "No consolidation history available"}
        
        operation_counts = defaultdict(int)
        total_confidence = 0.0
        
        for decision in self.consolidation_history:
            operation_counts[decision.operation.value] += 1
            total_confidence += decision.confidence
        
        avg_confidence = total_confidence / len(self.consolidation_history)
        
        return {
            "total_decisions": len(self.consolidation_history),
            "operation_breakdown": dict(operation_counts),
            "average_confidence": avg_confidence,
            "similarity_threshold": self.similarity_threshold
        }


class BatchProcessor:
    """Efficient batch processing for memory operations"""
    
    def __init__(self, batch_size: int = 100, max_wait_time: float = 1.0):
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.pending_operations: deque = deque()
        self.last_flush_time = time.time()
        self.lock = threading.Lock()
    
    async def add_operation(self, operation: Dict[str, Any]) -> Optional[List[Any]]:
        """Add operation to batch queue"""
        with self.lock:
            self.pending_operations.append(operation)
            
            # Check if we should flush
            should_flush = (
                len(self.pending_operations) >= self.batch_size or
                time.time() - self.last_flush_time >= self.max_wait_time
            )
            
            if should_flush:
                return await self._flush_batch()
        
        return None
    
    async def _flush_batch(self) -> List[Any]:
        """Process the current batch"""
        operations = []
        
        with self.lock:
            while self.pending_operations and len(operations) < self.batch_size:
                operations.append(self.pending_operations.popleft())
            self.last_flush_time = time.time()
        
        if not operations:
            return []
        
        # Process operations in parallel
        tasks = [self._process_single_operation(op) for op in operations]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def _process_single_operation(self, operation: Dict[str, Any]) -> Any:
        """Process a single operation"""
        # This would be implemented based on specific operation types
        operation_type = operation.get('type')
        
        if operation_type == 'embedding':
            # Simulate embedding computation
            await asyncio.sleep(0.01)
            return f"embedding_result_{operation.get('id')}"
        elif operation_type == 'storage':
            # Simulate storage operation
            await asyncio.sleep(0.005)
            return f"storage_result_{operation.get('id')}"
        else:
            return f"unknown_operation_{operation.get('id')}"
    
    async def force_flush(self) -> List[Any]:
        """Force flush all pending operations"""
        return await self._flush_batch()


class PerformanceMonitor:
    """Monitor and analyze performance metrics"""
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.metrics_history: List[PerformanceMetrics] = []
        self.active_operations: Dict[str, float] = {}
        self.lock = threading.Lock()
    
    def start_operation(self, operation_id: str, operation_name: str):
        """Start timing an operation"""
        with self.lock:
            self.active_operations[operation_id] = time.time()
    
    def end_operation(self, operation_id: str, operation_name: str, 
                     cache_hit_rate: float = 0.0, error_count: int = 0,
                     metadata: Dict[str, Any] = None) -> PerformanceMetrics:
        """End timing an operation and record metrics"""
        end_time = time.time()
        
        with self.lock:
            start_time = self.active_operations.pop(operation_id, end_time)
            duration = end_time - start_time
            
            # Calculate memory usage (simplified)
            import psutil
            process = psutil.Process()
            memory_usage_mb = process.memory_info().rss / 1024 / 1024
            
            # Calculate throughput
            throughput = 1.0 / duration if duration > 0 else 0.0
            
            metrics = PerformanceMetrics(
                operation_name=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                memory_usage_mb=memory_usage_mb,
                cache_hit_rate=cache_hit_rate,
                throughput_ops_per_sec=throughput,
                error_count=error_count,
                metadata=metadata or {}
            )
            
            self.metrics_history.append(metrics)
            
            # Limit history size
            if len(self.metrics_history) > self.max_history:
                self.metrics_history = self.metrics_history[-self.max_history:]
            
            return metrics
    
    def get_performance_summary(self, time_window_minutes: Optional[int] = None) -> Dict[str, Any]:
        """Get performance summary for the specified time window"""
        cutoff_time = None
        if time_window_minutes:
            cutoff_time = time.time() - (time_window_minutes * 60)
        
        relevant_metrics = [
            m for m in self.metrics_history
            if cutoff_time is None or m.start_time >= cutoff_time
        ]
        
        if not relevant_metrics:
            return {"message": "No metrics available for the specified time window"}
        
        # Aggregate statistics
        durations = [m.duration for m in relevant_metrics]
        cache_hit_rates = [m.cache_hit_rate for m in relevant_metrics]
        throughputs = [m.throughput_ops_per_sec for m in relevant_metrics]
        memory_usages = [m.memory_usage_mb for m in relevant_metrics]
        
        # Group by operation
        by_operation = defaultdict(list)
        for m in relevant_metrics:
            by_operation[m.operation_name].append(m)
        
        operation_stats = {}
        for op_name, op_metrics in by_operation.items():
            operation_stats[op_name] = {
                "count": len(op_metrics),
                "avg_duration": sum(m.duration for m in op_metrics) / len(op_metrics),
                "min_duration": min(m.duration for m in op_metrics),
                "max_duration": max(m.duration for m in op_metrics),
                "avg_throughput": sum(m.throughput_ops_per_sec for m in op_metrics) / len(op_metrics),
                "total_errors": sum(m.error_count for m in op_metrics)
            }
        
        return {
            "time_window_minutes": time_window_minutes,
            "total_operations": len(relevant_metrics),
            "overall_stats": {
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "avg_cache_hit_rate": sum(cache_hit_rates) / len(cache_hit_rates),
                "avg_throughput": sum(throughputs) / len(throughputs),
                "avg_memory_usage_mb": sum(memory_usages) / len(memory_usages)
            },
            "by_operation": operation_stats
        }
    
    def detect_performance_anomalies(self, threshold_multiplier: float = 2.0) -> List[Dict[str, Any]]:
        """Detect performance anomalies based on historical data"""
        anomalies = []
        
        if len(self.metrics_history) < 10:
            return anomalies
        
        # Group by operation type
        by_operation = defaultdict(list)
        for m in self.metrics_history:
            by_operation[m.operation_name].append(m.duration)
        
        for op_name, durations in by_operation.items():
            if len(durations) < 5:
                continue
            
            mean_duration = sum(durations) / len(durations)
            
            # Find recent anomalies
            recent_metrics = [m for m in self.metrics_history[-100:] if m.operation_name == op_name]
            
            for metric in recent_metrics:
                if metric.duration > mean_duration * threshold_multiplier:
                    anomalies.append({
                        "operation_name": op_name,
                        "timestamp": metric.start_time,
                        "duration": metric.duration,
                        "expected_duration": mean_duration,
                        "anomaly_factor": metric.duration / mean_duration,
                        "metadata": metric.metadata
                    })
        
        return anomalies


class PerformanceOptimizer:
    """Main performance optimization coordinator"""
    
    def __init__(self):
        self.cache = AdvancedCache()
        self.consolidator = MemoryConsolidator()
        self.batch_processor = BatchProcessor()
        self.monitor = PerformanceMonitor()
        self.optimization_history: List[Dict[str, Any]] = []
    
    def optimize_memory_operation(self, operation_type: str, **kwargs) -> Any:
        """Optimize a memory operation with caching and monitoring"""
        operation_id = f"{operation_type}_{int(time.time() * 1000)}"
        
        # Start monitoring
        self.monitor.start_operation(operation_id, operation_type)
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(operation_type, kwargs)
            cached_result = self.cache.get(cache_key)
            
            if cached_result is not None:
                # Cache hit
                self.monitor.end_operation(operation_id, operation_type, cache_hit_rate=1.0)
                return cached_result
            
            # Cache miss - perform operation
            result = self._execute_operation(operation_type, **kwargs)
            
            # Cache the result
            self.cache.set(cache_key, result)
            
            # End monitoring
            self.monitor.end_operation(operation_id, operation_type, cache_hit_rate=0.0)
            
            return result
            
        except Exception as e:
            self.monitor.end_operation(operation_id, operation_type, cache_hit_rate=0.0, error_count=1)
            raise
    
    def _generate_cache_key(self, operation_type: str, kwargs: Dict[str, Any]) -> str:
        """Generate a cache key for the operation"""
        # Create a stable hash from operation type and parameters
        content = f"{operation_type}:{json.dumps(kwargs, sort_keys=True, default=str)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _execute_operation(self, operation_type: str, **kwargs) -> Any:
        """Execute the actual operation"""
        # This would be implemented based on specific operation types
        if operation_type == "embedding_computation":
            # Simulate embedding computation
            time.sleep(0.01)
            return [0.1] * 1536  # Mock embedding vector
        
        elif operation_type == "vector_search":
            # Simulate vector search
            time.sleep(0.005)
            return [{"id": "mock_result", "score": 0.9}]
        
        elif operation_type == "graph_traversal":
            # Simulate graph traversal
            time.sleep(0.008)
            return [{"entity_id": "mock_entity", "distance": 2}]
        
        else:
            return {"result": f"mock_result_for_{operation_type}"}
    
    async def optimize_batch_operations(self, operations: List[Dict[str, Any]]) -> List[Any]:
        """Optimize batch operations"""
        results = []
        
        for operation in operations:
            result = await self.batch_processor.add_operation(operation)
            if result:
                results.extend(result)
        
        # Flush any remaining operations
        remaining = await self.batch_processor.force_flush()
        results.extend(remaining)
        
        return results
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on performance data"""
        recommendations = []
        
        # Analyze cache performance
        cache_stats = self.cache.get_stats()
        if cache_stats["hit_rate"] < 0.7:
            recommendations.append({
                "type": "cache_optimization",
                "priority": "high",
                "issue": f"Low cache hit rate: {cache_stats['hit_rate']:.2%}",
                "recommendation": "Consider increasing cache size or adjusting TTL",
                "current_config": cache_stats
            })
        
        # Analyze performance anomalies
        anomalies = self.monitor.detect_performance_anomalies()
        if anomalies:
            recommendations.append({
                "type": "performance_anomaly",
                "priority": "medium",
                "issue": f"Detected {len(anomalies)} performance anomalies",
                "recommendation": "Investigate slow operations and optimize bottlenecks",
                "anomalies": anomalies[:5]  # Show top 5
            })
        
        # Analyze consolidation effectiveness
        consolidation_stats = self.consolidator.get_consolidation_stats()
        if consolidation_stats and consolidation_stats.get("operation_breakdown", {}).get("NOOP", 0) > consolidation_stats.get("total_decisions", 1) * 0.3:
            recommendations.append({
                "type": "consolidation_tuning",
                "priority": "low",
                "issue": "High NOOP rate in memory consolidation",
                "recommendation": "Consider adjusting similarity threshold",
                "current_stats": consolidation_stats
            })
        
        return recommendations
    
    def export_performance_report(self) -> Dict[str, Any]:
        """Export comprehensive performance report"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cache_stats": self.cache.get_stats(),
            "performance_summary": self.monitor.get_performance_summary(time_window_minutes=60),
            "consolidation_stats": self.consolidator.get_consolidation_stats(),
            "anomalies": self.monitor.detect_performance_anomalies(),
            "optimization_recommendations": self.get_optimization_recommendations()
        } 