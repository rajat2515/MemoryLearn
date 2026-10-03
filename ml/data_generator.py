import random
import numpy as np

class WorkloadGenerator:
    """
    Generates synthetic memory access patterns for testing and training.
    """
    def __init__(self, address_space_size, seed=None):
        """
        Initialize the workload generator.
        
        Args:
            address_space_size: Size of the virtual address space
            seed: Random seed for reproducibility
        """
        self.address_space_size = address_space_size
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    def sequential_pattern(self, num_accesses, start_address=0, stride=1):
        """
        Generate sequential memory access pattern.
        
        Args:
            num_accesses: Number of memory accesses to generate
            start_address: Starting address
            stride: Address increment per access
            
        Returns:
            List of virtual addresses to access
        """
        pattern = []
        address = start_address
        
        for _ in range(num_accesses):
            # Ensure address is within bounds
            address = address % self.address_space_size
            pattern.append(address)
            address += stride
        
        return pattern
    
    def random_pattern(self, num_accesses):
        """
        Generate random memory access pattern.
        
        Args:
            num_accesses: Number of memory accesses to generate
            
        Returns:
            List of virtual addresses to access
        """
        return [random.randint(0, self.address_space_size - 1) for _ in range(num_accesses)]
    
    def locality_pattern(self, num_accesses, hot_region_size=0.2, hot_access_prob=0.8):
        """
        Generate memory access pattern with temporal and spatial locality.
        
        Args:
            num_accesses: Number of memory accesses to generate
            hot_region_size: Size of the "hot" region as a fraction of address space
            hot_access_prob: Probability of accessing the hot region
            
        Returns:
            List of virtual addresses to access
        """
        pattern = []
        hot_size = int(self.address_space_size * hot_region_size)
        hot_start = random.randint(0, self.address_space_size - hot_size)
        hot_end = hot_start + hot_size
        
        for _ in range(num_accesses):
            if random.random() < hot_access_prob:
                # Access hot region with higher probability
                address = random.randint(hot_start, hot_end - 1)
            else:
                # Access cold region
                if random.random() < 0.5 and hot_start > 0:
                    # Cold region before hot region
                    address = random.randint(0, hot_start - 1)
                else:
                    # Cold region after hot region
                    address = random.randint(hot_end, self.address_space_size - 1)
            
            pattern.append(address)
        
        return pattern
    
    def loop_pattern(self, num_accesses, loop_size=100):
        """
        Generate a looping access pattern that simulates program loops.
        
        Args:
            num_accesses: Number of memory accesses to generate
            loop_size: Size of the loop in number of addresses
            
        Returns:
            List of virtual addresses to access
        """
        pattern = []
        loop_start = random.randint(0, self.address_space_size - loop_size)
        loop_addresses = list(range(loop_start, loop_start + loop_size))
        
        # Add some randomness to simulate non-sequential accesses within loops
        random.shuffle(loop_addresses)
        
        # Generate the pattern by repeating the loop
        for i in range(num_accesses):
            idx = i % loop_size
            pattern.append(loop_addresses[idx])
        
        return pattern
    
    def mixed_pattern(self, num_accesses):
        """
        Generate a mixed access pattern with various behaviors.
        
        Args:
            num_accesses: Number of memory accesses to generate
            
        Returns:
            List of virtual addresses to access
        """
        pattern = []
        
        # Divide the accesses into segments
        segment_size = num_accesses // 4
        
        # Sequential segment
        pattern.extend(self.sequential_pattern(segment_size))
        
        # Random segment
        pattern.extend(self.random_pattern(segment_size))
        
        # Locality segment
        pattern.extend(self.locality_pattern(segment_size))
        
        # Loop segment
        pattern.extend(self.loop_pattern(num_accesses - len(pattern)))
        
        return pattern
    
    def generate_labeled_patterns(self, num_patterns=10, accesses_per_pattern=1000):
        """
        Generate labeled patterns for training the ML model.
        
        Args:
            num_patterns: Number of patterns to generate
            accesses_per_pattern: Number of accesses per pattern
            
        Returns:
            Dictionary mapping pattern types to lists of access patterns
        """
        patterns = {
            'sequential': [],
            'random': [],
            'locality': [],
            'loop': [],
            'mixed': []
        }
        
        for _ in range(num_patterns):
            patterns['sequential'].append(self.sequential_pattern(accesses_per_pattern))
            patterns['random'].append(self.random_pattern(accesses_per_pattern))
            patterns['locality'].append(self.locality_pattern(accesses_per_pattern))
            patterns['loop'].append(self.loop_pattern(accesses_per_pattern))
            patterns['mixed'].append(self.mixed_pattern(accesses_per_pattern))
        
        return patterns