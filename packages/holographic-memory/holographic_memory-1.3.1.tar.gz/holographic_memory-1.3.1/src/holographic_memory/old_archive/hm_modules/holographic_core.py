"""
Holographic Core Module - Main Integration Class

Integrates all modular components of the Holographic Memory System
while preserving the original API for backward compatibility.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
import time
from typing import Dict, Any, List, Optional, Union, Tuple

from .configuration import HRRConfig, HRRMemoryItem, create_config
from .vector_operations import VectorOperations
from .memory_management import MemoryManager
from .composite_operations import CompositeOperations
from .cleanup_operations import CleanupOperations
from .capacity_analysis import CapacityAnalyzer


class HolographicMemoryCore:
    """
    🌀 Modular Holographic Memory System - Core Integration Class
    
    Integrates all modular components while maintaining backward compatibility
    with the original HolographicMemory API.
    """
    
    def __init__(
        self,
        config: Optional[HRRConfig] = None,
        # Direct parameters (for backward compatibility)
        vector_dim: int = None,
        normalize: bool = None,
        noise_level: float = None,
        random_seed: Optional[int] = None,
        cleanup_memory: bool = None,
        capacity_threshold: Optional[int] = None,
        similarity_preservation: bool = None,
        unitary_vectors: bool = None,
        trace_composition: str = None,
        **kwargs
    ):
        """Initialize modular Holographic Memory System"""
        
        # Handle configuration
        if config is None:
            config = HRRConfig()
            
        # Override config with direct parameters if provided
        if vector_dim is not None:
            config.vector_dim = vector_dim
        if normalize is not None:
            config.normalize = normalize
        if noise_level is not None:
            config.noise_level = noise_level
        if random_seed is not None:
            config.random_seed = random_seed
        if cleanup_memory is not None:
            config.cleanup_memory = cleanup_memory
        if capacity_threshold is not None:
            config.capacity_threshold = capacity_threshold
        if similarity_preservation is not None:
            config.similarity_preservation = similarity_preservation
        if unitary_vectors is not None:
            config.unitary_vectors = unitary_vectors
        if trace_composition is not None:
            config.trace_composition = trace_composition
            
        # Apply additional kwargs
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            
        self.config = config
        
        # Initialize modular components
        self.vector_ops = VectorOperations(config)
        self.memory_manager = MemoryManager(config, self.vector_ops)
        self.composite_ops = CompositeOperations(config, self.vector_ops, self.memory_manager)
        self.cleanup_ops = CleanupOperations(config, self.vector_ops, self.memory_manager)
        self.capacity_analyzer = CapacityAnalyzer(config, self.vector_ops, 
                                                 self.memory_manager, self.cleanup_ops)
        
        print(f"🌀 Modular Holographic Memory System initialized")
        print(f"   Vector dimension: {config.vector_dim}")
        print(f"   Components: VectorOps, MemoryManager, CompositeOps, CleanupOps, CapacityAnalyzer")
        print(f"   Vector normalization: {'ON' if config.normalize else 'OFF'}")
        print(f"   Cleanup memory: {'ON' if config.cleanup_memory else 'OFF'}")
        print(f"   Theoretical capacity: {self.capacity_analyzer.theoretical_capacity():.1f} items")
    
    # ==================== CORE API METHODS ====================
    
    def create_vector(self, name: str, vector: Optional[np.ndarray] = None, 
                     metadata: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """Create and store a new HRR vector"""
        return self.memory_manager.create_vector(name, vector, metadata)
    
    def bind(self, vec_a: Union[str, np.ndarray], vec_b: Union[str, np.ndarray]) -> np.ndarray:
        """Circular convolution binding operation (⊗)
        
        # FIXME: Critical Issues in bind() Method - Core HRR Operation
        #
        # 1. MISSING CIRCULAR CONVOLUTION VALIDATION
        #    - No validation that vectors are suitable for circular convolution
        #    - Missing checks for vector length compatibility
        #    - Should validate that vectors are normalized if required
        #    - Solutions:
        #      a) Add vector validation: self._validate_hrr_vectors(a, b)
        #      b) Check dimension compatibility before FFT operations
        #      c) Add automatic normalization option for binding
        #    - Research note: Plate (1995) emphasized proper normalization for HRR
        #    - Example:
        #      ```python
        #      if len(a) != len(b):
        #          raise ValueError("HRR binding requires same-dimension vectors")
        #      if self.config.validate_binding and (np.linalg.norm(a) < 0.9 or np.linalg.norm(a) > 1.1):
        #          warnings.warn("Vector may not be properly normalized for HRR binding")
        #      ```
        #
        # 2. NO BINDING HISTORY OR PROVENANCE TRACKING
        #    - HRR binding creates complex compositions that are hard to debug
        #    - Missing tracking of what was bound with what
        #    - Should maintain binding history for analysis and unbinding
        #    - Solutions:
        #      a) Add binding record: self._record_binding(vec_a, vec_b, result)
        #      b) Store reverse lookup: bound_vector -> (component_a, component_b)
        #      c) Implement binding tree visualization
        #    - Critical for complex cognitive architectures using nested bindings
        #
        # 3. MISSING CAPACITY-AWARE BINDING
        #    - No consideration of memory capacity limits
        #    - Binding can degrade with too many superposed elements
        #    - Should warn when approaching capacity limits
        #    - Solutions:
        #      a) Check current memory load before binding
        #      b) Add capacity warnings: if load > threshold: warn_capacity()
        #      c) Implement graceful degradation strategies
        #    - Research basis: HRR has finite capacity that affects binding quality
        #
        # 4. NO ALTERNATIVE BINDING OPERATORS
        #    - Only supports circular convolution, missing other HRR variants
        #    - Should support alternative binding: XOR, multiplication, etc.
        #    - Missing support for structured binding (e.g., position-sensitive)
        #    - Solutions:
        #      a) Add binding_type parameter: bind(a, b, method='circular_conv')
        #      b) Support: 'circular_conv', 'xor', 'multiplication', 'permutation'
        #      c) Implement hybrid binding for different data types
        #    - Modern HRR research uses multiple binding operators
        """
        a = self._get_vector(vec_a)
        b = self._get_vector(vec_b)
        return self.vector_ops.bind(a, b)
    
    def unbind(self, bound_vec: np.ndarray, cue_vec: Union[str, np.ndarray]) -> np.ndarray:
        """Circular correlation unbinding operation (⊘)"""
        cue = self._get_vector(cue_vec)
        return self.vector_ops.unbind(bound_vec, cue)
    
    def superpose(self, vectors: List[Union[str, np.ndarray]], 
                 normalize: bool = True) -> np.ndarray:
        """Create superposition of multiple vectors (+)"""
        vector_arrays = []
        for vec in vectors:
            vector_arrays.append(self._get_vector(vec))
        return self.vector_ops.superpose(vector_arrays, normalize)
    
    def similarity(self, vec1: Union[str, np.ndarray], vec2: Union[str, np.ndarray]) -> float:
        """Calculate similarity between vectors"""
        a = self._get_vector(vec1)
        b = self._get_vector(vec2)
        return self.vector_ops.similarity(a, b)
    
    def _get_vector(self, vec: Union[str, np.ndarray]) -> np.ndarray:
        """Convert string name to vector or return vector as-is"""
        if isinstance(vec, str):
            return self.memory_manager.get_vector(vec)
        return vec
    
    def get_vector(self, name: str) -> np.ndarray:
        """Get vector by name (convenience method)"""
        return self.memory_manager.get_vector(name)
    
    # ==================== SIMPLE STORAGE API ====================
    
    def store(self, key: str, value: Union[str, np.ndarray]) -> None:
        """Store a key-value pair in holographic memory (simplified API)"""
        self.memory_manager.store_association(key, value)
    
    def retrieve(self, key: str) -> Optional[np.ndarray]:
        """Retrieve value associated with key (simplified API)"""
        return self.memory_manager.retrieve_association(key)
    
    # ==================== COMPOSITE MEMORY OPERATIONS ====================
    
    def create_hierarchy(self, structure: Dict, name: str) -> np.ndarray:
        """Create hierarchical structure using nested binding and superposition"""
        return self.composite_ops.create_hierarchy(structure, name)
    
    def create_sequence(self, items: List[str], sequence_name: str, 
                       encoding: str = None) -> np.ndarray:
        """Create sequence representation using positional encoding"""
        return self.composite_ops.create_sequence(items, sequence_name, encoding)
    
    def query_memory(self, memory_name: str, cue_role: str) -> Tuple[np.ndarray, str, float]:
        """Query composite memory with a role to retrieve filler"""
        retrieved, confidence = self.composite_ops.query_memory(memory_name, cue_role)
        
        # Cleanup retrieved vector
        candidates = list(self.memory_manager.memory_items.keys())
        best_match, cleanup_confidence = self.cleanup_ops.cleanup_memory(retrieved, candidates)
        
        # Use the higher confidence score
        final_confidence = max(confidence, cleanup_confidence)
        
        return retrieved, best_match, final_confidence
    
    def create_frame(self, attributes: Dict[str, Union[str, List[str]]], frame_name: str) -> np.ndarray:
        """Create frame representation"""
        return self.composite_ops.create_frame(attributes, frame_name)
    
    def blend_memories(self, memory_names: List[str], weights: Optional[List[float]] = None,
                      blend_name: str = None) -> np.ndarray:
        """Create weighted blend of multiple memories"""
        return self.composite_ops.blend_memories(memory_names, weights, blend_name)
    
    # ==================== CLEANUP AND ERROR CORRECTION ====================
    
    def cleanup_memory(self, noisy_vector: np.ndarray, 
                      candidates: Optional[List[str]] = None,
                      threshold: float = 0.1) -> Tuple[str, float]:
        """Clean up noisy vector by finding best match among stored vectors"""
        return self.cleanup_ops.cleanup_memory(noisy_vector, candidates, threshold)
    
    def create_cleanup_memory(self, item_names: List[str]):
        """Create auto-associative cleanup memory (Hopfield-style)"""
        return self.cleanup_ops.create_cleanup_memory(item_names)
    
    def hopfield_cleanup(self, noisy_vector: np.ndarray, max_iterations: int = 10) -> np.ndarray:
        """Use Hopfield network for cleanup"""
        return self.cleanup_ops.hopfield_cleanup(noisy_vector, max_iterations)
    
    # ==================== CAPACITY ANALYSIS ====================
    
    def analyze_capacity(self, n_test_items: int = 100, 
                        noise_levels: List[float] = None) -> Dict[str, Any]:
        """Analyze memory capacity following Plate (1995) methodology"""
        return self.capacity_analyzer.analyze_capacity(n_test_items, noise_levels)
    
    def run_plate_benchmarks(self, verbose: bool = True) -> Dict[str, Any]:
        """Run standard benchmarks from Plate (1995)"""
        return self.capacity_analyzer.run_plate_benchmarks(verbose)
    
    def benchmark_operations(self, n_trials: int = 1000) -> Dict[str, Any]:
        """Benchmark basic operation performance"""
        return self.capacity_analyzer.benchmark_operations(n_trials)
    
    def stress_test(self, max_items: int = None) -> Dict[str, Any]:
        """Stress test the memory system with increasing load"""
        return self.capacity_analyzer.stress_test(max_items)
    
    # ==================== ADVANCED FEATURES ====================
    
    def create_analogies(self, a: str, b: str, c: str) -> Tuple[np.ndarray, str, float]:
        """Create analogical reasoning: a:b :: c:?"""
        vec_a = self._get_vector(a)
        vec_b = self._get_vector(b)
        vec_c = self._get_vector(c)
        
        # Compute analogy using vector operations
        result = self.vector_ops.create_analogy_vector(vec_a, vec_b, vec_c)
        
        # Cleanup result
        candidates = list(self.memory_manager.memory_items.keys())
        best_match, confidence = self.cleanup_ops.cleanup_memory(result, candidates)
        
        return result, best_match, confidence
    
    def measure_representational_similarity(self, groups: Dict[str, List[str]]) -> np.ndarray:
        """Measure representational similarity matrix between groups of items"""
        all_items = []
        group_labels = []
        
        for group_name, items in groups.items():
            for item in items:
                if not self.memory_manager.has_vector(item):
                    self.memory_manager.create_vector(item)
                all_items.append(item)
                group_labels.append(group_name)
        
        # Create similarity matrix
        n_items = len(all_items)
        similarity_matrix = np.zeros((n_items, n_items))
        
        for i in range(n_items):
            for j in range(n_items):
                similarity_matrix[i, j] = self.similarity(all_items[i], all_items[j])
        
        return similarity_matrix
    
    def visualize_memory(self, memory_names: List[str], 
                        figsize: Tuple[int, int] = (12, 8)):
        """Visualize memory vectors using dimensionality reduction"""
        print("🌀 Memory Space Visualization:")
        print(f"   Total vectors: {len(self.memory_manager.memory_items)}")
        print(f"   Vector dimension: {self.config.vector_dim}")
        print(f"   Composite memories: {len(self.memory_manager.composite_memories)}")
        
        # Show similarity matrix for requested items (if small enough)
        if len(memory_names) <= 10:
            print(f"\n   Similarity Matrix for {memory_names}:")
            for i, name1 in enumerate(memory_names):
                row = []
                for name2 in memory_names:
                    if (self.memory_manager.has_vector(name1) and 
                        self.memory_manager.has_vector(name2)):
                        sim = self.similarity(name1, name2)
                        row.append(f"{sim:5.2f}")
                    else:
                        row.append("  ---")
                print(f"   {name1:10} {' '.join(row)}")
    
    # ==================== UTILITY METHODS ====================
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        base_stats = self.memory_manager.get_memory_stats()
        cleanup_stats = self.cleanup_ops.get_cleanup_stats()
        
        stats = {
            **base_stats,
            'theoretical_capacity': self.capacity_analyzer.theoretical_capacity(),
            'cleanup_stats': cleanup_stats,
            'configuration': self.config.__dict__,
            'modular_architecture': {
                'vector_operations': 'VectorOperations',
                'memory_management': 'MemoryManager', 
                'composite_operations': 'CompositeOperations',
                'cleanup_operations': 'CleanupOperations',
                'capacity_analysis': 'CapacityAnalyzer'
            }
        }
        
        return stats
    
    def save_memory(self, filename: str):
        """Save memory state to file"""
        self.memory_manager.save_memory(filename)
    
    def load_memory(self, filename: str):
        """Load memory state from file"""
        self.memory_manager.load_memory(filename)
    
    # ==================== BACKWARD COMPATIBILITY ====================
    
    def create_composite_memory(self, bindings: List[Tuple[str, str]], memory_name: str) -> np.ndarray:
        """Backward compatibility method"""
        return self.composite_ops.create_composite_memory(bindings, memory_name)
    
    def query_sequence_position(self, sequence_name: str, position: int) -> Tuple[np.ndarray, str, float]:
        """Backward compatibility method"""
        retrieved, confidence = self.composite_ops.query_sequence_position(sequence_name, position)
        
        # Cleanup retrieved vector
        candidates = list(self.memory_manager.memory_items.keys())
        best_match, cleanup_confidence = self.cleanup_ops.cleanup_memory(retrieved, candidates)
        
        # Use the higher confidence score
        final_confidence = max(confidence, cleanup_confidence)
        
        return retrieved, best_match, final_confidence
    
    # ==================== COMPONENT ACCESS ====================
    
    @property
    def memory_items(self) -> Dict[str, 'HRRMemoryItem']:
        """Access to memory items (for backward compatibility)"""
        return self.memory_manager.memory_items
    
    @property
    def composite_memories(self) -> Dict[str, np.ndarray]:
        """Access to composite memories (for backward compatibility)"""
        return self.memory_manager.composite_memories
    
    @property
    def cleanup_items(self) -> Dict[str, Any]:
        """Access to cleanup items (for backward compatibility)"""
        return self.cleanup_ops.cleanup_items
    
    # ==================== DEMO AND TESTING ====================
    
    def run_self_test(self) -> Dict[str, Any]:
        """Run comprehensive self-test of all modular components"""
        print("🧪 Running Modular System Self-Test")
        print("=" * 40)
        
        results = {}
        
        # Test 1: Basic vector operations
        try:
            print("\n1. Testing Vector Operations...")
            vec1 = self.create_vector("test_vec1")
            vec2 = self.create_vector("test_vec2")
            bound = self.bind(vec1, vec2)
            unbound = self.unbind(bound, vec1)
            sim = self.similarity(unbound, vec2)
            
            results['vector_operations'] = {
                'success': sim > 0.3,
                'binding_similarity': float(sim)
            }
            print(f"   ✓ Binding/unbinding similarity: {sim:.3f}")
            
        except Exception as e:
            results['vector_operations'] = {'error': str(e)}
            print(f"   ✗ Failed: {e}")
        
        # Test 2: Memory management
        try:
            print("\n2. Testing Memory Management...")
            self.store("key1", "value1")
            retrieved = self.retrieve("key1")
            
            results['memory_management'] = {
                'success': retrieved is not None,
                'storage_retrieval': retrieved is not None
            }
            print(f"   ✓ Storage and retrieval working")
            
        except Exception as e:
            results['memory_management'] = {'error': str(e)}
            print(f"   ✗ Failed: {e}")
        
        # Test 3: Composite operations
        try:
            print("\n3. Testing Composite Operations...")
            structure = {'color': ['red', 'blue'], 'shape': ['round']}
            hierarchy = self.create_hierarchy(structure, "test_hierarchy")
            retrieved, match, conf = self.query_memory("test_hierarchy", "color")
            
            results['composite_operations'] = {
                'success': conf > 0.1,
                'hierarchy_confidence': float(conf)
            }
            print(f"   ✓ Hierarchy creation and query: {conf:.3f}")
            
        except Exception as e:
            results['composite_operations'] = {'error': str(e)}
            print(f"   ✗ Failed: {e}")
        
        # Test 4: Cleanup operations
        try:
            print("\n4. Testing Cleanup Operations...")
            noisy_vec = vec1 + np.random.normal(0, 0.1, len(vec1))
            cleaned_name, conf = self.cleanup_memory(noisy_vec)
            
            results['cleanup_operations'] = {
                'success': conf > 0.1,
                'cleanup_confidence': float(conf)
            }
            print(f"   ✓ Cleanup operation: {conf:.3f}")
            
        except Exception as e:
            results['cleanup_operations'] = {'error': str(e)}
            print(f"   ✗ Failed: {e}")
        
        # Test 5: Capacity analysis (quick test)
        try:
            print("\n5. Testing Capacity Analysis...")
            theoretical = self.capacity_analyzer.theoretical_capacity()
            
            results['capacity_analysis'] = {
                'success': theoretical > 0,
                'theoretical_capacity': float(theoretical)
            }
            print(f"   ✓ Theoretical capacity: {theoretical:.1f}")
            
        except Exception as e:
            results['capacity_analysis'] = {'error': str(e)}
            print(f"   ✗ Failed: {e}")
        
        # Calculate overall success
        successful_tests = sum(1 for test_result in results.values() 
                             if isinstance(test_result, dict) and test_result.get('success', False))
        total_tests = len(results)
        
        results['overall'] = {
            'successful_tests': successful_tests,
            'total_tests': total_tests,
            'success_rate': successful_tests / total_tests if total_tests > 0 else 0.0
        }
        
        print(f"\n✅ Self-test complete: {successful_tests}/{total_tests} components passed")
        print(f"   Success rate: {results['overall']['success_rate']:.1%}")
        
        return results


# ==================== FACTORY FUNCTIONS ====================

def create_holographic_memory(memory_type: str = "standard", **kwargs) -> HolographicMemoryCore:
    """
    Factory function to create different types of holographic memory systems
    
    Parameters:
    -----------
    memory_type : str
        Type of memory: "standard", "high_capacity", "fast", or "research"
    **kwargs : additional arguments for memory initialization
    
    Returns:
    --------
    memory : HolographicMemoryCore
        Configured holographic memory system
    """
    config = create_config(memory_type, **kwargs)
    return HolographicMemoryCore(config)


# Backward compatibility alias
HolographicMemory = HolographicMemoryCore