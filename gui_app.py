"""
Crypto Sector Rotation Analyzer - GUI Application

A graphical interface for analyzing cryptocurrency sector rotation patterns.
"""
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
from pathlib import Path
import queue
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import DataLoader
from sector_aggregator import SectorAggregator
from rotation_analyzer import RotationAnalyzer
from visualizer import SectorVisualizer


class SectorRotationGUI:
    """Main GUI application for Crypto Sector Rotation Analyzer"""
    
    def __init__(self, root):
        """Initialize the GUI"""
        self.root = root
        self.root.title("Crypto Sector Rotation Analyzer")
        self.root.geometry("900x800")
        

        # Variables
        self.csv_directory    = tk.StringVar(value="/users/uzer/Documents/Coding/Python/Projects Ongoing/Crypto/crypto_sector_rotation_complete/binance_1d_csv")
        self.sector_file      = tk.StringVar(value="/users/uzer/Documents/Coding/Python/Projects Ongoing/Crypto/crypto_sector_rotation_complete/SYMBOLS_SECTORS_MERGED_Final.csv")
        self.output_directory = tk.StringVar(value="/users/uzer/Documents/Coding/Python/Projects Ongoing/Crypto/crypto_sector_rotation_complete/results")
        self.timeframe = tk.StringVar(value="1d")
        self.lookback_days = tk.IntVar(value=90)
        
        # Checkboxes for hierarchy levels
        self.analyze_category = tk.BooleanVar(value=False)
        self.analyze_subcategory = tk.BooleanVar(value=True)
        self.analyze_segment = tk.BooleanVar(value=False)
        
        # Checkboxes for visualizations
        self.gen_heatmap = tk.BooleanVar(value=True)
        self.gen_cumulative = tk.BooleanVar(value=True)
        self.gen_network = tk.BooleanVar(value=True)
        self.gen_leadlag = tk.BooleanVar(value=True)
        self.gen_race = tk.BooleanVar(value=False)  # Slow, off by default
        
        # Auto-scan variables
        self.auto_scan_enabled = tk.BooleanVar(value=True)
        self.new_symbols_found = []
        
        # Analysis state
        self.analysis_running = False
        self.log_queue = queue.Queue()
        
        # Build UI
        self.create_widgets()
        
        # Start log processor
        self.process_log_queue()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Crypto Sector Rotation Analyzer",
            font=('Helvetica', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=10)
        
        # Create sections
        row = 1
        row = self.create_file_section(main_frame, row)
        row = self.create_analysis_section(main_frame, row)
        row = self.create_visualization_section(main_frame, row)
        row = self.create_control_section(main_frame, row)
        row = self.create_log_section(main_frame, row)
    
    def create_file_section(self, parent, start_row):
        """Create file selection section"""
        frame = ttk.LabelFrame(parent, text="Data Sources", padding="10")
        frame.grid(row=start_row, column=0, sticky=(tk.W, tk.E), pady=5)
        frame.columnconfigure(1, weight=1)
        
        # CSV Directory
        ttk.Label(frame, text="CSV Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.csv_directory, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5
        )
        ttk.Button(frame, text="Browse...", command=self.browse_csv_directory).grid(
            row=0, column=2, padx=5
        )
        
        # Sector Classification File
        ttk.Label(frame, text="Sector File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.sector_file, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5
        )
        ttk.Button(frame, text="Browse...", command=self.browse_sector_file).grid(
            row=1, column=2, padx=5
        )
        
        # Output Directory
        ttk.Label(frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.output_directory, width=50).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=5
        )
        ttk.Button(frame, text="Browse...", command=self.browse_output_directory).grid(
            row=2, column=2, padx=5
        )
        
        # Auto-scan controls
        auto_frame = ttk.Frame(frame)
        auto_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Checkbutton(
            auto_frame, 
            text="Auto-scan for new CSV files",
            variable=self.auto_scan_enabled
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            auto_frame, 
            text="Scan Now",
            command=self.scan_for_new_files
        ).pack(side=tk.LEFT, padx=5)
        
        return start_row + 1
    
    def create_analysis_section(self, parent, start_row):
        """Create analysis parameters section"""
        frame = ttk.LabelFrame(parent, text="Analysis Parameters", padding="10")
        frame.grid(row=start_row, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Timeframe
        ttk.Label(frame, text="Timeframe:").grid(row=0, column=0, sticky=tk.W, pady=5)
        timeframe_combo = ttk.Combobox(
            frame, 
            textvariable=self.timeframe,
            values=["1d", "4h"],
            state="readonly",
            width=15
        )
        timeframe_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Lookback Days
        ttk.Label(frame, text="Lookback Days:").grid(row=0, column=2, sticky=tk.W, padx=20)
        lookback_spinbox = ttk.Spinbox(
            frame,
            from_=7,
            to=365,
            textvariable=self.lookback_days,
            width=10
        )
        lookback_spinbox.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # Hierarchy Levels
        ttk.Label(frame, text="Analyze Levels:").grid(row=1, column=0, sticky=tk.W, pady=10)
        
        levels_frame = ttk.Frame(frame)
        levels_frame.grid(row=1, column=1, columnspan=3, sticky=tk.W, padx=5)
        
        ttk.Checkbutton(
            levels_frame,
            text="Category",
            variable=self.analyze_category
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Checkbutton(
            levels_frame,
            text="Sub-Category",
            variable=self.analyze_subcategory
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Checkbutton(
            levels_frame,
            text="Segment",
            variable=self.analyze_segment
        ).pack(side=tk.LEFT, padx=10)
        
        return start_row + 1
    
    def create_visualization_section(self, parent, start_row):
        """Create visualization options section"""
        frame = ttk.LabelFrame(parent, text="Visualizations to Generate", padding="10")
        frame.grid(row=start_row, column=0, sticky=(tk.W, tk.E), pady=5)
        
        viz_frame = ttk.Frame(frame)
        viz_frame.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Checkbutton(
            viz_frame,
            text="Sector Heatmap",
            variable=self.gen_heatmap
        ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=2)
        
        ttk.Checkbutton(
            viz_frame,
            text="Cumulative Performance",
            variable=self.gen_cumulative
        ).grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)
        
        ttk.Checkbutton(
            viz_frame,
            text="Rotation Network",
            variable=self.gen_network
        ).grid(row=1, column=0, sticky=tk.W, padx=10, pady=2)
        
        ttk.Checkbutton(
            viz_frame,
            text="Lead-Lag Matrix",
            variable=self.gen_leadlag
        ).grid(row=1, column=1, sticky=tk.W, padx=10, pady=2)
        
        ttk.Checkbutton(
            viz_frame,
            text="Ranking Race (slow)",
            variable=self.gen_race
        ).grid(row=2, column=0, sticky=tk.W, padx=10, pady=2)
        
        return start_row + 1
    
    def create_control_section(self, parent, start_row):
        """Create control buttons section"""
        frame = ttk.Frame(parent, padding="10")
        frame.grid(row=start_row, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.run_button = ttk.Button(
            frame,
            text="Run Analysis",
            command=self.run_analysis,
            style="Accent.TButton"
        )
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            frame,
            text="Stop",
            command=self.stop_analysis,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            frame,
            text="Open Output Folder",
            command=self.open_output_folder
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            frame,
            text="Clear Log",
            command=self.clear_log
        ).pack(side=tk.RIGHT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            frame,
            mode='indeterminate',
            length=200
        )
        self.progress.pack(side=tk.RIGHT, padx=20)
        
        return start_row + 1
    
    def create_log_section(self, parent, start_row):
        """Create log output section"""
        frame = ttk.LabelFrame(parent, text="Analysis Log", padding="10")
        frame.grid(row=start_row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure expansion
        parent.rowconfigure(start_row, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            width=80,
            height=15,
            font=('Courier', 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        return start_row + 1
    
    # File Browser Methods
    
    def browse_csv_directory(self):
        """Open directory browser for CSV files"""
        directory = filedialog.askdirectory(
            title="Select CSV Directory",
            initialdir=Path.home() / "/Documents/Coding/Python/_Projects Ongoing/Crypto/crypto_sector_rotation_complete/"
        )
        if directory:
            self.csv_directory.set(directory)
            self.log(f"CSV directory set: {directory}")
            
            # Auto-scan if enabled
            if self.auto_scan_enabled.get():
                self.scan_for_new_files()
    
    def browse_sector_file(self):
        """Open file browser for sector classification file"""
        filename = filedialog.askopenfilename(
            title="Select Sector Classification File",
            initialdir=str(Path.home()) + "/Documents/Coding/Python/_Projects Ongoing/Crypto/crypto_sector_rotation_complete/",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.sector_file.set(filename)
            self.log(f"Sector file set: {filename}")
    
    def browse_output_directory(self):
        """Open directory browser for output location"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=Path.home() / "/Documents/Coding/Python/_Projects Ongoing/Crypto/crypto_sector_rotation_complete/"
        )
        if directory:
            self.output_directory.set(directory)
            self.log(f"Output directory set: {directory}")
    
    # Auto-scan Functionality
    
    def scan_for_new_files(self):
        """Scan CSV directory for new files not in sector classification"""
        if not self.csv_directory.get():
            messagebox.showwarning("No Directory", "Please select a CSV directory first.")
            return
        
        if not self.sector_file.get():
            messagebox.showwarning("No Sector File", "Please select a sector classification file first.")
            return
        
        self.log("\n=== Scanning for new CSV files ===")
        
        try:
            # Get all CSV files in directory
            csv_dir = Path(self.csv_directory.get())
            csv_files = list(csv_dir.glob(f"*USDT_{self.timeframe.get()}.csv"))
            
            self.log(f"Found {len(csv_files)} CSV files matching pattern")
            
            # Load sector classifications
            sector_df = pd.read_csv(self.sector_file.get(), header=None)
            sector_df.columns = ['symbol', 'category', 'subcategory', 'segment']
            known_symbols = set(sector_df['symbol'].str.strip().tolist())
            
            # Extract symbols from filenames
            new_symbols = []
            for csv_file in csv_files:
                # Extract symbol (e.g., BTCUSDT_1d.csv -> BTC)
                filename = csv_file.stem  # Remove .csv
                if filename.endswith(f'USDT_{self.timeframe.get()}'):
                    symbol = filename.replace(f'USDT_{self.timeframe.get()}', '')
                    
                    if symbol not in known_symbols and symbol not in ['', 'USDT']:
                        new_symbols.append(symbol)
            
            self.new_symbols_found = sorted(new_symbols)
            
            if new_symbols:
                self.log(f"\n🔍 Found {len(new_symbols)} NEW symbols not in sector classification:")
                for symbol in new_symbols[:20]:  # Show first 20
                    self.log(f"  - {symbol}")
                if len(new_symbols) > 20:
                    self.log(f"  ... and {len(new_symbols) - 20} more")
                
                self.log("\nℹ️  These symbols will be SKIPPED in analysis until added to sector file.")
                self.log("   To include them, edit your sector classification CSV file.")
                
                # Offer to open sector file
                response = messagebox.askyesno(
                    "New Symbols Found",
                    f"Found {len(new_symbols)} new symbols not in sector classification.\n\n"
                    f"Would you like to open the sector file to add them?\n\n"
                    f"(You can also continue without them for now)"
                )
                
                if response:
                    self.open_sector_file_for_editing()
            else:
                self.log("✓ All CSV files are already classified in sector file")
                messagebox.showinfo(
                    "Scan Complete",
                    "All CSV files are already in the sector classification file."
                )
        
        except Exception as e:
            self.log(f"❌ Error during scan: {str(e)}")
            messagebox.showerror("Scan Error", f"Error scanning files:\n{str(e)}")
    
    def open_sector_file_for_editing(self):
        """Open sector file in default text editor"""
        try:
            import subprocess
            import platform
            
            sector_file_path = self.sector_file.get()
            
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', sector_file_path])
            elif platform.system() == 'Windows':
                os.startfile(sector_file_path)
            else:  # Linux
                subprocess.call(['xdg-open', sector_file_path])
            
            self.log(f"Opened sector file in default editor: {sector_file_path}")
            
        except Exception as e:
            self.log(f"Could not open file automatically: {str(e)}")
            messagebox.showinfo(
                "Manual Edit Required",
                f"Please open and edit this file manually:\n\n{self.sector_file.get()}\n\n"
                f"Add new symbols in format:\nSYMBOL,Category,SubCategory,Segment"
            )
    
    # Analysis Control
    
    def run_analysis(self):
        """Start the analysis in a background thread"""
        # Validation
        if not self.csv_directory.get():
            messagebox.showerror("Missing Input", "Please select a CSV directory.")
            return
        
        if not self.sector_file.get():
            messagebox.showerror("Missing Input", "Please select a sector classification file.")
            return
        
        if not any([self.analyze_category.get(), self.analyze_subcategory.get(), self.analyze_segment.get()]):
            messagebox.showerror("Missing Selection", "Please select at least one hierarchy level to analyze.")
            return
        
        # Update UI state
        self.analysis_running = True
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()
        
        self.log("\n" + "="*70)
        self.log("STARTING ANALYSIS")
        self.log("="*70 + "\n")
        
        # Run in background thread
        thread = threading.Thread(target=self.run_analysis_thread, daemon=True)
        thread.start()
    
    def run_analysis_thread(self):
        """Background thread for running analysis"""
        try:
            # Import here to redirect output
            from dashboard import SectorRotationDashboard
            
            # Get selected levels
            levels = []
            if self.analyze_category.get():
                levels.append('category')
            if self.analyze_subcategory.get():
                levels.append('subcategory')
            if self.analyze_segment.get():
                levels.append('segment')
            
            self.log(f"Analyzing levels: {', '.join(levels)}")
            self.log(f"Timeframe: {self.timeframe.get()}")
            self.log(f"Lookback: {self.lookback_days.get()} days\n")
            
            # Initialize dashboard
            self.log("Initializing dashboard...")
            dashboard = SectorRotationDashboard(
                csv_directory=self.csv_directory.get(),
                sector_classification_path=self.sector_file.get(),
                timeframe=self.timeframe.get()
            )
            
            # Run analysis for each level
            for level in levels:
                if not self.analysis_running:
                    self.log("\n⚠️  Analysis stopped by user")
                    break
                
                self.log(f"\n{'='*70}")
                self.log(f"ANALYZING: {level.upper()}")
                self.log(f"{'='*70}\n")
                
                # Performance analysis
                self.log("Calculating sector performance...")
                dashboard.analyze_sector_performance(level=level, top_n=5)
                
                # Rotation analysis
                self.log("\nAnalyzing rotation patterns...")
                dashboard.analyze_rotation_patterns(level=level)
                
                # Generate visualizations
                if any([self.gen_heatmap.get(), self.gen_cumulative.get(), 
                       self.gen_network.get(), self.gen_leadlag.get(), self.gen_race.get()]):
                    
                    self.log("\nGenerating visualizations...")
                    output_dir = Path(self.output_directory.get())
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    visualizer = dashboard.visualizer
                    
                    if self.gen_heatmap.get():
                        self.log("  - Creating heatmap...")
                        visualizer.plot_sector_heatmap(
                            level=level,
                            lookback_days=self.lookback_days.get(),
                            save_path=output_dir / f'heatmap_{level}_{self.timeframe.get()}.html'
                        )
                    
                    if self.gen_cumulative.get():
                        self.log("  - Creating cumulative performance chart...")
                        visualizer.plot_cumulative_performance(
                            level=level,
                            lookback_days=self.lookback_days.get(),
                            top_n=15,
                            save_path=output_dir / f'cumulative_{level}_{self.timeframe.get()}.html'
                        )
                    
                    if self.gen_network.get():
                        self.log("  - Creating rotation network...")
                        visualizer.plot_rotation_network(
                            level=level,
                            save_path=output_dir / f'network_{level}_{self.timeframe.get()}.html'
                        )
                    
                    if self.gen_leadlag.get():
                        self.log("  - Creating lead-lag matrix...")
                        visualizer.plot_lead_lag_matrix(
                            level=level,
                            save_path=output_dir / f'leadlag_{level}_{self.timeframe.get()}.png'
                        )
                    
                    if self.gen_race.get():
                        self.log("  - Creating ranking race (this may take a while)...")
                        visualizer.plot_sector_rankings_race(
                            level=level,
                            lookback_days=self.lookback_days.get(),
                            save_path=output_dir / f'race_{level}_{self.timeframe.get()}.html'
                        )
            
            self.log(f"\n{'='*70}")
            self.log("✅ ANALYSIS COMPLETE!")
            self.log(f"{'='*70}\n")
            self.log(f"Output saved to: {self.output_directory.get()}")
            
            # Show completion message
            self.root.after(0, lambda: messagebox.showinfo(
                "Analysis Complete",
                f"Analysis completed successfully!\n\n"
                f"Results saved to:\n{self.output_directory.get()}"
            ))
            
        except Exception as e:
            error_msg = f"Analysis error: {str(e)}"
            self.log(f"\n❌ {error_msg}")
            self.root.after(0, lambda: messagebox.showerror("Analysis Error", error_msg))
        
        finally:
            # Reset UI state
            self.root.after(0, self.analysis_complete)
    
    def stop_analysis(self):
        """Stop the running analysis"""
        self.analysis_running = False
        self.log("\n⚠️  Stopping analysis...")
    
    def analysis_complete(self):
        """Reset UI after analysis completes"""
        self.analysis_running = False
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
    
    # Utility Methods
    
    def open_output_folder(self):
        """Open the output folder in file explorer"""
        output_dir = self.output_directory.get()
        
        if not os.path.exists(output_dir):
            messagebox.showwarning("Folder Not Found", "Output folder doesn't exist yet. Run an analysis first.")
            return
        
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', output_dir])
            elif platform.system() == 'Windows':
                os.startfile(output_dir)
            else:  # Linux
                subprocess.call(['xdg-open', output_dir])
            
            self.log(f"Opened output folder: {output_dir}")
            
        except Exception as e:
            self.log(f"Could not open folder: {str(e)}")
    
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.delete(1.0, tk.END)
    
    def log(self, message):
        """Add message to log (thread-safe)"""
        self.log_queue.put(message + "\n")
    
    def process_log_queue(self):
        """Process log messages from queue"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message)
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_log_queue)


def main():
    """Main entry point for GUI application"""
    root = tk.Tk()
    
    # Set theme
    style = ttk.Style()
    style.theme_use('clam')  # Use a modern theme
    
    # Create application
    app = SectorRotationGUI(root)
    
    # Start GUI loop
    root.mainloop()


if __name__ == "__main__":
    main()
