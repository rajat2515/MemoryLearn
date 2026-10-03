from vmm.algorithms.base_algorithm import BaseReplacementAlgorithm

class LRUReplacementAlgorithm(BaseReplacementAlgorithm):
    """
    Least Recently Used page replacement algorithm.
    
    Replaces the page that has not been used for the longest period of time.
    """
    def __init__(self, memory_manager):
        """
        Initialize the LRU algorithm.
        
        Args:
            memory_manager: Reference to the memory manager
        """
        super().__init__(memory_manager)
        # Dictionary mapping frame numbers to their last access time
        self.last_used_time = {}
        # Counter for tracking "time"
        self.time = 0
    
    def select_victim_frame(self):
        """
        Select a frame to be replaced using LRU policy.
        
        Returns:
            The frame number to be replaced
        """
        # Check if there are any free frames
        free_frame = self.memory_manager.page_table.get_free_frame()
        if free_frame is not None:
            # Initialize the new frame's last used time
            self.last_used_time[free_frame] = self.time
            return free_frame
        
        # If no free frames, select the least recently used frame
        if not self.last_used_time:
            # If no frames are tracked (should not happen), use frame 0
            self.last_used_time[0] = self.time
            return 0
        
        # Find the frame with the smallest last used time
        lru_frame = min(self.last_used_time, key=self.last_used_time.get)
        return lru_frame
    
    def page_accessed(self, page_number, frame_number):
        """
        Notify algorithm that a page has been accessed.
        
        For LRU, we update the last used time of the frame.
        
        Args:
            page_number: The page number accessed
            frame_number: The frame number where the page is stored
        """
        # Increment time
        self.time += 1
        # Update last used time for the accessed frame
        self.last_used_time[frame_number] = self.time