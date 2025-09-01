"""
Test script to verify benchmarking infrastructure functionality.

This script validates that the benchmarking framework correctly measures
timing performance with acceptable variance and produces consistent results.
"""
from klotho.benchmarks.core import BenchmarkRunner
from klotho.topos.graphs import Graph
import time


def test_basic_timing():
    """Test basic timing functionality with known operations."""
    runner = BenchmarkRunner(warmup_runs=2, timing_runs=5)
    
    # Test with a predictable sleep operation
    def sleep_10ms():
        time.sleep(0.01)  # 10ms sleep
    
    result = runner.benchmark(sleep_10ms, "sleep_10ms_test")
    
    # Verify timing is approximately correct (within reasonable variance)
    expected_time = 0.01  # 10ms
    assert 0.008 <= result.mean <= 0.015, f"Sleep timing off: {result.mean}"
    assert result.coefficient_of_variation() < 10, f"High variance: {result.coefficient_of_variation()}%"
    
    print(f"✓ Basic timing test passed: {result.mean*1000:.2f}ms ± {result.stdev*1000:.2f}ms")


def test_graph_creation_benchmark():
    """Test benchmarking with actual graph operations."""
    runner = BenchmarkRunner(warmup_runs=2, timing_runs=5)
    
    # Test empty graph creation
    def create_empty_graph():
        graph = Graph()
        return graph
    
    result = runner.benchmark(create_empty_graph, "empty_graph_creation")
    
    # Should be very fast (< 1ms typically)
    assert result.mean < 0.001, f"Graph creation too slow: {result.mean*1000:.2f}ms"
    
    print(f"✓ Graph creation test passed: {result.mean*1000:.3f}ms")


def test_node_addition_benchmark():
    """Test benchmarking node addition operations."""
    runner = BenchmarkRunner(warmup_runs=2, timing_runs=5)
    
    # Test adding 100 nodes
    def add_nodes():
        graph = Graph()
        for i in range(100):
            graph.add_node(value=i)
        return graph
    
    result = runner.benchmark(add_nodes, "add_100_nodes")
    
    # Should complete reasonably quickly
    assert result.mean < 0.01, f"Node addition too slow: {result.mean*1000:.2f}ms"
    
    print(f"✓ Node addition test passed: {result.mean*1000:.2f}ms for 100 nodes")


def test_consistency():
    """Test that repeated benchmarks give consistent results."""
    runner = BenchmarkRunner(warmup_runs=2, timing_runs=10)
    
    def simple_graph_op():
        graph = Graph()
        for i in range(10):
            graph.add_node(value=i)
        return len(graph)
    
    # Run the same benchmark twice
    result1 = runner.benchmark(simple_graph_op, "consistency_test_1")
    result2 = runner.benchmark(simple_graph_op, "consistency_test_2")
    
    # Results should be similar (within 20% of each other)
    ratio = max(result1.mean, result2.mean) / min(result1.mean, result2.mean)
    assert ratio < 1.2, f"Inconsistent results: {result1.mean} vs {result2.mean}"
    
    print(f"✓ Consistency test passed: {result1.mean*1000:.3f}ms vs {result2.mean*1000:.3f}ms")


def main():
    """Run all infrastructure tests."""
    print("Testing Klotho Benchmarking Infrastructure")
    print("=" * 50)
    
    try:
        test_basic_timing()
        test_graph_creation_benchmark()
        test_node_addition_benchmark()
        test_consistency()
        
        print("\n🎉 All infrastructure tests passed!")
        print("Benchmarking framework is ready for use.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main() 