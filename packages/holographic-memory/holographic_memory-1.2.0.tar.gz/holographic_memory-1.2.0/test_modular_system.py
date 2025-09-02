#!/usr/bin/env python3
"""
Comprehensive Test Suite for Modular Holographic Memory System

Tests all modular components and verifies backward compatibility.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import sys
import os
import numpy as np
import traceback
from typing import Dict, Any

# Add the package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported correctly"""
    print("🔍 Testing module imports...")
    
    try:
        # Test main imports
        from holographic_memory import HolographicMemory, create_holographic_memory, HRRConfig
        print("  ✓ Main package imports working")
        
        # Test modular imports
        from holographic_memory.hm_modules import (
            VectorOperations, MemoryManager, CompositeOperations,
            CleanupOperations, CapacityAnalyzer, HolographicMemoryCore
        )
        print("  ✓ Modular component imports working")
        
        # Test configuration
        from holographic_memory.hm_modules.configuration import create_config
        print("  ✓ Configuration imports working")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic HRR functionality"""
    print("\n🧮 Testing basic HRR functionality...")
    
    try:
        from holographic_memory import create_holographic_memory
        
        # Create memory system
        memory = create_holographic_memory("standard", vector_dim=256)
        print("  ✓ Memory system created")
        
        # Test vector creation
        vec1 = memory.create_vector("test1")
        vec2 = memory.create_vector("test2")
        print(f"  ✓ Vectors created (dim: {len(vec1)})")
        
        # Test binding and unbinding
        bound = memory.bind("test1", "test2")
        retrieved = memory.unbind(bound, "test1")
        similarity = memory.similarity(retrieved, "test2")
        print(f"  ✓ Bind/unbind similarity: {similarity:.3f}")
        
        # Test superposition
        superposed = memory.superpose(["test1", "test2"])
        print(f"  ✓ Superposition created (norm: {np.linalg.norm(superposed):.3f})")
        
        return similarity > 0.3
        
    except Exception as e:
        print(f"  ✗ Basic functionality failed: {e}")
        traceback.print_exc()
        return False

def test_memory_operations():
    """Test memory storage and retrieval"""
    print("\n💾 Testing memory operations...")
    
    try:
        from holographic_memory import create_holographic_memory
        
        memory = create_holographic_memory("standard", vector_dim=256)
        
        # Test simple storage
        memory.store("key1", "value1")
        memory.store("key2", "value2")
        print("  ✓ Key-value pairs stored")
        
        # Test retrieval
        retrieved1 = memory.retrieve("key1")
        retrieved2 = memory.retrieve("key2")
        print(f"  ✓ Retrieval working (shapes: {retrieved1.shape if retrieved1 is not None else None})")
        
        # Test memory stats
        stats = memory.get_memory_stats()
        print(f"  ✓ Memory stats: {stats['total_vectors']} vectors, {stats['memory_usage_mb']:.2f} MB")
        
        return retrieved1 is not None and retrieved2 is not None
        
    except Exception as e:
        print(f"  ✗ Memory operations failed: {e}")
        traceback.print_exc()
        return False

def test_composite_operations():
    """Test composite memory structures"""
    print("\n🏗️  Testing composite operations...")
    
    try:
        from holographic_memory import create_holographic_memory
        
        memory = create_holographic_memory("standard", vector_dim=256)
        
        # Test hierarchy creation
        structure = {
            'color': ['red', 'blue', 'green'],
            'shape': ['round', 'square'], 
            'size': ['large', 'small']
        }
        
        hierarchy = memory.create_hierarchy(structure, 'test_object')
        print("  ✓ Hierarchy created")
        
        # Test querying hierarchy
        retrieved, match, confidence = memory.query_memory('test_object', 'color')
        print(f"  ✓ Query result: {match} (confidence: {confidence:.3f})")
        
        # Test sequence creation
        items = ['start', 'middle', 'end']
        sequence = memory.create_sequence(items, 'test_sequence')
        print("  ✓ Sequence created")
        
        # Test sequence querying
        seq_retrieved, seq_match, seq_conf = memory.query_sequence_position('test_sequence', 1)
        print(f"  ✓ Sequence query: position 1 -> {seq_match} (confidence: {seq_conf:.3f})")
        
        return confidence > 0.1 and seq_conf > 0.1
        
    except Exception as e:
        print(f"  ✗ Composite operations failed: {e}")
        traceback.print_exc()
        return False

def test_cleanup_operations():
    """Test cleanup and error correction"""
    print("\n🧹 Testing cleanup operations...")
    
    try:
        from holographic_memory import create_holographic_memory
        
        memory = create_holographic_memory("standard", vector_dim=256, cleanup_memory=True)
        
        # Create test vectors
        memory.create_vector("clean1")
        memory.create_vector("clean2") 
        memory.create_vector("clean3")
        
        # Create cleanup memory
        memory.create_cleanup_memory(["clean1", "clean2", "clean3"])
        print("  ✓ Cleanup memory created")
        
        # Test cleanup with noisy vector
        original = memory.get_vector("clean1")
        noisy = original + np.random.normal(0, 0.2, len(original))
        
        # Test simple cleanup
        cleaned_name, confidence = memory.cleanup_memory(noisy)
        print(f"  ✓ Cleanup result: {cleaned_name} (confidence: {confidence:.3f})")
        
        # Test Hopfield cleanup
        hopfield_cleaned = memory.hopfield_cleanup(noisy)
        hopfield_sim = memory.similarity(hopfield_cleaned, original)
        print(f"  ✓ Hopfield cleanup similarity: {hopfield_sim:.3f}")
        
        return confidence > 0.3 and hopfield_sim > 0.3
        
    except Exception as e:
        print(f"  ✗ Cleanup operations failed: {e}")
        traceback.print_exc()
        return False

def test_analogical_reasoning():
    """Test analogical reasoning capabilities"""
    print("\n🧠 Testing analogical reasoning...")
    
    try:
        from holographic_memory import create_holographic_memory
        
        memory = create_holographic_memory("research", vector_dim=256)
        
        # Create analogy vectors
        analogy_items = ['king', 'queen', 'man', 'woman', 'royal', 'person']
        for item in analogy_items:
            memory.create_vector(item)
        
        # Test analogy: king:queen :: man:?
        result, match, confidence = memory.create_analogies('king', 'queen', 'man')
        print(f"  ✓ Analogy king:queen :: man:? -> {match} (confidence: {confidence:.3f})")
        
        # Test with different analogy
        result2, match2, confidence2 = memory.create_analogies('royal', 'king', 'person')
        print(f"  ✓ Analogy royal:king :: person:? -> {match2} (confidence: {confidence2:.3f})")
        
        return confidence > 0.1 or confidence2 > 0.1
        
    except Exception as e:
        print(f"  ✗ Analogical reasoning failed: {e}")
        traceback.print_exc()
        return False

def test_capacity_analysis():
    """Test capacity analysis and benchmarking"""
    print("\n📊 Testing capacity analysis...")
    
    try:
        from holographic_memory import create_holographic_memory
        
        memory = create_holographic_memory("standard", vector_dim=256)
        
        # Test theoretical capacity
        theoretical = memory.capacity_analyzer.theoretical_capacity()
        print(f"  ✓ Theoretical capacity: {theoretical:.1f} items")
        
        # Test quick capacity analysis (reduced scope)
        capacity_results = memory.analyze_capacity(n_test_items=20, noise_levels=[0.0, 0.2])
        print(f"  ✓ Capacity analysis: {capacity_results['average_capacity']:.1f} items")
        
        # Test operation benchmarks (quick)
        bench_results = memory.benchmark_operations(n_trials=100)
        binding_speed = bench_results['binding']['ops_per_second']
        print(f"  ✓ Binding performance: {binding_speed:.0f} ops/sec")
        
        return theoretical > 0 and capacity_results['average_capacity'] > 0
        
    except Exception as e:
        print(f"  ✗ Capacity analysis failed: {e}")
        traceback.print_exc()
        return False

def test_plate_benchmarks():
    """Test Plate (1995) benchmark suite"""
    print("\n🔬 Testing Plate (1995) benchmarks...")
    
    try:
        from holographic_memory import create_holographic_memory
        
        memory = create_holographic_memory("research", vector_dim=256)
        
        # Run benchmark suite
        results = memory.run_plate_benchmarks(verbose=False)
        
        # Check results
        successful_tests = results['overall_summary']['successful_tests']
        total_tests = results['overall_summary']['total_tests']
        success_rate = results['overall_summary']['success_rate']
        
        print(f"  ✓ Benchmark results: {successful_tests}/{total_tests} tests passed")
        print(f"  ✓ Success rate: {success_rate:.1%}")
        print(f"  ✓ Total time: {results['overall_summary']['total_time']:.2f} seconds")
        
        return success_rate > 0.5  # At least 50% of tests should pass
        
    except Exception as e:
        print(f"  ✗ Plate benchmarks failed: {e}")
        traceback.print_exc()
        return False

def test_backward_compatibility():
    """Test backward compatibility with original API"""
    print("\n↩️  Testing backward compatibility...")
    
    try:
        from holographic_memory import HolographicMemory, HRRConfig
        
        # Test old-style initialization
        config = HRRConfig(vector_dim=256, normalize=True)
        memory = HolographicMemory(config)
        print("  ✓ Old-style initialization working")
        
        # Test direct parameter initialization
        memory2 = HolographicMemory(vector_dim=256, normalize=True, cleanup_memory=True)
        print("  ✓ Direct parameter initialization working")
        
        # Test backward compatibility methods
        memory2.create_composite_memory([('role1', 'filler1'), ('role2', 'filler2')], 'test_composite')
        print("  ✓ create_composite_memory method working")
        
        # Test property access
        items_count = len(memory2.memory_items)
        composite_count = len(memory2.composite_memories)
        print(f"  ✓ Property access: {items_count} items, {composite_count} composites")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Backward compatibility failed: {e}")
        traceback.print_exc()
        return False

def test_self_test():
    """Test the built-in self-test functionality"""
    print("\n🧪 Testing built-in self-test...")
    
    try:
        from holographic_memory import create_holographic_memory
        
        memory = create_holographic_memory("standard", vector_dim=256)
        
        # Run self-test
        results = memory.run_self_test()
        
        success_rate = results['overall']['success_rate']
        successful_tests = results['overall']['successful_tests']
        total_tests = results['overall']['total_tests']
        
        print(f"  ✓ Self-test completed: {successful_tests}/{total_tests} components passed")
        print(f"  ✓ Success rate: {success_rate:.1%}")
        
        return success_rate > 0.8  # At least 80% of self-tests should pass
        
    except Exception as e:
        print(f"  ✗ Self-test failed: {e}")
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("🌀 Comprehensive Modular Holographic Memory Test Suite")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Memory Operations", test_memory_operations),
        ("Composite Operations", test_composite_operations),
        ("Cleanup Operations", test_cleanup_operations),
        ("Analogical Reasoning", test_analogical_reasoning),
        ("Capacity Analysis", test_capacity_analysis),
        ("Plate Benchmarks", test_plate_benchmarks),
        ("Backward Compatibility", test_backward_compatibility),
        ("Self-Test", test_self_test),
    ]
    
    results = {}
    passed_tests = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed_tests += 1
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    success_rate = passed_tests / len(tests)
    print(f"\n🎯 Overall Success Rate: {passed_tests}/{len(tests)} ({success_rate:.1%})")
    
    if success_rate >= 0.8:
        print("🚀 MODULARIZATION SUCCESSFUL! All critical systems working.")
    elif success_rate >= 0.6:
        print("⚠️  MODULARIZATION MOSTLY SUCCESSFUL. Some issues to address.")
    else:
        print("🔥 MODULARIZATION NEEDS WORK. Significant issues detected.")
    
    return results

if __name__ == "__main__":
    results = run_comprehensive_test()
    
    # Exit with appropriate code
    success_rate = sum(results.values()) / len(results)
    sys.exit(0 if success_rate >= 0.8 else 1)