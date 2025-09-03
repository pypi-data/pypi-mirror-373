"""
Traversal and path algorithm benchmarks for Klotho performance measurement.

Tests current BFS/DFS implementations and Tree operations to establish baseline
performance before RustworkX optimization refactoring.
"""
import time
from typing import Dict, List, Tuple
from klotho.benchmarks.core import BenchmarkRunner, BenchmarkResult
from klotho.topos.graphs import Graph, Tree
from klotho.chronos.rhythm_trees import RhythmTree
from pathlib import Path
import random


class TraversalBenchmarks:
    """Comprehensive benchmarks for graph traversal and path algorithms."""
    
    def __init__(self):
        self.runner = BenchmarkRunner(warmup_runs=3, timing_runs=10)
    
    def create_test_graphs(self) -> Dict[str, Graph]:
        """Create various test graphs for benchmarking."""
        graphs = {}
        
        # Small grid for quick tests
        graphs['grid_2d_small'] = Graph.grid_graph([range(10), range(10)])
        
        # Medium grid 
        graphs['grid_2d_medium'] = Graph.grid_graph([range(25), range(25)])
        
        # 3D grid
        graphs['grid_3d'] = Graph.grid_graph([range(8), range(8), range(8)])
        
        # Random sparse graph
        random.seed(42)
        sparse_graph = Graph()
        for i in range(100):
            sparse_graph.add_node(value=i)
        for _ in range(150):  # Sparse: ~3% of max edges
            u, v = random.randint(0, 99), random.randint(0, 99)
            if u != v and not sparse_graph.has_edge(u, v):
                sparse_graph.add_edge(u, v)
        graphs['random_sparse'] = sparse_graph
        
        # Random dense graph
        dense_graph = Graph()
        for i in range(50):
            dense_graph.add_node(value=i)
        for _ in range(800):  # Dense: ~65% of max edges
            u, v = random.randint(0, 49), random.randint(0, 49)
            if u != v and not dense_graph.has_edge(u, v):
                dense_graph.add_edge(u, v)
        graphs['random_dense'] = dense_graph
        
        return graphs
    
    def create_test_trees(self) -> Dict[str, Tree]:
        """Create various test trees for benchmarking."""
        trees = {}
        
        # Balanced binary tree (depth 5)
        trees['balanced_depth5'] = Tree(1, (
            (2, (4, 8, 9)),
            (3, (5, 10, 11), (6, 12, 13), (7, 14, 15))
        ))
        
        # Deep linear tree (depth 10)
        def create_linear_tree(depth):
            if depth == 0:
                return depth
            return (depth, (create_linear_tree(depth - 1),))
        
        trees['linear_depth10'] = Tree(*create_linear_tree(10))
        
        # Wide tree (many children)
        wide_children = tuple(range(2, 12))  # 10 children
        trees['wide_tree'] = Tree(1, wide_children)
        
        # Complex nested tree
        trees['complex_nested'] = Tree(1, (
            (2, (5, 6), (7, 8, 9)),
            (3, (10, (15, 16)), (11, 12)),
            (4, (13, 14), (17, (18, 19, 20)))
        ))
        
        return trees
    
    def benchmark_graph_traversals(self) -> List[BenchmarkResult]:
        """Benchmark BFS and DFS traversals on various graphs."""
        results = []
        graphs = self.create_test_graphs()
        
        for graph_name, graph in graphs.items():
            # Get a starting node (first node)
            start_node = next(iter(graph))
            
            # BFS traversal (using descendants which uses manual BFS)
            def bfs_traversal():
                # Use descendants method which implements BFS
                return list(graph.descendants(start_node))
            
            result = self.runner.benchmark(
                bfs_traversal,
                f"bfs_{graph_name}",
                metadata={
                    'algorithm': 'bfs',
                    'graph_type': graph_name,
                    'nodes': graph.number_of_nodes(),
                    'edges': graph.number_of_edges()
                }
            )
            results.append(result)
            
            # Simulate DFS traversal using a different approach
            def dfs_traversal():
                visited = set()
                result_nodes = []
                
                def dfs_visit(node):
                    if node in visited:
                        return
                    visited.add(node)
                    result_nodes.append(node)
                    for neighbor in graph.successors(node):
                        dfs_visit(neighbor)
                
                dfs_visit(start_node)
                return result_nodes
            
            result = self.runner.benchmark(
                dfs_traversal,
                f"dfs_{graph_name}",
                metadata={
                    'algorithm': 'dfs',
                    'graph_type': graph_name,
                    'nodes': graph.number_of_nodes(),
                    'edges': graph.number_of_edges()
                }
            )
            results.append(result)
        
        return results
    
    def benchmark_tree_operations(self) -> List[BenchmarkResult]:
        """Benchmark Tree-specific operations."""
        results = []
        trees = self.create_test_trees()
        
        for tree_name, tree in trees.items():
            # Get some test nodes
            all_nodes = list(tree.nodes)
            test_nodes = all_nodes[:min(5, len(all_nodes))]  # Test up to 5 nodes
            
            # Benchmark depth_of method (current manual BFS implementation)
            for i, node in enumerate(test_nodes):
                def depth_calculation():
                    return tree.depth_of(node)
                
                result = self.runner.benchmark(
                    depth_calculation,
                    f"depth_of_{tree_name}_node{i}",
                    metadata={
                        'operation': 'depth_of',
                        'tree_type': tree_name,
                        'total_nodes': tree.number_of_nodes(),
                        'tree_depth': tree.depth
                    }
                )
                results.append(result)
            
            # Benchmark ancestors calculation
            if len(test_nodes) > 2:
                test_node = test_nodes[2]  # Use a deeper node
                
                def ancestors_calculation():
                    return tree.ancestors(test_node)
                
                result = self.runner.benchmark(
                    ancestors_calculation,
                    f"ancestors_{tree_name}",
                    metadata={
                        'operation': 'ancestors',
                        'tree_type': tree_name,
                        'total_nodes': tree.number_of_nodes()
                    }
                )
                results.append(result)
            
            # Benchmark descendants calculation
            root_node = tree.root
            
            def descendants_calculation():
                return tree.descendants(root_node)
            
            result = self.runner.benchmark(
                descendants_calculation,
                f"descendants_{tree_name}",
                metadata={
                    'operation': 'descendants',
                    'tree_type': tree_name,
                    'total_nodes': tree.number_of_nodes()
                }
            )
            results.append(result)
            
            # Benchmark branch calculation
            if len(test_nodes) > 1:
                test_node = test_nodes[1]
                
                def branch_calculation():
                    return tree.branch(test_node)
                
                result = self.runner.benchmark(
                    branch_calculation,
                    f"branch_{tree_name}",
                    metadata={
                        'operation': 'branch',
                        'tree_type': tree_name,
                        'total_nodes': tree.number_of_nodes()
                    }
                )
                results.append(result)
        
        return results
    
    def benchmark_path_algorithms(self) -> List[BenchmarkResult]:
        """Benchmark path-finding operations."""
        results = []
        
        # Create a grid graph for path testing
        grid = Graph.grid_graph([range(20), range(20)])
        
        # Test shortest path-like operations
        nodes_list = list(grid.nodes)
        start_node = nodes_list[0]
        end_nodes = [nodes_list[50], nodes_list[150], nodes_list[300]]  # Different distances
        
        for i, end_node in enumerate(end_nodes):
            # Test ancestors path (Tree-like path finding)
            def path_via_ancestors():
                # This simulates finding a path by using ancestor-like traversal
                # Note: This is not a direct shortest path but tests traversal patterns
                visited = set()
                path = []
                current = start_node
                
                # Simple greedy path finding (not optimal, but tests traversal)
                while current != end_node and len(path) < 100:
                    if current in visited:
                        break
                    visited.add(current)
                    path.append(current)
                    
                    # Find next step toward target
                    neighbors = list(grid.neighbors(current))
                    if neighbors:
                        # Pick first available neighbor (simple heuristic)
                        current = neighbors[0]
                    else:
                        break
                
                return path
            
            result = self.runner.benchmark(
                path_via_ancestors,
                f"path_finding_distance{i}",
                metadata={
                    'operation': 'path_finding',
                    'start_node': start_node,
                    'end_node': end_node,
                    'graph_nodes': grid.number_of_nodes()
                }
            )
            results.append(result)
        
        return results
    
    def benchmark_scaling_behavior(self) -> List[BenchmarkResult]:
        """Benchmark how algorithms scale with graph size."""
        results = []
        
        # Test BFS scaling with grid size
        for size in [5, 10, 15, 20]:
            grid = Graph.grid_graph([range(size), range(size)])
            start_node = next(iter(grid))
            
            def bfs_scaling():
                return list(grid.descendants(start_node))
            
            result = self.runner.benchmark(
                bfs_scaling,
                f"bfs_scaling_grid{size}x{size}",
                metadata={
                    'operation': 'bfs_scaling',
                    'grid_size': size,
                    'total_nodes': size * size
                }
            )
            results.append(result)
        
        # Test Tree depth_of scaling with tree depth
        for depth in [3, 5, 8, 10]:
            # Create a linear tree of given depth
            def create_linear(d):
                if d == 0:
                    return d
                return (d, (create_linear(d - 1),))
            
            linear_tree = Tree(*create_linear(depth))
            deepest_node = 0  # The deepest node in our linear tree
            
            def depth_scaling():
                return linear_tree.depth_of(deepest_node)
            
            result = self.runner.benchmark(
                depth_scaling,
                f"depth_scaling_depth{depth}",
                metadata={
                    'operation': 'depth_scaling',
                    'tree_depth': depth,
                    'total_nodes': depth + 1
                }
            )
            results.append(result)
        
        return results
    
    def run_all_benchmarks(self) -> Dict[str, List[BenchmarkResult]]:
        """Run all traversal and path algorithm benchmarks."""
        print("Running Traversal and Path Algorithm Benchmarks...")
        print("=" * 55)
        
        all_results = {}
        
        print("Benchmarking graph traversals...")
        all_results['graph_traversals'] = self.benchmark_graph_traversals()
        
        print("Benchmarking tree operations...")
        all_results['tree_operations'] = self.benchmark_tree_operations()
        
        print("Benchmarking path algorithms...")
        all_results['path_algorithms'] = self.benchmark_path_algorithms()
        
        print("Benchmarking scaling behavior...")
        all_results['scaling'] = self.benchmark_scaling_behavior()
        
        return all_results
    
    def print_results_summary(self):
        """Print a comprehensive summary of traversal benchmark results."""
        print("\nTraversal and Path Algorithm Benchmark Summary")
        print("=" * 70)
        
        # Group results by operation type
        categories = {
            'Graph Traversals (BFS/DFS)': [r for r in self.runner.results if r.name.startswith(('bfs_', 'dfs_'))],
            'Tree Operations': [r for r in self.runner.results if any(op in r.name for op in ['depth_of', 'ancestors', 'descendants', 'branch'])],
            'Path Finding': [r for r in self.runner.results if 'path_finding' in r.name],
            'Scaling Tests': [r for r in self.runner.results if 'scaling' in r.name]
        }
        
        for category, results in categories.items():
            if results:
                print(f"\n{category}:")
                print("-" * 50)
                print(f"{'Test':<35} {'Mean (ms)':<12} {'CV%':<8} {'Nodes':<8}")
                print("-" * 50)
                
                for result in results:
                    mean_ms = result.mean * 1000
                    cv = result.coefficient_of_variation()
                    nodes = result.metadata.get('nodes', result.metadata.get('total_nodes', 'N/A'))
                    
                    print(f"{result.name:<35} {mean_ms:<12.3f} {cv:<8.1f} {nodes:<8}")
    
    def save_baseline_results(self, filepath: Path):
        """Save baseline results for future comparison."""
        self.runner.save_results(filepath)
        print(f"Traversal benchmark baseline saved to {filepath}")


def main():
    """Run traversal and path algorithm benchmarks."""
    benchmarks = TraversalBenchmarks()
    
    # Run all benchmarks
    all_results = benchmarks.run_all_benchmarks()
    
    # Print summary
    benchmarks.print_results_summary()
    
    # Save baseline results
    results_dir = Path("klotho/benchmarks/results")
    baseline_file = results_dir / "baseline_traversal_algorithms.json"
    benchmarks.save_baseline_results(baseline_file)
    
    print(f"\nTotal traversal tests run: {len(benchmarks.runner.results)}")
    print("Traversal algorithm benchmarks complete!")


if __name__ == "__main__":
    main() 