import numpy as np
from collections import Counter

class FeatureExtractor:
    """
    Extracts features from memory access patterns for ML model.
    """
    def __init__(self, page_size):
        """
        Initialize the feature extractor.
        
        Args:
            page_size: Size of a page in bytes
        """
        self.page_size = page_size
    
    def extract_features(self, access_pattern, window_size=100):
        """
        Extract features from an access pattern.
        
        Args:
            access_pattern: List of virtual addresses
            window_size: Size of sliding window for feature extraction
            
        Returns:
            Dictionary of features
        """
        if len(access_pattern) < window_size:
            # Pad with repeated values if access pattern is too short
            access_pattern = access_pattern * (window_size // len(access_pattern) + 1)
        
        # Convert addresses to page numbers
        page_accesses = [addr // self.page_size for addr in access_pattern]
        
        features = {}
        
        # Feature 1: Unique pages ratio in window
        # High for random access, low for sequential or locality
        unique_pages_ratio = len(set(page_accesses[-window_size:])) / window_size
        features['unique_pages_ratio'] = unique_pages_ratio
        
        # Feature 2: Sequential access ratio
        # Calculate how many accesses are sequential
        sequential_count = 0
        for i in range(1, len(page_accesses[-window_size:])):
            if page_accesses[-window_size + i] == page_accesses[-window_size + i - 1] + 1:
                sequential_count += 1
        sequential_ratio = sequential_count / (window_size - 1)
        features['sequential_ratio'] = sequential_ratio
        
        # Feature 3: Repeated access ratio
        # Count occurrences of each page
        page_counts = Counter(page_accesses[-window_size:])
        # Calculate ratio of pages accessed more than once
        repeated_pages = sum(1 for count in page_counts.values() if count > 1)
        repeated_ratio = repeated_pages / len(page_counts) if page_counts else 0
        features['repeated_ratio'] = repeated_ratio
        
        # Feature 4: Locality score
        # Calculate standard deviation of page numbers (lower means higher locality)
        locality_score = np.std(page_accesses[-window_size:]) / self.page_size
        features['locality_score'] = locality_score
        
        # Feature 5: Working set size
        # Number of unique pages in window
        working_set_size = len(set(page_accesses[-window_size:]))
        features['working_set_size'] = working_set_size
        
        # Feature 6: Page reuse distance
        # Calculate average distance between accesses to the same page
        reuse_distances = []
        last_seen = {}
        for i, page in enumerate(page_accesses[-window_size:]):
            if page in last_seen:
                reuse_distances.append(i - last_seen[page])
            last_seen[page] = i
        avg_reuse_distance = np.mean(reuse_distances) if reuse_distances else window_size
        features['avg_reuse_distance'] = avg_reuse_distance / window_size  # Normalize
        
        return features