from vmm.algorithms.fifo import FIFOReplacementAlgorithm
from vmm.algorithms.lru import LRUReplacementAlgorithm
from vmm.algorithms.clock import ClockReplacementAlgorithm
from vmm.algorithms.optimal import OptimalReplacementAlgorithm

# Dictionary mapping algorithm names to their classes
replacement_algorithms = {
    'fifo': FIFOReplacementAlgorithm,
    'lru': LRUReplacementAlgorithm,
    'clock': ClockReplacementAlgorithm,
    'optimal': OptimalReplacementAlgorithm
}

def get_algorithm(name, memory_manager):
    """
    Factory function to create replacement algorithm instances.
    
    Args:
        name: The name of the algorithm
        memory_manager: Reference to the memory manager
        
    Returns:
        An instance of the requested algorithm
    """
    if name.lower() not in replacement_algorithms:
        raise ValueError(f"Unknown algorithm: {name}")
    
    return replacement_algorithms[name.lower()](memory_manager)