from vmm.algorithms.base_algorithm import BaseReplacementAlgorithm

class ClockReplacementAlgorithm(BaseReplacementAlgorithm):
    """
    Clock (Second Chance) page replacement algorithm.
    
    This algorithm uses a circular list and reference bits to implement
    a more sophisticated replacement policy than FIFO, giving pages a
    "second chance" if they have been referenced recently.
    """
    
    def __init__(self, memory_manager):
        super().__init__(memory_manager)
        self.clock_hand = 0  # Points to current position in the clock
        self.reference_bits = [False] * memory_manager.num_frames
        self.dirty_bits = [False] * memory_manager.num_frames
        self.frame_pages = [None] * memory_manager.num_frames  # Track which page is in each frame
        self.loaded_frames = set()  # Track which frames have pages loaded
        
    def select_victim_frame(self):
        """
        Select a frame for replacement using the clock algorithm.
        
        Returns:
            Frame number to replace
        """
        # If we have empty frames, use them first
        for frame in range(self.memory_manager.num_frames):
            if frame not in self.loaded_frames:
                self.loaded_frames.add(frame)
                return frame
        
        # All frames are occupied, use clock algorithm
        while True:
            current_frame = self.clock_hand
            
            # Check reference bit
            if not self.reference_bits[current_frame]:
                # Page hasn't been referenced recently, select it
                victim_frame = current_frame
                self.clock_hand = (self.clock_hand + 1) % self.memory_manager.num_frames
                
                # Reset bits for the victim frame
                self.reference_bits[victim_frame] = False
                self.dirty_bits[victim_frame] = False
                
                return victim_frame
            else:
                # Give page a second chance - clear reference bit
                self.reference_bits[current_frame] = False
                self.clock_hand = (self.clock_hand + 1) % self.memory_manager.num_frames
    
    def page_accessed(self, page_number, frame_number):
        """
        Update algorithm state when a page is accessed.
        
        Args:
            page_number: The page that was accessed
            frame_number: The frame containing the page
        """
        if frame_number < len(self.reference_bits):
            self.reference_bits[frame_number] = True
            self.frame_pages[frame_number] = page_number
            self.loaded_frames.add(frame_number)
    
    def page_written(self, page_number, frame_number):
        """
        Mark a page as dirty when it's written to.
        
        Args:
            page_number: The page that was written to
            frame_number: The frame containing the page
        """
        if frame_number < len(self.dirty_bits):
            self.dirty_bits[frame_number] = True
    
    def get_algorithm_stats(self):
        """
        Return algorithm-specific statistics.
        
        Returns:
            Dictionary of algorithm statistics
        """
        return {
            'algorithm': 'clock',
            'clock_hand_position': self.clock_hand,
            'pages_with_reference_bit': sum(self.reference_bits),
            'dirty_pages': sum(self.dirty_bits),
            'loaded_frames': len(self.loaded_frames)
        } 