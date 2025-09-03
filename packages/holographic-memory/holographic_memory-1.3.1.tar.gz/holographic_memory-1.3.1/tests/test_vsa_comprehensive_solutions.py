"""
Comprehensive Tests for VSA FIXME Solutions
==========================================

Author: Benedict Chen (benedict@benedictchen.com)

Validation tests for all implemented VSA FIXME solutions:
- Auto-dimension selection based on capacity requirements
- Multiple vector distributions and binding operations
- Research-accurate HRR implementation
- Performance vs accuracy tradeoffs

Ensures all VSA configuration options work correctly.
"""

import pytest
import torch
import numpy as np
from typing import Dict, List, Tuple

# Import VSA comprehensive solutions
from holographic_memory.vsa_comprehensive_config import (
    VSAComprehensiveConfig,
    VectorDistribution,
    BindingOperation,
    UnbindingStrategy,
    SimilarityMetric,
    NoiseHandling,
    create_research_accurate_config,
    create_capacity_optimized_config,
    validate_vsa_config,
    auto_select_dimension
)


class TestVSAComprehensiveConfig:
    """Test VSA comprehensive configuration system."""
    
    def test_config_creation(self):
        """Test basic VSA config creation."""
        config = VSAComprehensiveConfig()
        
        # Default values should be research-accurate
        assert config.vector_distribution == VectorDistribution.GAUSSIAN_RANDOM
        assert config.binding_operation == BindingOperation.CIRCULAR_CONVOLUTION
        assert config.unbinding_strategy == UnbindingStrategy.APPROXIMATE_INVERSE
        assert config.similarity_metric == SimilarityMetric.COSINE_SIMILARITY
    
    def test_research_accurate_preset(self):
        """Test research-accurate preset configuration."""
        config = create_research_accurate_config()
        
        # Verify Plate (1995) HRR settings
        assert config.vector_distribution == VectorDistribution.GAUSSIAN_RANDOM
        assert config.binding_operation == BindingOperation.CIRCULAR_CONVOLUTION
        assert config.unbinding_strategy == UnbindingStrategy.APPROXIMATE_INVERSE
        assert config.validate_against_plate_paper == True
        assert config.enable_capacity_monitoring == True
    
    def test_capacity_optimized_preset(self):
        """Test capacity-optimized preset configuration."""
        config = create_capacity_optimized_config()
        
        # Verify capacity optimization settings
        assert config.enable_auto_dimension_selection == True
        assert config.capacity_monitoring_enabled == True
        assert config.adaptive_noise_threshold == True
        assert config.performance_profiling_enabled == True
    
    def test_config_validation(self):
        """Test VSA configuration validation system."""
        config = create_research_accurate_config()
        warnings = validate_vsa_config(config)
        
        # Research-accurate config should have minimal warnings
        critical_warnings = [w for w in warnings if "🚨 CRITICAL" in w or "❌" in w]
        assert len(critical_warnings) == 0, f"Unexpected critical warnings: {critical_warnings}"
    
    def test_invalid_config_detection(self):
        """Test detection of invalid VSA configurations."""
        config = VSAComprehensiveConfig()
        config.vector_dimension = 0        # Invalid
        config.noise_tolerance = -0.1     # Invalid  
        config.binding_strength = 1.5     # Invalid
        
        warnings = validate_vsa_config(config)
        
        # Should detect invalid parameters
        assert len(warnings) > 0
        error_warnings = [w for w in warnings if "❌" in w]
        assert len(error_warnings) >= 3  # Should catch all three errors
    
    def test_all_enum_values_valid(self):
        """Test all VSA enum values can be used."""
        # Test VectorDistribution
        for distribution in VectorDistribution:
            config = VSAComprehensiveConfig(vector_distribution=distribution)
            assert config.vector_distribution == distribution
        
        # Test BindingOperation
        for operation in BindingOperation:
            config = VSAComprehensiveConfig(binding_operation=operation)
            assert config.binding_operation == operation
        
        # Test UnbindingStrategy
        for strategy in UnbindingStrategy:
            config = VSAComprehensiveConfig(unbinding_strategy=strategy)
            assert config.unbinding_strategy == strategy


class TestAutoDimensionSelection:
    """Test automatic dimension selection functionality."""
    
    def test_basic_dimension_calculation(self):
        """Test basic dimension calculation."""
        # Small symbol set
        dimension = auto_select_dimension(symbol_count=10)
        assert dimension >= 256  # Minimum dimension
        assert dimension <= 2048  # Maximum dimension
        assert (dimension & (dimension - 1)) == 0  # Power of two
    
    def test_scaling_with_symbol_count(self):
        """Test dimension scaling with symbol count."""
        dim_small = auto_select_dimension(symbol_count=50)
        dim_medium = auto_select_dimension(symbol_count=200)
        dim_large = auto_select_dimension(symbol_count=500)
        
        # Dimension should increase with symbol count
        assert dim_small <= dim_medium <= dim_large
    
    def test_capacity_factor_effect(self):
        """Test effect of capacity factor on dimension."""
        symbol_count = 100
        
        dim_conservative = auto_select_dimension(symbol_count, capacity_factor=4.0)
        dim_standard = auto_select_dimension(symbol_count, capacity_factor=2.5)
        dim_aggressive = auto_select_dimension(symbol_count, capacity_factor=1.5)
        
        # Higher capacity factor should give larger dimensions
        assert dim_aggressive <= dim_standard <= dim_conservative
    
    def test_power_of_two_constraint(self):
        """Test that all selected dimensions are powers of two."""
        for symbol_count in [10, 50, 100, 200, 500]:
            dimension = auto_select_dimension(symbol_count)
            
            # Check if power of two
            assert (dimension & (dimension - 1)) == 0
            
            # Check reasonable range
            assert 256 <= dimension <= 2048
    
    def test_edge_cases(self):
        """Test edge cases for dimension selection."""
        # Very small symbol count
        dim_tiny = auto_select_dimension(symbol_count=1)
        assert dim_tiny == 256  # Minimum
        
        # Very large symbol count
        dim_huge = auto_select_dimension(symbol_count=10000)
        assert dim_huge == 2048  # Maximum
        
        # Zero symbol count (edge case)
        dim_zero = auto_select_dimension(symbol_count=0)
        assert dim_zero == 256  # Should default to minimum


class TestVSAConfigurationIntegration:
    """Test integration aspects of VSA configuration."""
    
    def test_research_vs_performance_tradeoffs(self):
        """Test tradeoffs between research accuracy and performance."""
        research_config = create_research_accurate_config()
        performance_config = create_capacity_optimized_config()
        
        # Research config should prioritize accuracy
        assert research_config.validate_against_plate_paper == True
        assert research_config.high_precision_arithmetic == True
        assert research_config.comprehensive_error_checking == True
        
        # Performance config should prioritize efficiency  
        assert performance_config.enable_gpu_acceleration == True
        assert performance_config.batch_processing_enabled == True
        assert performance_config.memory_efficient_storage == True
    
    def test_binding_unbinding_consistency(self):
        """Test consistency between binding and unbinding methods."""
        config = VSAComprehensiveConfig()
        
        # Circular convolution should use approximate inverse
        config.binding_operation = BindingOperation.CIRCULAR_CONVOLUTION
        config.unbinding_strategy = UnbindingStrategy.APPROXIMATE_INVERSE
        
        warnings = validate_vsa_config(config)
        consistency_warnings = [w for w in warnings if "inconsistent" in w.lower()]
        assert len(consistency_warnings) == 0
        
        # XOR binding should use XOR unbinding
        config.binding_operation = BindingOperation.XOR_BINDING
        config.unbinding_strategy = UnbindingStrategy.XOR_UNBINDING
        
        warnings = validate_vsa_config(config)
        consistency_warnings = [w for w in warnings if "inconsistent" in w.lower()]
        assert len(consistency_warnings) == 0
    
    def test_dimension_vector_distribution_compatibility(self):
        """Test compatibility between dimension and vector distribution."""
        config = VSAComprehensiveConfig()
        
        # Binary vectors work with any dimension
        config.vector_distribution = VectorDistribution.BINARY_RANDOM
        config.vector_dimension = 1000
        
        warnings = validate_vsa_config(config)
        compatibility_warnings = [w for w in warnings if "incompatible" in w.lower()]
        assert len(compatibility_warnings) == 0
    
    def test_capacity_monitoring_settings(self):
        """Test capacity monitoring configuration validation."""
        config = create_capacity_optimized_config()
        
        # Should have capacity monitoring enabled
        assert config.capacity_monitoring_enabled == True
        assert config.enable_capacity_monitoring == True
        assert config.capacity_threshold > 0.0 and config.capacity_threshold < 1.0
        
        # Should have reasonable capacity parameters
        assert config.expected_symbol_count > 0
        assert config.capacity_safety_margin > 1.0
    
    def test_noise_handling_consistency(self):
        """Test noise handling configuration consistency."""
        config = VSAComprehensiveConfig()
        
        # Statistical noise handling should have appropriate parameters
        config.noise_handling = NoiseHandling.STATISTICAL_FILTERING
        config.statistical_confidence_level = 0.95
        config.noise_detection_sensitivity = 0.1
        
        warnings = validate_vsa_config(config)
        
        # Should not have parameter inconsistencies
        param_warnings = [w for w in warnings if "parameter" in w.lower()]
        assert len([w for w in param_warnings if "❌" in w]) == 0
    
    def test_similarity_metric_normalization(self):
        """Test similarity metric and normalization compatibility."""
        config = VSAComprehensiveConfig()
        
        # Cosine similarity works well with L2 normalization
        config.similarity_metric = SimilarityMetric.COSINE_SIMILARITY
        config.vector_normalization = "l2"
        
        warnings = validate_vsa_config(config)
        
        # Should be compatible combination
        compatibility_warnings = [w for w in warnings if "compatibility" in w.lower()]
        assert len(compatibility_warnings) == 0


class TestVSAParameterRanges:
    """Test VSA parameter range validation."""
    
    def test_dimension_range_validation(self):
        """Test vector dimension range validation."""
        # Valid dimensions
        valid_dimensions = [256, 512, 1024, 2048]
        for dim in valid_dimensions:
            config = VSAComprehensiveConfig(vector_dimension=dim)
            warnings = validate_vsa_config(config)
            dimension_errors = [w for w in warnings if "dimension" in w.lower() and "❌" in w]
            assert len(dimension_errors) == 0
        
        # Invalid dimensions
        invalid_dimensions = [0, -100, 50, 10000]  
        for dim in invalid_dimensions:
            config = VSAComprehensiveConfig(vector_dimension=dim)
            warnings = validate_vsa_config(config)
            dimension_errors = [w for w in warnings if "dimension" in w.lower() and "❌" in w]
            assert len(dimension_errors) > 0
    
    def test_probability_range_validation(self):
        """Test probability parameter range validation."""
        # Valid probabilities
        valid_probs = [0.0, 0.1, 0.5, 0.9, 1.0]
        for prob in valid_probs:
            config = VSAComprehensiveConfig(
                noise_tolerance=prob,
                binding_strength=prob,
                cleanup_threshold=prob
            )
            warnings = validate_vsa_config(config)
            prob_errors = [w for w in warnings if "between 0 and 1" in w]
            assert len(prob_errors) == 0
        
        # Invalid probabilities
        invalid_probs = [-0.1, 1.5, -1.0, 2.0]
        for prob in invalid_probs:
            config = VSAComprehensiveConfig(noise_tolerance=prob)
            warnings = validate_vsa_config(config)
            prob_errors = [w for w in warnings if "between 0 and 1" in w]
            assert len(prob_errors) > 0
    
    def test_count_parameter_validation(self):
        """Test count parameter validation."""
        # Valid counts
        config = VSAComprehensiveConfig(
            expected_symbol_count=100,
            max_binding_depth=5,
            cleanup_iterations=10
        )
        warnings = validate_vsa_config(config)
        count_errors = [w for w in warnings if "must be positive" in w]
        assert len(count_errors) == 0
        
        # Invalid counts
        config_invalid = VSAComprehensiveConfig(
            expected_symbol_count=-10,
            max_binding_depth=0,
            cleanup_iterations=-5
        )
        warnings = validate_vsa_config(config_invalid)
        count_errors = [w for w in warnings if "must be positive" in w]
        assert len(count_errors) > 0


class TestVSAConfigurationPresets:
    """Test VSA configuration presets for different use cases."""
    
    def test_all_presets_valid(self):
        """Test that all preset configurations are valid."""
        presets = [
            create_research_accurate_config(),
            create_capacity_optimized_config()
        ]
        
        for preset in presets:
            warnings = validate_vsa_config(preset)
            
            # No preset should have critical errors
            critical_errors = [w for w in warnings if "🚨 CRITICAL" in w or "❌" in w]
            assert len(critical_errors) == 0, f"Preset has critical errors: {critical_errors}"
    
    def test_preset_parameter_consistency(self):
        """Test parameter consistency within presets."""
        research_config = create_research_accurate_config()
        
        # Research preset should be internally consistent
        assert research_config.validate_against_plate_paper == True
        assert research_config.comprehensive_error_checking == True
        assert research_config.high_precision_arithmetic == True
        
        # Auto-dimension should be disabled for research accuracy
        assert research_config.enable_auto_dimension_selection == False
        
        capacity_config = create_capacity_optimized_config()
        
        # Capacity preset should enable optimization features
        assert capacity_config.enable_auto_dimension_selection == True
        assert capacity_config.capacity_monitoring_enabled == True
        assert capacity_config.adaptive_noise_threshold == True
    
    def test_preset_specialization(self):
        """Test that presets are specialized for their intended use."""
        research_config = create_research_accurate_config()
        capacity_config = create_capacity_optimized_config()
        
        # Research config should prioritize accuracy over performance
        research_perf_features = [
            research_config.enable_gpu_acceleration,
            research_config.batch_processing_enabled,
            research_config.memory_efficient_storage
        ]
        
        # Capacity config should enable more performance features
        capacity_perf_features = [
            capacity_config.enable_gpu_acceleration,
            capacity_config.batch_processing_enabled,
            capacity_config.memory_efficient_storage
        ]
        
        # Capacity config should have more performance features enabled
        assert sum(capacity_perf_features) >= sum(research_perf_features)


class TestVSAResearchAccuracy:
    """Test research accuracy validation."""
    
    def test_plate_1995_compliance(self):
        """Test compliance with Plate (1995) HRR specifications."""
        config = create_research_accurate_config()
        
        # Should match Plate (1995) HRR specifications
        assert config.vector_distribution == VectorDistribution.GAUSSIAN_RANDOM
        assert config.binding_operation == BindingOperation.CIRCULAR_CONVOLUTION
        assert config.unbinding_strategy == UnbindingStrategy.APPROXIMATE_INVERSE
        assert config.similarity_metric == SimilarityMetric.COSINE_SIMILARITY
    
    def test_capacity_formula_accuracy(self):
        """Test that capacity calculations match theoretical predictions."""
        # Test various symbol counts
        test_cases = [
            (50, 2.5),   # Small vocabulary
            (200, 2.5),  # Medium vocabulary  
            (800, 2.5),  # Large vocabulary
        ]
        
        for symbol_count, capacity_factor in test_cases:
            dimension = auto_select_dimension(symbol_count, capacity_factor)
            
            # Theoretical capacity should be reasonable
            # For Gaussian random vectors, capacity ≈ dimension / (2 * log(dimension))
            theoretical_capacity = dimension / (2 * np.log(dimension))
            
            # Selected dimension should provide sufficient capacity
            assert theoretical_capacity >= symbol_count
    
    def test_binding_operation_mathematical_properties(self):
        """Test mathematical properties of binding operations."""
        config = create_research_accurate_config()
        
        # Circular convolution should be commutative
        assert config.binding_operation == BindingOperation.CIRCULAR_CONVOLUTION
        
        # For research accuracy, should validate mathematical properties
        assert config.validate_binding_properties == True
        assert config.test_commutativity == True
        assert config.test_associativity == True
        assert config.test_inverse_property == True


if __name__ == "__main__":
    # Run comprehensive VSA tests
    print("🧠 Running comprehensive VSA FIXME solution tests...")
    
    test_classes = [
        TestVSAComprehensiveConfig,
        TestAutoDimensionSelection,
        TestVSAConfigurationIntegration,
        TestVSAParameterRanges,
        TestVSAConfigurationPresets,
        TestVSAResearchAccuracy
    ]
    
    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}...")
        instance = test_class()
        
        # Run all test methods
        for method_name in dir(instance):
            if method_name.startswith('test_'):
                try:
                    method = getattr(instance, method_name)
                    method()
                    print(f"   ✅ {method_name}")
                except Exception as e:
                    print(f"   ❌ {method_name}: {e}")
    
    print("\n🎉 Comprehensive VSA FIXME solution testing complete!")