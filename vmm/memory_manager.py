class MemoryManager:
    """
    Manages the virtual memory system, including address translation and page replacement.
    """
    def __init__(self, virtual_memory_size=2**16, page_size=2**8, physical_memory_size=2**10):
        """
        Initialize the memory manager.
        
        Args:
            virtual_memory_size: Size of virtual memory in bytes
            page_size: Size of a page in bytes
            physical_memory_size: Size of physical memory in bytes
        """
        self.virtual_memory_size = virtual_memory_size
        self.page_size = page_size
        self.physical_memory_size = physical_memory_size
        
        # Calculate the number of pages and frames
        self.num_pages = virtual_memory_size // page_size
        self.num_frames = physical_memory_size // page_size
        
        # Initialize memory structures
        self.virtual_memory = [0] * virtual_memory_size
        self.physical_memory = [0] * physical_memory_size
        
        # Initialize page table
        from vmm.page_table import PageTable
        self.page_table = PageTable(self.num_pages, self.num_frames)
        
        # Initially, no replacement algorithm is set
        self.replacement_algorithm = None
        
        # Performance metrics
        self.page_faults = 0
        self.memory_accesses = 0
        self.hit_ratio = 0.0
        self.write_operations = 0
        self.read_operations = 0
        self.disk_writes = 0  # When dirty pages are written back
        
        # Advanced VMM features
        self.enable_write_tracking = True
        self.enable_prefetching = False
        self.prefetch_window = 2
    
    def set_replacement_algorithm(self, algorithm):
        """Set the page replacement algorithm."""
        self.replacement_algorithm = algorithm
        
    def access_memory(self, virtual_address, is_write=False):
        """
        Access memory at the given virtual address.
        
        Args:
            virtual_address: The virtual address to access
            is_write: Whether this is a write operation
            
        Returns:
            The value at the given virtual address
        """
        if virtual_address < 0 or virtual_address >= self.virtual_memory_size:
            raise ValueError(f"Virtual address {virtual_address} out of bounds")
        
        self.memory_accesses += 1
        if is_write:
            self.write_operations += 1
        else:
            self.read_operations += 1
        
        # Calculate page number and offset
        page_number = virtual_address // self.page_size
        offset = virtual_address % self.page_size
        
        # Check if page is in physical memory
        frame_number = self.page_table.get_frame_number(page_number)
        
        if frame_number is None:
            # Page fault - page not in physical memory
            self.page_faults += 1
            
            # Use replacement algorithm to find a frame to replace
            if self.replacement_algorithm is None:
                raise RuntimeError("No replacement algorithm set")
            
            frame_number = self.replacement_algorithm.select_victim_frame()
            
            # If a page is being replaced, check if it's dirty
            replaced_page = self.page_table.get_page_number(frame_number)
            if replaced_page is not None:
                # Check if the replaced page is dirty (needs to be written back)
                if hasattr(self.replacement_algorithm, 'dirty_bits') and \
                   frame_number < len(self.replacement_algorithm.dirty_bits) and \
                   self.replacement_algorithm.dirty_bits[frame_number]:
                    self.disk_writes += 1
                
                self.page_table.remove_mapping(replaced_page)
            
            # Add new mapping to page table
            self.page_table.add_mapping(page_number, frame_number)
            
            # Notify algorithm of page access
            self.replacement_algorithm.page_accessed(page_number, frame_number)
            
            # Handle prefetching if enabled
            if self.enable_prefetching:
                self._prefetch_pages(page_number)
        else:
            # Page hit - page already in physical memory
            # Notify algorithm of page access
            self.replacement_algorithm.page_accessed(page_number, frame_number)
        
        # Handle write operations
        if is_write and hasattr(self.replacement_algorithm, 'page_written'):
            self.replacement_algorithm.page_written(page_number, frame_number)
        
        # Calculate physical address
        physical_address = frame_number * self.page_size + offset
        
        # Update hit ratio
        self.hit_ratio = (self.memory_accesses - self.page_faults) / self.memory_accesses
        
        # Return value at physical address
        return self.physical_memory[physical_address]
    
    def write_memory(self, virtual_address, value):
        """
        Write a value to the given virtual address.
        
        Args:
            virtual_address: The virtual address to write to
            value: The value to write
        """
        if virtual_address < 0 or virtual_address >= self.virtual_memory_size:
            raise ValueError(f"Virtual address {virtual_address} out of bounds")
        
        # Access memory first to ensure page is in physical memory
        self.access_memory(virtual_address)
        
        # Calculate page number and offset
        page_number = virtual_address // self.page_size
        offset = virtual_address % self.page_size
        
        # Get frame number from page table
        frame_number = self.page_table.get_frame_number(page_number)
        
        # Calculate physical address
        physical_address = frame_number * self.page_size + offset
        
        # Write value to physical memory
        self.physical_memory[physical_address] = value
        
        # Also write to virtual memory for simulation purposes
        self.virtual_memory[virtual_address] = value
    
    def _prefetch_pages(self, current_page):
        """
        Prefetch nearby pages when prefetching is enabled.
        
        Args:
            current_page: The page that was just accessed
        """
        for i in range(1, self.prefetch_window + 1):
            next_page = current_page + i
            if next_page < self.num_pages:
                # Check if page is not already in memory
                if self.page_table.get_frame_number(next_page) is None:
                    # Find an empty frame or don't prefetch if all are full
                    for frame in range(self.num_frames):
                        if self.page_table.get_page_number(frame) is None:
                            self.page_table.add_mapping(next_page, frame)
                            if hasattr(self.replacement_algorithm, 'page_accessed'):
                                self.replacement_algorithm.page_accessed(next_page, frame)
                            break
    
    def get_metrics(self):
        """Return current performance metrics."""
        miss_ratio = self.page_faults / self.memory_accesses if self.memory_accesses > 0 else 0
        write_ratio = self.write_operations / self.memory_accesses if self.memory_accesses > 0 else 0
        
        metrics = {
            'page_faults': self.page_faults,
            'memory_accesses': self.memory_accesses,
            'hit_ratio': self.hit_ratio,
            'miss_ratio': miss_ratio,
            'write_operations': self.write_operations,
            'read_operations': self.read_operations,
            'write_ratio': write_ratio,
            'disk_writes': self.disk_writes
        }
        
        # Add algorithm-specific metrics if available
        if hasattr(self.replacement_algorithm, 'get_algorithm_stats'):
            algorithm_stats = self.replacement_algorithm.get_algorithm_stats()
            metrics.update(algorithm_stats)
        
        return metrics
    
    def reset_metrics(self):
        """Reset performance metrics."""
        self.page_faults = 0
        self.memory_accesses = 0
        self.hit_ratio = 0.0
        self.write_operations = 0
        self.read_operations = 0
        self.disk_writes = 0