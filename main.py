import time
from vmm.memory_manager import MemoryManager
from vmm.algorithms import get_algorithm
from ml.data_generator import WorkloadGenerator
from ml.feature_extractor import FeatureExtractor
from ml.model import PageReplacementPredictor
from visualization.visualizer import MemoryVisualizer

def evaluate_algorithm(memory_manager, algorithm_name, access_pattern):
    """
    Evaluate a page replacement algorithm on an access pattern.
    
    Args:
        memory_manager: Memory manager instance
        algorithm_name: Name of the algorithm to evaluate
        access_pattern: List of memory addresses to access
        
    Returns:
        Dictionary of performance metrics
    """
    # Reset memory manager state
    memory_manager.page_table = memory_manager.page_table.__class__(
        memory_manager.num_pages, memory_manager.num_frames
    )
    memory_manager.reset_metrics()
    
    # Set replacement algorithm
    algorithm = get_algorithm(algorithm_name, memory_manager)
    memory_manager.set_replacement_algorithm(algorithm)
    
    # Process memory accesses
    for address in access_pattern:
        memory_manager.access_memory(address)
    
    # Return metrics
    metrics = memory_manager.get_metrics()
    metrics['algorithm'] = algorithm_name
    
    return metrics

def train_ml_model(memory_manager, predictor, extractor):
    """
    Train the ML model with generated data and perform cross-validation.
    
    Args:
        memory_manager: Memory manager instance
        predictor: ML model instance
        extractor: Feature extractor instance
        
    Returns:
        Trained predictor
    """
    import random
    import numpy as np
    from sklearn.model_selection import cross_val_score

    print("Generating training data...")
    # Generate more synthetic workloads (increased from 5 to 20 per pattern type)
    generator = WorkloadGenerator(memory_manager.virtual_memory_size)
    patterns = generator.generate_labeled_patterns(num_patterns=20, accesses_per_pattern=1000)
    
    # Evaluate algorithms on each pattern
    all_features = []
    best_algorithms = []
    
    algorithms = ['fifo', 'lru']
    fifo_wins = 0
    lru_wins = 0
    ties = 0
    
    for pattern_type, pattern_list in patterns.items():
        print(f"Processing {pattern_type} patterns...")
        pattern_fifo_wins = 0
        pattern_lru_wins = 0
        pattern_ties = 0
        
        for i, pattern in enumerate(pattern_list):
            # Extract features from pattern
            features = extractor.extract_features(pattern)
            all_features.append(features)
            
            # Evaluate each algorithm on the pattern
            algorithm_metrics = {}
            for algorithm in algorithms:
                metrics = evaluate_algorithm(memory_manager, algorithm, pattern)
                algorithm_metrics[algorithm] = metrics
            
            # Print detailed comparison
            print(f"  Pattern {i+1}:")
            for algorithm in algorithms:
                metrics = algorithm_metrics[algorithm]
                print(f"    {algorithm.upper()}: Hit ratio: {metrics['hit_ratio']:.4f}, Page faults: {metrics['page_faults']}")
            
            # Find algorithms with the maximum hit ratio
            max_hit_ratio = max(algorithm_metrics[alg]['hit_ratio'] for alg in algorithms)
            best_algorithms_list = [alg for alg in algorithms 
                                   if algorithm_metrics[alg]['hit_ratio'] == max_hit_ratio]
            
            if len(best_algorithms_list) > 1:
                # We have a tie - randomly select to avoid bias
                ties += 1
                pattern_ties += 1
                best_algorithm = random.choice(best_algorithms_list)
                print(f"    TIE: Randomly selected {best_algorithm}")
            else:
                best_algorithm = best_algorithms_list[0]
                print(f"    Best algorithm is {best_algorithm}")
            
            best_algorithms.append(best_algorithm)
            
            # Count wins by algorithm
            if best_algorithm == 'fifo':
                fifo_wins += 1
                pattern_fifo_wins += 1
            else:
                lru_wins += 1
                pattern_lru_wins += 1
        
        print(f"  {pattern_type} summary: FIFO wins: {pattern_fifo_wins}, LRU wins: {pattern_lru_wins}, Ties: {pattern_ties}")
    
    print(f"\nOverall algorithm wins: FIFO: {fifo_wins}, LRU: {lru_wins}, Ties: {ties}")
    
    # Perform cross-validation
    # Preprocess features for cross-validation
    X_processed, _ = predictor.preprocess_features(all_features)
    y = np.array(best_algorithms)
    
    # Perform 5-fold cross-validation
    print("\nPerforming 5-fold cross-validation...")
    cv_scores = cross_val_score(predictor.model, X_processed, y, cv=5)
    print(f"Cross-validation scores: {cv_scores}")
    print(f"Mean CV accuracy: {cv_scores.mean():.4f}")
    
    # Train the final model on all data
    print("\nTraining final model...")
    accuracy = predictor.train(all_features, best_algorithms)
    print(f"Model trained with accuracy: {accuracy:.4f}")
    
    # Print feature importance
    importance = predictor.feature_importance()
    print("Feature importance:")
    for feature, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
        if score > 0.01:  # Only show features with significant importance
            print(f"  {feature}: {score:.4f}")
    
    return predictor




def run_with_predictor(memory_manager, predictor, extractor, access_pattern):
    """
    Run memory manager with ML-based algorithm selection.
    
    Args:
        memory_manager: Memory manager instance
        predictor: Trained ML model instance
        extractor: Feature extractor instance
        access_pattern: List of memory addresses to access
        
    Returns:
        Dictionary of performance metrics
    """
    # Extract features from the current access pattern
    features = extractor.extract_features(access_pattern)
    
    # Predict best algorithm
    best_algorithm = predictor.predict(features)
    print(f"Predicted best algorithm: {best_algorithm}")
    
    # Evaluate with the predicted algorithm
    return evaluate_algorithm(memory_manager, best_algorithm, access_pattern)

def main():
    """Main function to run the MemoryLearn prototype."""
    print("MemoryLearn Project - Phase 1 Prototype")
    
    # Initialize components
    virtual_memory_size = 2**16  # 64KB
    page_size = 2**8             # 256B
    physical_memory_size = 2**10  # 1KB
    
    memory_manager = MemoryManager(
        virtual_memory_size=virtual_memory_size,
        page_size=page_size,
        physical_memory_size=physical_memory_size
    )
    
    extractor = FeatureExtractor(page_size)
    predictor = PageReplacementPredictor()
    visualizer = MemoryVisualizer()
    
    # Train the ML model
    predictor = train_ml_model(memory_manager, predictor, extractor)
    
    # Generate test workload
    generator = WorkloadGenerator(memory_manager.virtual_memory_size, seed=42)
    test_pattern = generator.mixed_pattern(2000)
    
    # Evaluate each algorithm and the ML predictor
    algorithms = ['fifo', 'lru']
    all_metrics = {}
    
    for algorithm in algorithms:
        print(f"\nEvaluating {algorithm.upper()}...")
        metrics = evaluate_algorithm(memory_manager, algorithm, test_pattern)
        all_metrics[algorithm] = metrics
        print(f"  Page faults: {metrics['page_faults']}")
        print(f"  Hit ratio: {metrics['hit_ratio']:.4f}")
    
    print("\nEvaluating ML-based algorithm selection...")
    ml_metrics = run_with_predictor(memory_manager, predictor, extractor, test_pattern)
    all_metrics['ml'] = ml_metrics
    print(f"  Selected algorithm: {ml_metrics['algorithm']}")
    print(f"  Page faults: {ml_metrics['page_faults']}")
    print(f"  Hit ratio: {ml_metrics['hit_ratio']:.4f}")
    
    # Visualize results
    visualizer.plot_hit_ratios(all_metrics)
    visualizer.plot_page_faults(all_metrics)
    
    print("\nVisualization saved to 'hit_ratio.png' and 'page_faults.png'")

if __name__ == "__main__":
    main()