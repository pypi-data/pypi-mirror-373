"""
Core benchmarking utilities for Klotho graph performance measurement.

Provides consistent framework for running and reporting benchmark results
during the RustworkX refactoring project.
"""
import time
import statistics
from typing import Callable, Dict, List, Any, Optional
import json
from pathlib import Path


class BenchmarkResult:
    """Container for benchmark timing and metadata."""
    
    def __init__(self, name: str, times: List[float], metadata: Optional[Dict] = None):
        self.name = name
        self.times = times
        self.metadata = metadata or {}
        
    @property
    def mean(self) -> float:
        """Mean execution time."""
        return statistics.mean(self.times)
    
    @property
    def median(self) -> float:
        """Median execution time."""
        return statistics.median(self.times)
    
    @property
    def stdev(self) -> float:
        """Standard deviation of execution times."""
        return statistics.stdev(self.times) if len(self.times) > 1 else 0.0
    
    @property
    def min_time(self) -> float:
        """Minimum execution time."""
        return min(self.times)
    
    @property
    def max_time(self) -> float:
        """Maximum execution time."""
        return max(self.times)
    
    def coefficient_of_variation(self) -> float:
        """Coefficient of variation (stdev/mean) as percentage."""
        return (self.stdev / self.mean) * 100 if self.mean > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'times': self.times,
            'mean': self.mean,
            'median': self.median,
            'stdev': self.stdev,
            'min': self.min_time,
            'max': self.max_time,
            'cv_percent': self.coefficient_of_variation(),
            'metadata': self.metadata
        }


class BenchmarkRunner:
    """Framework for running consistent performance benchmarks."""
    
    def __init__(self, warmup_runs: int = 3, timing_runs: int = 10):
        self.warmup_runs = warmup_runs
        self.timing_runs = timing_runs
        self.results: List[BenchmarkResult] = []
    
    def benchmark(self, 
                  func: Callable, 
                  name: str, 
                  setup_func: Optional[Callable] = None,
                  teardown_func: Optional[Callable] = None,
                  metadata: Optional[Dict] = None) -> BenchmarkResult:
        """
        Benchmark a function with consistent methodology.
        
        Args:
            func: Function to benchmark
            name: Name for the benchmark
            setup_func: Optional setup function called before each run
            teardown_func: Optional teardown function called after each run
            metadata: Optional metadata to store with results
            
        Returns:
            BenchmarkResult containing timing data
        """
        # Warmup runs
        for _ in range(self.warmup_runs):
            if setup_func:
                setup_func()
            func()
            if teardown_func:
                teardown_func()
        
        # Timing runs
        times = []
        for _ in range(self.timing_runs):
            if setup_func:
                setup_func()
            
            start_time = time.perf_counter()
            func()
            end_time = time.perf_counter()
            
            if teardown_func:
                teardown_func()
            
            times.append(end_time - start_time)
        
        result = BenchmarkResult(name, times, metadata)
        self.results.append(result)
        return result
    
    def save_results(self, filepath: Path):
        """Save benchmark results to JSON file."""
        data = {
            'config': {
                'warmup_runs': self.warmup_runs,
                'timing_runs': self.timing_runs
            },
            'results': [result.to_dict() for result in self.results]
        }
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def clear_results(self):
        """Clear all stored results."""
        self.results.clear()
    
    def print_summary(self):
        """Print a summary of all benchmark results."""
        if not self.results:
            print("No benchmark results available.")
            return
        
        print(f"\nBenchmark Results Summary ({len(self.results)} tests)")
        print("=" * 80)
        print(f"{'Test Name':<40} {'Mean (ms)':<12} {'CV%':<8} {'Min (ms)':<12} {'Max (ms)':<12}")
        print("-" * 80)
        
        for result in self.results:
            mean_ms = result.mean * 1000
            min_ms = result.min_time * 1000
            max_ms = result.max_time * 1000
            cv = result.coefficient_of_variation()
            
            print(f"{result.name:<40} {mean_ms:<12.3f} {cv:<8.1f} {min_ms:<12.3f} {max_ms:<12.3f}")


def compare_results(baseline_file: Path, current_file: Path) -> Dict[str, Dict]:
    """
    Compare benchmark results from two files.
    
    Args:
        baseline_file: Path to baseline results JSON
        current_file: Path to current results JSON
        
    Returns:
        Dictionary containing comparison metrics
    """
    with open(baseline_file) as f:
        baseline_data = json.load(f)
    
    with open(current_file) as f:
        current_data = json.load(f)
    
    # Create lookup for baseline results
    baseline_lookup = {r['name']: r for r in baseline_data['results']}
    
    comparisons = {}
    for current_result in current_data['results']:
        name = current_result['name']
        
        if name in baseline_lookup:
            baseline_result = baseline_lookup[name]
            
            # Calculate improvement percentage
            baseline_mean = baseline_result['mean']
            current_mean = current_result['mean']
            improvement = ((baseline_mean - current_mean) / baseline_mean) * 100
            
            comparisons[name] = {
                'baseline_mean': baseline_mean,
                'current_mean': current_mean,
                'improvement_percent': improvement,
                'baseline_stdev': baseline_result['stdev'],
                'current_stdev': current_result['stdev'],
                'significant': abs(improvement) > 5.0  # > 5% change considered significant
            }
    
    return comparisons


def print_comparison(comparisons: Dict[str, Dict]):
    """Print a formatted comparison of benchmark results."""
    print(f"\nPerformance Comparison ({len(comparisons)} tests)")
    print("=" * 90)
    print(f"{'Test Name':<40} {'Baseline (ms)':<15} {'Current (ms)':<15} {'Improvement':<15}")
    print("-" * 90)
    
    total_improvements = []
    for name, comp in comparisons.items():
        baseline_ms = comp['baseline_mean'] * 1000
        current_ms = comp['current_mean'] * 1000
        improvement = comp['improvement_percent']
        
        # Color coding for significant changes
        if comp['significant']:
            if improvement > 0:
                status = f"+{improvement:.1f}% ✓"
            else:
                status = f"{improvement:.1f}% ✗"
        else:
            status = f"{improvement:.1f}%"
        
        print(f"{name:<40} {baseline_ms:<15.3f} {current_ms:<15.3f} {status:<15}")
        total_improvements.append(improvement)
    
    if total_improvements:
        avg_improvement = statistics.mean(total_improvements)
        print("-" * 90)
        print(f"{'AVERAGE IMPROVEMENT':<40} {'':<30} {avg_improvement:+.1f}%") 