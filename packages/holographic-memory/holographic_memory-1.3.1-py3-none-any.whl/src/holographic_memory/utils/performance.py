"""
⚡ Performance Monitoring Utilities
=================================

This module provides utilities for monitoring and optimizing performance
in the holographic memory system, including profiling and benchmarking tools.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import time
import psutil
import functools
from typing import Dict, Any, Optional, Callable, List, Tuple
from dataclasses import dataclass, field
from contextlib import contextmanager
import numpy as np
import warnings


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    
    execution_time: float = 0.0
    memory_used_mb: float = 0.0
    peak_memory_mb: float = 0.0
    cpu_percent: float = 0.0
    operations_per_second: Optional[float] = None
    function_name: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProfileManager:
    """
    Manager for collecting and analyzing performance profiles.
    """
    
    def __init__(self):
        self.profiles: List[PerformanceMetrics] = []
        self.active_profiles: Dict[str, float] = {}
        self.memory_baseline: float = self._get_memory_usage()
    
    def start_profile(self, name: str) -> None:
        """Start profiling a named operation."""
        self.active_profiles[name] = time.perf_counter()
    
    def end_profile(self, name: str, 
                   operation_count: Optional[int] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> PerformanceMetrics:
        """End profiling and record metrics."""
        if name not in self.active_profiles:
            raise ValueError(f"No active profile found for '{name}'")
        
        end_time = time.perf_counter()
        start_time = self.active_profiles.pop(name)
        execution_time = end_time - start_time
        
        # Collect system metrics
        current_memory = self._get_memory_usage()
        memory_used = current_memory - self.memory_baseline
        
        try:
            cpu_percent = psutil.cpu_percent()
        except:
            cpu_percent = 0.0
        
        # Calculate operations per second
        ops_per_second = None
        if operation_count is not None and execution_time > 0:
            ops_per_second = operation_count / execution_time
        
        metrics = PerformanceMetrics(
            execution_time=execution_time,
            memory_used_mb=memory_used,
            peak_memory_mb=current_memory,
            cpu_percent=cpu_percent,
            operations_per_second=ops_per_second,
            function_name=name,
            metadata=metadata or {}
        )
        
        self.profiles.append(metrics)
        return metrics
    
    def get_summary(self, function_name: Optional[str] = None) -> Dict[str, Any]:
        """Get summary statistics for profiles."""
        if function_name:
            profiles = [p for p in self.profiles if p.function_name == function_name]
        else:
            profiles = self.profiles
        
        if not profiles:
            return {}
        
        execution_times = [p.execution_time for p in profiles]
        memory_usage = [p.memory_used_mb for p in profiles]
        
        return {
            'count': len(profiles),
            'total_time': sum(execution_times),
            'mean_time': np.mean(execution_times),
            'std_time': np.std(execution_times),
            'min_time': min(execution_times),
            'max_time': max(execution_times),
            'mean_memory_mb': np.mean(memory_usage),
            'max_memory_mb': max(memory_usage),
            'total_operations': sum(p.operations_per_second * p.execution_time 
                                  for p in profiles 
                                  if p.operations_per_second is not None)
        }
    
    def clear_profiles(self, function_name: Optional[str] = None) -> None:
        """Clear stored profiles."""
        if function_name:
            self.profiles = [p for p in self.profiles if p.function_name != function_name]
        else:
            self.profiles.clear()
    
    @staticmethod
    def _get_memory_usage() -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except:
            return 0.0


class MemoryTracker:
    """
    Context manager for tracking memory usage.
    """
    
    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_memory = 0.0
        self.peak_memory = 0.0
        self.end_memory = 0.0
    
    def __enter__(self):
        self.start_memory = self._get_memory()
        self.peak_memory = self.start_memory
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_memory = self._get_memory()
    
    def update_peak(self):
        """Update peak memory usage."""
        current = self._get_memory()
        if current > self.peak_memory:
            self.peak_memory = current
    
    @property
    def memory_delta(self) -> float:
        """Memory usage change in MB."""
        return self.end_memory - self.start_memory
    
    @property
    def peak_delta(self) -> float:
        """Peak memory above baseline in MB."""
        return self.peak_memory - self.start_memory
    
    @staticmethod
    def _get_memory() -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except:
            return 0.0


class TimeTracker:
    """
    Context manager for tracking execution time.
    """
    
    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_time = 0.0
        self.end_time = 0.0
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
    
    @property
    def elapsed_time(self) -> float:
        """Elapsed time in seconds."""
        return self.end_time - self.start_time
    
    @property
    def elapsed_ms(self) -> float:
        """Elapsed time in milliseconds."""
        return self.elapsed_time * 1000


def benchmark_operation(func: Callable, 
                       *args, 
                       n_runs: int = 10,
                       warmup_runs: int = 2,
                       **kwargs) -> Dict[str, Any]:
    """
    Benchmark a function with multiple runs.
    
    Parameters
    ----------
    func : Callable
        Function to benchmark
    *args : Any
        Function arguments
    n_runs : int, default=10
        Number of benchmark runs
    warmup_runs : int, default=2
        Number of warmup runs (not counted)
    **kwargs : Any
        Function keyword arguments
        
    Returns
    -------
    Dict[str, Any]
        Benchmark results
    """
    # Warmup runs
    for _ in range(warmup_runs):
        try:
            func(*args, **kwargs)
        except Exception:
            pass
    
    # Benchmark runs
    times = []
    memory_deltas = []
    results = []
    
    for i in range(n_runs):
        with MemoryTracker() as mem_tracker:
            with TimeTracker() as time_tracker:
                try:
                    result = func(*args, **kwargs)
                    results.append(result)
                    success = True
                except Exception as e:
                    results.append(e)
                    success = False
            
            if success:
                times.append(time_tracker.elapsed_time)
                memory_deltas.append(mem_tracker.memory_delta)
    
    if not times:
        return {
            'error': 'All benchmark runs failed',
            'n_runs': n_runs,
            'successful_runs': 0
        }
    
    return {
        'n_runs': n_runs,
        'successful_runs': len(times),
        'mean_time': np.mean(times),
        'std_time': np.std(times),
        'min_time': min(times),
        'max_time': max(times),
        'median_time': np.median(times),
        'mean_memory_delta_mb': np.mean(memory_deltas),
        'max_memory_delta_mb': max(memory_deltas) if memory_deltas else 0,
        'times': times,
        'memory_deltas': memory_deltas,
        'results': results
    }


def memory_usage() -> Dict[str, float]:
    """
    Get current memory usage information.
    
    Returns
    -------
    Dict[str, float]
        Memory usage statistics
    """
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / (1024 * 1024),
            'vms_mb': memory_info.vms / (1024 * 1024),
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / (1024 * 1024),
            'total_mb': psutil.virtual_memory().total / (1024 * 1024)
        }
    except Exception as e:
        warnings.warn(f"Cannot get memory usage: {e}")
        return {}


@contextmanager
def execution_timer(name: str = "operation", 
                   print_result: bool = True):
    """
    Context manager for timing code execution.
    
    Parameters
    ----------
    name : str, default="operation"
        Name of the operation
    print_result : bool, default=True
        Whether to print the timing result
    """
    start_time = time.perf_counter()
    try:
        yield
    finally:
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        if print_result:
            if elapsed < 0.001:
                print(f"{name} completed in {elapsed * 1000000:.1f} μs")
            elif elapsed < 1.0:
                print(f"{name} completed in {elapsed * 1000:.1f} ms")
            else:
                print(f"{name} completed in {elapsed:.3f} s")


def profile_function(include_memory: bool = True, 
                    include_return_value: bool = False):
    """
    Decorator to profile function execution.
    
    Parameters
    ----------
    include_memory : bool, default=True
        Whether to track memory usage
    include_return_value : bool, default=False
        Whether to include return value in profile
        
    Returns
    -------
    Callable
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            
            if include_memory:
                start_memory = MemoryTracker._get_memory()
            
            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                result = e
                success = False
            
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            
            # Create profile info
            profile_info = {
                'function_name': func.__name__,
                'execution_time': execution_time,
                'success': success,
                'args_count': len(args),
                'kwargs_count': len(kwargs)
            }
            
            if include_memory:
                end_memory = MemoryTracker._get_memory()
                profile_info['memory_delta_mb'] = end_memory - start_memory
            
            if include_return_value and success:
                if hasattr(result, '__len__') and not isinstance(result, str):
                    profile_info['return_size'] = len(result)
                else:
                    profile_info['return_type'] = type(result).__name__
            
            # Store profile (could extend to use ProfileManager)
            if not hasattr(func, '_profiles'):
                func._profiles = []
            func._profiles.append(profile_info)
            
            if not success:
                raise result
            
            return result
        
        # Add method to get profiles
        def get_profiles():
            return getattr(func, '_profiles', [])
        
        def clear_profiles():
            if hasattr(func, '_profiles'):
                func._profiles.clear()
        
        wrapper.get_profiles = get_profiles
        wrapper.clear_profiles = clear_profiles
        
        return wrapper
    
    return decorator


class PerformanceAnalyzer:
    """
    Analyzer for performance data and bottleneck identification.
    """
    
    def __init__(self):
        self.profiles: List[PerformanceMetrics] = []
    
    def add_profiles(self, profiles: List[PerformanceMetrics]) -> None:
        """Add profiles to the analyzer."""
        self.profiles.extend(profiles)
    
    def identify_bottlenecks(self, 
                           time_threshold: float = 1.0,
                           memory_threshold_mb: float = 100.0) -> Dict[str, List[str]]:
        """
        Identify performance bottlenecks.
        
        Parameters
        ----------
        time_threshold : float, default=1.0
            Execution time threshold in seconds
        memory_threshold_mb : float, default=100.0
            Memory usage threshold in MB
            
        Returns
        -------
        Dict[str, List[str]]
            Dictionary of bottleneck types and affected functions
        """
        bottlenecks = {
            'slow_functions': [],
            'memory_intensive': [],
            'frequent_calls': []
        }
        
        # Group profiles by function
        function_stats = {}
        for profile in self.profiles:
            func_name = profile.function_name
            if func_name not in function_stats:
                function_stats[func_name] = {
                    'times': [],
                    'memory_usage': [],
                    'call_count': 0
                }
            
            function_stats[func_name]['times'].append(profile.execution_time)
            function_stats[func_name]['memory_usage'].append(profile.memory_used_mb)
            function_stats[func_name]['call_count'] += 1
        
        # Analyze each function
        for func_name, stats in function_stats.items():
            # Check execution time
            mean_time = np.mean(stats['times'])
            if mean_time > time_threshold:
                bottlenecks['slow_functions'].append(func_name)
            
            # Check memory usage
            max_memory = max(stats['memory_usage'])
            if max_memory > memory_threshold_mb:
                bottlenecks['memory_intensive'].append(func_name)
            
            # Check call frequency (top 10% of functions by call count)
            call_counts = [s['call_count'] for s in function_stats.values()]
            if len(call_counts) > 10:  # Only if we have enough data
                threshold_90th = np.percentile(call_counts, 90)
                if stats['call_count'] >= threshold_90th:
                    bottlenecks['frequent_calls'].append(func_name)
        
        return bottlenecks
    
    def generate_report(self) -> str:
        """Generate a performance analysis report."""
        if not self.profiles:
            return "No performance data available"
        
        report = ["Performance Analysis Report", "=" * 30, ""]
        
        # Overall statistics
        total_time = sum(p.execution_time for p in self.profiles)
        total_memory = sum(p.memory_used_mb for p in self.profiles)
        
        report.extend([
            f"Total Profiles: {len(self.profiles)}",
            f"Total Execution Time: {total_time:.3f} seconds",
            f"Total Memory Used: {total_memory:.1f} MB",
            ""
        ])
        
        # Function breakdown
        function_stats = {}
        for profile in self.profiles:
            func_name = profile.function_name
            if func_name not in function_stats:
                function_stats[func_name] = {
                    'times': [],
                    'memory': [],
                    'count': 0
                }
            
            function_stats[func_name]['times'].append(profile.execution_time)
            function_stats[func_name]['memory'].append(profile.memory_used_mb)
            function_stats[func_name]['count'] += 1
        
        report.append("Function Performance:")
        report.append("-" * 20)
        
        for func_name, stats in sorted(function_stats.items(), 
                                     key=lambda x: sum(x[1]['times']), 
                                     reverse=True):
            total_func_time = sum(stats['times'])
            mean_func_time = np.mean(stats['times'])
            max_memory = max(stats['memory'])
            
            report.append(
                f"{func_name:25} | "
                f"Calls: {stats['count']:4d} | "
                f"Total: {total_func_time:8.3f}s | "
                f"Mean: {mean_func_time:8.3f}s | "
                f"Max Mem: {max_memory:6.1f}MB"
            )
        
        # Bottlenecks
        bottlenecks = self.identify_bottlenecks()
        if any(bottlenecks.values()):
            report.extend(["", "Identified Bottlenecks:", "-" * 20])
            
            for category, functions in bottlenecks.items():
                if functions:
                    report.append(f"{category}: {', '.join(functions)}")
        
        return "\n".join(report)