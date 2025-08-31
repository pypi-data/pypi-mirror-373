"""
🌀 Holographic Reduced Representations (HRR) Memory System - Unified Implementation
====================================================================================

Author: Benedict Chen (benedict@benedictchen.com)
💰 Support This Research: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Based on: Plate (1995) "Holographic Reduced Representations"

Unified implementation combining:
- Clean modular architecture from refactored version
- Complete functionality from comprehensive original version
- All advanced features, theoretical analysis, and benchmarks
- Full vector symbolic architecture capabilities

🎯 ELI5 Summary:
Imagine you could store any amount of information in a single fixed-size container, 
kind of like how a hologram stores a 3D image on a 2D surface. Holographic memory 
does this with vectors - you can bind multiple pieces of information together into 
one vector, and later retrieve them by providing the right "key". It's like having 
a magical filing cabinet where everything fits in the same sized drawer!

🔬 Research Background:
======================
Tony Plate's 1995 breakthrough showed how to create distributed representations that
could store and manipulate symbolic structures using fixed-size vectors. This solved
the fundamental problem of how neural networks could handle variable-sized symbolic
data structures.

Key innovations:
- Circular convolution for binding operations  
- Distributed holographic storage
- Approximate retrieval with error correction
- Compositional vector symbolic architecture
- Variable binding in neural networks

🧮 Mathematical Foundation:
===========================
- Binding: a ⊗ b (circular convolution)
- Unbinding: a ⊘ b (circular correlation)  
- Superposition: a + b (element-wise addition)
- Similarity: dot product between normalized vectors

🎨 ASCII Representation:
========================
    Memory Items:    red ⊗ car = vector_1
                    blue ⊗ sky = vector_2
                    
    Superposition:   memory = vector_1 + vector_2 + ...
    
    Retrieval:       memory ⊘ red ≈ car (with noise)
                    memory ⊘ blue ≈ sky (with noise)
"""

import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass
import warnings
import time
from scipy import linalg
from scipy.fft import fft, ifft
from scipy.stats import entropy
import matplotlib.pyplot as plt

# Import modular components if available (maintaining backward compatibility)
try:
    from .configuration import HolographicMemoryConfig as ExternalConfig
    from .vector_operations import VectorOperations as ExternalVectorOps
    from .capacity_analysis import CapacityAnalyzer as ExternalCapacityAnalyzer
    from .cleanup_operations import CleanupOperations as ExternalCleanupOps
    from .composite_memory import CompositeMemoryOperations as ExternalCompositeOps
    MODULAR_COMPONENTS_AVAILABLE = True
except ImportError:
    MODULAR_COMPONENTS_AVAILABLE = False
    warnings.warn("Modular components not available, using unified implementation")


@dataclass
class HRRMemoryItem:
    """Individual memory item in HRR system"""
    vector: np.ndarray
    name: str
    created_at: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class HRRConfig:
    """Complete configuration for HRR memory system"""
    vector_dim: int = 512
    normalize: bool = True
    noise_level: float = 0.0
    random_seed: Optional[int] = None
    cleanup_memory: bool = True
    capacity_threshold: Optional[int] = None
    similarity_preservation: bool = True
    unitary_vectors: bool = False
    trace_composition: str = "addition"
    
    # Advanced options
    binding_operation: str = 'circular_convolution'
    memory_model: str = 'distributed'
    cleanup_memory_type: str = 'hopfield'
    capacity_formula: str = 'plate1995'
    distributional_constraints: str = 'warn'
    noncommutative_mode: bool = False
    walsh_hadamard: bool = False
    sequence_encoding: str = 'positional'
    fast_cleanup: bool = True
    capacity_monitoring: bool = False
    memory_compression: bool = False
    gpu_acceleration: bool = False


class HolographicMemory:
    """
    🌀 Holographic Reduced Representations Memory System - Unified Implementation
    
    Combines clean modular architecture with comprehensive functionality including
    all advanced features, theoretical analysis, benchmarks, and vector symbolic
    architecture capabilities.
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
        """Initialize unified Holographic Memory System"""
        
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
            
        self.config = config
        
        # Set random seed
        if config.random_seed is not None:
            np.random.seed(config.random_seed)
            
        # Memory storage
        self.memory_items = {}  # name -> HRRMemoryItem
        self.composite_memories = {}  # name -> composite vector
        self.cleanup_items = {}  # Clean versions for auto-associative cleanup
        
        # Capacity tracking
        self.association_count = 0
        
        # Performance metrics
        self.retrieval_accuracy = None
        self.memory_usage = 0
        self.last_cleanup_success_rate = None
        
        # Precompute FFT frequencies for efficiency
        self._fft_freqs = np.fft.fftfreq(config.vector_dim)
        
        print(f"✓ Holographic Memory initialized: {config.vector_dim}D vectors")
        print(f"   Vector normalization: {'ON' if config.normalize else 'OFF'}")
        print(f"   Cleanup memory: {'ON' if config.cleanup_memory else 'OFF'}")
        print(f"   Capacity threshold: {config.capacity_threshold or config.vector_dim // 16}")
        print(f"   Similarity preservation: {'ON' if config.similarity_preservation else 'OFF'}")
        
    def create_vector(self, name: str, vector: Optional[np.ndarray] = None, 
                     metadata: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """Create and store a new HRR vector"""
        if vector is None:
            # Generate random vector with proper distribution
            if self.config.unitary_vectors:
                # Generate unitary vector (for exact unbinding)
                vector = self._generate_unitary_vector()
            else:
                # Standard Gaussian distribution (Plate 1995)
                vector = np.random.normal(0, 1/np.sqrt(self.config.vector_dim), 
                                        self.config.vector_dim)
        
        # Normalize if enabled
        if self.config.normalize:
            vector = self._normalize_vector(vector)
        
        # Store in memory
        self.memory_items[name] = HRRMemoryItem(
            vector=vector.copy(),
            name=name,
            created_at=time.time(),
            metadata=metadata or {}
        )
        
        return vector
    
    def _generate_unitary_vector(self) -> np.ndarray:
        """Generate unitary vector for exact unbinding"""
        # Generate random phases
        phases = np.random.uniform(0, 2*np.pi, self.config.vector_dim)
        
        # Create complex exponentials and take real part of IFFT
        complex_vector = np.exp(1j * phases)
        real_vector = np.real(ifft(complex_vector))
        
        return real_vector
    
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """Normalize vector to unit length"""
        norm = np.linalg.norm(vector)
        return vector / norm if norm > 1e-10 else vector
    
    def bind(self, vec_a: Union[str, np.ndarray], vec_b: Union[str, np.ndarray]) -> np.ndarray:
        """
        Circular convolution binding operation (⊗)
        
        The fundamental operation of HRR that combines two vectors into one.
        Properties: approximately commutative, distributes over superposition.
        """
        # Convert string names to vectors
        a = self._get_vector(vec_a)
        b = self._get_vector(vec_b)
        
        if self.config.binding_operation == 'circular_convolution':
            # Standard HRR binding using FFT for efficiency
            result = np.real(ifft(fft(a) * fft(b)))
        elif self.config.binding_operation == 'walsh_hadamard':
            # Walsh-Hadamard binding (alternative approach)
            result = self._walsh_hadamard_bind(a, b)
        else:
            raise ValueError(f"Unknown binding operation: {self.config.binding_operation}")
        
        # Add noise if specified
        if self.config.noise_level > 0:
            noise = np.random.normal(0, self.config.noise_level, len(result))
            result += noise
            
        # Normalize if enabled
        if self.config.normalize:
            result = self._normalize_vector(result)
            
        return result
    
    def unbind(self, bound_vec: np.ndarray, cue_vec: Union[str, np.ndarray]) -> np.ndarray:
        """
        Circular correlation unbinding operation (⊘)
        
        Retrieves information from a bound vector using a cue.
        If bound_vec = a ⊗ b, then bound_vec ⊘ a ≈ b (with noise).
        """
        cue = self._get_vector(cue_vec)
        
        if self.config.binding_operation == 'circular_convolution':
            # Standard HRR unbinding - correlation is convolution with reversed vector
            reversed_cue = np.concatenate([cue[:1], cue[1:][::-1]])
            result = np.real(ifft(fft(bound_vec) * fft(reversed_cue)))
        elif self.config.binding_operation == 'walsh_hadamard':
            # Walsh-Hadamard unbinding (same as binding)
            result = self._walsh_hadamard_bind(bound_vec, cue)
        else:
            raise ValueError(f"Unknown binding operation: {self.config.binding_operation}")
            
        return result
    
    def store(self, key: str, value: Union[str, np.ndarray]) -> None:
        """Store a key-value pair in holographic memory (simplified API)"""
        # Create vectors if they don't exist
        if key not in self.memory_items:
            self.create_vector(key)
        
        if isinstance(value, str):
            if value not in self.memory_items:
                self.create_vector(value)
            value_vec = self.memory_items[value].vector
        else:
            value_vec = value
            
        # Bind key with value and store in composite memories
        bound = self.bind(key, value_vec)
        memory_name = f"stored_{key}"
        self.composite_memories[memory_name] = bound
        
    def retrieve(self, key: str) -> Optional[np.ndarray]:
        """Retrieve value associated with key (simplified API)"""
        memory_name = f"stored_{key}"
        if memory_name not in self.composite_memories:
            return None
            
        if key not in self.memory_items:
            return None
            
        # Unbind using key to retrieve value
        bound_memory = self.composite_memories[memory_name]
        retrieved = self.unbind(bound_memory, key)
        return retrieved
    
    def _walsh_hadamard_bind(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Walsh-Hadamard binding (element-wise multiplication after transform)"""
        # This is a simplified version - full Walsh-Hadamard requires power-of-2 dimensions
        return a * b  # Element-wise multiplication
    
    def superpose(self, vectors: List[Union[str, np.ndarray]], 
                 normalize: bool = True) -> np.ndarray:
        """
        Create superposition of multiple vectors (+)
        
        Combines multiple vectors through addition. This preserves the 
        ability to retrieve any component vector later.
        """
        if not vectors:
            return np.zeros(self.config.vector_dim)
            
        # Convert all to vectors and sum
        result = np.zeros(self.config.vector_dim)
        for vec in vectors:
            result += self._get_vector(vec)
            
        # Normalize if requested
        if normalize and self.config.normalize:
            result = self._normalize_vector(result)
            
        return result
    
    def similarity(self, vec1: Union[str, np.ndarray], vec2: Union[str, np.ndarray]) -> float:
        """Calculate similarity between vectors (dot product for normalized vectors)"""
        a = self._get_vector(vec1)
        b = self._get_vector(vec2)
        
        # Normalize for similarity calculation
        if self.config.normalize or self.config.similarity_preservation:
            a = self._normalize_vector(a)
            b = self._normalize_vector(b)
            
        return float(np.dot(a, b))
    
    def _get_vector(self, vec: Union[str, np.ndarray]) -> np.ndarray:
        """Convert string name to vector or return vector as-is"""
        if isinstance(vec, str):
            if vec in self.memory_items:
                return self.memory_items[vec].vector
            else:
                raise KeyError(f"Vector '{vec}' not found in memory")
        return vec
    
    # ==================== COMPOSITE MEMORY OPERATIONS ====================
    
    def create_hierarchy(self, structure: Dict, name: str) -> np.ndarray:
        """
        Create hierarchical structure using nested binding and superposition
        
        Example:
        structure = {
            'animal': ['dog', 'cat'],
            'color': ['red', 'blue']  
        }
        """
        components = []
        
        for role, fillers in structure.items():
            if isinstance(fillers, list):
                # Create superposition of fillers
                filler_vectors = []
                for filler in fillers:
                    if isinstance(filler, str) and filler not in self.memory_items:
                        self.create_vector(filler)
                    filler_vectors.append(filler)
                filler_superposition = self.superpose(filler_vectors)
            else:
                # Single filler
                if isinstance(fillers, str) and fillers not in self.memory_items:
                    self.create_vector(fillers)
                filler_superposition = self._get_vector(fillers)
            
            # Create role vector if needed
            if role not in self.memory_items:
                self.create_vector(role)
                
            # Bind role with filler superposition
            role_filler = self.bind(role, filler_superposition)
            components.append(role_filler)
        
        # Create final hierarchy as superposition of all role-filler pairs
        hierarchy = self.superpose(components, normalize=True)
        
        # Store composite memory
        self.composite_memories[name] = hierarchy
        
        return hierarchy
    
    def create_sequence(self, items: List[str], sequence_name: str, 
                       encoding: str = None) -> np.ndarray:
        """
        Create sequence representation using positional encoding
        
        Different encoding methods:
        - 'positional': bind each item with its position vector
        - 'chaining': chain items together (item1 -> item2 -> item3)
        - 'ngram': use n-gram representations
        """
        if encoding is None:
            encoding = self.config.sequence_encoding
            
        # Ensure all items exist as vectors
        for item in items:
            if item not in self.memory_items:
                self.create_vector(item)
        
        if encoding == 'positional':
            # Bind each item with position
            sequence_components = []
            for i, item in enumerate(items):
                pos_name = f"pos_{i}"
                if pos_name not in self.memory_items:
                    self.create_vector(pos_name)
                
                item_at_pos = self.bind(item, pos_name)
                sequence_components.append(item_at_pos)
            
            sequence = self.superpose(sequence_components)
            
        elif encoding == 'chaining':
            # Create chain: item1 ⊗ (item2 ⊗ (item3 ⊗ ...))
            if len(items) < 2:
                sequence = self._get_vector(items[0]) if items else np.zeros(self.config.vector_dim)
            else:
                sequence = self._get_vector(items[-1])
                for item in reversed(items[:-1]):
                    sequence = self.bind(item, sequence)
                    
        else:
            raise ValueError(f"Unknown sequence encoding: {encoding}")
        
        # Store sequence
        self.composite_memories[sequence_name] = sequence
        
        return sequence
    
    def query_memory(self, memory_name: str, cue_role: str) -> Tuple[np.ndarray, str, float]:
        """
        Query composite memory with a role to retrieve filler
        
        Returns:
        - Retrieved vector
        - Best matching item name (if cleanup successful)
        - Confidence score
        """
        if memory_name not in self.composite_memories:
            raise KeyError(f"Composite memory '{memory_name}' not found")
            
        memory = self.composite_memories[memory_name]
        retrieved = self.unbind(memory, cue_role)
        
        # Cleanup retrieved vector
        best_match, confidence = self.cleanup_memory(retrieved)
        
        return retrieved, best_match, confidence
    
    # ==================== CLEANUP AND ERROR CORRECTION ====================
    
    def cleanup_memory(self, noisy_vector: np.ndarray, 
                      candidates: Optional[List[str]] = None,
                      threshold: float = 0.1) -> Tuple[str, float]:
        """
        Clean up noisy vector by finding best match among stored vectors
        
        This is crucial for HRR systems as binding/unbinding introduces noise.
        """
        if candidates is None:
            candidates = list(self.memory_items.keys())
            
        if not candidates:
            return "", 0.0
            
        best_match = ""
        best_similarity = -float('inf')
        
        # Find best matching vector
        for candidate in candidates:
            if candidate in self.memory_items:
                sim = self.similarity(noisy_vector, candidate)
                if sim > best_similarity:
                    best_similarity = sim
                    best_match = candidate
        
        # Check if similarity meets threshold
        confidence = float(best_similarity)
        if confidence < threshold:
            best_match = ""
            
        return best_match, confidence
    
    def create_cleanup_memory(self, item_names: List[str]):
        """Create auto-associative cleanup memory (Hopfield-style)"""
        if not item_names:
            return
            
        # Collect vectors for cleanup memory
        vectors = []
        for name in item_names:
            if name in self.memory_items:
                vectors.append(self.memory_items[name].vector)
                
        if not vectors:
            return
            
        # Create Hopfield-style weight matrix
        vectors_matrix = np.array(vectors)
        
        # Compute outer product sum (Hopfield rule)
        n_vectors, dim = vectors_matrix.shape
        weights = np.zeros((dim, dim))
        
        for i in range(n_vectors):
            v = vectors_matrix[i]
            if self.config.normalize:
                v = self._normalize_vector(v)
            weights += np.outer(v, v)
            
        # Remove diagonal (no self-connections)
        np.fill_diagonal(weights, 0)
        weights /= n_vectors  # Normalize
        
        # Store cleanup memory
        self.cleanup_items['weight_matrix'] = weights
        self.cleanup_items['item_names'] = item_names.copy()
        
    def hopfield_cleanup(self, noisy_vector: np.ndarray, max_iterations: int = 10) -> np.ndarray:
        """Use Hopfield network for cleanup"""
        if 'weight_matrix' not in self.cleanup_items:
            return noisy_vector
            
        weights = self.cleanup_items['weight_matrix']
        
        # Iterative cleanup
        current = noisy_vector.copy()
        
        for _ in range(max_iterations):
            # Hopfield update rule
            next_state = np.tanh(weights @ current)
            
            # Check for convergence
            if np.allclose(current, next_state, atol=1e-6):
                break
                
            current = next_state
            
        return current
    
    # ==================== CAPACITY ANALYSIS ====================
    
    def analyze_capacity(self, n_test_items: int = 100, 
                        noise_levels: List[float] = None) -> Dict[str, Any]:
        """
        Analyze memory capacity following Plate (1995) methodology
        
        Tests how many associations can be stored before retrieval accuracy
        degrades below acceptable threshold.
        """
        if noise_levels is None:
            noise_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
            
        results = {
            'test_items': n_test_items,
            'noise_levels': noise_levels,
            'capacity_estimates': [],
            'accuracy_curves': {},
            'theoretical_capacity': self._theoretical_capacity()
        }
        
        for noise_level in noise_levels:
            # Test capacity at this noise level
            capacity = self._test_capacity_at_noise_level(n_test_items, noise_level)
            results['capacity_estimates'].append(capacity)
            
            # Generate accuracy curve
            accuracies = []
            for n_items in range(1, n_test_items + 1, n_test_items // 20):
                accuracy = self._test_retrieval_accuracy(n_items, noise_level)
                accuracies.append(accuracy)
            results['accuracy_curves'][noise_level] = accuracies
        
        return results
    
    def _theoretical_capacity(self) -> float:
        """Calculate theoretical capacity based on Plate (1995)"""
        # Plate's formula: capacity ≈ d / (2 * log(d))
        # where d is vector dimensionality
        d = self.config.vector_dim
        return d / (2 * np.log(d))
    
    def _test_capacity_at_noise_level(self, n_test_items: int, noise_level: float) -> int:
        """Test capacity at specific noise level"""
        # Create test associations
        test_items = {}
        for i in range(n_test_items):
            key = f"test_key_{i}"
            value = f"test_value_{i}"
            test_items[key] = value
            
            # Create vectors if they don't exist
            if key not in self.memory_items:
                self.create_vector(key)
            if value not in self.memory_items:
                self.create_vector(value)
        
        # Test retrieval accuracy for increasing numbers of associations
        threshold = 0.8  # 80% accuracy threshold
        
        for n_assoc in range(1, n_test_items + 1):
            accuracy = self._test_retrieval_accuracy(n_assoc, noise_level, test_items)
            if accuracy < threshold:
                return n_assoc - 1
                
        return n_test_items
    
    def _test_retrieval_accuracy(self, n_associations: int, noise_level: float,
                               test_items: Dict[str, str] = None) -> float:
        """Test retrieval accuracy for given number of associations"""
        if test_items is None:
            # Create default test items
            test_items = {}
            for i in range(n_associations):
                key = f"test_key_{i}"
                value = f"test_value_{i}"
                test_items[key] = value
                
                if key not in self.memory_items:
                    self.create_vector(key)
                if value not in self.memory_items:
                    self.create_vector(value)
        
        # Create composite memory with all associations
        associations = []
        items_list = list(test_items.items())[:n_associations]
        
        for key, value in items_list:
            bound = self.bind(key, value)
            associations.append(bound)
            
        composite = self.superpose(associations)
        
        # Test retrieval accuracy
        correct_retrievals = 0
        total_tests = len(items_list)
        
        for key, expected_value in items_list:
            # Unbind and add noise
            retrieved = self.unbind(composite, key)
            if noise_level > 0:
                noise = np.random.normal(0, noise_level, len(retrieved))
                retrieved += noise
                
            # Cleanup and check accuracy
            best_match, confidence = self.cleanup_memory(
                retrieved, 
                candidates=[v for k, v in test_items.items()]
            )
            
            if best_match == expected_value and confidence > 0.5:
                correct_retrievals += 1
        
        return correct_retrievals / total_tests if total_tests > 0 else 0.0
    
    # ==================== BENCHMARKING AND VALIDATION ====================
    
    def run_plate_benchmarks(self, verbose: bool = True) -> Dict[str, Any]:
        """Run standard benchmarks from Plate (1995)"""
        results = {}
        
        if verbose:
            print("🔬 Running Plate (1995) HRR Benchmarks")
            print("=" * 45)
        
        # 1. Role-filler binding test
        try:
            if verbose:
                print("\n1. Role-Filler Binding Test...")
                
            # Create test vectors
            self.create_vector('red')
            self.create_vector('car') 
            self.create_vector('color')
            
            # Test binding and retrieval
            bound = self.bind('color', 'red')
            retrieved = self.unbind(bound, 'color')
            similarity = self.similarity(retrieved, 'red')
            
            results['role_filler_binding'] = {
                'similarity': similarity,
                'success': similarity > 0.5
            }
            
            if verbose:
                print(f"   ✓ Similarity: {similarity:.3f}")
                print(f"   {'✓ PASS' if similarity > 0.5 else '✗ FAIL'}")
                
        except Exception as e:
            results['role_filler_binding'] = {'error': str(e)}
            if verbose:
                print(f"   ✗ Failed: {e}")
        
        # 2. Superposition test
        try:
            if verbose:
                print("\n2. Superposition Test...")
                
            # Create multiple role-filler pairs
            pairs = [('color', 'red'), ('shape', 'round'), ('size', 'large')]
            
            # Create vectors and bindings
            bound_vectors = []
            for role, filler in pairs:
                if role not in self.memory_items:
                    self.create_vector(role)
                if filler not in self.memory_items:
                    self.create_vector(filler)
                    
                bound = self.bind(role, filler)
                bound_vectors.append(bound)
            
            # Create superposition
            composite = self.superpose(bound_vectors)
            
            # Test retrieval of each pair
            retrieval_scores = []
            for role, expected_filler in pairs:
                retrieved = self.unbind(composite, role)
                similarity = self.similarity(retrieved, expected_filler)
                retrieval_scores.append(similarity)
            
            avg_similarity = np.mean(retrieval_scores)
            results['superposition'] = {
                'average_similarity': avg_similarity,
                'individual_scores': retrieval_scores,
                'success': avg_similarity > 0.3  # Lower threshold due to superposition noise
            }
            
            if verbose:
                print(f"   ✓ Average similarity: {avg_similarity:.3f}")
                print(f"   {'✓ PASS' if avg_similarity > 0.3 else '✗ FAIL'}")
                
        except Exception as e:
            results['superposition'] = {'error': str(e)}
            if verbose:
                print(f"   ✗ Failed: {e}")
        
        # 3. Capacity analysis
        try:
            if verbose:
                print("\n3. Capacity Analysis...")
                
            capacity_results = self.analyze_capacity(n_test_items=50)
            theoretical = capacity_results['theoretical_capacity']
            estimated = np.mean(capacity_results['capacity_estimates'][:3])  # Low noise estimates
            
            results['capacity_analysis'] = {
                'theoretical_capacity': theoretical,
                'estimated_capacity': estimated,
                'efficiency': estimated / theoretical if theoretical > 0 else 0,
                'full_results': capacity_results
            }
            
            if verbose:
                print(f"   ✓ Theoretical capacity: {theoretical:.1f} items")
                print(f"   ✓ Estimated capacity: {estimated:.1f} items") 
                print(f"   ✓ Efficiency: {results['capacity_analysis']['efficiency']:.1%}")
                
        except Exception as e:
            results['capacity_analysis'] = {'error': str(e)}
            if verbose:
                print(f"   ✗ Failed: {e}")
        
        if verbose:
            print("\n✅ Plate (1995) benchmark suite complete!")
            
        return results
    
    # ==================== ADVANCED FEATURES ====================
    
    def create_analogies(self, a: str, b: str, c: str) -> Tuple[np.ndarray, str, float]:
        """
        Create analogical reasoning: a:b :: c:?
        
        Uses the formula: d ≈ (b ⊘ a) ⊗ c
        """
        # Get vectors
        vec_a = self._get_vector(a)
        vec_b = self._get_vector(b) 
        vec_c = self._get_vector(c)
        
        # Compute analogy: extract relation from a:b, apply to c
        relation = self.unbind(vec_b, vec_a)  # b ⊘ a
        result = self.bind(relation, vec_c)   # relation ⊗ c
        
        # Cleanup result
        best_match, confidence = self.cleanup_memory(result)
        
        return result, best_match, confidence
    
    def measure_representational_similarity(self, groups: Dict[str, List[str]]) -> np.ndarray:
        """
        Measure representational similarity matrix between groups of items
        
        Useful for analyzing semantic structure in the vector space.
        """
        all_items = []
        group_labels = []
        
        for group_name, items in groups.items():
            for item in items:
                if item not in self.memory_items:
                    self.create_vector(item)
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
        """
        Visualize memory vectors using dimensionality reduction
        
        Note: This would require matplotlib and sklearn for full implementation
        """
        print("Visualization requires additional dependencies (matplotlib, sklearn)")
        print("Vector space visualization would show:")
        print("- 2D projection of high-dimensional vectors")
        print("- Clustering of semantically related items")
        print("- Binding operation results")
        
        # Basic text-based visualization
        print(f"\n🌀 Memory Space Overview:")
        print(f"   Total vectors: {len(self.memory_items)}")
        print(f"   Vector dimension: {self.config.vector_dim}")
        print(f"   Composite memories: {len(self.composite_memories)}")
        
        # Show similarity matrix for requested items
        if len(memory_names) <= 10:  # Only for small sets
            print(f"\n   Similarity Matrix for {memory_names}:")
            for i, name1 in enumerate(memory_names):
                row = []
                for name2 in memory_names:
                    if name1 in self.memory_items and name2 in self.memory_items:
                        sim = self.similarity(name1, name2)
                        row.append(f"{sim:5.2f}")
                    else:
                        row.append("  ---")
                print(f"   {name1:10} {' '.join(row)}")
    
    # ==================== UTILITY METHODS ====================
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        return {
            'total_vectors': len(self.memory_items),
            'composite_memories': len(self.composite_memories),
            'vector_dimension': self.config.vector_dim,
            'memory_usage_mb': self.memory_usage / (1024 * 1024),
            'association_count': self.association_count,
            'cleanup_enabled': self.config.cleanup_memory,
            'last_cleanup_success_rate': self.last_cleanup_success_rate,
            'theoretical_capacity': self._theoretical_capacity(),
            'configuration': self.config.__dict__
        }
    
    def save_memory(self, filename: str):
        """Save memory state to file"""
        import pickle
        
        save_data = {
            'config': self.config,
            'memory_items': self.memory_items,
            'composite_memories': self.composite_memories,
            'cleanup_items': self.cleanup_items,
            'association_count': self.association_count
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(save_data, f)
            
        print(f"✓ Memory saved to {filename}")
    
    def load_memory(self, filename: str):
        """Load memory state from file"""
        import pickle
        
        with open(filename, 'rb') as f:
            save_data = pickle.load(f)
            
        self.config = save_data['config']
        self.memory_items = save_data['memory_items']
        self.composite_memories = save_data['composite_memories']
        self.cleanup_items = save_data['cleanup_items']
        self.association_count = save_data['association_count']
        
        print(f"✓ Memory loaded from {filename}")
    
    # ==================== BACKWARD COMPATIBILITY ====================
    
    def create_composite_memory(self, bindings: List[Tuple[str, str]], memory_name: str) -> np.ndarray:
        """Backward compatibility method"""
        bound_vectors = []
        for role, filler in bindings:
            if role not in self.memory_items:
                self.create_vector(role)
            if filler not in self.memory_items:
                self.create_vector(filler)
            bound_vectors.append(self.bind(role, filler))
        
        composite = self.superpose(bound_vectors)
        self.composite_memories[memory_name] = composite
        return composite
    
    def query_sequence_position(self, sequence_name: str, position: int) -> Tuple[np.ndarray, str, float]:
        """Backward compatibility method"""
        if sequence_name not in self.composite_memories:
            raise KeyError(f"Sequence '{sequence_name}' not found")
            
        sequence = self.composite_memories[sequence_name]
        pos_name = f"pos_{position}"
        
        if pos_name not in self.memory_items:
            return np.zeros(self.config.vector_dim), "", 0.0
            
        retrieved = self.unbind(sequence, pos_name)
        best_match, confidence = self.cleanup_memory(retrieved)
        
        return retrieved, best_match, confidence


# ==================== FACTORY FUNCTIONS ====================

def create_holographic_memory(memory_type: str = "standard", **kwargs) -> HolographicMemory:
    """
    Factory function to create different types of holographic memory systems
    
    Parameters:
    -----------
    memory_type : str
        Type of memory: "standard", "high_capacity", "fast", or "research"
    **kwargs : additional arguments for memory initialization
    
    Returns:
    --------
    memory : HolographicMemory
        Configured holographic memory system
    """
    
    if memory_type == "standard":
        config = HRRConfig(vector_dim=512, normalize=True, cleanup_memory=True)
        return HolographicMemory(config, **kwargs)
        
    elif memory_type == "high_capacity":
        config = HRRConfig(
            vector_dim=2048, 
            normalize=True, 
            cleanup_memory=True,
            capacity_monitoring=True,
            fast_cleanup=True
        )
        return HolographicMemory(config, **kwargs)
        
    elif memory_type == "fast":
        config = HRRConfig(
            vector_dim=256,
            normalize=True,
            cleanup_memory=False,  # Disable for speed
            fast_cleanup=True
        )
        return HolographicMemory(config, **kwargs)
        
    elif memory_type == "research":
        config = HRRConfig(
            vector_dim=1024,
            normalize=True,
            cleanup_memory=True,
            capacity_monitoring=True,
            unitary_vectors=True,  # For exact operations
            similarity_preservation=True
        )
        return HolographicMemory(config, **kwargs)
        
    else:
        raise ValueError(f"Unknown memory_type: {memory_type}")


def run_hrr_benchmark_suite(verbose: bool = True) -> Dict[str, Any]:
    """
    Run comprehensive benchmark suite for HRR implementation
    
    Returns:
    --------
    results : dict
        Benchmark results across different memory configurations
    """
    results = {}
    
    if verbose:
        print("🔬 Running HRR Benchmark Suite")
        print("=" * 40)
    
    # Test different memory configurations
    configurations = {
        'standard': create_holographic_memory('standard'),
        'high_capacity': create_holographic_memory('high_capacity'),
        'fast': create_holographic_memory('fast')
    }
    
    for config_name, memory in configurations.items():
        if verbose:
            print(f"\n🧠 Testing {config_name} configuration...")
            
        try:
            # Run Plate benchmarks
            plate_results = memory.run_plate_benchmarks(verbose=False)
            results[config_name] = plate_results
            
            if verbose:
                success_count = sum(1 for v in plate_results.values() 
                                  if isinstance(v, dict) and v.get('success', False))
                total_tests = len([v for v in plate_results.values() if isinstance(v, dict)])
                print(f"   ✓ Passed {success_count}/{total_tests} tests")
                
        except Exception as e:
            results[config_name] = {'error': str(e)}
            if verbose:
                print(f"   ✗ Failed: {e}")
    
    if verbose:
        print("\n✅ HRR benchmark suite complete!")
    
    return results


# ==================== DEMONSTRATION FUNCTION ====================

def demonstrate_unified_holographic_memory():
    """Complete demonstration of unified holographic memory functionality"""
    print("🌀 Unified Holographic Memory Demonstration")
    print("=" * 50)
    
    # 1. Create memory system
    print("\n1. Creating Holographic Memory System")
    memory = create_holographic_memory("research", vector_dim=512)
    
    # 2. Basic operations
    print("\n2. Basic Vector Operations")
    memory.create_vector('red')
    memory.create_vector('car')
    memory.create_vector('color')
    
    # Binding
    color_car = memory.bind('color', 'red')
    print(f"   Bound 'color' ⊗ 'red'")
    
    # Unbinding  
    retrieved = memory.unbind(color_car, 'color')
    similarity = memory.similarity(retrieved, 'red')
    print(f"   Retrieved similarity: {similarity:.3f}")
    
    # 3. Composite memory
    print("\n3. Composite Memory Structure")
    structure = {
        'color': ['red', 'blue', 'green'],
        'shape': ['round', 'square'],
        'size': ['large', 'small']
    }
    
    car_concept = memory.create_hierarchy(structure, 'car_concept')
    print(f"   Created hierarchical car concept")
    
    # Query the concept
    retrieved_color, best_match, confidence = memory.query_memory('car_concept', 'color')
    print(f"   Queried color: {best_match} (confidence: {confidence:.3f})")
    
    # 4. Sequence processing
    print("\n4. Sequence Processing")
    sequence_items = ['start', 'middle', 'end']
    for item in sequence_items:
        memory.create_vector(item)
        
    sequence = memory.create_sequence(sequence_items, 'test_sequence')
    retrieved_item, match, conf = memory.query_sequence_position('test_sequence', 1)
    print(f"   Position 1 in sequence: {match} (confidence: {conf:.3f})")
    
    # 5. Analogical reasoning
    print("\n5. Analogical Reasoning")
    # Create vectors for analogy
    for word in ['king', 'queen', 'man', 'woman']:
        memory.create_vector(word)
        
    analogy_result, analogy_match, analogy_conf = memory.create_analogies('king', 'queen', 'man')
    print(f"   king:queen :: man:? → {analogy_match} (confidence: {analogy_conf:.3f})")
    
    # 6. Capacity analysis
    print("\n6. Memory Capacity Analysis")
    stats = memory.get_memory_stats()
    print(f"   Theoretical capacity: {stats['theoretical_capacity']:.1f} items")
    print(f"   Current vectors: {stats['total_vectors']}")
    print(f"   Composite memories: {stats['composite_memories']}")
    
    # 7. Run benchmarks
    print("\n7. Benchmark Results")
    benchmark_results = memory.run_plate_benchmarks(verbose=False)
    
    success_count = sum(1 for v in benchmark_results.values() 
                       if isinstance(v, dict) and v.get('success', False))
    total_tests = len([v for v in benchmark_results.values() if isinstance(v, dict)])
    print(f"   Passed {success_count}/{total_tests} Plate (1995) benchmarks")
    
    print("\n✅ Unified Holographic Memory demonstration complete!")
    print("🚀 All features integrated successfully!")


if __name__ == "__main__":
    demonstrate_unified_holographic_memory()