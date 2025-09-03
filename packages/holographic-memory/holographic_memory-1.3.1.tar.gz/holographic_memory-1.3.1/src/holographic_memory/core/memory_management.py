"""
🗄️ Memory Management for Holographic Memory System
=================================================

This module implements memory management functionality for holographic memory
systems, including vector registration, lifecycle management, and resource
optimization.

Based on principles from Plate (1995) and modern memory management techniques.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict
import time
import warnings

from .hrr_operations import HRRVector


@dataclass
class VectorRecord:
    """
    📝 Record for tracking a managed vector.
    
    Contains metadata and lifecycle information for vectors
    in the holographic memory system.
    """
    
    name: str
    vector: HRRVector
    creation_time: float = field(default_factory=time.time)
    access_count: int = 0
    last_access_time: float = field(default_factory=time.time)
    reference_count: int = 1
    size_bytes: int = 0
    is_persistent: bool = False
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.vector and hasattr(self.vector, 'data'):
            self.size_bytes = self.vector.data.nbytes


class MemoryManager:
    """
    🗄️ Memory Manager for Holographic Memory System
    
    Manages the lifecycle of holographic vectors, including creation,
    access tracking, garbage collection, and resource optimization.
    
    Parameters
    ----------
    vector_dim : int, default=512
        Default vector dimension
    capacity_threshold : int, optional
        Maximum number of vectors to manage
    gc_threshold : float, default=0.8
        Capacity threshold to trigger garbage collection
    enable_auto_gc : bool, default=True
        Enable automatic garbage collection
    """
    
    def __init__(self,
                 vector_dim: int = 512,
                 capacity_threshold: Optional[int] = None,
                 gc_threshold: float = 0.8,
                 enable_auto_gc: bool = True):
        
        self.vector_dim = vector_dim
        self.capacity_threshold = capacity_threshold or (vector_dim * 10)
        self.gc_threshold = gc_threshold
        self.enable_auto_gc = enable_auto_gc
        
        # Storage for managed vectors
        self.vectors: Dict[str, VectorRecord] = {}
        self.vector_groups: Dict[str, List[str]] = defaultdict(list)
        
        # Statistics
        self.stats = {
            'vectors_created': 0,
            'vectors_accessed': 0,
            'vectors_deleted': 0,
            'gc_collections': 0,
            'total_memory_allocated': 0,
            'peak_memory_usage': 0,
            'current_memory_usage': 0
        }
        
        # Configuration
        self.config = {
            'max_idle_time': 3600.0,  # 1 hour
            'min_access_count': 1,
            'gc_frequency': 100,  # operations
            'memory_limit_mb': None
        }
        
        self.operation_count = 0
    
    def register_vector(self, 
                       name: str, 
                       vector: HRRVector,
                       is_persistent: bool = False,
                       tags: Optional[List[str]] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a vector with the memory manager.
        
        Parameters
        ----------
        name : str
            Unique name for the vector
        vector : HRRVector
            Vector to register
        is_persistent : bool, default=False
            Whether vector should persist through garbage collection
        tags : List[str], optional
            Tags for organizing vectors
        metadata : Dict[str, Any], optional
            Additional metadata
            
        Returns
        -------
        bool
            True if registered successfully
        """
        if name in self.vectors:
            # Update existing record
            record = self.vectors[name]
            record.vector = vector
            record.reference_count += 1
            record.last_access_time = time.time()
            if tags:
                record.tags.extend(tags)
            if metadata:
                record.metadata.update(metadata)
        else:
            # Create new record
            record = VectorRecord(
                name=name,
                vector=vector,
                is_persistent=is_persistent,
                tags=tags or [],
                metadata=metadata or {}
            )
            
            self.vectors[name] = record
            self.stats['vectors_created'] += 1
            
            # Add to groups based on tags
            for tag in record.tags:
                self.vector_groups[tag].append(name)
        
        # Update memory usage
        self._update_memory_stats()
        
        # Check for auto garbage collection
        if self.enable_auto_gc:
            self.operation_count += 1
            if (self.operation_count % self.config['gc_frequency'] == 0 or
                self._capacity_exceeded()):
                self._auto_garbage_collect()
        
        return True
    
    def get_vector(self, name: str) -> Optional[HRRVector]:
        """
        Retrieve a managed vector by name.
        
        Parameters
        ----------
        name : str
            Name of the vector
            
        Returns
        -------
        HRRVector or None
            The requested vector, or None if not found
        """
        if name not in self.vectors:
            return None
        
        record = self.vectors[name]
        record.access_count += 1
        record.last_access_time = time.time()
        
        self.stats['vectors_accessed'] += 1
        
        return record.vector
    
    def get_or_create_vector(self, 
                           name: str,
                           vector_data: Optional[np.ndarray] = None) -> HRRVector:
        """
        Get existing vector or create new one.
        
        Parameters
        ----------
        name : str
            Vector name
        vector_data : np.ndarray, optional
            Data for new vector if creation needed
            
        Returns
        -------
        HRRVector
            Existing or newly created vector
        """
        existing = self.get_vector(name)
        if existing is not None:
            return existing
        
        # Create new vector
        if vector_data is None:
            vector_data = np.random.randn(self.vector_dim)
            vector_data = vector_data / np.linalg.norm(vector_data)
        
        new_vector = HRRVector(data=vector_data, name=name)
        self.register_vector(name, new_vector)
        
        return new_vector
    
    def delete_vector(self, name: str) -> bool:
        """
        Delete a managed vector.
        
        Parameters
        ----------
        name : str
            Name of vector to delete
            
        Returns
        -------
        bool
            True if deleted successfully
        """
        if name not in self.vectors:
            return False
        
        record = self.vectors[name]
        
        # Remove from groups
        for tag in record.tags:
            if name in self.vector_groups[tag]:
                self.vector_groups[tag].remove(name)
        
        # Remove record
        del self.vectors[name]
        self.stats['vectors_deleted'] += 1
        
        # Update memory stats
        self._update_memory_stats()
        
        return True
    
    def list_vectors(self, 
                    tag_filter: Optional[str] = None,
                    include_metadata: bool = False) -> List[Union[str, Dict[str, Any]]]:
        """
        List managed vectors.
        
        Parameters
        ----------
        tag_filter : str, optional
            Only include vectors with this tag
        include_metadata : bool, default=False
            Include metadata in results
            
        Returns
        -------
        List[str] or List[Dict[str, Any]]
            List of vector names or detailed records
        """
        if tag_filter:
            vector_names = self.vector_groups.get(tag_filter, [])
            records = [self.vectors[name] for name in vector_names if name in self.vectors]
        else:
            records = list(self.vectors.values())
        
        if include_metadata:
            return [{
                'name': record.name,
                'creation_time': record.creation_time,
                'access_count': record.access_count,
                'last_access_time': record.last_access_time,
                'size_bytes': record.size_bytes,
                'is_persistent': record.is_persistent,
                'tags': record.tags,
                'metadata': record.metadata
            } for record in records]
        else:
            return [record.name for record in records]
    
    def garbage_collect(self, force: bool = False) -> Dict[str, Any]:
        """
        Perform garbage collection on managed vectors.
        
        Parameters
        ----------
        force : bool, default=False
            Force collection even if not needed
            
        Returns
        -------
        Dict[str, Any]
            Collection statistics
        """
        if not force and not self._should_garbage_collect():
            return {'collected': 0, 'reason': 'not needed'}
        
        collection_start = time.time()
        current_time = time.time()
        vectors_to_delete = []
        
        # Identify candidates for deletion
        for name, record in self.vectors.items():
            if record.is_persistent:
                continue
            
            # Check idle time
            idle_time = current_time - record.last_access_time
            if idle_time > self.config['max_idle_time']:
                vectors_to_delete.append(name)
                continue
            
            # Check access frequency
            if record.access_count < self.config['min_access_count']:
                vectors_to_delete.append(name)
                continue
        
        # Sort by priority (least recently used first)
        vectors_to_delete.sort(key=lambda name: self.vectors[name].last_access_time)
        
        # Delete vectors until under capacity
        deleted_count = 0
        memory_freed = 0
        
        target_capacity = int(self.capacity_threshold * 0.7)  # Clean to 70% capacity
        
        for name in vectors_to_delete:
            if len(self.vectors) <= target_capacity and not force:
                break
            
            record = self.vectors[name]
            memory_freed += record.size_bytes
            
            self.delete_vector(name)
            deleted_count += 1
        
        collection_time = time.time() - collection_start
        self.stats['gc_collections'] += 1
        
        return {
            'collected': deleted_count,
            'memory_freed_bytes': memory_freed,
            'collection_time': collection_time,
            'vectors_remaining': len(self.vectors)
        }
    
    def optimize_memory(self) -> Dict[str, Any]:
        """
        Optimize memory usage and organization.
        
        Returns
        -------
        Dict[str, Any]
            Optimization results
        """
        start_time = time.time()
        
        # Reorganize vector groups
        self.vector_groups.clear()
        for name, record in self.vectors.items():
            for tag in record.tags:
                self.vector_groups[tag].append(name)
        
        # Update memory statistics
        self._update_memory_stats()
        
        # Suggest optimizations
        suggestions = []
        
        if len(self.vectors) > self.capacity_threshold * 0.9:
            suggestions.append('Consider increasing capacity_threshold or enabling auto-GC')
        
        if self.stats['current_memory_usage'] > 1000:  # MB
            suggestions.append('High memory usage detected - consider garbage collection')
        
        unused_vectors = [name for name, record in self.vectors.items() 
                         if record.access_count == 0 and not record.is_persistent]
        
        if len(unused_vectors) > 10:
            suggestions.append(f'{len(unused_vectors)} unused vectors could be cleaned up')
        
        optimization_time = time.time() - start_time
        
        return {
            'optimization_time': optimization_time,
            'suggestions': suggestions,
            'unused_vectors': len(unused_vectors),
            'memory_usage_mb': self.stats['current_memory_usage'],
            'vector_groups': {tag: len(vectors) for tag, vectors in self.vector_groups.items()}
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory management statistics."""
        self._update_memory_stats()
        
        # Calculate derived statistics
        avg_vector_size = (self.stats['current_memory_usage'] * 1024 * 1024 / 
                          max(1, len(self.vectors)))
        
        capacity_utilization = len(self.vectors) / self.capacity_threshold
        
        # Access pattern analysis
        if self.vectors:
            access_counts = [record.access_count for record in self.vectors.values()]
            avg_access_count = np.mean(access_counts)
            access_std = np.std(access_counts)
        else:
            avg_access_count = 0
            access_std = 0
        
        # Age analysis
        current_time = time.time()
        if self.vectors:
            ages = [(current_time - record.creation_time) / 3600  # hours
                   for record in self.vectors.values()]
            avg_age_hours = np.mean(ages)
            oldest_vector_hours = max(ages)
        else:
            avg_age_hours = 0
            oldest_vector_hours = 0
        
        stats = self.stats.copy()
        stats.update({
            'num_vectors': len(self.vectors),
            'capacity_utilization': capacity_utilization,
            'avg_vector_size_bytes': avg_vector_size,
            'avg_access_count': avg_access_count,
            'access_count_std': access_std,
            'avg_age_hours': avg_age_hours,
            'oldest_vector_hours': oldest_vector_hours,
            'num_persistent_vectors': sum(1 for r in self.vectors.values() if r.is_persistent),
            'num_groups': len(self.vector_groups),
            'operation_count': self.operation_count
        })
        
        return stats
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state for serialization."""
        return {
            'vector_dim': self.vector_dim,
            'capacity_threshold': self.capacity_threshold,
            'gc_threshold': self.gc_threshold,
            'enable_auto_gc': self.enable_auto_gc,
            'vectors': {
                name: {
                    'vector_data': record.vector.data,
                    'vector_metadata': record.vector.metadata,
                    'creation_time': record.creation_time,
                    'access_count': record.access_count,
                    'last_access_time': record.last_access_time,
                    'reference_count': record.reference_count,
                    'is_persistent': record.is_persistent,
                    'tags': record.tags,
                    'metadata': record.metadata
                } for name, record in self.vectors.items()
            },
            'vector_groups': dict(self.vector_groups),
            'stats': self.stats,
            'config': self.config,
            'operation_count': self.operation_count
        }
    
    def load_state(self, state: Dict[str, Any]):
        """Load state from serialization."""
        self.vector_dim = state['vector_dim']
        self.capacity_threshold = state['capacity_threshold']
        self.gc_threshold = state['gc_threshold']
        self.enable_auto_gc = state['enable_auto_gc']
        
        # Restore vectors
        self.vectors = {}
        for name, vector_data in state['vectors'].items():
            vector = HRRVector(
                data=vector_data['vector_data'],
                name=name,
                metadata=vector_data['vector_metadata']
            )
            
            record = VectorRecord(
                name=name,
                vector=vector,
                creation_time=vector_data['creation_time'],
                access_count=vector_data['access_count'],
                last_access_time=vector_data['last_access_time'],
                reference_count=vector_data['reference_count'],
                is_persistent=vector_data['is_persistent'],
                tags=vector_data['tags'],
                metadata=vector_data['metadata']
            )
            
            self.vectors[name] = record
        
        # Restore other state
        self.vector_groups = defaultdict(list, state['vector_groups'])
        self.stats = state['stats']
        self.config = state['config']
        self.operation_count = state['operation_count']
        
        # Update memory statistics
        self._update_memory_stats()
    
    def clear(self):
        """Clear all managed vectors and reset statistics."""
        self.vectors.clear()
        self.vector_groups.clear()
        
        # Reset statistics but keep configuration
        for key in ['vectors_created', 'vectors_accessed', 'vectors_deleted', 
                   'gc_collections', 'total_memory_allocated', 'peak_memory_usage',
                   'current_memory_usage']:
            self.stats[key] = 0
        
        self.operation_count = 0
    
    def _update_memory_stats(self):
        """Update memory usage statistics."""
        current_usage = sum(record.size_bytes for record in self.vectors.values())
        current_usage_mb = current_usage / (1024 * 1024)
        
        self.stats['current_memory_usage'] = current_usage_mb
        
        if current_usage_mb > self.stats['peak_memory_usage']:
            self.stats['peak_memory_usage'] = current_usage_mb
    
    def _capacity_exceeded(self) -> bool:
        """Check if capacity threshold is exceeded."""
        return len(self.vectors) > self.capacity_threshold
    
    def _should_garbage_collect(self) -> bool:
        """Determine if garbage collection should run."""
        if len(self.vectors) > self.capacity_threshold * self.gc_threshold:
            return True
        
        memory_limit = self.config.get('memory_limit_mb')
        if memory_limit and self.stats['current_memory_usage'] > memory_limit:
            return True
        
        return False
    
    def _auto_garbage_collect(self):
        """Perform automatic garbage collection if needed."""
        if self._should_garbage_collect():
            try:
                result = self.garbage_collect()
                if result['collected'] > 0:
                    warnings.warn(f"Auto-GC collected {result['collected']} vectors")
            except Exception as e:
                warnings.warn(f"Auto-GC failed: {e}")
    
    def __repr__(self) -> str:
        return (f"MemoryManager(vectors={len(self.vectors)}, "
                f"capacity={self.capacity_threshold}, "
                f"memory={self.stats['current_memory_usage']:.1f}MB)")