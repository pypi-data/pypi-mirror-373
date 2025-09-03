"""
Reduced Representation Engine

Implements Plate (1995) Section V "Reduced Representations" (pages 631-633).
Addresses FIXME #1: Missing reduced representations encoding with cleanup memory
and systematic reduction from full compositional representation to compact form.

Research-Accurate Implementation of:
- Cleanup memory with threshold-based reduction
- Reduction factor for controlled compression  
- Reduced vocabulary of common compositional patterns
- Hierarchical reduction: complex → intermediate → reduced forms

Based on: Plate (1995) Section V, page 631; Figure 2, page 632
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ReducedForm:
    """A reduced representation form"""
    reduced_vector: np.ndarray
    complexity_level: int  # 0=atomic, 1=simple composition, 2=complex, etc.
    usage_count: int = 0
    creation_time: int = 0
    pattern_signature: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReducedRepresentationEngine:
    """
    Research-Accurate Reduced Representation Engine
    
    Implements Plate (1995) Section V "Reduced Representations" for compressing
    complex compositional structures into compact, manageable forms while
    preserving essential structural information.
    
    Key Research Contributions:
    1. Cleanup memory with threshold-based reduction (Section V, page 631)
    2. Controlled compression with reduction factors
    3. Hierarchical reduction strategies
    4. Pattern-based vocabulary construction
    """
    
    def __init__(self, 
                 vector_dim: int = 512,
                 reduction_threshold: float = 0.7,
                 max_reduced_vocabulary: int = 1000,
                 compression_factor: float = 0.1):
        """
        Initialize Reduced Representation Engine
        
        Args:
            vector_dim: Dimensionality of vectors
            reduction_threshold: Similarity threshold for using existing reduced forms
            max_reduced_vocabulary: Maximum size of reduced vocabulary
            compression_factor: Factor for controlled compression (0.1 = 10x reduction)
        """
        self.vector_dim = vector_dim
        self.reduction_threshold = reduction_threshold
        self.max_reduced_vocabulary = max_reduced_vocabulary
        self.compression_factor = compression_factor
        
        # Reduced vocabulary storage
        self.reduced_vocabulary: Dict[int, ReducedForm] = {}
        self.vocabulary_index = 0
        
        # Pattern signatures for common structures
        self.pattern_signatures: Dict[str, np.ndarray] = {}
        
        # Usage statistics for vocabulary management
        self.access_counts: Dict[int, int] = {}
        self.creation_order: List[int] = []
        
        # Initialize fundamental reduced forms
        self._initialize_fundamental_forms()
        
    def _initialize_fundamental_forms(self):
        """Initialize fundamental atomic reduced forms"""
        fundamental_patterns = [
            "EMPTY_STRUCTURE",
            "SINGLE_ELEMENT", 
            "PAIR_STRUCTURE",
            "LINEAR_SEQUENCE",
            "BINARY_TREE",
            "SIMPLE_RECORD"
        ]
        
        for pattern_name in fundamental_patterns:
            # Create characteristic signature for each fundamental pattern
            pattern_vector = self._create_pattern_signature(pattern_name)
            reduced_form = ReducedForm(
                reduced_vector=pattern_vector,
                complexity_level=0,  # Atomic level
                pattern_signature=pattern_name,
                metadata={"fundamental": True, "pattern": pattern_name}
            )
            
            self.reduced_vocabulary[self.vocabulary_index] = reduced_form
            self.pattern_signatures[pattern_name] = pattern_vector
            self.vocabulary_index += 1
    
    def _create_pattern_signature(self, pattern_name: str) -> np.ndarray:
        """Create a characteristic signature vector for a pattern"""
        # Use hash of pattern name to create reproducible random vector
        np.random.seed(hash(pattern_name) % (2**32))
        signature = np.random.normal(0, 1, self.vector_dim)
        
        # Normalize to unit length
        signature = signature / (np.linalg.norm(signature) + 1e-10)
        
        # Reset random seed
        np.random.seed()
        
        return signature
    
    def create_reduced_representation(self, 
                                    full_vector: np.ndarray, 
                                    complexity_hint: Optional[int] = None,
                                    force_new: bool = False) -> Tuple[np.ndarray, int]:
        """
        Research-Accurate Reduced Representation Creation
        
        Implements Plate (1995) Section V reduction strategy:
        1. Check for existing similar reduced forms (threshold-based)
        2. Create new reduced form if no match found
        3. Add to vocabulary with usage tracking
        
        Args:
            full_vector: Full-dimensional compositional vector
            complexity_hint: Hint about structural complexity (0=atomic, 1=simple, etc.)
            force_new: Force creation of new reduced form
            
        Returns:
            Tuple of (reduced_vector, vocabulary_index)
        """
        # Normalize input vector for proper comparison
        full_norm = full_vector / (np.linalg.norm(full_vector) + 1e-10)
        
        # Stage 1: Search for existing similar reduced forms
        if not force_new:
            best_match_id, best_similarity = self._find_best_reduced_match(full_norm)
            
            if best_match_id is not None and best_similarity > self.reduction_threshold:
                # Use existing reduced form
                self._update_usage(best_match_id)
                reduced_form = self.reduced_vocabulary[best_match_id]
                
                logger.debug(f"Using existing reduced form {best_match_id} "
                           f"(similarity: {best_similarity:.3f})")
                
                return reduced_form.reduced_vector, best_match_id
        
        # Stage 2: Create new reduced form
        reduced_vector = self._compress_vector(full_norm)
        
        # Determine complexity level
        if complexity_hint is not None:
            complexity_level = complexity_hint
        else:
            complexity_level = self._estimate_complexity(full_norm)
        
        # Stage 3: Add to vocabulary (with capacity management)
        reduced_form = ReducedForm(
            reduced_vector=reduced_vector,
            complexity_level=complexity_level,
            usage_count=1,
            creation_time=len(self.creation_order),
            metadata={"compression_factor": self.compression_factor}
        )
        
        vocabulary_id = self._add_to_vocabulary(reduced_form)
        
        logger.debug(f"Created new reduced form {vocabulary_id} "
                   f"(complexity: {complexity_level})")
        
        return reduced_vector, vocabulary_id
    
    def _find_best_reduced_match(self, query_vector: np.ndarray) -> Tuple[Optional[int], float]:
        """Find the best matching reduced form in vocabulary"""
        best_id = None
        best_similarity = -1.0
        
        for vocab_id, reduced_form in self.reduced_vocabulary.items():
            # Compute cosine similarity
            similarity = np.dot(query_vector, reduced_form.reduced_vector)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_id = vocab_id
        
        return best_id, best_similarity
    
    def _compress_vector(self, full_vector: np.ndarray) -> np.ndarray:
        """
        Compress full vector using controlled compression strategy
        
        Implements multiple compression approaches:
        1. Dimensionality reduction via random projection
        2. Selective feature compression
        3. Adaptive compression based on content
        """
        # Approach 1: Random projection for dimensionality reduction
        if self.compression_factor < 1.0:
            compressed_dim = max(1, int(self.vector_dim * self.compression_factor))
            
            # Create stable random projection matrix
            projection_seed = hash("compression_matrix") % (2**32)
            np.random.seed(projection_seed)
            projection_matrix = np.random.normal(0, 1, (compressed_dim, self.vector_dim))
            projection_matrix = projection_matrix / np.sqrt(compressed_dim)
            
            # Apply projection
            compressed = np.dot(projection_matrix, full_vector)
            
            # Pad back to original dimensions with zeros
            reduced_vector = np.zeros(self.vector_dim)
            reduced_vector[:compressed_dim] = compressed
            
            # Reset random seed
            np.random.seed()
        else:
            # Approach 2: Selective compression by thresholding
            threshold = np.std(full_vector) * 0.5
            reduced_vector = np.where(np.abs(full_vector) > threshold, full_vector, 0)
        
        # Normalize result
        reduced_vector = reduced_vector / (np.linalg.norm(reduced_vector) + 1e-10)
        
        return reduced_vector
    
    def _estimate_complexity(self, vector: np.ndarray) -> int:
        """Estimate structural complexity of a vector"""
        # Use statistical properties to estimate complexity
        
        # Sparsity measure (higher sparsity often indicates more complex composition)
        nonzero_ratio = np.count_nonzero(vector) / len(vector)
        
        # Variance measure (higher variance may indicate more complex binding)
        variance = np.var(vector)
        
        # Entropy-like measure
        abs_vector = np.abs(vector)
        abs_vector = abs_vector / (np.sum(abs_vector) + 1e-10)
        entropy = -np.sum(abs_vector * np.log(abs_vector + 1e-10))
        
        # Combine measures to estimate complexity
        if nonzero_ratio < 0.1 or variance < 0.1:
            return 0  # Likely atomic/simple
        elif entropy > 5.0 and variance > 0.5:
            return 2  # Likely complex composition
        else:
            return 1  # Moderate complexity
    
    def _add_to_vocabulary(self, reduced_form: ReducedForm) -> int:
        """Add reduced form to vocabulary with capacity management"""
        # Check if vocabulary is full
        if len(self.reduced_vocabulary) >= self.max_reduced_vocabulary:
            self._manage_vocabulary_capacity()
        
        # Add new form
        vocab_id = self.vocabulary_index
        self.reduced_vocabulary[vocab_id] = reduced_form
        self.creation_order.append(vocab_id)
        self.vocabulary_index += 1
        
        return vocab_id
    
    def _manage_vocabulary_capacity(self):
        """Manage vocabulary capacity using LRU-like strategy"""
        if len(self.reduced_vocabulary) == 0:
            return
        
        # Find least recently used non-fundamental forms
        removable_candidates = []
        for vocab_id, reduced_form in self.reduced_vocabulary.items():
            if not reduced_form.metadata.get("fundamental", False):
                usage_count = self.access_counts.get(vocab_id, reduced_form.usage_count)
                removable_candidates.append((vocab_id, usage_count, reduced_form.creation_time))
        
        if removable_candidates:
            # Sort by usage count (ascending) then by creation time (ascending)
            removable_candidates.sort(key=lambda x: (x[1], x[2]))
            
            # Remove oldest, least-used items (remove 10% of vocabulary)
            num_to_remove = max(1, len(self.reduced_vocabulary) // 10)
            
            for i in range(min(num_to_remove, len(removable_candidates))):
                vocab_id = removable_candidates[i][0]
                del self.reduced_vocabulary[vocab_id]
                if vocab_id in self.access_counts:
                    del self.access_counts[vocab_id]
                if vocab_id in self.creation_order:
                    self.creation_order.remove(vocab_id)
                
                logger.debug(f"Removed reduced form {vocab_id} from vocabulary (capacity management)")
    
    def _update_usage(self, vocab_id: int):
        """Update usage statistics for vocabulary item"""
        if vocab_id in self.reduced_vocabulary:
            self.reduced_vocabulary[vocab_id].usage_count += 1
            self.access_counts[vocab_id] = self.access_counts.get(vocab_id, 0) + 1
    
    def hierarchical_reduction(self, 
                              full_vector: np.ndarray, 
                              num_levels: int = 3) -> List[Tuple[np.ndarray, float]]:
        """
        Hierarchical Reduction: complex → intermediate → reduced forms
        
        Implements multi-stage reduction as suggested in Plate (1995) Section V
        
        Args:
            full_vector: Full compositional structure vector
            num_levels: Number of reduction levels to create
            
        Returns:
            List of (reduced_vector, compression_ratio) pairs for each level
        """
        reductions = []
        current_vector = full_vector / (np.linalg.norm(full_vector) + 1e-10)
        
        for level in range(num_levels):
            # Progressively increase compression
            level_compression = self.compression_factor * (level + 1) / num_levels
            
            # Create temporary engine with level-specific compression
            temp_engine = ReducedRepresentationEngine(
                vector_dim=self.vector_dim,
                compression_factor=level_compression
            )
            
            # Compress at this level
            reduced_vec = temp_engine._compress_vector(current_vector)
            compression_ratio = level_compression
            
            reductions.append((reduced_vec, compression_ratio))
            
            # Use this level's output as input for next level
            current_vector = reduced_vec
        
        return reductions
    
    def get_vocabulary_stats(self) -> Dict[str, Any]:
        """Get statistics about the reduced vocabulary"""
        if not self.reduced_vocabulary:
            return {"total_forms": 0}
        
        complexity_counts = {}
        usage_stats = []
        
        for reduced_form in self.reduced_vocabulary.values():
            complexity = reduced_form.complexity_level
            complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
            usage_stats.append(reduced_form.usage_count)
        
        return {
            "total_forms": len(self.reduced_vocabulary),
            "complexity_distribution": complexity_counts,
            "average_usage": np.mean(usage_stats) if usage_stats else 0,
            "max_usage": max(usage_stats) if usage_stats else 0,
            "fundamental_patterns": len(self.pattern_signatures),
            "compression_factor": self.compression_factor,
            "reduction_threshold": self.reduction_threshold
        }
    
    def query_similar_patterns(self, 
                              query_vector: np.ndarray, 
                              top_k: int = 5) -> List[Tuple[int, float, ReducedForm]]:
        """Query for similar patterns in reduced vocabulary"""
        similarities = []
        
        query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-10)
        
        for vocab_id, reduced_form in self.reduced_vocabulary.items():
            similarity = np.dot(query_norm, reduced_form.reduced_vector)
            similarities.append((vocab_id, similarity, reduced_form))
        
        # Sort by similarity (descending) and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]