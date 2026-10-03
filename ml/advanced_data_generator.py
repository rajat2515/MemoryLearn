import random
import numpy as np
import time
import threading
from collections import deque
from typing import List, Dict, Tuple, Optional

class RealTimeWorkloadGenerator:
    """
    Advanced real-time workload generator that simulates realistic memory access patterns
    with configurable parameters and real-time streaming capabilities.
    """
    
    def __init__(self, virtual_memory_size: int, page_size: int = 256):
        self.virtual_memory_size = virtual_memory_size
        self.page_size = page_size
        self.num_pages = virtual_memory_size // page_size
        
        # Real-time generation state
        self.is_generating = False
        self.generation_thread = None
        self.access_queue = deque()
        self.generation_rate = 1000  # accesses per second
        
        # Pattern parameters
        self.workload_params = {
            'temporal_locality': 0.7,      # Probability of accessing recently used pages
            'spatial_locality': 0.6,       # Probability of accessing nearby pages
            'working_set_size': 64,        # Number of frequently accessed pages
            'phase_duration': 5000,        # How long each phase lasts
            'write_probability': 0.3,      # Probability of write operations
            'burst_probability': 0.1,      # Probability of burst access
            'burst_size': 50              # Size of burst accesses
        }
        
        # Workload state
        self.current_phase = 'random'
        self.phase_counter = 0
        self.working_set = set()
        self.recent_accesses = deque(maxlen=100)
        self.last_address = 0
        
    def configure_workload(self, **params):
        """
        Configure workload generation parameters.
        
        Args:
            **params: Parameter values to update
        """
        self.workload_params.update(params)
        print(f"Updated workload parameters: {params}")
    
    def start_real_time_generation(self, rate: int = 1000):
        """
        Start real-time workload generation in a separate thread.
        
        Args:
            rate: Generation rate (accesses per second)
        """
        if self.is_generating:
            return
        
        self.generation_rate = rate
        self.is_generating = True
        self.generation_thread = threading.Thread(target=self._generate_real_time, daemon=True)
        self.generation_thread.start()
        print(f"Started real-time generation at {rate} accesses/second")
    
    def stop_real_time_generation(self):
        """Stop real-time workload generation."""
        self.is_generating = False
        if self.generation_thread:
            self.generation_thread.join()
        print("Stopped real-time generation")
    
    def get_next_access(self) -> Optional[Tuple[int, bool]]:
        """
        Get the next memory access from the real-time queue.
        
        Returns:
            Tuple of (address, is_write) or None if queue is empty
        """
        if self.access_queue:
            return self.access_queue.popleft()
        return None
    
    def _generate_real_time(self):
        """Real-time generation loop running in separate thread."""
        while self.is_generating:
            start_time = time.time()
            
            # Generate a batch of accesses
            batch_size = max(1, self.generation_rate // 100)  # Generate in small batches
            for _ in range(batch_size):
                if not self.is_generating:
                    break
                
                address, is_write = self._generate_single_access()
                self.access_queue.append((address, is_write))
            
            # Control generation rate
            elapsed = time.time() - start_time
            sleep_time = max(0, batch_size / self.generation_rate - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def _generate_single_access(self) -> Tuple[int, bool]:
        """
        Generate a single memory access based on current workload parameters.
        
        Returns:
            Tuple of (address, is_write)
        """
        # Update phase if needed
        self.phase_counter += 1
        if self.phase_counter >= self.workload_params['phase_duration']:
            self._switch_phase()
            self.phase_counter = 0
        
        # Generate address based on current phase and locality
        address = self._generate_address()
        is_write = random.random() < self.workload_params['write_probability']
        
        # Update state
        self.recent_accesses.append(address)
        self.last_address = address
        
        return address, is_write
    
    def _generate_address(self) -> int:
        """Generate a memory address based on locality patterns."""
        # Check for burst access
        if random.random() < self.workload_params['burst_probability']:
            return self._generate_burst_access()
        
        # Temporal locality - access recently used pages
        if (self.recent_accesses and 
            random.random() < self.workload_params['temporal_locality']):
            return random.choice(list(self.recent_accesses))
        
        # Spatial locality - access nearby pages
        if (self.last_address > 0 and 
            random.random() < self.workload_params['spatial_locality']):
            offset = random.randint(-2, 2) * self.page_size
            address = self.last_address + offset
            if 0 <= address < self.virtual_memory_size:
                return address
        
        # Phase-specific generation
        if self.current_phase == 'sequential':
            return self._generate_sequential()
        elif self.current_phase == 'working_set':
            return self._generate_working_set()
        elif self.current_phase == 'scan':
            return self._generate_scan()
        else:  # random
            return random.randint(0, self.virtual_memory_size - 1)
    
    def _generate_burst_access(self) -> int:
        """Generate burst access pattern."""
        base_address = random.randint(0, self.virtual_memory_size - 
                                     self.workload_params['burst_size'] * self.page_size)
        offset = random.randint(0, self.workload_params['burst_size'] - 1) * self.page_size
        return base_address + offset
    
    def _generate_sequential(self) -> int:
        """Generate sequential access pattern."""
        if self.last_address + self.page_size < self.virtual_memory_size:
            return self.last_address + self.page_size
        else:
            return random.randint(0, self.virtual_memory_size - 1)
    
    def _generate_working_set(self) -> int:
        """Generate access within working set."""
        if not self.working_set:
            # Initialize working set
            self.working_set = set(random.randint(0, self.num_pages - 1) 
                                 for _ in range(self.workload_params['working_set_size']))
        
        page = random.choice(list(self.working_set))
        return page * self.page_size + random.randint(0, self.page_size - 1)
    
    def _generate_scan(self) -> int:
        """Generate scanning access pattern."""
        page = (self.phase_counter // 10) % self.num_pages
        return page * self.page_size + random.randint(0, self.page_size - 1)
    
    def _switch_phase(self):
        """Switch to next workload phase."""
        phases = ['random', 'sequential', 'working_set', 'scan']
        current_idx = phases.index(self.current_phase)
        self.current_phase = phases[(current_idx + 1) % len(phases)]
        
        # Reset working set for new phase
        if self.current_phase == 'working_set':
            self.working_set.clear()
        
        print(f"Switched to phase: {self.current_phase}")
    
    def generate_benchmark_suite(self) -> Dict[str, List[Tuple[int, bool]]]:
        """
        Generate a comprehensive benchmark suite with various patterns.
        
        Returns:
            Dictionary mapping pattern names to access sequences
        """
        benchmarks = {}
        
        # Database-like workload
        benchmarks['database'] = self._generate_database_workload(5000)
        
        # Web server workload
        benchmarks['webserver'] = self._generate_webserver_workload(5000)
        
        # Scientific computation
        benchmarks['scientific'] = self._generate_scientific_workload(5000)
        
        # Gaming workload
        benchmarks['gaming'] = self._generate_gaming_workload(5000)
        
        # Operating system workload
        benchmarks['os'] = self._generate_os_workload(5000)
        
        return benchmarks
    
    def _generate_database_workload(self, size: int) -> List[Tuple[int, bool]]:
        """Generate database-like access pattern."""
        accesses = []
        # High locality, many writes, working set pattern
        working_set = set(random.randint(0, self.num_pages - 1) for _ in range(64))
        
        for _ in range(size):
            if random.random() < 0.8:  # High temporal locality
                page = random.choice(list(working_set))
            else:
                page = random.randint(0, self.num_pages - 1)
            
            address = page * self.page_size + random.randint(0, self.page_size - 1)
            is_write = random.random() < 0.4  # 40% writes
            accesses.append((address, is_write))
        
        return accesses
    
    def _generate_webserver_workload(self, size: int) -> List[Tuple[int, bool]]:
        """Generate web server-like access pattern."""
        accesses = []
        # Mix of hot content and random requests
        hot_pages = set(random.randint(0, min(100, self.num_pages - 1)) for _ in range(20))
        
        for _ in range(size):
            if random.random() < 0.6:  # 60% hot content
                page = random.choice(list(hot_pages))
            else:
                page = random.randint(0, self.num_pages - 1)
            
            address = page * self.page_size + random.randint(0, self.page_size - 1)
            is_write = random.random() < 0.1  # 10% writes (mostly reads)
            accesses.append((address, is_write))
        
        return accesses
    
    def _generate_scientific_workload(self, size: int) -> List[Tuple[int, bool]]:
        """Generate scientific computation access pattern."""
        accesses = []
        # Sequential with some random accesses
        
        for i in range(size):
            if random.random() < 0.7:  # 70% sequential
                page = (i // 10) % self.num_pages
            else:
                page = random.randint(0, self.num_pages - 1)
            
            address = page * self.page_size + random.randint(0, self.page_size - 1)
            is_write = random.random() < 0.2  # 20% writes
            accesses.append((address, is_write))
        
        return accesses
    
    def _generate_gaming_workload(self, size: int) -> List[Tuple[int, bool]]:
        """Generate gaming-like access pattern."""
        accesses = []
        # High spatial locality with bursts
        
        current_region = 0
        region_size = self.num_pages // 10
        
        for i in range(size):
            if i % 500 == 0:  # Switch regions periodically
                current_region = (current_region + 1) % 10
            
            if random.random() < 0.8:  # High spatial locality
                page = current_region * region_size + random.randint(0, region_size - 1)
                page = min(page, self.num_pages - 1)
            else:
                page = random.randint(0, self.num_pages - 1)
            
            address = page * self.page_size + random.randint(0, self.page_size - 1)
            is_write = random.random() < 0.3  # 30% writes
            accesses.append((address, is_write))
        
        return accesses
    
    def _generate_os_workload(self, size: int) -> List[Tuple[int, bool]]:
        """Generate OS-like access pattern."""
        accesses = []
        # Mixed pattern with system areas
        system_pages = set(range(0, min(32, self.num_pages)))  # System area
        
        for _ in range(size):
            if random.random() < 0.3:  # 30% system accesses
                page = random.choice(list(system_pages))
            else:
                # Fix for small memory sizes
                if self.num_pages > 32:
                    page = random.randint(32, self.num_pages - 1)
                else:
                    page = random.randint(0, self.num_pages - 1)
            
            address = page * self.page_size + random.randint(0, self.page_size - 1)
            is_write = random.random() < 0.25  # 25% writes
            accesses.append((address, is_write))
        
        return accesses
    
    def get_generation_stats(self) -> Dict:
        """Get statistics about the current generation state."""
        return {
            'is_generating': self.is_generating,
            'generation_rate': self.generation_rate,
            'queue_size': len(self.access_queue),
            'current_phase': self.current_phase,
            'phase_counter': self.phase_counter,
            'working_set_size': len(self.working_set),
            'recent_accesses': len(self.recent_accesses),
            'workload_params': self.workload_params.copy()
        } 