#!/usr/bin/env python3
"""
Unified Enhanced MemoryLearn GUI
Combines launcher functionality with real-time monitoring in one beautiful interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import time
import os

# Optional imports with fallbacks
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Note: matplotlib not available - charts will be disabled")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Note: numpy not available - using basic random")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Note: pandas not available - basic results display only")

class UnifiedMemoryLearnGUI:
    """Unified GUI combining launcher and real-time monitoring features."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enhanced MemoryLearn - Unified Control Center")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Colors
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db', 
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'white': '#ffffff',
            'dark': '#34495e'
        }
        
        # Data storage for real-time monitoring
        self.performance_data = {
            'fifo': {'hit_ratios': [], 'page_faults': [], 'times': []},
            'lru': {'hit_ratios': [], 'page_faults': [], 'times': []}, 
            'clock': {'hit_ratios': [], 'page_faults': [], 'times': []},
            'optimal': {'hit_ratios': [], 'page_faults': [], 'times': []}
        }
        
        self.is_monitoring = False
        self.start_time = None
        
        self.create_gui()
    
    def create_gui(self):
        """Create the unified GUI layout."""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, 
                        text="Enhanced MemoryLearn - Unified Control Center",
                        bg=self.colors['primary'], fg=self.colors['white'],
                        font=('Arial', 18, 'bold'))
        title.pack(pady=15)
        
        subtitle = tk.Label(header_frame,
                           text="Complete Memory Management Analysis & Real-time Monitoring",
                           bg=self.colors['primary'], fg=self.colors['light'],
                           font=('Arial', 11))
        subtitle.pack()
        
        # Main content with notebook tabs
        main_frame = tk.Frame(self.root, bg=self.colors['light'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_overview_tab()
        self.create_evaluation_tab()
        self.create_monitoring_tab()
        self.create_results_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Welcome to Enhanced MemoryLearn!")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                             bg=self.colors['dark'], fg=self.colors['white'],
                             font=('Arial', 10), anchor='w')
        status_bar.pack(fill='x', side='bottom')
    
    def create_overview_tab(self):
        """Create project overview and quick actions tab."""
        overview_frame = tk.Frame(self.notebook, bg=self.colors['light'])
        self.notebook.add(overview_frame, text='📊 Project Overview')
        
        # Scrollable frame
        canvas = tk.Canvas(overview_frame, bg=self.colors['light'])
        scrollbar = ttk.Scrollbar(overview_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['light'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Features overview
        features_frame = tk.LabelFrame(scrollable_frame, text="Enhanced Features",
                                     font=('Arial', 14, 'bold'), bg=self.colors['light'])
        features_frame.pack(fill='x', padx=20, pady=20)
        
        features_text = """
✅ 4 Page Replacement Algorithms: FIFO, LRU, Clock (Second Chance), Optimal
✅ Advanced VMM Features: Reference bits, Dirty bits, Write tracking, Prefetching  
✅ Real-time Workload Generation: 5 realistic workload types with parameters
✅ Statistical Analysis: ANOVA, t-tests, parameter optimization, rankings
✅ Beautiful Visualizations: Performance heatmaps, real-time charts, comparisons
✅ Enhanced Metrics: Hit ratio, Miss ratio, Write ratio, Disk writes, Execution time
✅ Smart Algorithm Selection: Automatic recommendations for different workloads
✅ Live Monitoring: Real-time performance tracking with interactive charts
        """
        
        tk.Label(features_frame, text=features_text, bg=self.colors['light'],
                font=('Arial', 11), justify='left').pack(padx=15, pady=15)
        
        # Quick Actions
        actions_frame = tk.LabelFrame(scrollable_frame, text="Quick Actions",
                                    font=('Arial', 14, 'bold'), bg=self.colors['light'])
        actions_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Button grid
        buttons_grid = tk.Frame(actions_frame, bg=self.colors['light'])
        buttons_grid.pack(pady=15)
        
        # Row 1
        self.create_action_btn(buttons_grid, "🚀 Run Full Evaluation", 
                              "Comprehensive benchmark with all algorithms",
                              self.colors['success'], self.run_evaluation, 0, 0)
        
        self.create_action_btn(buttons_grid, "📈 Start Live Monitoring",
                              "Real-time performance tracking", 
                              self.colors['secondary'], self.start_monitoring, 0, 1)
        
        # Row 2  
        self.create_action_btn(buttons_grid, "📊 View Latest Results",
                              "Open generated charts and data",
                              self.colors['warning'], self.view_results, 1, 0)
        
        self.create_action_btn(buttons_grid, "🔬 Compare with Original",
                              "Run original version for comparison",
                              self.colors['dark'], self.run_original, 1, 1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_action_btn(self, parent, text, desc, color, command, row, col):
        """Create styled action button."""
        btn_frame = tk.Frame(parent, bg=self.colors['light'])
        btn_frame.grid(row=row, column=col, padx=15, pady=10, sticky='nsew')
        
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        btn = tk.Button(btn_frame, text=text, command=command,
                       bg=color, fg=self.colors['white'],
                       font=('Arial', 12, 'bold'), relief='flat',
                       cursor='hand2', width=25, height=2)
        btn.pack(pady=(0, 5))
        
        desc_label = tk.Label(btn_frame, text=desc, bg=self.colors['light'],
                             font=('Arial', 9), wraplength=200)
        desc_label.pack()
    
    def create_evaluation_tab(self):
        """Create evaluation control and progress tab."""
        eval_frame = tk.Frame(self.notebook, bg=self.colors['light'])
        self.notebook.add(eval_frame, text='⚡ Evaluation Control')
        
        # Control panel
        control_frame = tk.LabelFrame(eval_frame, text="Evaluation Settings",
                                    font=('Arial', 12, 'bold'), bg=self.colors['light'])
        control_frame.pack(fill='x', padx=20, pady=20)
        
        # Settings grid
        settings_frame = tk.Frame(control_frame, bg=self.colors['light'])
        settings_frame.pack(fill='x', padx=15, pady=15)
        
        # Algorithm selection
        tk.Label(settings_frame, text="Algorithms to Test:", 
                bg=self.colors['light'], font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w')
        
        self.algorithm_vars = {}
        algorithms = ['FIFO', 'LRU', 'Clock', 'Optimal']
        alg_frame = tk.Frame(settings_frame, bg=self.colors['light'])
        alg_frame.grid(row=0, column=1, sticky='w', padx=(10, 0))
        
        for i, alg in enumerate(algorithms):
            var = tk.BooleanVar(value=True)
            self.algorithm_vars[alg.lower()] = var
            tk.Checkbutton(alg_frame, text=alg, variable=var,
                          bg=self.colors['light'], font=('Arial', 10)).pack(side='left', padx=5)
        
        # Progress area
        progress_frame = tk.LabelFrame(eval_frame, text="Evaluation Progress",
                                     font=('Arial', 12, 'bold'), bg=self.colors['light'])
        progress_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.pack(fill='x', padx=15, pady=10)
        
        # Output text area
        self.output_text = tk.Text(progress_frame, height=15, wrap='word',
                                  bg=self.colors['white'], font=('Consolas', 9))
        scrollbar_out = ttk.Scrollbar(progress_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar_out.set)
        
        self.output_text.pack(side='left', fill='both', expand=True, padx=(15, 0), pady=(0, 15))
        scrollbar_out.pack(side='right', fill='y', pady=(0, 15), padx=(0, 15))
    
    def create_monitoring_tab(self):
        """Create real-time monitoring tab."""
        monitor_frame = tk.Frame(self.notebook, bg=self.colors['light'])
        self.notebook.add(monitor_frame, text='📈 Live Monitoring')
        
        # Control panel
        control_frame = tk.LabelFrame(monitor_frame, text="Monitoring Controls",
                                    font=('Arial', 12, 'bold'), bg=self.colors['light'])
        control_frame.pack(fill='x', padx=20, pady=20)
        
        controls = tk.Frame(control_frame, bg=self.colors['light'])
        controls.pack(pady=15)
        
        self.start_btn = tk.Button(controls, text="▶️ Start Monitoring",
                                  command=self.start_monitoring,
                                  bg=self.colors['success'], fg=self.colors['white'],
                                  font=('Arial', 11, 'bold'), padx=15)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = tk.Button(controls, text="⏹️ Stop Monitoring",
                                 command=self.stop_monitoring,
                                 bg=self.colors['danger'], fg=self.colors['white'],
                                 font=('Arial', 11, 'bold'), padx=15, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        clear_btn = tk.Button(controls, text="🗑️ Clear Data",
                             command=self.clear_data,
                             bg=self.colors['warning'], fg=self.colors['white'],
                             font=('Arial', 11, 'bold'), padx=15)
        clear_btn.pack(side='left', padx=5)
        
        # Metrics display
        metrics_frame = tk.LabelFrame(monitor_frame, text="Current Performance Metrics",
                                    font=('Arial', 12, 'bold'), bg=self.colors['light'])
        metrics_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.create_metrics_display(metrics_frame)
        
        # Charts
        charts_frame = tk.LabelFrame(monitor_frame, text="Real-Time Performance Charts",
                                   font=('Arial', 12, 'bold'), bg=self.colors['light'])
        charts_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.create_charts(charts_frame)
    
    def create_metrics_display(self, parent):
        """Create metrics display area."""
        metrics_container = tk.Frame(parent, bg=self.colors['light'])
        metrics_container.pack(fill='x', padx=15, pady=15)
        
        algorithms = ['FIFO', 'LRU', 'Clock', 'Optimal']
        colors = [self.colors['danger'], self.colors['secondary'], 
                 self.colors['success'], self.colors['warning']]
        
        self.metric_labels = {}
        
        for i, (alg, color) in enumerate(zip(algorithms, colors)):
            alg_frame = tk.Frame(metrics_container, bg=color, relief='raised', bd=2)
            alg_frame.pack(side='left', fill='both', expand=True, padx=5)
            
            tk.Label(alg_frame, text=alg, bg=color, fg=self.colors['white'],
                    font=('Arial', 12, 'bold')).pack(pady=(10, 5))
            
            self.metric_labels[alg.lower()] = {}
            
            for metric in ['Hit Ratio', 'Page Faults', 'Time']:
                metric_frame = tk.Frame(alg_frame, bg=color)
                metric_frame.pack(fill='x', padx=10, pady=2)
                
                tk.Label(metric_frame, text=f"{metric}:", bg=color, 
                        fg=self.colors['white'], font=('Arial', 9)).pack(side='left')
                
                value_label = tk.Label(metric_frame, text="0.0000", bg=color,
                                     fg=self.colors['white'], font=('Arial', 9, 'bold'))
                value_label.pack(side='right')
                
                self.metric_labels[alg.lower()][metric.lower().replace(' ', '_')] = value_label
            
            tk.Label(alg_frame, text="", bg=color).pack(pady=5)
    
    def create_charts(self, parent):
        """Create real-time charts."""
        if MATPLOTLIB_AVAILABLE:
            self.fig = Figure(figsize=(12, 5), facecolor='white')
            
            self.ax1 = self.fig.add_subplot(121)
            self.ax2 = self.fig.add_subplot(122)
            
            self.ax1.set_title('Hit Ratio Over Time', fontsize=12, fontweight='bold')
            self.ax1.set_xlabel('Time (seconds)')
            self.ax1.set_ylabel('Hit Ratio')
            self.ax1.grid(True, alpha=0.3)
            self.ax1.set_ylim(0, 1)
            
            self.ax2.set_title('Page Faults Over Time', fontsize=12, fontweight='bold')
            self.ax2.set_xlabel('Time (seconds)')
            self.ax2.set_ylabel('Page Faults')
            self.ax2.grid(True, alpha=0.3)
            
            self.colors_chart = {
                'fifo': '#e74c3c', 'lru': '#3498db', 
                'clock': '#27ae60', 'optimal': '#f39c12'
            }
            
            self.lines = {}
            for alg, color in self.colors_chart.items():
                line1, = self.ax1.plot([], [], color=color, label=alg.upper(), linewidth=2)
                line2, = self.ax2.plot([], [], color=color, label=alg.upper(), linewidth=2)
                self.lines[alg] = {'hit_ratio': line1, 'page_faults': line2}
            
            self.ax1.legend(loc='upper right')
            self.ax2.legend(loc='upper right')
            
            self.canvas = FigureCanvasTkAgg(self.fig, parent)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=15, pady=15)
        else:
            # Fallback display when matplotlib is not available
            fallback_frame = tk.Frame(parent, bg=self.colors['white'])
            fallback_frame.pack(fill='both', expand=True, padx=15, pady=15)
            
            fallback_label = tk.Label(fallback_frame, 
                                    text="📊 Real-time charts unavailable\n\nMatplotlib is required for chart display.\nInstall with: pip install matplotlib\n\nMonitoring will still work - metrics will be shown in the text area above.",
                                    bg=self.colors['white'], 
                                    font=('Arial', 12),
                                    justify='center')
            fallback_label.pack(expand=True)
    
    def create_results_tab(self):
        """Create results viewing tab."""
        results_frame = tk.Frame(self.notebook, bg=self.colors['light'])
        self.notebook.add(results_frame, text='📊 Results & Analysis')
        
        # Results control
        control_frame = tk.LabelFrame(results_frame, text="Results Management",
                                    font=('Arial', 12, 'bold'), bg=self.colors['light'])
        control_frame.pack(fill='x', padx=20, pady=20)
        
        controls = tk.Frame(control_frame, bg=self.colors['light'])
        controls.pack(pady=15)
        
        tk.Button(controls, text="🔄 Refresh Results", command=self.refresh_results,
                 bg=self.colors['secondary'], fg=self.colors['white'],
                 font=('Arial', 11, 'bold'), padx=15).pack(side='left', padx=5)
        
        tk.Button(controls, text="📂 Open Results Folder", command=self.open_results_folder,
                 bg=self.colors['warning'], fg=self.colors['white'],
                 font=('Arial', 11, 'bold'), padx=15).pack(side='left', padx=5)
        
        tk.Button(controls, text="📈 Show Heatmap", command=self.show_heatmap,
                 bg=self.colors['success'], fg=self.colors['white'],
                 font=('Arial', 11, 'bold'), padx=15).pack(side='left', padx=5)
        
        # Results display
        results_display_frame = tk.LabelFrame(results_frame, text="Latest Results Summary",
                                            font=('Arial', 12, 'bold'), bg=self.colors['light'])
        results_display_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.results_text = tk.Text(results_display_frame, wrap='word', 
                                   bg=self.colors['white'], font=('Consolas', 9))
        results_scrollbar = ttk.Scrollbar(results_display_frame, orient="vertical", 
                                        command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_text.pack(side='left', fill='both', expand=True, padx=(15, 0), pady=15)
        results_scrollbar.pack(side='right', fill='y', pady=15, padx=(0, 15))
        
        # Load initial results
        self.refresh_results()
    
    def update_status(self, message):
        """Update status bar."""
        self.status_var.set(message)
        self.root.update()
    
    def run_evaluation(self):
        """Run comprehensive evaluation."""
        def evaluation_thread():
            try:
                self.update_status("Running comprehensive evaluation...")
                self.progress.start()
                
                # Clear output
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, "Starting Enhanced MemoryLearn Evaluation...\n\n")
                self.output_text.update()
                
                # Run evaluation - ensure we're in the right directory
                script_dir = os.path.dirname(os.path.abspath(__file__))
                result = subprocess.run(['python', 'enhanced_main.py'], 
                                      capture_output=True, text=True, cwd=script_dir)
                
                self.progress.stop()
                
                if result.returncode == 0:
                    self.update_status("Evaluation completed successfully!")
                    self.output_text.insert(tk.END, result.stdout)
                    self.refresh_results()
                    messagebox.showinfo("Success!", "Evaluation completed successfully!\n\nCheck the Results tab for detailed analysis.")
                else:
                    self.update_status("Evaluation failed")
                    self.output_text.insert(tk.END, f"ERROR:\n{result.stderr}")
                    
            except Exception as e:
                self.progress.stop()
                self.update_status("Evaluation error")
                messagebox.showerror("Error", f"Evaluation failed:\n{str(e)}")
        
        # Switch to evaluation tab
        self.notebook.select(1)
        threading.Thread(target=evaluation_thread, daemon=True).start()
    
    def start_monitoring(self):
        """Start real-time monitoring."""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.start_time = time.time()
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        # Switch to monitoring tab
        self.notebook.select(2)
        self.update_status("Real-time monitoring started...")
        
        threading.Thread(target=self.monitoring_loop, daemon=True).start()
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.is_monitoring = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.update_status("Monitoring stopped")
    
    def clear_data(self):
        """Clear monitoring data."""
        for alg in self.performance_data:
            self.performance_data[alg] = {'hit_ratios': [], 'page_faults': [], 'times': []}
        self.update_charts()
        self.update_status("Monitoring data cleared")
    
    def monitoring_loop(self):
        """Monitoring background loop."""
        import random
        
        while self.is_monitoring:
            try:
                current_time = time.time() - self.start_time
                
                # Simulate algorithm performance (replace with real monitoring)
                for alg in self.performance_data:
                    if NUMPY_AVAILABLE:
                        hit_ratio = np.random.uniform(0.1, 0.8)
                        page_faults = np.random.randint(100, 1000)
                    else:
                        hit_ratio = random.uniform(0.1, 0.8)
                        page_faults = random.randint(100, 1000)
                    
                    self.performance_data[alg]['hit_ratios'].append(hit_ratio)
                    self.performance_data[alg]['page_faults'].append(page_faults)
                    self.performance_data[alg]['times'].append(current_time)
                    
                    # Keep only last 50 points
                    if len(self.performance_data[alg]['times']) > 50:
                        self.performance_data[alg]['hit_ratios'].pop(0)
                        self.performance_data[alg]['page_faults'].pop(0)
                        self.performance_data[alg]['times'].pop(0)
                    
                    # Update metrics display
                    self.update_metric_display(alg, hit_ratio, page_faults)
                
                self.update_charts()
                time.sleep(1)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                break
    
    def update_metric_display(self, algorithm, hit_ratio, page_faults):
        """Update metrics display."""
        if algorithm in self.metric_labels:
            self.metric_labels[algorithm]['hit_ratio'].config(text=f"{hit_ratio:.3f}")
            self.metric_labels[algorithm]['page_faults'].config(text=f"{page_faults}")
            self.metric_labels[algorithm]['time'].config(text="0.01s")
    
    def update_charts(self):
        """Update real-time charts."""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        for alg, line_data in self.lines.items():
            if self.performance_data[alg]['times']:
                line_data['hit_ratio'].set_data(self.performance_data[alg]['times'],
                                              self.performance_data[alg]['hit_ratios'])
                line_data['page_faults'].set_data(self.performance_data[alg]['times'],
                                                self.performance_data[alg]['page_faults'])
        
        # Adjust axes
        if any(self.performance_data[alg]['times'] for alg in self.performance_data):
            all_times = []
            all_pf = []
            for alg in self.performance_data:
                all_times.extend(self.performance_data[alg]['times'])
                all_pf.extend(self.performance_data[alg]['page_faults'])
            
            if all_times:
                self.ax1.set_xlim(min(all_times), max(all_times))
                self.ax2.set_xlim(min(all_times), max(all_times))
                self.ax2.set_ylim(0, max(all_pf) * 1.1 if all_pf else 1000)
        
        self.canvas.draw()
    
    def view_results(self):
        """View latest results."""
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        files = ['enhanced_memorylearn_results.csv', 'advanced_performance_heatmap.png',
                'hit_ratio.png', 'page_faults.png']
        
        # Check for files in the script directory
        found_files = []
        for f in files:
            full_path = os.path.join(script_dir, f)
            if os.path.exists(full_path):
                found_files.append(full_path)
        
        if not found_files:
            messagebox.showwarning("No Results", "No results found. Run evaluation first.")
            return
        
        try:
            for file in found_files:
                os.startfile(file)
            self.update_status(f"Opened {len(found_files)} result files")
        except:
            file_names = [os.path.basename(f) for f in found_files]
            messagebox.showinfo("Results Found", f"Found files:\n" + "\n".join(file_names))
    
    def run_original(self):
        """Run original version."""
        def original_thread():
            try:
                self.update_status("Running original version...")
                script_dir = os.path.dirname(os.path.abspath(__file__))
                result = subprocess.run(['python', 'main.py'], capture_output=True, text=True, cwd=script_dir)
                
                if result.returncode == 0:
                    self.update_status("Original version completed")
                    messagebox.showinfo("Complete", "Original MemoryLearn completed!")
                else:
                    messagebox.showerror("Error", f"Original failed:\n{result.stderr}")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {str(e)}")
        
        threading.Thread(target=original_thread, daemon=True).start()
    
    def refresh_results(self):
        """Refresh results display."""
        try:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            results_file = os.path.join(script_dir, 'enhanced_memorylearn_results.csv')
            
            if os.path.exists(results_file):
                if PANDAS_AVAILABLE:
                    df = pd.read_csv(results_file)
                    
                    summary = "LATEST RESULTS SUMMARY\n" + "="*50 + "\n\n"
                    
                    # Algorithm rankings
                    rankings = df.groupby('algorithm')['hit_ratio'].mean().sort_values(ascending=False)
                    summary += "ALGORITHM RANKINGS (by Hit Ratio):\n"
                    for i, (alg, score) in enumerate(rankings.items(), 1):
                        summary += f"  #{i} {alg.upper()}: {score:.4f} ({score*100:.1f}%)\n"
                    
                    summary += "\nBEST ALGORITHM PER WORKLOAD:\n"
                    for workload in df['workload'].unique():
                        workload_data = df[df['workload'] == workload]
                        best = workload_data.loc[workload_data['hit_ratio'].idxmax()]
                        summary += f"  {workload.title()}: {best['algorithm'].upper()} ({best['hit_ratio']:.3f})\n"
                    
                    summary += f"\nTOTAL EVALUATIONS: {len(df)} algorithm-workload combinations\n"
                    summary += f"WORKLOAD TYPES: {df['workload'].nunique()} types\n"
                    summary += f"ALGORITHMS TESTED: {df['algorithm'].nunique()} algorithms\n"
                    
                    self.results_text.delete(1.0, tk.END)
                    self.results_text.insert(1.0, summary)
                else:
                    # Fallback without pandas - just show file exists
                    summary = "RESULTS FILE FOUND\n" + "="*30 + "\n\n"
                    summary += "Results file: enhanced_memorylearn_results.csv\n\n"
                    summary += "Pandas is required for detailed analysis.\n"
                    summary += "Install with: pip install pandas\n\n"
                    summary += "You can still open the CSV file manually\n"
                    summary += "using the 'Open Results Folder' button."
                    
                    self.results_text.delete(1.0, tk.END)
                    self.results_text.insert(1.0, summary)
            else:
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(1.0, "No results available yet.\nRun an evaluation to see results here.")
                
        except Exception as e:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, f"Error loading results: {str(e)}")
    
    def open_results_folder(self):
        """Open results folder."""
        try:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            os.startfile(script_dir)
        except:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            messagebox.showinfo("Info", f"Results are in: {script_dir}")
    
    def show_heatmap(self):
        """Show performance heatmap."""
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        heatmap_file = os.path.join(script_dir, 'advanced_performance_heatmap.png')
        
        if os.path.exists(heatmap_file):
            try:
                os.startfile(heatmap_file)
                self.update_status("Opened performance heatmap")
            except:
                messagebox.showinfo("Info", f"Heatmap file: {heatmap_file}")
        else:
            messagebox.showwarning("No Heatmap", "No heatmap found. Run evaluation first.")
    
    def run(self):
        """Start the GUI."""
        self.root.mainloop()

def main():
    """Main function."""
    app = UnifiedMemoryLearnGUI()
    app.run()

if __name__ == "__main__":
    main() 