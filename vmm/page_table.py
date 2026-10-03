class PageTable:
    """
    Represents a page table that maps virtual pages to physical frames.
    """
    def __init__(self, num_pages, num_frames):
        """
        Initialize page table.
        
        Args:
            num_pages: Number of pages in virtual memory
            num_frames: Number of frames in physical memory
        """
        self.num_pages = num_pages
        self.num_frames = num_frames
        
        # Initialize page table with None entries (indicating not in physical memory)
        self.page_to_frame = [None] * num_pages
        
        # Reverse mapping from frames to pages (useful for page replacement)
        self.frame_to_page = [None] * num_frames
    
    def add_mapping(self, page_number, frame_number):
        """
        Add a mapping from page to frame.
        
        Args:
            page_number: The virtual page number
            frame_number: The physical frame number
        """
        if page_number < 0 or page_number >= self.num_pages:
            raise ValueError(f"Page number {page_number} out of bounds")
        if frame_number < 0 or frame_number >= self.num_frames:
            raise ValueError(f"Frame number {frame_number} out of bounds")
        
        self.page_to_frame[page_number] = frame_number
        self.frame_to_page[frame_number] = page_number
    
    def remove_mapping(self, page_number):
        """
        Remove a mapping for the given page.
        
        Args:
            page_number: The virtual page number
        """
        if page_number < 0 or page_number >= self.num_pages:
            raise ValueError(f"Page number {page_number} out of bounds")
        
        frame_number = self.page_to_frame[page_number]
        if frame_number is not None:
            self.frame_to_page[frame_number] = None
        self.page_to_frame[page_number] = None
    
    def get_frame_number(self, page_number):
        """
        Get the frame number for the given page.
        
        Args:
            page_number: The virtual page number
            
        Returns:
            The physical frame number, or None if page is not in memory
        """
        if page_number < 0 or page_number >= self.num_pages:
            raise ValueError(f"Page number {page_number} out of bounds")
        
        return self.page_to_frame[page_number]
    
    def get_page_number(self, frame_number):
        """
        Get the page number for the given frame.
        
        Args:
            frame_number: The physical frame number
            
        Returns:
            The virtual page number, or None if frame is free
        """
        if frame_number < 0 or frame_number >= self.num_frames:
            raise ValueError(f"Frame number {frame_number} out of bounds")
        
        return self.frame_to_page[frame_number]
    
    def is_page_in_memory(self, page_number):
        """
        Check if the given page is in memory.
        
        Args:
            page_number: The virtual page number
            
        Returns:
            True if page is in memory, False otherwise
        """
        return self.get_frame_number(page_number) is not None
    
    def get_free_frame(self):
        """
        Get a free frame if available.
        
        Returns:
            A free frame number, or None if no free frames
        """
        try:
            return self.frame_to_page.index(None)
        except ValueError:
            return None