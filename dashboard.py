"""
Main Dashboard for Crypto Sector Rotation Analysis

Interactive dashboard for analyzing sector rotation patterns across hierarchy levels.
"""

import argparse
from pathlib import Path
try:
    from .data_loader import DataLoader
    from .sector_aggregator import SectorAggregator
    from .rotation_analyzer import RotationAnalyzer
    from .visualizer import SectorVisualizer
except ImportError:
    from data_loader import DataLoader
    from sector_aggregator import SectorAggregator
    from rotation_analyzer import RotationAnalyzer
    from visualizer import SectorVisualizer


class SectorRotationDashboard:
    """Main dashboard controller"""
    
    def __init__(self,
                 csv_directory: str,
                 sector_classification_path: str,
                 timeframe: str = '1d'):
        """
        Initialize dashboard
        
        Args:
            csv_directory: Path to CSV files
            sector_classification_path: Path to sector classification CSV
            timeframe: '1d' or '4h'
        """
        print(f"\n{'='*60}")
        print("CRYPTO SECTOR ROTATION ANALYZER")
        print(f"{'='*60}")
        
        # Initialize components
        print(f"\nLoading data (timeframe: {timeframe})...")
        self.loader = DataLoader(csv_directory, sector_classification_path, timeframe)
        self.loader.load_all_coins()
        
        print("Building sector hierarchy...")
        self.loader.build_sector_hierarchy()
        
        print("Initializing analysis modules...")
        self.aggregator = SectorAggregator(self.loader)
        self.analyzer = RotationAnalyzer(self.aggregator)
        self.visualizer = SectorVisualizer(self.aggregator, self.analyzer)
        
        self.timeframe = timeframe
        
        print("\n✓ Dashboard initialized successfully!")
    
    def show_data_coverage(self):
        """Display data coverage statistics"""
        print(f"\n{'='*60}")
        print("DATA COVERAGE REPORT")
        print(f"{'='*60}")
        
        coverage = self.loader.get_coverage_report()
        print(coverage)
        
        # Print hierarchy summary
        hierarchy = self.loader.sector_hierarchy
        
        print(f"\n\nSECTOR HIERARCHY SUMMARY:")
        print(f"  Categories: {len(hierarchy)}")
        
        for cat, subcats in hierarchy.items():
            total_segments = sum(len(segs) for segs in subcats.values())
            total_coins = sum(
                len(coins) 
                for subcat in subcats.values() 
                for coins in subcat.values()
            )
            print(f"\n  {cat}:")
            print(f"    Sub-categories: {len(subcats)}")
            print(f"    Segments: {total_segments}")
            print(f"    Total coins: {total_coins}")
    
    def analyze_sector_performance(self, 
                                  level: str = 'subcategory',
                                  top_n: int = 10):
        """
        Analyze and display sector performance
        
        Args:
            level: 'category', 'subcategory', or 'segment'
            top_n: Number of top/bottom performers to show
        """
        print(f"\n{'='*60}")
        print(f"SECTOR PERFORMANCE ANALYSIS - {level.upper()}")
        print(f"{'='*60}")
        
        # Get rankings
        rankings = self.aggregator.get_sector_rankings(
            level=level,
            metric='avg_return',
            top_n=top_n
        )
        
        if rankings.empty:
            print("No performance data available")
            return
        
        # Display top performers
        top = rankings[rankings['rank_type'] == 'Top']
        print(f"\n🔥 TOP {top_n} PERFORMERS:")
        print("-" * 80)
        for idx, row in top.iterrows():
            print(f"  {str(row['sector']):40s} | Return: {row['avg_return']:6.2f}% | "
                  f"Breadth: {row['breadth_pct']:5.1f}% | Coins: {row['coin_count']:.0f}")
        
        # Display bottom performers
        bottom = rankings[rankings['rank_type'] == 'Bottom']
        print(f"\n❄️  BOTTOM {top_n} PERFORMERS:")
        print("-" * 80)
        for idx, row in bottom.iterrows():
            print(f"  {str(row['sector']):40s} | Return: {row['avg_return']:6.2f}% | "
                  f"Breadth: {row['breadth_pct']:5.1f}% | Coins: {row['coin_count']:.0f}")
    
    def analyze_rotation_patterns(self, level: str = 'subcategory'):
        """
        Analyze and display rotation patterns
        
        Args:
            level: Hierarchy level to analyze
        """
        print(f"\n{'='*60}")
        print(f"ROTATION PATTERN ANALYSIS - {level.upper()}")
        print(f"{'='*60}")
        
        # Rotation sequence
        print("\n📅 ROTATION SEQUENCE (by momentum peaks):")
        print("-" * 80)
        sequence = self.analyzer.detect_rotation_sequence(level=level, lookback_days=60)
        
        for i, (sector, date, momentum) in enumerate(sequence[:15], 1):
            print(f"  {i:2d}. {str(sector):40s} | Peak: {date.strftime('%Y-%m-%d')} | "
                  f"Momentum: {momentum:6.2f}%")
        
        # Capital flows
        print("\n💰 STRONGEST CAPITAL ROTATION FLOWS:")
        print("-" * 80)
        flows = self.analyzer.get_strongest_rotations(level=level, n_flows=10)
        
        if not flows.empty:
            for idx, row in flows.iterrows():
                print(f"  {str(row['from_sector']):25s} → {str(row['to_sector']):25s} | "
                      f"Flow: {row['total_flow']:7.1f} | "
                      f"Events: {row['occurrences']:.0f}")
        else:
            print("  No significant flows detected")
        
        # Lead-lag relationships
        print("\n🔮 LEAD-LAG RELATIONSHIPS (Top predictive correlations):")
        print("-" * 80)
        lead_lag = self.analyzer.calculate_lead_lag_correlation(
            level=level,
            max_lag_days=7
        )
        
        if not lead_lag.empty:
            # Show strongest leading relationships
            significant = lead_lag[
                (lead_lag['correlation'].abs() > 0.5) &
                (lead_lag['lag_days'] > 0)
            ].head(10)
            
            for idx, row in significant.iterrows():
                print(f"  {str(row['sector_lead']):25s} leads {str(row['sector_lag']):25s} by "
                      f"{row['lag_days']:.0f} days (r={row['correlation']:+.3f})")
        else:
            print("  No significant lead-lag relationships found")
    
    def generate_all_visualizations(self,
                                   level: str = 'subcategory',
                                   output_dir: str = './output',
                                   lookback_days: int = 90):
        """
        Generate all visualization outputs
        
        Args:
            level: Hierarchy level
            output_dir: Directory to save outputs
            lookback_days: Days to analyze
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"GENERATING VISUALIZATIONS - {level.upper()}")
        print(f"{'='*60}")
        print(f"Output directory: {output_path.absolute()}")
        
        # 1. Sector heatmap
        print("\n1. Creating sector performance heatmap...")
        self.visualizer.plot_sector_heatmap(
            level=level,
            lookback_days=lookback_days,
            save_path=output_path / f'heatmap_{level}_{self.timeframe}.html'
        )
        
        # 2. Cumulative performance
        print("2. Creating cumulative performance chart...")
        self.visualizer.plot_cumulative_performance(
            level=level,
            lookback_days=lookback_days,
            top_n=15,
            save_path=output_path / f'cumulative_{level}_{self.timeframe}.html'
        )
        
        # 3. Rotation network
        print("3. Creating rotation network graph...")
        self.visualizer.plot_rotation_network(
            level=level,
            min_flow_strength=5.0,
            save_path=output_path / f'network_{level}_{self.timeframe}.html'
        )
        
        # 4. Lead-lag matrix
        print("4. Creating lead-lag correlation matrix...")
        self.visualizer.plot_lead_lag_matrix(
            level=level,
            max_lag_days=7,
            save_path=output_path / f'leadlag_{level}_{self.timeframe}.png'
        )
        
        # 5. Ranking race
        print("5. Creating sector ranking race animation...")
        self.visualizer.plot_sector_rankings_race(
            level=level,
            lookback_days=lookback_days,
            save_path=output_path / f'race_{level}_{self.timeframe}.html'
        )
        
        print(f"\n✓ All visualizations saved to {output_path.absolute()}")
    
    def run_full_analysis(self,
                         levels: list = ['category', 'subcategory', 'segment'],
                         output_dir: str = './output'):
        """
        Run complete analysis across all hierarchy levels
        
        Args:
            levels: List of hierarchy levels to analyze
            output_dir: Output directory
        """
        # Data coverage
        self.show_data_coverage()
        
        # Analyze each level
        for level in levels:
            print(f"\n\n{'#'*60}")
            print(f"# ANALYZING: {level.upper()}")
            print(f"{'#'*60}")
            
            # Performance analysis
            self.analyze_sector_performance(level=level)
            
            # Rotation analysis
            self.analyze_rotation_patterns(level=level)
            
            # Generate visualizations
            self.generate_all_visualizations(level=level, output_dir=output_dir)
        
        print(f"\n\n{'='*60}")
        print("✓ ANALYSIS COMPLETE!")
        print(f"{'='*60}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Crypto Sector Rotation Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze daily data for all hierarchy levels
  python dashboard.py --csv-dir /path/to/csvs --timeframe 1d
  
  # Analyze 4-hour data for subcategory level only
  python dashboard.py --csv-dir /path/to/csvs --timeframe 4h --level subcategory
  
  # Custom output directory
  python dashboard.py --csv-dir /path/to/csvs --output ./my_analysis
        """
    )
    
    parser.add_argument(
        '--csv-dir',
        type=str,
        required=True,
        help='Directory containing CSV files'
    )
    
    parser.add_argument(
        '--sector-file',
        type=str,
        default='/mnt/user-data/uploads/SYMBOLS_SECTORS_MERGED_Final.csv',
        help='Path to sector classification CSV'
    )
    
    parser.add_argument(
        '--timeframe',
        type=str,
        choices=['1d', '4h'],
        default='1d',
        help='Timeframe to analyze'
    )
    
    parser.add_argument(
        '--level',
        type=str,
        choices=['category', 'subcategory', 'segment', 'all'],
        default='all',
        help='Hierarchy level to analyze'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='./output',
        help='Output directory for visualizations'
    )
    
    parser.add_argument(
        '--lookback',
        type=int,
        default=90,
        help='Days to look back for analysis'
    )
    
    args = parser.parse_args()
    
    # Initialize dashboard
    dashboard = SectorRotationDashboard(
        csv_directory=args.csv_dir,
        sector_classification_path=args.sector_file,
        timeframe=args.timeframe
    )
    
    # Determine levels to analyze
    if args.level == 'all':
        levels = ['category', 'subcategory', 'segment']
    else:
        levels = [args.level]
    
    # Run analysis
    dashboard.run_full_analysis(
        levels=levels,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()
