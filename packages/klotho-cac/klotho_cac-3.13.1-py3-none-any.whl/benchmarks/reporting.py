"""
Benchmark results reporting and comparison system for Klotho refactoring project.

Provides tools for storing results, generating comparisons, and creating
detailed HTML reports with visualizations.
"""
import json
import statistics
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import seaborn as sns
from scipy import stats
import numpy as np


class BenchmarkReporter:
    """Advanced benchmark reporting and comparison system."""
    
    def __init__(self, results_dir: Path = None):
        self.results_dir = results_dir or Path("klotho/benchmarks/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def load_results(self, filepath: Path) -> Dict[str, Any]:
        """Load benchmark results from JSON file."""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def save_results_with_metadata(self, results: List[Dict], 
                                   filename: str, 
                                   metadata: Dict[str, Any] = None) -> Path:
        """Save results with timestamp and metadata."""
        timestamp = datetime.now().isoformat()
        
        data = {
            'timestamp': timestamp,
            'metadata': metadata or {},
            'results': results,
            'summary': {
                'total_tests': len(results),
                'categories': self._categorize_results(results)
            }
        }
        
        filepath = self.results_dir / f"{filename}_{timestamp.split('T')[0]}.json"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    def _categorize_results(self, results: List[Dict]) -> Dict[str, int]:
        """Categorize results by test type."""
        categories = {}
        for result in results:
            name = result['name']
            
            # Determine category based on test name patterns
            if 'grid' in name or 'complete' in name or 'lattice' in name:
                category = 'generation'
            elif any(op in name for op in ['bfs', 'dfs', 'depth_of', 'ancestors', 'descendants']):
                category = 'traversal'
            elif 'path_finding' in name:
                category = 'pathfinding'
            elif 'scaling' in name:
                category = 'scaling'
            else:
                category = 'other'
            
            categories[category] = categories.get(category, 0) + 1
        
        return categories
    
    def compare_results(self, baseline_file: Path, 
                       current_file: Path,
                       significance_threshold: float = 0.05) -> Dict[str, Any]:
        """
        Compare benchmark results with statistical analysis.
        
        Args:
            baseline_file: Path to baseline results
            current_file: Path to current results  
            significance_threshold: P-value threshold for significance testing
            
        Returns:
            Detailed comparison analysis
        """
        baseline = self.load_results(baseline_file)
        current = self.load_results(current_file)
        
        # Extract results arrays
        baseline_results = baseline.get('results', baseline)
        current_results = current.get('results', current)
        
        # Create lookup dictionaries
        baseline_lookup = {r['name']: r for r in baseline_results}
        current_lookup = {r['name']: r for r in current_results}
        
        comparisons = {}
        statistical_summary = {
            'significant_improvements': 0,
            'significant_regressions': 0,
            'no_significant_change': 0,
            'missing_tests': 0
        }
        
        for name in baseline_lookup.keys():
            if name in current_lookup:
                baseline_result = baseline_lookup[name]
                current_result = current_lookup[name]
                
                # Extract timing data
                baseline_times = baseline_result.get('times', [baseline_result.get('mean', 0)])
                current_times = current_result.get('times', [current_result.get('mean', 0)])
                
                baseline_mean = baseline_result.get('mean', statistics.mean(baseline_times))
                current_mean = current_result.get('mean', statistics.mean(current_times))
                
                # Calculate improvement percentage
                improvement = ((baseline_mean - current_mean) / baseline_mean) * 100
                
                # Perform statistical significance test (Welch's t-test)
                if len(baseline_times) > 1 and len(current_times) > 1:
                    t_stat, p_value = stats.ttest_ind(baseline_times, current_times, equal_var=False)
                    significant = p_value < significance_threshold
                else:
                    t_stat, p_value = None, None
                    significant = abs(improvement) > 5.0  # Fallback: >5% change
                
                # Calculate effect size (Cohen's d)
                effect_size = self._calculate_cohens_d(baseline_times, current_times)
                
                comparison_data = {
                    'baseline_mean': baseline_mean,
                    'current_mean': current_mean,
                    'baseline_stdev': baseline_result.get('stdev', 0),
                    'current_stdev': current_result.get('stdev', 0),
                    'improvement_percent': improvement,
                    'p_value': p_value,
                    't_statistic': t_stat,
                    'significant': significant,
                    'effect_size': effect_size,
                    'category': self._get_test_category(name)
                }
                
                comparisons[name] = comparison_data
                
                # Update statistical summary
                if significant:
                    if improvement > 0:
                        statistical_summary['significant_improvements'] += 1
                    else:
                        statistical_summary['significant_regressions'] += 1
                else:
                    statistical_summary['no_significant_change'] += 1
            else:
                statistical_summary['missing_tests'] += 1
        
        # Calculate category-wise statistics
        category_stats = self._calculate_category_statistics(comparisons)
        
        return {
            'comparisons': comparisons,
            'statistical_summary': statistical_summary,
            'category_statistics': category_stats,
            'baseline_file': str(baseline_file),
            'current_file': str(current_file),
            'comparison_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_cohens_d(self, baseline: List[float], current: List[float]) -> Optional[float]:
        """Calculate Cohen's d effect size."""
        if len(baseline) < 2 or len(current) < 2:
            return None
        
        baseline_mean = statistics.mean(baseline)
        current_mean = statistics.mean(current)
        baseline_std = statistics.stdev(baseline)
        current_std = statistics.stdev(current)
        
        pooled_std = np.sqrt(((len(baseline) - 1) * baseline_std**2 + 
                             (len(current) - 1) * current_std**2) / 
                            (len(baseline) + len(current) - 2))
        
        if pooled_std == 0:
            return None
        
        return (current_mean - baseline_mean) / pooled_std
    
    def _get_test_category(self, test_name: str) -> str:
        """Determine test category from name."""
        if any(pattern in test_name for pattern in ['grid', 'complete', 'lattice', 'random']):
            return 'generation'
        elif any(pattern in test_name for pattern in ['bfs', 'dfs', 'depth_of', 'ancestors', 'descendants']):
            return 'traversal'
        elif 'path_finding' in test_name:
            return 'pathfinding'
        elif 'scaling' in test_name:
            return 'scaling'
        else:
            return 'other'
    
    def _calculate_category_statistics(self, comparisons: Dict[str, Dict]) -> Dict[str, Dict]:
        """Calculate statistics by test category."""
        categories = {}
        
        for name, comp in comparisons.items():
            category = comp['category']
            if category not in categories:
                categories[category] = {
                    'improvements': [],
                    'p_values': [],
                    'effect_sizes': [],
                    'test_count': 0
                }
            
            categories[category]['improvements'].append(comp['improvement_percent'])
            if comp['p_value'] is not None:
                categories[category]['p_values'].append(comp['p_value'])
            if comp['effect_size'] is not None:
                categories[category]['effect_sizes'].append(comp['effect_size'])
            categories[category]['test_count'] += 1
        
        # Calculate summary statistics for each category
        for category, data in categories.items():
            improvements = data['improvements']
            categories[category]['mean_improvement'] = statistics.mean(improvements)
            categories[category]['median_improvement'] = statistics.median(improvements)
            categories[category]['improvement_stdev'] = statistics.stdev(improvements) if len(improvements) > 1 else 0
        
        return categories
    
    def generate_visualizations(self, comparison_data: Dict[str, Any], 
                              output_dir: Path = None) -> List[Path]:
        """Generate comparison visualizations."""
        output_dir = output_dir or self.results_dir / "visualizations"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        comparisons = comparison_data['comparisons']
        
        # 1. Overall improvement distribution
        improvements = [comp['improvement_percent'] for comp in comparisons.values()]
        
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        plt.hist(improvements, bins=20, alpha=0.7, edgecolor='black')
        plt.axvline(x=0, color='red', linestyle='--', label='No change')
        plt.xlabel('Improvement (%)')
        plt.ylabel('Number of tests')
        plt.title('Distribution of Performance Improvements')
        plt.legend()
        
        # 2. Improvement by category
        plt.subplot(1, 2, 2)
        categories = comparison_data['category_statistics']
        cat_names = list(categories.keys())
        cat_improvements = [categories[cat]['mean_improvement'] for cat in cat_names]
        
        bars = plt.bar(cat_names, cat_improvements, alpha=0.7)
        plt.axhline(y=0, color='red', linestyle='--')
        plt.xlabel('Test Category')
        plt.ylabel('Mean Improvement (%)')
        plt.title('Performance Improvement by Category')
        plt.xticks(rotation=45)
        
        # Color bars based on improvement
        for bar, improvement in zip(bars, cat_improvements):
            if improvement > 5:
                bar.set_color('green')
            elif improvement < -5:
                bar.set_color('red')
            else:
                bar.set_color('gray')
        
        plt.tight_layout()
        improvement_plot = output_dir / "improvement_analysis.png"
        plt.savefig(improvement_plot, dpi=300, bbox_inches='tight')
        plt.close()
        generated_files.append(improvement_plot)
        
        # 3. Before/After comparison scatter plot
        plt.figure(figsize=(10, 8))
        baseline_means = [comp['baseline_mean'] * 1000 for comp in comparisons.values()]  # Convert to ms
        current_means = [comp['current_mean'] * 1000 for comp in comparisons.values()]
        
        plt.scatter(baseline_means, current_means, alpha=0.6, s=50)
        
        # Add diagonal line for "no change"
        max_val = max(max(baseline_means), max(current_means))
        plt.plot([0, max_val], [0, max_val], 'r--', label='No change')
        
        plt.xlabel('Baseline Performance (ms)')
        plt.ylabel('Current Performance (ms)')
        plt.title('Before vs After Performance Comparison')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Add improvement regions
        plt.fill_between([0, max_val], [0, max_val], [0, 0], alpha=0.1, color='green', label='Improvement region')
        
        scatter_plot = output_dir / "before_after_scatter.png"
        plt.savefig(scatter_plot, dpi=300, bbox_inches='tight')
        plt.close()
        generated_files.append(scatter_plot)
        
        # 4. Statistical significance visualization
        plt.figure(figsize=(12, 6))
        
        significant_improvements = [(name, comp['improvement_percent']) 
                                  for name, comp in comparisons.items() 
                                  if comp['significant'] and comp['improvement_percent'] > 0]
        significant_regressions = [(name, comp['improvement_percent']) 
                                 for name, comp in comparisons.items() 
                                 if comp['significant'] and comp['improvement_percent'] < 0]
        
        if significant_improvements:
            names, improvements = zip(*significant_improvements[:10])  # Top 10
            plt.subplot(1, 2, 1)
            plt.barh(range(len(names)), improvements, color='green', alpha=0.7)
            plt.yticks(range(len(names)), [name[:25] + '...' if len(name) > 25 else name for name in names])
            plt.xlabel('Improvement (%)')
            plt.title('Significant Performance Improvements')
            plt.grid(True, alpha=0.3)
        
        if significant_regressions:
            names, regressions = zip(*significant_regressions[:10])  # Top 10
            plt.subplot(1, 2, 2)
            plt.barh(range(len(names)), regressions, color='red', alpha=0.7)
            plt.yticks(range(len(names)), [name[:25] + '...' if len(name) > 25 else name for name in names])
            plt.xlabel('Regression (%)')
            plt.title('Significant Performance Regressions')
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        significance_plot = output_dir / "significance_analysis.png"
        plt.savefig(significance_plot, dpi=300, bbox_inches='tight')
        plt.close()
        generated_files.append(significance_plot)
        
        return generated_files
    
    def generate_html_report(self, comparison_data: Dict[str, Any], 
                           visualization_files: List[Path] = None,
                           output_file: Path = None) -> Path:
        """Generate comprehensive HTML report."""
        output_file = output_file or self.results_dir / f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Generate visualizations if not provided
        if visualization_files is None:
            visualization_files = self.generate_visualizations(comparison_data)
        
        comparisons = comparison_data['comparisons']
        stats_summary = comparison_data['statistical_summary']
        category_stats = comparison_data['category_statistics']
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Klotho Graph Classes Performance Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1, h2, h3 {{ color: #333; }}
        .summary {{ background-color: #e9f4ff; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; }}
        .improvement {{ color: #28a745; }}
        .regression {{ color: #dc3545; }}
        .neutral {{ color: #6c757d; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f8f9fa; font-weight: bold; }}
        .visualization {{ text-align: center; margin: 30px 0; }}
        .visualization img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px; }}
        .category-section {{ margin: 30px 0; padding: 20px; background-color: #f8f9fa; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Klotho Graph Classes Performance Analysis Report</h1>
        <p><strong>Generated:</strong> {comparison_data['comparison_timestamp']}</p>
        <p><strong>Baseline:</strong> {comparison_data['baseline_file']}</p>
        <p><strong>Current:</strong> {comparison_data['current_file']}</p>
        
        <div class="summary">
            <h2>Executive Summary</h2>
            <div class="metric">
                <div class="metric-value improvement">{stats_summary['significant_improvements']}</div>
                <div>Significant Improvements</div>
            </div>
            <div class="metric">
                <div class="metric-value regression">{stats_summary['significant_regressions']}</div>
                <div>Significant Regressions</div>
            </div>
            <div class="metric">
                <div class="metric-value neutral">{stats_summary['no_significant_change']}</div>
                <div>No Significant Change</div>
            </div>
            <div class="metric">
                <div class="metric-value">{len(comparisons)}</div>
                <div>Total Tests</div>
            </div>
        </div>
        
        <h2>Performance by Category</h2>
        """
        
        for category, stats in category_stats.items():
            improvement_class = "improvement" if stats['mean_improvement'] > 5 else "regression" if stats['mean_improvement'] < -5 else "neutral"
            html_content += f"""
        <div class="category-section">
            <h3>{category.title()} Operations</h3>
            <p>Mean Improvement: <span class="{improvement_class}">{stats['mean_improvement']:.1f}%</span></p>
            <p>Tests: {stats['test_count']}</p>
            <p>Standard Deviation: ±{stats['improvement_stdev']:.1f}%</p>
        </div>
            """
        
        # Add visualizations
        if visualization_files:
            html_content += "<h2>Performance Visualizations</h2>"
            for viz_file in visualization_files:
                rel_path = viz_file.name  # Just use filename for relative path
                html_content += f"""
        <div class="visualization">
            <h3>{viz_file.stem.replace('_', ' ').title()}</h3>
            <img src="{rel_path}" alt="{viz_file.stem}">
        </div>
                """
        
        # Detailed results table
        html_content += """
        <h2>Detailed Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Test Name</th>
                    <th>Category</th>
                    <th>Baseline (ms)</th>
                    <th>Current (ms)</th>
                    <th>Improvement</th>
                    <th>Significant</th>
                    <th>Effect Size</th>
                </tr>
            </thead>
            <tbody>
        """
        
        # Sort by improvement percentage
        sorted_comparisons = sorted(comparisons.items(), 
                                  key=lambda x: x[1]['improvement_percent'], 
                                  reverse=True)
        
        for name, comp in sorted_comparisons:
            improvement_class = "improvement" if comp['improvement_percent'] > 5 else "regression" if comp['improvement_percent'] < -5 else "neutral"
            significance_text = "Yes" if comp['significant'] else "No"
            effect_size_text = f"{comp['effect_size']:.3f}" if comp['effect_size'] is not None else "N/A"
            
            html_content += f"""
                <tr>
                    <td>{name}</td>
                    <td>{comp['category'].title()}</td>
                    <td>{comp['baseline_mean']*1000:.3f}</td>
                    <td>{comp['current_mean']*1000:.3f}</td>
                    <td class="{improvement_class}">{comp['improvement_percent']:+.1f}%</td>
                    <td>{significance_text}</td>
                    <td>{effect_size_text}</td>
                </tr>
            """
        
        html_content += """
            </tbody>
        </table>
        
        <h2>Methodology</h2>
        <p>This report compares performance benchmarks using statistical analysis including:</p>
        <ul>
            <li><strong>Statistical Significance:</strong> Welch's t-test with p < 0.05 threshold</li>
            <li><strong>Effect Size:</strong> Cohen's d for practical significance assessment</li>
            <li><strong>Categorization:</strong> Tests grouped by operation type for targeted analysis</li>
            <li><strong>Visualization:</strong> Multiple charts showing different aspects of performance</li>
        </ul>
        
    </div>
</body>
</html>
        """
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        return output_file
    
    def print_comparison_summary(self, comparison_data: Dict[str, Any]):
        """Print a concise comparison summary to console."""
        comparisons = comparison_data['comparisons']
        stats_summary = comparison_data['statistical_summary']
        category_stats = comparison_data['category_statistics']
        
        print("\nBenchmark Comparison Summary")
        print("=" * 50)
        print(f"Total Tests: {len(comparisons)}")
        print(f"Significant Improvements: {stats_summary['significant_improvements']}")
        print(f"Significant Regressions: {stats_summary['significant_regressions']}")
        print(f"No Significant Change: {stats_summary['no_significant_change']}")
        
        print("\nBy Category:")
        print("-" * 30)
        for category, stats in category_stats.items():
            improvement = stats['mean_improvement']
            status = "↑" if improvement > 5 else "↓" if improvement < -5 else "→"
            print(f"{category.title():<15} {status} {improvement:+6.1f}% ({stats['test_count']} tests)")
        
        # Top improvements and regressions
        sorted_by_improvement = sorted(comparisons.items(), 
                                     key=lambda x: x[1]['improvement_percent'], 
                                     reverse=True)
        
        print("\nTop 5 Improvements:")
        print("-" * 30)
        for name, comp in sorted_by_improvement[:5]:
            if comp['improvement_percent'] > 0:
                sig_indicator = "*" if comp['significant'] else ""
                print(f"{name[:30]:<30} {comp['improvement_percent']:+6.1f}%{sig_indicator}")
        
        print("\nTop 5 Regressions:")
        print("-" * 30)
        for name, comp in sorted_by_improvement[-5:]:
            if comp['improvement_percent'] < 0:
                sig_indicator = "*" if comp['significant'] else ""
                print(f"{name[:30]:<30} {comp['improvement_percent']:+6.1f}%{sig_indicator}")


def main():
    """Example usage of the reporting system."""
    reporter = BenchmarkReporter()
    
    # Example: compare two result files (you would have actual files)
    print("Benchmark Reporting System Demo")
    print("=" * 40)
    print("This system provides:")
    print("- Statistical comparison analysis")
    print("- Automated visualization generation") 
    print("- Comprehensive HTML reports")
    print("- Category-based performance analysis")
    print("- Effect size calculations")
    print("\nReady to use with actual benchmark results!")


if __name__ == "__main__":
    main() 