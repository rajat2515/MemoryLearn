#!/usr/bin/env python3
"""
Enhanced MemoryLearn Project - Advanced Memory Management Learning System
with Clock algorithm, Optimal algorithm, advanced VMM features, and comprehensive evaluation.
"""

import time
import numpy as np
import pandas as pd
from vmm.memory_manager import MemoryManager
from vmm.algorithms import get_algorithm
from ml.data_generator import WorkloadGenerator
from ml.feature_extractor import FeatureExtractor
from ml.model import PageReplacementPredictor
from visualization.visualizer import MemoryVisualizer
from ml.advanced_data_generator import RealTimeWorkloadGenerator
from ml.advanced_evaluator import AdvancedAlgorithmEvaluator

def evaluate_algorithm_enhanced(memory_manager, algorithm_name, access_pattern):
    """
    Enhanced algorithm evaluation with write operations and advanced metrics.
    
    Args:
        memory_manager: Memory manager instance
        algorithm_name: Name of the algorithm to evaluate
        access_pattern: List of (address, is_write) tuples
        
    Returns:
        Dictionary of performance metrics
    """
    # Reset memory manager state
    memory_manager.page_table = memory_manager.page_table.__class__(
        memory_manager.num_pages, memory_manager.num_frames
    )
    memory_manager.reset_metrics()
    
    # Set replacement algorithm
    if algorithm_name == 'optimal':
        # Extract addresses for optimal algorithm
        addresses = [addr for addr, _ in access_pattern]
        algorithm = get_algorithm(algorithm_name, memory_manager)
        algorithm.set_future_references(addresses)
    else:
        algorithm = get_algorithm(algorithm_name, memory_manager)
    
    memory_manager.set_replacement_algorithm(algorithm)
    
    # Process memory accesses with write support
    start_time = time.time()
    for address, is_write in access_pattern:
        memory_manager.access_memory(address, is_write)
    execution_time = time.time() - start_time
    
    # Get comprehensive metrics
    metrics = memory_manager.get_metrics()
    metrics['algorithm'] = algorithm_name
    metrics['execution_time'] = execution_time
    
    return metrics

def run_comprehensive_benchmark():
    """Run comprehensive benchmark with all algorithms and workload types."""
    print("=" * 80)
    print("ENHANCED MEMORYLEARN PROJECT - COMPREHENSIVE BENCHMARK")
    print("=" * 80)
    
    # Verify all algorithms are available
    print(">> ALGORITHM AVAILABILITY CHECK:")
    from vmm.algorithms import replacement_algorithms
    available_algorithms = list(replacement_algorithms.keys())
    print(f"   Available algorithms: {available_algorithms}")
    
    # All algorithms including new ones
    algorithms = ['fifo', 'lru', 'clock', 'optimal']
    
    # Check if all required algorithms are available
    missing_algorithms = [alg for alg in algorithms if alg not in available_algorithms]
    if missing_algorithms:
        print(f"   [WARNING] Missing algorithms: {missing_algorithms}")
        algorithms = [alg for alg in algorithms if alg in available_algorithms]
    
    print(f"   [OK] Will test {len(algorithms)} algorithms: {[alg.upper() for alg in algorithms]}")
    print()
    
    # Initialize enhanced components
    virtual_memory_size = 2**16  # 64KB
    page_size = 2**8             # 256B
    physical_memory_size = 2**12  # 4KB (increased from 1KB)
    
    memory_manager = MemoryManager(
        virtual_memory_size=virtual_memory_size,
        page_size=page_size,
        physical_memory_size=physical_memory_size
    )
    
    # Enable advanced features
    memory_manager.enable_prefetching = True
    memory_manager.prefetch_window = 2
    
    # Create advanced workload generator
    advanced_generator = RealTimeWorkloadGenerator(
        virtual_memory_size=virtual_memory_size,
        page_size=page_size
    )
    
    # Configure workload parameters
    advanced_generator.configure_workload(
        temporal_locality=0.8,
        spatial_locality=0.7,
        working_set_size=32,
        write_probability=0.25,
        burst_probability=0.15
    )
    
    # Generate comprehensive benchmark suite
    print("Generating advanced benchmark workloads...")
    benchmark_suite = advanced_generator.generate_benchmark_suite()
    
    # Results storage
    all_results = []
    
    print(f"\nTesting {len(algorithms)} algorithms on {len(benchmark_suite)} workload types...")
    print("-" * 80)
    
    # Run comprehensive evaluation
    for workload_name, workload_pattern in benchmark_suite.items():
        print(f"\n>> WORKLOAD: {workload_name.upper()}")
        print(f"   Pattern size: {len(workload_pattern)} accesses")
        print(f"   Write percentage: {sum(1 for _, is_write in workload_pattern if is_write) / len(workload_pattern) * 100:.1f}%")
        
        workload_results = {}
        
        for algorithm in algorithms:
            print(f"   >> Testing {algorithm.upper()} algorithm...", end=" ")
            
            try:
                metrics = evaluate_algorithm_enhanced(
                    memory_manager, algorithm, workload_pattern
                )
                workload_results[algorithm] = metrics
                
                print(f"[COMPLETE]")
                print(f"      Hit ratio: {metrics['hit_ratio']:.4f} ({metrics['hit_ratio']*100:.1f}%)")
                print(f"      Page faults: {metrics['page_faults']}")
                print(f"      Execution time: {metrics['execution_time']:.4f}s")
                print(f"      Write operations: {metrics.get('write_operations', 0)}")
                
                # Store results
                result_record = {
                    'workload': workload_name,
                    'algorithm': algorithm,
                    **metrics
                }
                all_results.append(result_record)
                
            except Exception as e:
                print(f"[FAILED] {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Show workload summary with clearer winner display
        if workload_results:
            print(f"\n   >> WORKLOAD WINNERS:")
            
            # Best hit ratio
            best_hit_algo = max(workload_results.keys(), key=lambda x: workload_results[x]['hit_ratio'])
            best_hit_ratio = workload_results[best_hit_algo]['hit_ratio']
            print(f"      [BEST HIT RATIO] {best_hit_algo.upper()} - {best_hit_ratio:.4f} ({best_hit_ratio*100:.1f}%)")
            
            # Fewest page faults
            best_pf_algo = min(workload_results.keys(), key=lambda x: workload_results[x]['page_faults'])
            best_pf_count = workload_results[best_pf_algo]['page_faults']
            print(f"      [FEWEST PAGE FAULTS] {best_pf_algo.upper()} - {best_pf_count} faults")
            
            # Fastest execution
            fastest_algo = min(workload_results.keys(), key=lambda x: workload_results[x]['execution_time'])
            fastest_time = workload_results[fastest_algo]['execution_time']
            print(f"      [FASTEST EXECUTION] {fastest_algo.upper()} - {fastest_time:.4f}s")
            
            # Overall recommendation for this workload
            overall_best = best_hit_algo  # Default to best hit ratio
            print(f"      [RECOMMENDED FOR {workload_name.upper()}] {overall_best.upper()}")
    
    # Create comprehensive analysis
    print("\n" + "=" * 80)
    print("COMPREHENSIVE ANALYSIS")
    print("=" * 80)
    
    if not all_results:
        print("[ERROR] No results to analyze. Check algorithm implementation.")
        return None
    
    df = pd.DataFrame(all_results)
    
    # Overall algorithm performance
    print("\n>> OVERALL ALGORITHM PERFORMANCE:")
    overall_stats = df.groupby('algorithm').agg({
        'hit_ratio': ['mean', 'std', 'min', 'max'],
        'page_faults': ['mean', 'std', 'min', 'max'],
        'execution_time': ['mean', 'std'],
        'write_operations': 'mean',
        'disk_writes': 'mean'
    }).round(4)
    
    print(overall_stats.to_string())
    
    # Best algorithm per workload
    print("\n>> ALGORITHM SELECTION BY WORKLOAD TYPE:")
    for workload in df['workload'].unique():
        workload_data = df[df['workload'] == workload]
        best_hit_ratio = workload_data.loc[workload_data['hit_ratio'].idxmax()]
        best_page_faults = workload_data.loc[workload_data['page_faults'].idxmin()]
        
        print(f"\n  >> {workload.title()} Workload Analysis:")
        print(f"    [BEST HIT RATIO] {best_hit_ratio['algorithm'].upper()} ({best_hit_ratio['hit_ratio']:.4f})")
        print(f"    [BEST PAGE FAULTS] {best_page_faults['algorithm'].upper()} ({best_page_faults['page_faults']} faults)")
        
        # Show all algorithm performance for this workload
        print(f"    >> All Algorithm Performance:")
        for _, row in workload_data.iterrows():
            alg = row['algorithm'].upper()
            hit_ratio = row['hit_ratio']
            page_faults = row['page_faults']
            time_taken = row['execution_time']
            print(f"       {alg:8} -> Hit: {hit_ratio:.4f} | Faults: {page_faults:4d} | Time: {time_taken:.4f}s")
    
    # Algorithm rankings
    print("\n>> OVERALL ALGORITHM RANKINGS:")
    
    # Rank by hit ratio
    hit_ratio_ranking = df.groupby('algorithm')['hit_ratio'].mean().sort_values(ascending=False)
    print("\n  >> Ranked by Hit Ratio (Higher is Better):")
    for i, (alg, score) in enumerate(hit_ratio_ranking.items(), 1):
        ranking = f"#{i}"
        print(f"    {ranking} {alg.upper()}: {score:.4f} ({score*100:.1f}%)")
    
    # Rank by page faults (lower is better)
    page_fault_ranking = df.groupby('algorithm')['page_faults'].mean().sort_values()
    print("\n  >> Ranked by Page Faults (Lower is Better):")
    for i, (alg, score) in enumerate(page_fault_ranking.items(), 1):
        ranking = f"#{i}"
        print(f"    {ranking} {alg.upper()}: {score:.1f} faults avg")
    
    # Advanced metrics analysis
    print("\n>> ADVANCED METRICS ANALYSIS:")
    advanced_stats = df.groupby('algorithm').agg({
        'write_ratio': 'mean',
        'miss_ratio': 'mean',
        'disk_writes': 'mean'
    }).round(4)
    
    for alg in advanced_stats.index:
        stats = advanced_stats.loc[alg]
        print(f"  >> {alg.upper()} Performance Profile:")
        print(f"      Write ratio: {stats['write_ratio']:.4f} ({stats['write_ratio']*100:.1f}%)")
        print(f"      Miss ratio: {stats['miss_ratio']:.4f} ({stats['miss_ratio']*100:.1f}%)")
        print(f"      Disk writes: {stats['disk_writes']:.1f} avg")
    
    # Performance recommendations
    print("\n>> SMART ALGORITHM SELECTION GUIDE:")
    
    # Find the most consistent algorithm
    consistency_scores = df.groupby('algorithm')['hit_ratio'].std()
    most_consistent = consistency_scores.idxmin()
    print(f"  [MOST CONSISTENT] {most_consistent.upper()} (std dev: {consistency_scores[most_consistent]:.4f})")
    
    # Find the fastest algorithm
    speed_ranking = df.groupby('algorithm')['execution_time'].mean().sort_values()
    fastest = speed_ranking.index[0]
    print(f"  [FASTEST EXECUTION] {fastest.upper()} ({speed_ranking[fastest]:.4f}s avg)")
    
    # Overall recommendation
    overall_scores = df.groupby('algorithm').apply(
        lambda x: x['hit_ratio'].mean() * 0.6 + (1 - x['miss_ratio'].mean()) * 0.4
    ).sort_values(ascending=False)
    
    best_overall = overall_scores.index[0]
    print(f"  [OVERALL CHAMPION] {best_overall.upper()} (composite score: {overall_scores[best_overall]:.4f})")
    
    print(f"\n>> ALGORITHM SELECTION RECOMMENDATIONS:")
    print(f"  • For HIGH PERFORMANCE: Use {hit_ratio_ranking.index[0].upper()}")
    print(f"  • For LOW MEMORY PRESSURE: Use {page_fault_ranking.index[0].upper()}")
    print(f"  • For SPEED CRITICAL: Use {fastest.upper()}")
    print(f"  • For CONSISTENT RESULTS: Use {most_consistent.upper()}")
    print(f"  • For BALANCED WORKLOADS: Use {best_overall.upper()}")
    
    # Create enhanced visualizations
    print("\n>> Generating enhanced visualizations...")
    visualizer = MemoryVisualizer()
    
    # Convert to old format for compatibility
    old_format_results = {}
    for _, row in df.iterrows():
        alg = row['algorithm']
        if alg not in old_format_results:
            old_format_results[alg] = row.to_dict()
    
    try:
        visualizer.plot_hit_ratios(old_format_results)
        visualizer.plot_page_faults(old_format_results)
        print("[OK] Basic visualizations saved")
        
        # Create advanced heatmap
        create_advanced_heatmap(df)
        
    except Exception as e:
        print(f"[WARNING] Visualization error: {e}")
    
    print("\n" + "=" * 80)
    print("ENHANCED MEMORYLEARN EVALUATION COMPLETE!")
    print("=" * 80)
    
    return df

def create_advanced_heatmap(df):
    """Create advanced heatmap visualization."""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Create heatmap of algorithm performance across workloads
        pivot_data = df.pivot_table(
            values='hit_ratio', 
            index='workload', 
            columns='algorithm', 
            aggfunc='mean'
        )
        
        plt.figure(figsize=(10, 6))
        sns.heatmap(pivot_data, annot=True, cmap='RdYlGn', fmt='.3f', 
                   cbar_kws={'label': 'Hit Ratio'})
        plt.title('Algorithm Performance Heatmap\n(Hit Ratio by Workload Type)', 
                 fontsize=14, fontweight='bold')
        plt.xlabel('Algorithm')
        plt.ylabel('Workload Type')
        plt.tight_layout()
        plt.savefig('advanced_performance_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("[OK] Advanced heatmap saved as 'advanced_performance_heatmap.png'")
        
    except ImportError:
        print("[WARNING] Seaborn not available for advanced heatmap")
    except Exception as e:
        print(f"[WARNING] Advanced heatmap error: {e}")

def demonstrate_real_time_features():
    """Demonstrate real-time workload generation features."""
    print("\n" + "=" * 80)
    print("REAL-TIME WORKLOAD GENERATION DEMONSTRATION")
    print("=" * 80)
    
    # Create real-time generator
    generator = RealTimeWorkloadGenerator(
        virtual_memory_size=65536,
        page_size=256
    )
    
    print(">> Current workload parameters:")
    stats = generator.get_generation_stats()
    for param, value in stats['workload_params'].items():
        print(f"  {param}: {value}")
    
    print(f"\n>> Starting real-time generation for 5 seconds...")
    generator.start_real_time_generation(rate=100)  # 100 accesses per second
    
    try:
        collected_accesses = []
        start_time = time.time()
        
        while time.time() - start_time < 5:
            access = generator.get_next_access()
            if access:
                collected_accesses.append(access)
            time.sleep(0.01)
        
        generator.stop_real_time_generation()
        
        print(f"[OK] Collected {len(collected_accesses)} real-time accesses")
        
        # Analyze the collected data
        if collected_accesses:
            addresses = [addr for addr, _ in collected_accesses]
            writes = sum(1 for _, is_write in collected_accesses if is_write)
            
            print(f"  [STATS] Write ratio: {writes/len(collected_accesses):.2%}")
            print(f"  [STATS] Address range: {min(addresses)} - {max(addresses)}")
            print(f"  [STATS] Unique addresses: {len(set(addresses))}")
    
    except Exception as e:
        print(f"[ERROR] Real-time demo error: {e}")
        generator.stop_real_time_generation()

def main():
    """Enhanced main function with comprehensive evaluation."""
    print(">> Starting Enhanced MemoryLearn Project...")
    
    try:
        # Run comprehensive benchmark
        results_df = run_comprehensive_benchmark()
        
        # Demonstrate real-time features
        demonstrate_real_time_features()
        
        # Save results
        results_df.to_csv('enhanced_memorylearn_results.csv', index=False)
        print(f"\n[SAVE] Results saved to 'enhanced_memorylearn_results.csv'")
        
        print("\n[SUCCESS] Enhanced MemoryLearn evaluation completed successfully!")
        print("   Check the generated files for detailed results and visualizations.")
        
    except Exception as e:
        print(f"[ERROR] Error in enhanced evaluation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 