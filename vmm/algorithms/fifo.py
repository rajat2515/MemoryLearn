from vmm.algorithms.base_algorithm import BaseReplacementAlgorithm
from collections import deque

class FIFOReplacementAlgorithm(BaseReplacementAlgorithm):
    """
    First-In-First-Out page replacement algorithm.
    
    Replaces the page that has been in memory the longest.
    """
    def __init__(self, memory_manager):
        """
        Initialize the FIFO algorithm.
        
        Args:
            memory_manager: Reference to the memory manager
        """
        super().__init__(memory_manager)
        # Queue of frame numbers in order of loading
        self.frame_queue = deque()
    
    def select_victim_frame(self):
        """
        Select a frame to be replaced using FIFO policy.
        
        Returns:
            The frame number to be replaced
        """
        # Check if there are any free frames
        free_frame = self.memory_manager.page_table.get_free_frame()
        if free_frame is not None:
            self.frame_queue.append(free_frame)
            return free_frame
        
        # If no free frames, select the oldest frame
        if not self.frame_queue:
            # If frame queue is empty (should not happen), use frame 0
            return 0
        
        oldest_frame = self.frame_queue.popleft()
        self.frame_queue.append(oldest_frame)
        return oldest_frame
    
    def page_accessed(self, page_number, frame_number):
        """
        Notify algorithm that a page has been accessed.
        
        For FIFO, we only track newly loaded frames.
        
        Args:
            page_number: The page number accessed
            frame_number: The frame number where the page is stored
        """
        # In FIFO, we only need to add new frames to the queue
        # If the frame is not in the queue, add it
        if frame_number not in self.frame_queue:
            self.frame_queue.append(frame_number)