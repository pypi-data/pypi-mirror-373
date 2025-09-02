"""
Graph generation benchmarks for Klotho performance measurement.

Tests various graph creation operations to establish baseline performance
before RustworkX optimization refactoring.
"""
import time
import psutil
import os
from typing import Dict, List, Tuple
from klotho.benchmarks.core import BenchmarkRunner, BenchmarkResult
from klotho.topos.graphs import Graph, Tree
from klotho.topos.graphs.lattices import Lattice
from pathlib import Path


class GraphGenerationBenchmarks:
    """Comprehensive benchmarks for graph generation operations."""
    
    def __init__(self):
        self.runner = BenchmarkRunner(warmup_runs=3, timing_runs=10)
        self.memory_measurements = {}
    
    def measure_memory_usage(self, func, name: str) -> Tuple[float, int]:
        """
        Measure memory usage during function execution.
        
        Returns:
            Tuple of (execution_time, peak_memory_mb)
        """
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.perf_counter()
        result = func()
        end_time = time.perf_counter()
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = peak_memory - initial_memory
        
        return end_time - start_time, memory_used
    
    def benchmark_grid_graphs(self) -> List[BenchmarkResult]:
        """Benchmark grid graph generation with various dimensions."""
        results = []
        
        # 1D grids (path graphs)
        for n in [100, 500, 1000]:
            def create_1d_grid():
                return Graph.grid_graph([range(n)])
            
            result = self.runner.benchmark(
                create_1d_grid, 
                f"grid_1d_n{n}",
                metadata={'dimension': 1, 'size': n, 'nodes': n}
            )
            results.append(result)
            
            # Memory measurement
            exec_time, memory_mb = self.measure_memory_usage(create_1d_grid, f"grid_1d_n{n}")
            self.memory_measurements[f"grid_1d_n{n}"] = memory_mb
        
        # 2D grids
        for size in [10, 20, 50, 100]:
            def create_2d_grid():
                return Graph.grid_graph([range(size), range(size)])
            
            result = self.runner.benchmark(
                create_2d_grid,
                f"grid_2d_{size}x{size}",
                metadata={'dimension': 2, 'size': size, 'nodes': size * size}
            )
            results.append(result)
            
            # Memory measurement
            exec_time, memory_mb = self.measure_memory_usage(create_2d_grid, f"grid_2d_{size}x{size}")
            self.memory_measurements[f"grid_2d_{size}x{size}"] = memory_mb
        
        # 3D grids
        for size in [5, 8, 10]:
            def create_3d_grid():
                return Graph.grid_graph([range(size), range(size), range(size)])
            
            result = self.runner.benchmark(
                create_3d_grid,
                f"grid_3d_{size}x{size}x{size}",
                metadata={'dimension': 3, 'size': size, 'nodes': size ** 3}
            )
            results.append(result)
            
            # Memory measurement
            exec_time, memory_mb = self.measure_memory_usage(create_3d_grid, f"grid_3d_{size}x{size}x{size}")
            self.memory_measurements[f"grid_3d_{size}x{size}x{size}"] = memory_mb
        
        # 4D grids (smaller sizes due to exponential growth)
        for size in [3, 4, 5]:
            def create_4d_grid():
                return Graph.grid_graph([range(size), range(size), range(size), range(size)])
            
            result = self.runner.benchmark(
                create_4d_grid,
                f"grid_4d_{size}x{size}x{size}x{size}",
                metadata={'dimension': 4, 'size': size, 'nodes': size ** 4}
            )
            results.append(result)
            
            # Memory measurement
            exec_time, memory_mb = self.measure_memory_usage(create_4d_grid, f"grid_4d_{size}x{size}x{size}x{size}")
            self.memory_measurements[f"grid_4d_{size}x{size}x{size}x{size}"] = memory_mb
        
        return results
    
    def benchmark_complete_graphs(self) -> List[BenchmarkResult]:
        """Benchmark complete graph generation."""
        results = []
        
        for n in [10, 50, 100, 200]:
            def create_complete_graph():
                return Graph.complete_graph(n)
            
            result = self.runner.benchmark(
                create_complete_graph,
                f"complete_n{n}",
                metadata={'type': 'complete', 'nodes': n, 'edges': n * (n - 1) // 2}
            )
            results.append(result)
            
            # Memory measurement
            exec_time, memory_mb = self.measure_memory_usage(create_complete_graph, f"complete_n{n}")
            self.memory_measurements[f"complete_n{n}"] = memory_mb
        
        return results
    
    def benchmark_lattice_creation(self) -> List[BenchmarkResult]:
        """Benchmark lattice creation with different resolutions."""
        results = []
        
        # 2D lattices
        for res in [10, 20, 50]:
            def create_2d_lattice():
                return Lattice(dimensionality=2, resolution=res, bipolar=True)
            
            result = self.runner.benchmark(
                create_2d_lattice,
                f"lattice_2d_res{res}",
                metadata={'type': 'lattice', 'dimension': 2, 'resolution': res}
            )
            results.append(result)
        
        # 3D lattices
        for res in [5, 8, 10]:
            def create_3d_lattice():
                return Lattice(dimensionality=3, resolution=res, bipolar=True)
            
            result = self.runner.benchmark(
                create_3d_lattice,
                f"lattice_3d_res{res}",
                metadata={'type': 'lattice', 'dimension': 3, 'resolution': res}
            )
            results.append(result)
        
        return results
    
    def benchmark_random_graphs(self) -> List[BenchmarkResult]:
        """Benchmark random graph generation with varying densities."""
        results = []
        
        # Note: Klotho doesn't have a built-in random graph generator,
        # so we'll create one manually to benchmark edge addition patterns
        for n in [50, 100]:
            for density in [0.1, 0.5, 0.9]:
                import random
                random.seed(42)  # Consistent results
                
                def create_random_graph():
                    graph = Graph()
                    
                    # Add nodes
                    for i in range(n):
                        graph.add_node(value=i)
                    
                    # Add edges based on density
                    max_edges = n * (n - 1) // 2
                    target_edges = int(max_edges * density)
                    
                    edges_added = 0
                    attempts = 0
                    while edges_added < target_edges and attempts < target_edges * 2:
                        u = random.randint(0, n - 1)
                        v = random.randint(0, n - 1)
                        if u != v and not graph.has_edge(u, v):
                            graph.add_edge(u, v)
                            edges_added += 1
                        attempts += 1
                    
                    return graph
                
                result = self.runner.benchmark(
                    create_random_graph,
                    f"random_n{n}_d{int(density*100)}",
                    metadata={'type': 'random', 'nodes': n, 'density': density}
                )
                results.append(result)
        
        return results
    
    def run_all_benchmarks(self) -> Dict[str, List[BenchmarkResult]]:
        """Run all graph generation benchmarks."""
        print("Running Graph Generation Benchmarks...")
        print("=" * 50)
        
        all_results = {}
        
        print("Benchmarking grid graphs...")
        all_results['grid_graphs'] = self.benchmark_grid_graphs()
        
        print("Benchmarking complete graphs...")
        all_results['complete_graphs'] = self.benchmark_complete_graphs()
        
        print("Benchmarking lattices...")
        all_results['lattices'] = self.benchmark_lattice_creation()
        
        print("Benchmarking random graphs...")
        all_results['random_graphs'] = self.benchmark_random_graphs()
        
        return all_results
    
    def print_results_summary(self):
        """Print a comprehensive summary of all benchmark results."""
        print("\nGraph Generation Benchmark Summary")
        print("=" * 70)
        
        # Print results by category
        categories = {
            'Grid Graphs': [r for r in self.runner.results if 'grid' in r.name],
            'Complete Graphs': [r for r in self.runner.results if 'complete' in r.name],
            'Lattices': [r for r in self.runner.results if 'lattice' in r.name],
            'Random Graphs': [r for r in self.runner.results if 'random' in r.name]
        }
        
        for category, results in categories.items():
            if results:
                print(f"\n{category}:")
                print("-" * 40)
                print(f"{'Test':<25} {'Mean (ms)':<12} {'CV%':<8} {'Memory (MB)':<12}")
                print("-" * 40)
                
                for result in results:
                    mean_ms = result.mean * 1000
                    cv = result.coefficient_of_variation()
                    memory_mb = self.memory_measurements.get(result.name, 0)
                    
                    print(f"{result.name:<25} {mean_ms:<12.2f} {cv:<8.1f} {memory_mb:<12.1f}")
    
    def save_baseline_results(self, filepath: Path):
        """Save baseline results for future comparison."""
        self.runner.save_results(filepath)
        
        # Also save memory measurements
        memory_file = filepath.parent / f"{filepath.stem}_memory.json"
        import json
        with open(memory_file, 'w') as f:
            json.dump(self.memory_measurements, f, indent=2)
        
        print(f"Baseline results saved to {filepath}")
        print(f"Memory measurements saved to {memory_file}")


def main():
    """Run graph generation benchmarks and save baseline results."""
    benchmarks = GraphGenerationBenchmarks()
    
    # Run all benchmarks
    all_results = benchmarks.run_all_benchmarks()
    
    # Print summary
    benchmarks.print_results_summary()
    
    # Save baseline results
    results_dir = Path("klotho/benchmarks/results")
    baseline_file = results_dir / "baseline_graph_generation.json"
    benchmarks.save_baseline_results(baseline_file)
    
    print(f"\nTotal tests run: {len(benchmarks.runner.results)}")
    print("Graph generation benchmarks complete!")


if __name__ == "__main__":
    main() 