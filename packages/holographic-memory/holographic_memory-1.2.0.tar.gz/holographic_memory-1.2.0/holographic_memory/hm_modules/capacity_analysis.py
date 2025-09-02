"""
Capacity Analysis and Benchmarking Module for Holographic Memory System

Implements capacity analysis following Plate (1995) methodology and
comprehensive benchmarking suite for HRR systems.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
import time
from typing import Dict, List, Any, Tuple, Optional
from .configuration import HRRConfig
from .vector_operations import VectorOperations
from .memory_management import MemoryManager
from .cleanup_operations import CleanupOperations


class CapacityAnalyzer:
    """Analyzes memory capacity and runs benchmarks for HRR systems"""
    
    def __init__(self, config: HRRConfig, vector_ops: VectorOperations, 
                 memory_manager: MemoryManager, cleanup_ops: CleanupOperations):
        """Initialize capacity analyzer"""
        self.config = config
        self.vector_ops = vector_ops
        self.memory_manager = memory_manager
        self.cleanup_ops = cleanup_ops
        
        print(f"✓ Capacity Analyzer initialized")
    
    def theoretical_capacity(self) -> float:
        """
        Calculate theoretical capacity based on Plate (1995)
        
        Returns:
        --------
        capacity : float
            Theoretical capacity in number of associations
        """
        if self.config.capacity_formula == 'plate1995':
            # Plate's formula: capacity ≈ d / (2 * log(d))
            # where d is vector dimensionality
            d = self.config.vector_dim
            return d / (2 * np.log(d))
        elif self.config.capacity_formula == 'conservative':
            # More conservative estimate
            return self.config.vector_dim / 16
        elif self.config.capacity_formula == 'optimistic':
            # More optimistic estimate
            return self.config.vector_dim / 8
        else:
            raise ValueError(f"Unknown capacity formula: {self.config.capacity_formula}")
    
    def analyze_capacity(self, n_test_items: int = 100, 
                        noise_levels: List[float] = None) -> Dict[str, Any]:
        """
        Analyze memory capacity following Plate (1995) methodology
        
        Tests how many associations can be stored before retrieval accuracy
        degrades below acceptable threshold.
        
        Parameters:
        -----------
        n_test_items : int
            Number of test items to use
        noise_levels : List[float], optional
            Noise levels to test
        
        Returns:
        --------
        results : Dict[str, Any]
            Comprehensive capacity analysis results
        """
        if noise_levels is None:
            noise_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
            
        print(f"🔬 Analyzing capacity with {n_test_items} test items...")
        
        results = {
            'test_items': n_test_items,
            'noise_levels': noise_levels,
            'capacity_estimates': [],
            'accuracy_curves': {},
            'theoretical_capacity': self.theoretical_capacity(),
            'timestamp': time.time()
        }
        
        for i, noise_level in enumerate(noise_levels):
            print(f"  Testing noise level {noise_level:.1f} ({i+1}/{len(noise_levels)})")
            
            # Test capacity at this noise level
            capacity = self._test_capacity_at_noise_level(n_test_items, noise_level)
            results['capacity_estimates'].append(capacity)
            
            # Generate accuracy curve
            accuracies = []
            test_points = range(1, min(n_test_items + 1, int(self.theoretical_capacity()) + 20), 
                              max(1, n_test_items // 20))
            
            for n_items in test_points:
                accuracy = self._test_retrieval_accuracy(n_items, noise_level)
                accuracies.append((n_items, accuracy))
            
            results['accuracy_curves'][noise_level] = accuracies
        
        # Calculate summary statistics
        results['average_capacity'] = np.mean(results['capacity_estimates'])
        results['capacity_efficiency'] = results['average_capacity'] / results['theoretical_capacity']
        
        print(f"✓ Capacity analysis complete")
        print(f"  Theoretical: {results['theoretical_capacity']:.1f}")
        print(f"  Average measured: {results['average_capacity']:.1f}")
        print(f"  Efficiency: {results['capacity_efficiency']:.1%}")
        
        return results
    
    def _test_capacity_at_noise_level(self, n_test_items: int, noise_level: float) -> int:
        """Test capacity at specific noise level"""
        # Create test associations
        test_items = {}
        for i in range(n_test_items):
            key = f"cap_test_key_{i}"
            value = f"cap_test_value_{i}"
            test_items[key] = value
            
            # Create vectors if they don't exist
            if not self.memory_manager.has_vector(key):
                self.memory_manager.create_vector(key)
            if not self.memory_manager.has_vector(value):
                self.memory_manager.create_vector(value)
        
        # Test retrieval accuracy for increasing numbers of associations
        threshold = 0.8  # 80% accuracy threshold
        
        for n_assoc in range(1, n_test_items + 1):
            accuracy = self._test_retrieval_accuracy(n_assoc, noise_level, test_items)
            if accuracy < threshold:
                return max(0, n_assoc - 1)
                
        return n_test_items
    
    def _test_retrieval_accuracy(self, n_associations: int, noise_level: float,
                               test_items: Dict[str, str] = None) -> float:
        """Test retrieval accuracy for given number of associations"""
        if test_items is None:
            # Create default test items
            test_items = {}
            for i in range(n_associations):
                key = f"acc_test_key_{i}"
                value = f"acc_test_value_{i}"
                test_items[key] = value
                
                if not self.memory_manager.has_vector(key):
                    self.memory_manager.create_vector(key)
                if not self.memory_manager.has_vector(value):
                    self.memory_manager.create_vector(value)
        
        # Create composite memory with all associations
        associations = []
        items_list = list(test_items.items())[:n_associations]
        
        for key, value in items_list:
            key_vec = self.memory_manager.get_vector(key)
            value_vec = self.memory_manager.get_vector(value)
            bound = self.vector_ops.bind(key_vec, value_vec)
            associations.append(bound)
            
        composite = self.vector_ops.superpose(associations)
        
        # Test retrieval accuracy
        correct_retrievals = 0
        total_tests = len(items_list)
        
        for key, expected_value in items_list:
            # Unbind and add noise
            key_vec = self.memory_manager.get_vector(key)
            retrieved = self.vector_ops.unbind(composite, key_vec)
            
            if noise_level > 0:
                noise = np.random.normal(0, noise_level, len(retrieved))
                retrieved += noise
                
            # Cleanup and check accuracy
            value_candidates = [v for k, v in test_items.items()]
            best_match, confidence = self.cleanup_ops.cleanup_memory(
                retrieved, 
                candidates=value_candidates
            )
            
            if best_match == expected_value and confidence > 0.5:
                correct_retrievals += 1
        
        return correct_retrievals / total_tests if total_tests > 0 else 0.0
    
    def run_plate_benchmarks(self, verbose: bool = True) -> Dict[str, Any]:
        """Run standard benchmarks from Plate (1995)"""
        results = {}
        
        if verbose:
            print("🔬 Running Plate (1995) HRR Benchmarks")
            print("=" * 45)
        
        start_time = time.time()
        
        # 1. Role-filler binding test
        try:
            if verbose:
                print("\n1. Role-Filler Binding Test...")
                
            # Create test vectors
            if not self.memory_manager.has_vector('red'):
                self.memory_manager.create_vector('red')
            if not self.memory_manager.has_vector('car'):
                self.memory_manager.create_vector('car')
            if not self.memory_manager.has_vector('color'):
                self.memory_manager.create_vector('color')
            
            # Test binding and retrieval
            red_vec = self.memory_manager.get_vector('red')
            car_vec = self.memory_manager.get_vector('car')
            color_vec = self.memory_manager.get_vector('color')
            
            bound = self.vector_ops.bind(color_vec, red_vec)
            retrieved = self.vector_ops.unbind(bound, color_vec)
            similarity = self.vector_ops.similarity(retrieved, red_vec)
            
            results['role_filler_binding'] = {
                'similarity': float(similarity),
                'success': similarity > 0.5,
                'test_time': time.time() - start_time
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
                
            test_start = time.time()
            
            # Create multiple role-filler pairs
            pairs = [('color', 'red'), ('shape', 'round'), ('size', 'large')]
            
            # Create vectors and bindings
            bound_vectors = []
            for role, filler in pairs:
                if not self.memory_manager.has_vector(role):
                    self.memory_manager.create_vector(role)
                if not self.memory_manager.has_vector(filler):
                    self.memory_manager.create_vector(filler)
                    
                role_vec = self.memory_manager.get_vector(role)
                filler_vec = self.memory_manager.get_vector(filler)
                bound = self.vector_ops.bind(role_vec, filler_vec)
                bound_vectors.append(bound)
            
            # Create superposition
            composite = self.vector_ops.superpose(bound_vectors)
            
            # Test retrieval of each pair
            retrieval_scores = []
            for role, expected_filler in pairs:
                role_vec = self.memory_manager.get_vector(role)
                expected_vec = self.memory_manager.get_vector(expected_filler)
                retrieved = self.vector_ops.unbind(composite, role_vec)
                similarity = self.vector_ops.similarity(retrieved, expected_vec)
                retrieval_scores.append(float(similarity))
            
            avg_similarity = np.mean(retrieval_scores)
            results['superposition'] = {
                'average_similarity': float(avg_similarity),
                'individual_scores': retrieval_scores,
                'success': avg_similarity > 0.3,  # Lower threshold due to superposition noise
                'test_time': time.time() - test_start
            }
            
            if verbose:
                print(f"   ✓ Average similarity: {avg_similarity:.3f}")
                print(f"   {'✓ PASS' if avg_similarity > 0.3 else '✗ FAIL'}")
                
        except Exception as e:
            results['superposition'] = {'error': str(e)}
            if verbose:
                print(f"   ✗ Failed: {e}")
        
        # 3. Capacity analysis (reduced scope for benchmarking)
        try:
            if verbose:
                print("\n3. Capacity Analysis...")
                
            test_start = time.time()
            capacity_results = self.analyze_capacity(n_test_items=30, noise_levels=[0.0, 0.2, 0.4])
            theoretical = capacity_results['theoretical_capacity']
            estimated = capacity_results['average_capacity']
            
            results['capacity_analysis'] = {
                'theoretical_capacity': float(theoretical),
                'estimated_capacity': float(estimated),
                'efficiency': float(estimated / theoretical) if theoretical > 0 else 0.0,
                'test_time': time.time() - test_start,
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
        
        # 4. Analogical reasoning test
        try:
            if verbose:
                print("\n4. Analogical Reasoning Test...")
                
            test_start = time.time()
            
            # Create analogy vectors
            analogy_items = ['king', 'queen', 'man', 'woman']
            for item in analogy_items:
                if not self.memory_manager.has_vector(item):
                    self.memory_manager.create_vector(item)
            
            # Test king:queen :: man:woman
            king_vec = self.memory_manager.get_vector('king')
            queen_vec = self.memory_manager.get_vector('queen')
            man_vec = self.memory_manager.get_vector('man')
            woman_vec = self.memory_manager.get_vector('woman')
            
            analogy_result = self.vector_ops.create_analogy_vector(king_vec, queen_vec, man_vec)
            similarity = self.vector_ops.similarity(analogy_result, woman_vec)
            
            results['analogical_reasoning'] = {
                'similarity_to_expected': float(similarity),
                'success': similarity > 0.2,  # Lower threshold for analogy
                'test_time': time.time() - test_start
            }
            
            if verbose:
                print(f"   ✓ Similarity to 'woman': {similarity:.3f}")
                print(f"   {'✓ PASS' if similarity > 0.2 else '✗ FAIL'}")
                
        except Exception as e:
            results['analogical_reasoning'] = {'error': str(e)}
            if verbose:
                print(f"   ✗ Failed: {e}")
        
        # Calculate overall score
        successful_tests = sum(1 for test_result in results.values() 
                             if isinstance(test_result, dict) and test_result.get('success', False))
        total_tests = len([r for r in results.values() if isinstance(r, dict)])
        
        results['overall_summary'] = {
            'successful_tests': successful_tests,
            'total_tests': total_tests,
            'success_rate': successful_tests / total_tests if total_tests > 0 else 0.0,
            'total_time': time.time() - start_time
        }
        
        if verbose:
            print(f"\n✅ Plate (1995) benchmark suite complete!")
            print(f"   Passed {successful_tests}/{total_tests} tests ({results['overall_summary']['success_rate']:.1%})")
            print(f"   Total time: {results['overall_summary']['total_time']:.2f} seconds")
            
        return results
    
    def benchmark_operations(self, n_trials: int = 1000) -> Dict[str, Any]:
        """
        Benchmark basic operation performance
        
        Parameters:
        -----------
        n_trials : int
            Number of trials for each operation
        
        Returns:
        --------
        results : Dict[str, Any]
            Performance benchmarking results
        """
        print(f"⚡ Benchmarking operations with {n_trials} trials...")
        
        # Create test vectors
        test_vectors = []
        for i in range(10):
            name = f"bench_vec_{i}"
            vec = self.memory_manager.create_vector(name)
            test_vectors.append(vec)
        
        results = {}
        
        # Benchmark binding
        start_time = time.time()
        for _ in range(n_trials):
            a = test_vectors[np.random.randint(0, len(test_vectors))]
            b = test_vectors[np.random.randint(0, len(test_vectors))]
            _ = self.vector_ops.bind(a, b)
        bind_time = time.time() - start_time
        results['binding'] = {
            'total_time': bind_time,
            'ops_per_second': n_trials / bind_time,
            'time_per_op_ms': (bind_time / n_trials) * 1000
        }
        
        # Benchmark unbinding
        start_time = time.time()
        for _ in range(n_trials):
            a = test_vectors[np.random.randint(0, len(test_vectors))]
            b = test_vectors[np.random.randint(0, len(test_vectors))]
            _ = self.vector_ops.unbind(a, b)
        unbind_time = time.time() - start_time
        results['unbinding'] = {
            'total_time': unbind_time,
            'ops_per_second': n_trials / unbind_time,
            'time_per_op_ms': (unbind_time / n_trials) * 1000
        }
        
        # Benchmark superposition
        start_time = time.time()
        for _ in range(n_trials):
            vecs = [test_vectors[i] for i in np.random.choice(len(test_vectors), 3, replace=False)]
            _ = self.vector_ops.superpose(vecs)
        superpose_time = time.time() - start_time
        results['superposition'] = {
            'total_time': superpose_time,
            'ops_per_second': n_trials / superpose_time,
            'time_per_op_ms': (superpose_time / n_trials) * 1000
        }
        
        # Benchmark similarity
        start_time = time.time()
        for _ in range(n_trials):
            a = test_vectors[np.random.randint(0, len(test_vectors))]
            b = test_vectors[np.random.randint(0, len(test_vectors))]
            _ = self.vector_ops.similarity(a, b)
        similarity_time = time.time() - start_time
        results['similarity'] = {
            'total_time': similarity_time,
            'ops_per_second': n_trials / similarity_time,
            'time_per_op_ms': (similarity_time / n_trials) * 1000
        }
        
        print("✓ Operation benchmarking complete")
        for op_name, metrics in results.items():
            print(f"  {op_name}: {metrics['ops_per_second']:.0f} ops/sec ({metrics['time_per_op_ms']:.3f} ms/op)")
        
        return results
    
    def stress_test(self, max_items: int = None) -> Dict[str, Any]:
        """
        Stress test the memory system with increasing load
        
        Parameters:
        -----------
        max_items : int, optional
            Maximum number of items to test (defaults to 2x theoretical capacity)
        
        Returns:
        --------
        results : Dict[str, Any]
            Stress test results
        """
        if max_items is None:
            max_items = int(2 * self.theoretical_capacity())
        
        print(f"💪 Stress testing up to {max_items} items...")
        
        results = {
            'max_items': max_items,
            'performance_curve': [],
            'memory_usage_curve': [],
            'error_threshold_reached': None
        }
        
        test_points = np.logspace(1, np.log10(max_items), 20, dtype=int)
        
        for n_items in test_points:
            start_time = time.time()
            
            # Create test items
            test_vectors = []
            for i in range(n_items):
                name = f"stress_test_{i}"
                if not self.memory_manager.has_vector(name):
                    vec = self.memory_manager.create_vector(name)
                    test_vectors.append(vec)
            
            # Test operations performance
            operation_times = []
            for _ in range(min(100, 1000 // n_items + 1)):  # Fewer trials for larger sets
                a = test_vectors[np.random.randint(0, len(test_vectors))]
                b = test_vectors[np.random.randint(0, len(test_vectors))]
                
                op_start = time.time()
                bound = self.vector_ops.bind(a, b)
                retrieved = self.vector_ops.unbind(bound, a)
                similarity = self.vector_ops.similarity(retrieved, b)
                op_time = time.time() - op_start
                
                operation_times.append(op_time)
            
            avg_op_time = np.mean(operation_times)
            memory_stats = self.memory_manager.get_memory_stats()
            
            results['performance_curve'].append({
                'n_items': n_items,
                'avg_operation_time': avg_op_time,
                'ops_per_second': 1.0 / avg_op_time if avg_op_time > 0 else float('inf'),
                'total_time': time.time() - start_time
            })
            
            results['memory_usage_curve'].append({
                'n_items': n_items,
                'memory_mb': memory_stats['memory_usage_mb'],
                'total_vectors': memory_stats['total_vectors']
            })
            
            print(f"  {n_items} items: {avg_op_time*1000:.2f} ms/op, {memory_stats['memory_usage_mb']:.1f} MB")
        
        print("✓ Stress testing complete")
        
        return results