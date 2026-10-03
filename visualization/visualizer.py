import matplotlib.pyplot as plt
import numpy as np

class MemoryVisualizer:
    """
    Visualizes memory management system performance.
    """
    def __init__(self):
        """Initialize the visualizer."""
        pass
    
    def plot_hit_ratios(self, metrics_dict, filename='hit_ratio.png'):
        """
        Plot hit ratios for different algorithms.
        
        Args:
            metrics_dict: Dictionary mapping algorithm names to metrics
            filename: Output file name
        """
        algorithms = list(metrics_dict.keys())
        hit_ratios = [metrics_dict[alg]['hit_ratio'] for alg in algorithms]
        
        plt.figure(figsize=(10, 6))
        plt.bar(algorithms, hit_ratios, color=['blue', 'green', 'red'])
        plt.ylabel('Hit Ratio')
        plt.title('Memory Access Hit Ratio by Algorithm')
        plt.ylim(0, 1)
        
        # Add values on top of bars
        for i, v in enumerate(hit_ratios):
            plt.text(i, v + 0.02, f'{v:.4f}', ha='center')
        
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
    
    def plot_page_faults(self, metrics_dict, filename='page_faults.png'):
        """
        Plot page faults for different algorithms.
        
        Args:
            metrics_dict: Dictionary mapping algorithm names to metrics
            filename: Output file name
        """
        algorithms = list(metrics_dict.keys())
        page_faults = [metrics_dict[alg]['page_faults'] for alg in algorithms]
        
        plt.figure(figsize=(10, 6))
        plt.bar(algorithms, page_faults, color=['blue', 'green', 'red'])
        plt.ylabel('Page Faults')
        plt.title('Page Faults by Algorithm')
        
        # Add values on top of bars
        for i, v in enumerate(page_faults):
            plt.text(i, v + 10, str(v), ha='center')
        
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
    
    def plot_memory_state(self, memory_manager, filename='memory_state.png'):
        """
        Visualize the current state of memory.
        
        Args:
            memory_manager: Memory manager instance
            filename: Output file name
        """
        page_table = memory_manager.page_table
        num_frames = memory_manager.num_frames
        
        # Create array showing which pages are in which frames
        frame_contents = np.array([page_table.get_page_number(i) for i in range(num_frames)])
        
        plt.figure(figsize=(12, 6))
        
        # Plot physical memory frames
        plt.subplot(1, 2, 1)
        plt.bar(range(num_frames), [1] * num_frames, color='lightgray', edgecolor='black')
        plt.xticks(range(num_frames))
        plt.xlabel('Frame Number')
        plt.title('Physical Memory Frames')
        
        # Add page numbers to frames
        for i in range(num_frames):
            page = frame_contents[i]
            if page is not None:
                plt.text(i, 0.5, f'P{page}', ha='center', va='center')
            else:
                plt.text(i, 0.5, 'Empty', ha='center', va='center')
        
        # Plot page table
        plt.subplot(1, 2, 2)
        pages_in_memory = [i for i in range(page_table.num_pages) if page_table.is_page_in_memory(i)]
        plt.bar(pages_in_memory, [1] * len(pages_in_memory), color='lightblue', edgecolor='black')
        plt.xlabel('Page Number')
        plt.title('Pages in Memory')
        
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
    
    def plot_access_pattern(self, access_pattern, page_size, filename='access_pattern.png'):
        """
        Visualize a memory access pattern.
        
        Args:
            access_pattern: List of memory addresses
            page_size: Size of a page in bytes
            filename: Output file name
        """
        # Convert addresses to page numbers
        page_accesses = [addr // page_size for addr in access_pattern]
        
        plt.figure(figsize=(12, 6))
        
        # Plot address accesses over time
        plt.subplot(2, 1, 1)
        plt.plot(access_pattern, marker='.', linestyle='-', markersize=3)
        plt.xlabel('Access Number')
        plt.ylabel('Virtual Address')
        plt.title('Memory Access Pattern')
        
        # Plot page accesses over time
        plt.subplot(2, 1, 2)
        plt.plot(page_accesses, marker='.', linestyle='-', markersize=3)
        plt.xlabel('Access Number')
        plt.ylabel('Page Number')
        plt.title('Page Access Pattern')
        
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()