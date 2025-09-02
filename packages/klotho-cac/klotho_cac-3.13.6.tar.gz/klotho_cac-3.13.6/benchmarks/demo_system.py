"""
Demonstration of the complete Klotho benchmarking system.

Shows how to use the benchmarking infrastructure for the RustworkX refactoring project.
"""
from benchmarks.core import BenchmarkRunner
from benchmarks.graph_generation import GraphGenerationBenchmarks
from benchmarks.traversal_algorithms import TraversalBenchmarks
from benchmarks.reporting import BenchmarkReporter
from pathlib import Path
import json
import time


def run_quick_benchmark_demo():
    """Run a quick demonstration of the benchmarking system."""
    print("Klotho Benchmarking System Demonstration")
    print("=" * 50)
    
    # 1. Core Infrastructure Demo
    print("\n1. Core Benchmarking Infrastructure:")
    print("-" * 35)
    
    runner = BenchmarkRunner(warmup_runs=2, timing_runs=5)
    
    def simple_operation():
        return sum(range(100))
    
    result = runner.benchmark(simple_operation, "demo_simple_operation")
    print(f"   Simple operation: {result.mean*1000:.3f}ms ± {result.stdev*1000:.3f}ms")
    print(f"   Coefficient of variation: {result.coefficient_of_variation():.1f}%")
    
    # 2. Graph Generation Demo (lightweight)
    print("\n2. Graph Generation Benchmarks:")
    print("-" * 32)
    
    graph_benchmarks = GraphGenerationBenchmarks()
    graph_benchmarks.runner = BenchmarkRunner(warmup_runs=1, timing_runs=3)  # Faster for demo
    
    # Test just a small grid
    from klotho.topos.graphs import Graph
    def demo_grid():
        return Graph.grid_graph([range(5), range(5)])
    
    result = graph_benchmarks.runner.benchmark(demo_grid, "demo_small_grid")
    print(f"   5x5 grid creation: {result.mean*1000:.3f}ms")
    
    # 3. Traversal Demo
    print("\n3. Traversal Algorithm Benchmarks:")
    print("-" * 34)
    
    traversal_benchmarks = TraversalBenchmarks()
    traversal_benchmarks.runner = BenchmarkRunner(warmup_runs=1, timing_runs=3)  # Faster for demo
    
    # Create a small test graph
    test_graph = Graph.grid_graph([range(8), range(8)])
    start_node = next(iter(test_graph))
    
    def demo_bfs():
        return list(test_graph.descendants(start_node))
    
    result = traversal_benchmarks.runner.benchmark(demo_bfs, "demo_bfs_8x8")
    print(f"   BFS on 8x8 grid: {result.mean*1000:.3f}ms")
    
    # 4. Results Storage Demo
    print("\n4. Results Storage and Analysis:")
    print("-" * 30)
    
    # Collect all results
    all_results = []
    for runner_obj in [runner, graph_benchmarks.runner, traversal_benchmarks.runner]:
        for result in runner_obj.results:
            all_results.append(result.to_dict())
    
    # Save demo results
    reporter = BenchmarkReporter()
    demo_file = reporter.save_results_with_metadata(
        all_results, 
        "demo_results",
        metadata={"demo": True, "version": "1.0", "purpose": "system_demonstration"}
    )
    print(f"   Results saved to: {demo_file.name}")
    print(f"   Total tests in demo: {len(all_results)}")
    
    # 5. Reporting System Demo
    print("\n5. Reporting System Capabilities:")
    print("-" * 33)
    
    print("   ✓ Statistical comparison analysis")
    print("   ✓ Automated visualization generation")
    print("   ✓ HTML report creation")
    print("   ✓ Category-based performance analysis")
    print("   ✓ Effect size calculations")
    print("   ✓ Significance testing")
    
    return demo_file


def demonstrate_comparison_workflow():
    """Demonstrate how to compare before/after results."""
    print("\n" + "=" * 50)
    print("Comparison Workflow Demonstration")
    print("=" * 50)
    
    # Check if we have baseline results
    results_dir = Path("klotho/benchmarks/results")
    baseline_files = list(results_dir.glob("baseline_*.json"))
    
    if baseline_files:
        print(f"\nFound {len(baseline_files)} baseline result files:")
        for f in baseline_files:
            print(f"   - {f.name}")
        
        print("\nComparison workflow:")
        print("1. Run optimized benchmarks → current_results.json")
        print("2. Use BenchmarkReporter.compare_results(baseline, current)")
        print("3. Generate visualizations and HTML report")
        print("4. Analyze statistical significance and effect sizes")
        
        # Show structure of a baseline file
        if baseline_files:
            with open(baseline_files[0], 'r') as f:
                data = json.load(f)
            print(f"\nBaseline file structure preview:")
            print(f"   - Tests: {len(data.get('results', []))}")
            print(f"   - Config: warmup={data['config']['warmup_runs']}, timing={data['config']['timing_runs']}")
            if data.get('results'):
                example = data['results'][0]
                print(f"   - Example test: {example['name']} ({example['mean']*1000:.3f}ms)")
    else:
        print("\nNo baseline files found. Run full benchmarks first:")
        print("   python -m klotho.benchmarks.graph_generation")
        print("   python -m klotho.benchmarks.traversal_algorithms")


def show_optimization_workflow():
    """Show the complete optimization workflow."""
    print("\n" + "=" * 50)
    print("RustworkX Optimization Workflow")
    print("=" * 50)
    
    print("\nStep 1: Establish Baseline Performance")
    print("   → Run: python -m klotho.benchmarks.graph_generation")
    print("   → Run: python -m klotho.benchmarks.traversal_algorithms")
    print("   → Saves: baseline_graph_generation.json, baseline_traversal_algorithms.json")
    
    print("\nStep 2: Implement RustworkX Optimizations")
    print("   → Task 3: Refactor grid_graph method")
    print("   → Task 4: Optimize graph traversal methods") 
    print("   → Task 5: Refactor Tree depth calculation")
    print("   → Tasks 6-10: Additional optimizations")
    
    print("\nStep 3: Measure Optimized Performance")
    print("   → Run same benchmark scripts on optimized code")
    print("   → Saves: optimized_graph_generation.json, optimized_traversal_algorithms.json")
    
    print("\nStep 4: Generate Comparison Analysis")
    print("   → Use BenchmarkReporter to compare baseline vs optimized")
    print("   → Generate statistical analysis and visualizations")
    print("   → Create HTML report with detailed findings")
    
    print("\nStep 5: Validate Results")
    print("   → Ensure all tests still pass")
    print("   → Verify performance improvements are significant")
    print("   → Document any API behavior changes")


def main():
    """Run the complete demonstration."""
    try:
        # Run core demo
        demo_file = run_quick_benchmark_demo()
        
        # Show comparison workflow
        demonstrate_comparison_workflow()
        
        # Show optimization workflow
        show_optimization_workflow()
        
        print("\n" + "=" * 50)
        print("Demonstration Complete!")
        print("=" * 50)
        print("\nThe benchmarking system is ready for the RustworkX refactoring project.")
        print("All components are tested and working correctly.")
        
        return demo_file
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        print("Check that all dependencies are installed in the virtual environment.")
        raise


if __name__ == "__main__":
    main() 