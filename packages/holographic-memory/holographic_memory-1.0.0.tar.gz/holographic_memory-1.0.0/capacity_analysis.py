"""
Capacity analysis for Holographic Memory
Implements Plate 1995 capacity formulas and empirical testing
"""

import numpy as np
from typing import Dict, Any, Optional, List


class CapacityAnalyzer:
    """Handles capacity analysis for HolographicMemory systems"""
    
    def __init__(self, memory_instance):
        self.memory = memory_instance
    
    def analyze_capacity(self, noise_threshold: float = 0.1) -> Dict[str, Any]:
        """
        Analyze HRR capacity according to Plate 1995 Section IX
        Implementing FIXME suggestion for capacity analysis

        Formula from paper: k > n/(16 ln²(m/q)) where:
        - k = number of terms in sum
        - n = vector dimension
        - m = number of distinct items
        - q = noise level threshold
        """
        n = self.memory.vector_dim
        m = len(self.memory.memory_items)
        q = noise_threshold

        if m == 0:
            theoretical_limit = float('inf')
        else:
            # Plate's formula: k > n/(16 ln²(m/q))
            if q >= m:  # Avoid log of negative/zero
                theoretical_limit = n // 16
            else:
                theoretical_limit = n / (16 * (np.log(m/q) ** 2))

        current_usage = self.memory.association_count
        usage_ratio = current_usage / theoretical_limit if theoretical_limit > 0 else 0

        # Empirical capacity test
        empirical_accuracy = self._test_retrieval_accuracy()

        capacity_info = {
            'vector_dimension': n,
            'stored_items': m,
            'associations_made': current_usage,
            'theoretical_capacity': int(theoretical_limit) if theoretical_limit != float('inf') else 999999,
            'usage_ratio': usage_ratio,
            'empirical_accuracy': empirical_accuracy,
            'capacity_status': 'OK' if usage_ratio < 0.8 else 'WARNING' if usage_ratio < 1.0 else 'EXCEEDED',
            'noise_threshold': q
        }

        return capacity_info
    
    def _test_retrieval_accuracy(self, n_tests: int = 10) -> float:
        """Test empirical retrieval accuracy"""
        if len(self.memory.memory_items) < 2:
            return 1.0  # Perfect accuracy with few items
        
        accuracies = []
        items = list(self.memory.memory_items.keys())
        
        for _ in range(min(n_tests, len(items) - 1)):
            # Pick random pair
            idx_a, idx_b = np.random.choice(len(items), 2, replace=False)
            name_a, name_b = items[idx_a], items[idx_b]
            
            # Test binding and unbinding
            bound = self.memory.bind(name_a, name_b)
            unbound = self.memory.unbind(bound, name_a)
            
            # Measure similarity
            target = self.memory.memory_items[name_b].vector
            similarity = np.corrcoef(unbound, target)[0, 1]
            accuracies.append(max(0, similarity))  # Clamp to [0, 1]
        
        return np.mean(accuracies) if accuracies else 1.0
    
    def memory_capacity_analysis(self, n_test_items: int = 100) -> Dict[str, Any]:
        """
        Comprehensive capacity analysis with empirical testing
        """
        # Store original state
        original_items = self.memory.memory_items.copy()
        original_count = self.memory.association_count
        
        try:
            # Clear memory for clean test
            self.memory.memory_items.clear()
            self.memory.association_count = 0
            
            # Generate test items
            test_items = []
            for i in range(n_test_items):
                item_name = f"test_item_{i}"
                vector = self.memory.create_vector(item_name)
                test_items.append(item_name)
            
            # Test capacity at different load levels
            load_levels = [0.1, 0.3, 0.5, 0.7, 0.9]
            capacity_results = {}
            
            for load in load_levels:
                n_associations = int(load * n_test_items)
                
                # Create associations
                for i in range(n_associations):
                    a_idx = i % len(test_items)
                    b_idx = (i + 1) % len(test_items)
                    self.memory.bind(test_items[a_idx], test_items[b_idx])
                
                # Test retrieval accuracy
                accuracy = self._test_retrieval_accuracy(n_tests=20)
                
                capacity_results[f"load_{load}"] = {
                    'associations': n_associations,
                    'accuracy': accuracy,
                    'degradation': 1.0 - accuracy
                }
            
            return {
                'test_items': n_test_items,
                'load_analysis': capacity_results,
                'theoretical_analysis': self.analyze_capacity()
            }
            
        finally:
            # Restore original state
            self.memory.memory_items = original_items
            self.memory.association_count = original_count