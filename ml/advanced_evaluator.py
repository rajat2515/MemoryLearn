import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from scipy import stats
from sklearn.model_selection import ParameterGrid
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
import time

@dataclass
class EvaluationResult:
    """Data class to store evaluation results."""
    algorithm: str
    workload: str
    metrics: Dict[str, float]
    parameters: Dict[str, Any]
    execution_time: float
    timestamp: float

class AdvancedAlgorithmEvaluator:
    """
    Advanced evaluation system for page replacement algorithms with comprehensive
    statistical analysis, parameter tuning, and performance profiling.
    """
    
    def __init__(self, memory_manager, algorithms: List[str]):
        self.memory_manager = memory_manager
        self.algorithms = algorithms
        self.results = []
        self.parameter_grids = {
            'memory_manager': {
                'physical_memory_size': [1024, 2048, 4096],
                'enable_prefetching': [True, False],
                'prefetch_window': [1, 2, 4]
            }
        }
        
    def add_parameter_grid(self, component: str, grid: Dict[str, List]):
        """
        Add parameter grid for tuning.
        
        Args:
            component: Component name (e.g., 'memory_manager', 'workload')
            grid: Parameter grid dictionary
        """
        self.parameter_grids[component] = grid
    
    def comprehensive_evaluation(self, workload_generator, test_patterns: Dict[str, List], 
                               runs_per_config: int = 5) -> pd.DataFrame:
        """
        Perform comprehensive evaluation with multiple runs and statistical analysis.
        
        Args:
            workload_generator: Workload generator instance
            test_patterns: Dictionary of test patterns
            runs_per_config: Number of runs per configuration
            
        Returns:
            DataFrame with detailed results
        """
        print("Starting comprehensive evaluation...")
        all_results = []
        
        # Generate parameter combinations
        param_combinations = list(ParameterGrid(self.parameter_grids.get('memory_manager', {})))
        if not param_combinations:
            param_combinations = [{}]  # At least one run with default parameters
        
        total_configs = len(param_combinations) * len(self.algorithms) * len(test_patterns)
        current_config = 0
        
        for params in param_combinations:
            # Configure memory manager
            original_params = self._configure_memory_manager(params)
            
            for algorithm in self.algorithms:
                for pattern_name, pattern_data in test_patterns.items():
                    print(f"Evaluating {algorithm} on {pattern_name} "
                          f"({current_config + 1}/{total_configs})")
                    
                    # Multiple runs for statistical significance
                    run_results = []
                    for run in range(runs_per_config):
                        result = self._single_evaluation(algorithm, pattern_name, 
                                                       pattern_data, params, run)
                        run_results.append(result)
                        all_results.append(result)
                    
                    # Calculate statistics for this configuration
                    self._calculate_run_statistics(run_results, algorithm, 
                                                 pattern_name, params)
                    
                    current_config += 1
            
            # Restore original parameters
            self._restore_memory_manager(original_params)
        
        # Convert to DataFrame for analysis
        df = self._results_to_dataframe(all_results)
        self.results.extend(all_results)
        
        print("Comprehensive evaluation completed!")
        return df
    
    def _configure_memory_manager(self, params: Dict) -> Dict:
        """Configure memory manager with parameters and return original values."""
        original_params = {}
        
        for param, value in params.items():
            if hasattr(self.memory_manager, param):
                original_params[param] = getattr(self.memory_manager, param)
                setattr(self.memory_manager, param, value)
        
        return original_params
    
    def _restore_memory_manager(self, original_params: Dict):
        """Restore memory manager to original parameters."""
        for param, value in original_params.items():
            setattr(self.memory_manager, param, value)
    
    def _single_evaluation(self, algorithm: str, workload: str, pattern_data: List,
                          params: Dict, run: int) -> EvaluationResult:
        """Perform single evaluation run."""
        from vmm.algorithms import get_algorithm
        
        start_time = time.time()
        
        # Reset memory manager
        self.memory_manager.reset_metrics()
        
        # Set algorithm
        if algorithm == 'optimal':
            # Extract addresses for optimal algorithm
            addresses = [addr for addr, _ in pattern_data]
            alg_instance = get_algorithm(algorithm, self.memory_manager)
            alg_instance.set_future_references(addresses)
        else:
            alg_instance = get_algorithm(algorithm, self.memory_manager)
        
        self.memory_manager.set_replacement_algorithm(alg_instance)
        
        # Process pattern
        for address, is_write in pattern_data:
            self.memory_manager.access_memory(address, is_write)
        
        execution_time = time.time() - start_time
        metrics = self.memory_manager.get_metrics()
        
        return EvaluationResult(
            algorithm=algorithm,
            workload=workload,
            metrics=metrics,
            parameters=params.copy(),
            execution_time=execution_time,
            timestamp=time.time()
        )
    
    def _calculate_run_statistics(self, run_results: List[EvaluationResult],
                                algorithm: str, workload: str, params: Dict):
        """Calculate statistics across multiple runs."""
        if len(run_results) < 2:
            return
        
        # Extract metrics
        metrics_lists = {}
        for result in run_results:
            for metric, value in result.metrics.items():
                if isinstance(value, (int, float)):
                    if metric not in metrics_lists:
                        metrics_lists[metric] = []
                    metrics_lists[metric].append(value)
        
        # Calculate statistics
        stats_summary = {}
        for metric, values in metrics_lists.items():
            if len(values) > 1:
                stats_summary[f"{metric}_mean"] = np.mean(values)
                stats_summary[f"{metric}_std"] = np.std(values)
                stats_summary[f"{metric}_min"] = np.min(values)
                stats_summary[f"{metric}_max"] = np.max(values)
                stats_summary[f"{metric}_median"] = np.median(values)
        
        print(f"  Statistics for {algorithm} on {workload}:")
        print(f"    Hit ratio: {stats_summary.get('hit_ratio_mean', 0):.4f} ± "
              f"{stats_summary.get('hit_ratio_std', 0):.4f}")
        print(f"    Page faults: {stats_summary.get('page_faults_mean', 0):.1f} ± "
              f"{stats_summary.get('page_faults_std', 0):.1f}")
    
    def _results_to_dataframe(self, results: List[EvaluationResult]) -> pd.DataFrame:
        """Convert results to pandas DataFrame."""
        data = []
        for result in results:
            row = {
                'algorithm': result.algorithm,
                'workload': result.workload,
                'execution_time': result.execution_time,
                'timestamp': result.timestamp
            }
            row.update(result.metrics)
            row.update({f"param_{k}": v for k, v in result.parameters.items()})
            data.append(row)
        
        return pd.DataFrame(data)
    
    def statistical_comparison(self, df: pd.DataFrame, metric: str = 'hit_ratio') -> Dict:
        """
        Perform statistical comparison between algorithms.
        
        Args:
            df: Results DataFrame
            metric: Metric to compare
            
        Returns:
            Dictionary with statistical test results
        """
        print(f"\nStatistical comparison for {metric}:")
        
        results = {}
        algorithms = df['algorithm'].unique()
        
        # ANOVA test
        groups = [df[df['algorithm'] == alg][metric].values for alg in algorithms]
        f_stat, p_value = stats.f_oneway(*groups)
        
        results['anova'] = {
            'f_statistic': f_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
        
        print(f"ANOVA F-statistic: {f_stat:.4f}, p-value: {p_value:.6f}")
        
        # Pairwise t-tests
        pairwise_results = {}
        for i, alg1 in enumerate(algorithms):
            for alg2 in algorithms[i+1:]:
                group1 = df[df['algorithm'] == alg1][metric].values
                group2 = df[df['algorithm'] == alg2][metric].values
                
                t_stat, p_val = stats.ttest_ind(group1, group2)
                pairwise_results[f"{alg1}_vs_{alg2}"] = {
                    't_statistic': t_stat,
                    'p_value': p_val,
                    'significant': p_val < 0.05,
                    'effect_size': (np.mean(group1) - np.mean(group2)) / np.sqrt(
                        (np.var(group1) + np.var(group2)) / 2)
                }
                
                print(f"{alg1} vs {alg2}: t={t_stat:.4f}, p={p_val:.6f}")
        
        results['pairwise'] = pairwise_results
        
        return results
    
    def generate_performance_report(self, df: pd.DataFrame) -> str:
        """Generate comprehensive performance report."""
        report = "# Memory Management Algorithm Performance Report\n\n"
        
        # Overall summary
        report += "## Overall Summary\n\n"
        summary = df.groupby('algorithm').agg({
            'hit_ratio': ['mean', 'std', 'min', 'max'],
            'page_faults': ['mean', 'std', 'min', 'max'],
            'execution_time': ['mean', 'std']
        }).round(4)
        
        report += summary.to_string() + "\n\n"
        
        # Best performing algorithm per workload
        report += "## Best Algorithm per Workload\n\n"
        for workload in df['workload'].unique():
            workload_data = df[df['workload'] == workload]
            best_hit_ratio = workload_data.groupby('algorithm')['hit_ratio'].mean().idxmax()
            best_page_faults = workload_data.groupby('algorithm')['page_faults'].mean().idxmin()
            
            report += f"**{workload.title()} Workload:**\n"
            report += f"- Best hit ratio: {best_hit_ratio}\n"
            report += f"- Fewest page faults: {best_page_faults}\n\n"
        
        return report
    
    def create_visualizations(self, df: pd.DataFrame, save_dir: str = "."):
        """Create comprehensive visualizations."""
        plt.style.use('seaborn-v0_8')
        
        # 1. Performance comparison heatmap
        plt.figure(figsize=(12, 8))
        pivot_data = df.pivot_table(values='hit_ratio', index='workload', 
                                   columns='algorithm', aggfunc='mean')
        sns.heatmap(pivot_data, annot=True, cmap='RdYlGn', fmt='.3f')
        plt.title('Hit Ratio by Algorithm and Workload')
        plt.tight_layout()
        plt.savefig(f"{save_dir}/performance_heatmap.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        # 2. Box plots for each metric
        metrics = ['hit_ratio', 'page_faults', 'execution_time']
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        for i, metric in enumerate(metrics):
            sns.boxplot(data=df, x='algorithm', y=metric, ax=axes[i])
            axes[i].set_title(f'{metric.replace("_", " ").title()} Distribution')
            axes[i].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{save_dir}/distribution_plots.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        # 3. Algorithm performance across workloads
        plt.figure(figsize=(14, 10))
        for i, workload in enumerate(df['workload'].unique()):
            plt.subplot(2, 3, i + 1)
            workload_data = df[df['workload'] == workload]
            sns.barplot(data=workload_data, x='algorithm', y='hit_ratio')
            plt.title(f'{workload.title()} Workload')
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{save_dir}/workload_comparison.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        # 4. Execution time comparison
        plt.figure(figsize=(10, 6))
        exec_time_summary = df.groupby('algorithm')['execution_time'].agg(['mean', 'std'])
        exec_time_summary.plot(kind='bar', y='mean', yerr='std', capsize=4)
        plt.title('Algorithm Execution Time Comparison')
        plt.ylabel('Execution Time (seconds)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{save_dir}/execution_time_comparison.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Visualizations saved to {save_dir}/")
    
    def optimize_parameters(self, workload_generator, validation_pattern: List,
                          target_metric: str = 'hit_ratio', maximize: bool = True) -> Dict:
        """
        Optimize algorithm parameters using grid search.
        
        Args:
            workload_generator: Workload generator instance
            validation_pattern: Validation pattern for optimization
            target_metric: Metric to optimize
            maximize: Whether to maximize or minimize the metric
            
        Returns:
            Dictionary with best parameters and performance
        """
        print(f"Optimizing parameters for {target_metric}...")
        
        best_score = float('-inf') if maximize else float('inf')
        best_params = {}
        best_algorithm = None
        
        optimization_results = []
        
        # Test each algorithm with parameter combinations
        for algorithm in self.algorithms:
            param_grid = self.parameter_grids.get('memory_manager', {})
            
            for params in ParameterGrid(param_grid):
                # Configure and test
                original_params = self._configure_memory_manager(params)
                
                try:
                    result = self._single_evaluation(algorithm, 'optimization', 
                                                   validation_pattern, params, 0)
                    score = result.metrics.get(target_metric, 0)
                    
                    optimization_results.append({
                        'algorithm': algorithm,
                        'params': params,
                        'score': score,
                        'metrics': result.metrics
                    })
                    
                    # Check if this is the best configuration
                    is_better = (maximize and score > best_score) or \
                              (not maximize and score < best_score)
                    
                    if is_better:
                        best_score = score
                        best_params = params.copy()
                        best_algorithm = algorithm
                
                finally:
                    self._restore_memory_manager(original_params)
        
        print(f"Best configuration found:")
        print(f"  Algorithm: {best_algorithm}")
        print(f"  Parameters: {best_params}")
        print(f"  {target_metric}: {best_score:.4f}")
        
        return {
            'best_algorithm': best_algorithm,
            'best_parameters': best_params,
            'best_score': best_score,
            'all_results': optimization_results
        }
    
    def real_time_monitoring(self, workload_generator, duration: int = 60, 
                           update_interval: int = 5) -> Dict:
        """
        Monitor algorithm performance in real-time.
        
        Args:
            workload_generator: Real-time workload generator
            duration: Monitoring duration in seconds
            update_interval: Update interval in seconds
            
        Returns:
            Dictionary with monitoring results
        """
        print(f"Starting real-time monitoring for {duration} seconds...")
        
        monitoring_results = {alg: [] for alg in self.algorithms}
        start_time = time.time()
        
        # Start workload generation
        workload_generator.start_real_time_generation()
        
        try:
            while time.time() - start_time < duration:
                update_start = time.time()
                
                # Collect accesses for this interval
                interval_accesses = []
                while time.time() - update_start < update_interval:
                    access = workload_generator.get_next_access()
                    if access:
                        interval_accesses.append(access)
                    else:
                        time.sleep(0.001)  # Small delay if no access available
                
                if interval_accesses:
                    # Test each algorithm on this interval
                    for algorithm in self.algorithms:
                        result = self._single_evaluation(algorithm, 'real_time',
                                                       interval_accesses, {}, 0)
                        
                        monitoring_results[algorithm].append({
                            'timestamp': time.time(),
                            'interval_size': len(interval_accesses),
                            'metrics': result.metrics
                        })
                
                print(f"Monitored {len(interval_accesses)} accesses in last {update_interval}s")
        
        finally:
            workload_generator.stop_real_time_generation()
        
        print("Real-time monitoring completed!")
        return monitoring_results 