from vmm.algorithms.base_algorithm import BaseReplacementAlgorithm

class OptimalReplacementAlgorithm(BaseReplacementAlgorithm):
    """
    Optimal (OPT) page replacement algorithm.
    
    This algorithm has perfect knowledge of future page references and always
    selects the page that will be referenced furthest in the future (or never again).
    This serves as a theoretical optimal baseline for comparison.
    """
    
    def __init__(self, memory_manager, future_references=None):
        super().__init__(memory_manager)
        self.future_references = future_references or []
        self.current_position = 0
        self.frame_pages = [None] * memory_manager.num_frames
        self.loaded_frames = set()
        
    def set_future_references(self, references):
        """
        Set the future reference string for optimal decisions.
        
        Args:
            references: List of future page references
        """
        self.future_references = references
        self.current_position = 0
    
    def select_victim_frame(self):
        """
        Select a frame for replacement using optimal strategy.
        
        Returns:
            Frame number to replace
        """
        # If we have empty frames, use them first
        for frame in range(self.memory_manager.num_frames):
            if frame not in self.loaded_frames:
                self.loaded_frames.add(frame)
                return frame
        
        # All frames are occupied, find the optimal victim
        furthest_distance = -1
        victim_frame = 0
        
        for frame in range(self.memory_manager.num_frames):
            page_in_frame = self.frame_pages[frame]
            
            # Find when this page will be referenced next
            next_reference = self._find_next_reference(page_in_frame)
            
            if next_reference == -1:  # Page never referenced again
                return frame
            elif next_reference > furthest_distance:
                furthest_distance = next_reference
                victim_frame = frame
        
        return victim_frame
    
    def _find_next_reference(self, page_number):
        """
        Find the next reference to a specific page.
        
        Args:
            page_number: Page to search for
            
        Returns:
            Position of next reference, or -1 if never referenced again
        """
        for i in range(self.current_position + 1, len(self.future_references)):
            if self.future_references[i] == page_number:
                return i - self.current_position
        return -1  # Never referenced again
    
    def page_accessed(self, page_number, frame_number):
        """
        Update algorithm state when a page is accessed.
        
        Args:
            page_number: The page that was accessed
            frame_number: The frame containing the page
        """
        if frame_number < len(self.frame_pages):
            self.frame_pages[frame_number] = page_number
            self.loaded_frames.add(frame_number)
        self.current_position += 1
    
    def get_algorithm_stats(self):
        """
        Return algorithm-specific statistics.
        
        Returns:
            Dictionary of algorithm statistics
        """
        return {
            'algorithm': 'optimal',
            'current_position': self.current_position,
            'loaded_frames': len(self.loaded_frames),
            'references_remaining': len(self.future_references) - self.current_position
        } 