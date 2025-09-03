"""
⚡ Performance Utilities for Tensor Product Binding
===================================================

This module provides performance monitoring, profiling, and optimization
utilities for the tensor product binding system. It includes timing
decorators, memory profiling, and parallel processing helpers.
"""

import time
import functools
import gc
from typing import Any, Callable, List, Dict, Optional, Iterable
import numpy as np
import warnings
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil
import os


def timing_decorator(func: Callable) -> Callable:
    """
    Decorator to measure function execution time.
    
    Parameters
    ----------
    func : Callable
        Function to time
        
    Returns
    -------
    Callable
        Wrapped function with timing
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        print(f"{func.__name__} executed in {execution_time:.4f} seconds")
        
        # Store timing in result if it's a dict
        if isinstance(result, dict):
            result['_execution_time'] = execution_time
        
        return result
    
    return wrapper


def profile_memory_usage(func: Callable) -> Callable:
    """
    Decorator to profile memory usage of a function.
    
    Parameters
    ----------
    func : Callable
        Function to profile
        
    Returns
    -------
    Callable
        Wrapped function with memory profiling
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Force garbage collection before measurement
        gc.collect()
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Execute function
        result = func(*args, **kwargs)
        
        # Get final memory usage
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_delta = final_memory - initial_memory
        print(f"{func.__name__} memory usage: {memory_delta:+.2f} MB "
              f"(initial: {initial_memory:.2f} MB, final: {final_memory:.2f} MB)")
        
        # Store memory info in result if it's a dict
        if isinstance(result, dict):
            result['_memory_usage'] = {
                'initial_mb': initial_memory,
                'final_mb': final_memory,
                'delta_mb': memory_delta
            }
        
        return result
    
    return wrapper


class PerformanceProfiler:
    """
    🔍 Context manager for detailed performance profiling.
    
    Usage:
        with PerformanceProfiler("my_operation") as prof:
            # ... your code here ...
        print(prof.get_stats())
    """
    
    def __init__(self, operation_name: str = "operation"):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.initial_memory = None
        self.final_memory = None
        self.stats = {}
    
    def __enter__(self):
        gc.collect()
        process = psutil.Process(os.getpid())
        
        self.start_time = time.perf_counter()
        self.initial_memory = process.memory_info().rss / 1024 / 1024
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        
        gc.collect()
        process = psutil.Process(os.getpid())
        self.final_memory = process.memory_info().rss / 1024 / 1024
        
        # Calculate statistics
        self.stats = {
            'operation': self.operation_name,
            'execution_time_sec': self.end_time - self.start_time,
            'initial_memory_mb': self.initial_memory,
            'final_memory_mb': self.final_memory,
            'memory_delta_mb': self.final_memory - self.initial_memory,
            'cpu_count': psutil.cpu_count(),
            'exception_occurred': exc_type is not None
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return self.stats.copy()


def benchmark_binding_operation(operation_func: Callable,
                               role_dims: List[int] = None,
                               filler_dims: List[int] = None,
                               num_iterations: int = 100) -> Dict[str, Any]:
    """
    Benchmark a binding operation across different vector dimensions.
    
    Parameters
    ----------
    operation_func : Callable
        Binding operation function to benchmark
    role_dims : List[int], optional
        List of role vector dimensions to test
    filler_dims : List[int], optional  
        List of filler vector dimensions to test
    num_iterations : int, default=100
        Number of iterations per test
        
    Returns
    -------
    Dict[str, Any]
        Benchmark results
    """
    if role_dims is None:
        role_dims = [32, 64, 128, 256]
    if filler_dims is None:
        filler_dims = role_dims
    
    results = {
        'operation': operation_func.__name__,
        'num_iterations': num_iterations,
        'results': []
    }
    
    for role_dim in role_dims:
        for filler_dim in filler_dims:
            # Generate test vectors
            role_vec = np.random.randn(role_dim)
            filler_vec = np.random.randn(filler_dim)
            
            # Benchmark operation
            times = []
            memory_deltas = []
            
            for _ in range(num_iterations):
                with PerformanceProfiler() as prof:
                    try:
                        result = operation_func(role_vec, filler_vec)
                    except Exception as e:
                        # Skip this configuration if it fails
                        break
                
                stats = prof.get_stats()
                times.append(stats['execution_time_sec'])
                memory_deltas.append(stats['memory_delta_mb'])
            
            if times:  # Only record if we got successful runs
                test_result = {
                    'role_dim': role_dim,
                    'filler_dim': filler_dim,
                    'mean_time_sec': np.mean(times),
                    'std_time_sec': np.std(times),
                    'min_time_sec': np.min(times),
                    'max_time_sec': np.max(times),
                    'mean_memory_delta_mb': np.mean(memory_deltas),
                    'successful_iterations': len(times)
                }
                results['results'].append(test_result)
    
    return results


def batch_process(items: Iterable[Any],
                 process_func: Callable,
                 batch_size: int = 32,
                 show_progress: bool = True) -> List[Any]:
    """
    Process items in batches for memory efficiency.
    
    Parameters
    ----------
    items : Iterable[Any]
        Items to process
    process_func : Callable
        Function to apply to each batch
    batch_size : int, default=32
        Size of each batch
    show_progress : bool, default=True
        Whether to show progress
        
    Returns
    -------
    List[Any]
        Processed results
    """
    items_list = list(items)
    total_items = len(items_list)
    results = []
    
    for i in range(0, total_items, batch_size):
        batch = items_list[i:i + batch_size]
        
        if show_progress:
            batch_num = i // batch_size + 1
            total_batches = (total_items + batch_size - 1) // batch_size
            print(f"Processing batch {batch_num}/{total_batches} "
                  f"(items {i+1}-{min(i+batch_size, total_items)})")
        
        # Process batch
        try:
            batch_result = process_func(batch)
            if isinstance(batch_result, list):
                results.extend(batch_result)
            else:
                results.append(batch_result)
        except Exception as e:
            warnings.warn(f"Batch {batch_num} failed: {e}")
            continue
        
        # Force garbage collection between batches
        gc.collect()
    
    return results


def parallel_map(func: Callable,
                items: Iterable[Any],
                max_workers: Optional[int] = None,
                use_processes: bool = False) -> List[Any]:
    """
    Apply function to items in parallel.
    
    Parameters
    ----------
    func : Callable
        Function to apply to each item
    items : Iterable[Any]
        Items to process
    max_workers : int, optional
        Maximum number of workers (default: CPU count)
    use_processes : bool, default=False
        Use processes instead of threads
        
    Returns
    -------
    List[Any]
        Results in original order
    """
    items_list = list(items)
    
    if len(items_list) == 0:
        return []
    
    if max_workers is None:
        max_workers = min(len(items_list), psutil.cpu_count())
    
    # Choose executor type
    executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
    
    try:
        with executor_class(max_workers=max_workers) as executor:
            results = list(executor.map(func, items_list))
        return results
    
    except Exception as e:
        warnings.warn(f"Parallel processing failed, falling back to sequential: {e}")
        return [func(item) for item in items_list]


def memory_efficient_operation(operation_func: Callable,
                              *args,
                              memory_limit_mb: float = 1000.0,
                              **kwargs) -> Any:
    """
    Execute operation with memory monitoring and cleanup.
    
    Parameters
    ----------
    operation_func : Callable
        Operation to execute
    *args
        Arguments to pass to operation
    memory_limit_mb : float, default=1000.0
        Memory limit in MB (warning if exceeded)
    **kwargs
        Keyword arguments to pass to operation
        
    Returns
    -------
    Any
        Operation result
    """
    # Initial cleanup
    gc.collect()
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024
    
    try:
        # Execute operation
        result = operation_func(*args, **kwargs)
        
        # Check memory usage
        current_memory = process.memory_info().rss / 1024 / 1024
        memory_used = current_memory - initial_memory
        
        if memory_used > memory_limit_mb:
            warnings.warn(f"Operation used {memory_used:.2f} MB "
                         f"(limit: {memory_limit_mb:.2f} MB)")
        
        return result
    
    finally:
        # Cleanup regardless of success/failure
        gc.collect()


class BatchTimer:
    """
    ⏱️ Timer for batch operations with statistics.
    
    Usage:
        timer = BatchTimer()
        for item in items:
            with timer:
                process(item)
        print(timer.get_stats())
    """
    
    def __init__(self):
        self.times = []
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            elapsed = time.perf_counter() - self.start_time
            self.times.append(elapsed)
    
    def get_stats(self) -> Dict[str, float]:
        """Get timing statistics."""
        if not self.times:
            return {'count': 0}
        
        times = np.array(self.times)
        return {
            'count': len(times),
            'total_time': np.sum(times),
            'mean_time': np.mean(times),
            'std_time': np.std(times),
            'min_time': np.min(times),
            'max_time': np.max(times),
            'median_time': np.median(times)
        }
    
    def reset(self):
        """Reset timer statistics."""
        self.times.clear()


def optimize_numpy_performance():
    """
    Apply NumPy performance optimizations.
    
    This function sets NumPy threading and optimization settings
    for better performance in tensor operations.
    """
    try:
        # Set number of threads for BLAS operations
        os.environ['OMP_NUM_THREADS'] = str(psutil.cpu_count())
        os.environ['OPENBLAS_NUM_THREADS'] = str(psutil.cpu_count())
        os.environ['MKL_NUM_THREADS'] = str(psutil.cpu_count())
        
        # Enable NumPy optimization
        np.seterr(over='warn', invalid='warn')
        
        print(f"NumPy performance optimized for {psutil.cpu_count()} threads")
        
    except Exception as e:
        warnings.warn(f"Could not apply all NumPy optimizations: {e}")