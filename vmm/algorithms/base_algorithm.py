from abc import ABC, abstractmethod

class BaseReplacementAlgorithm(ABC):
    """
    Abstract base class for page replacement algorithms.
    """
    def __init__(self, memory_manager):
        """
        Initialize the algorithm.
        
        Args:
            memory_manager: Reference to the memory manager
        """
        self.memory_manager = memory_manager
    
    @abstractmethod
    def select_victim_frame(self):
        """
        Select a frame to be replaced.
        
        Returns:
            The frame number to be replaced
        """
        pass
    
    @abstractmethod
    def page_accessed(self, page_number, frame_number):
        """
        Notify algorithm that a page has been accessed.
        
        Args:
            page_number: The page number accessed
            frame_number: The frame number where the page is stored
        """
        pass