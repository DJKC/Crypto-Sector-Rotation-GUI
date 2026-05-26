"""
Sector Aggregator Module

Calculates aggregate performance metrics for sectors at different hierarchy levels.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
try:
    from .data_loader import DataLoader
except ImportError:
    from data_loader import DataLoader


class SectorAggregator:
    """Aggregates coin-level data to sector-level metrics"""
    
    def __init__(self, data_loader: DataLoader):
        """
        Initialize with a data loader
        
        Args:
            data_loader: Initialized DataLoader instance
        """
        self.loader = data_loader
        self.sector_timeseries = {}
    
    def calculate_returns(self, 
                         df: pd.DataFrame,
                         periods: List[int] = [1, 7, 30]) -> pd.DataFrame:
        """
        Calculate percentage returns for multiple periods
        
        Args:
            df: DataFrame with 'close' column
            periods: List of periods (in bars) to calculate returns
            
        Returns:
            DataFrame with return columns added
        """
        result = df.copy()
        
        for period in periods:
            result[f'ret_{period}d'] = result['close'].pct_change(period) * 100
        
        return result
    
    def aggregate_sector_performance(self,
                                    level: str,
                                    start_date: Optional[str] = None,
                                    end_date: Optional[str] = None,
                                    equal_weight: bool = True) -> pd.DataFrame:
        """
        Calculate aggregate performance for all sectors at a given hierarchy level
        
        Args:
            level: 'category', 'subcategory', or 'segment'
            start_date: Start date for analysis (YYYY-MM-DD)
            end_date: End date for analysis (YYYY-MM-DD)
            equal_weight: If True, equal-weight average; if False, cap-weighted (requires cap data)
            
        Returns:
            DataFrame with columns: [date, sector, avg_return, breadth, momentum, coin_count]
        """
        # Build hierarchy if not already done
        if not self.loader.sector_hierarchy:
            self.loader.build_sector_hierarchy()
        
        # Get all unique sectors at this level
        if level == 'category':
            sectors = list(self.loader.sector_hierarchy.keys())
        elif level == 'subcategory':
            sectors = []
            for cat in self.loader.sector_hierarchy.values():
                sectors.extend(cat.keys())
            sectors = list(set(sectors))
        elif level == 'segment':
            sectors = []
            for cat in self.loader.sector_hierarchy.values():
                for subcat in cat.values():
                    sectors.extend(subcat.keys())
            sectors = list(set(sectors))
        else:
            raise ValueError(f"Invalid level: {level}")
        
        print(f"\nCalculating sector performance for {len(sectors)} {level}s...")
        
        sector_results = []
        
        for sector_name in sectors:
            # Get all symbols in this sector
            symbols = self.loader.get_symbols_in_sector(level, sector_name)
            
            if not symbols:
                continue
            
            # Collect returns for all coins in sector
            sector_returns_list = []
            
            for symbol in symbols:
                if symbol not in self.loader.data_cache:
                    continue
                
                df = self.loader.data_cache[symbol].copy()
                
                # Filter date range if specified
                if start_date:
                    df = df[df.index >= start_date]
                if end_date:
                    df = df[df.index <= end_date]
                
                if df.empty:
                    continue
                
                # Calculate daily returns
                df['return'] = df['close'].pct_change() * 100
                df = df.dropna()
                
                # Add symbol identifier
                df['symbol'] = symbol
                
                sector_returns_list.append(df[['return', 'symbol']])
            
            if not sector_returns_list:
                continue
            
            # Combine all returns
            sector_returns = pd.concat(sector_returns_list)
            
            # Group by date and calculate sector metrics
            daily_metrics = sector_returns.groupby(sector_returns.index).agg({
                'return': ['mean', 'median', 'std', 'count', lambda x: (x > 0).sum() / len(x) * 100]
            })
            
            daily_metrics.columns = ['avg_return', 'median_return', 'volatility', 'coin_count', 'breadth_pct']
            daily_metrics['sector'] = sector_name
            daily_metrics['level'] = level
            
            # Calculate momentum (7-day rate of change of avg return)
            daily_metrics['momentum'] = daily_metrics['avg_return'].rolling(7).mean()
            
            sector_results.append(daily_metrics.reset_index())
        
        if sector_results:
            result_df = pd.concat(sector_results, ignore_index=False)
            result_df = result_df.reset_index()
            result_df = result_df.rename(columns={'datetime': 'date'} if 'datetime' in result_df.columns else {})
            return result_df
        else:
            return pd.DataFrame()
    
    def create_sector_timeseries(self,
                                level: str,
                                lookback_days: int = 90) -> Dict[str, pd.DataFrame]:
        """
        Create time series of cumulative returns for each sector
        
        Args:
            level: 'category', 'subcategory', or 'segment'
            lookback_days: Number of days to look back
            
        Returns:
            Dict mapping sector_name -> DataFrame with cumulative returns
        """
        # Calculate performance
        perf_df = self.aggregate_sector_performance(level=level)
        
        if perf_df.empty:
            return {}
        
        # Filter to lookback period
        end_date = perf_df['date'].max()
        start_date = end_date - pd.Timedelta(days=lookback_days)
        perf_df = perf_df[perf_df['date'] >= start_date]
        
        # Calculate cumulative returns for each sector
        sector_timeseries = {}
        
        for sector in perf_df['sector'].unique():
            sector_data = perf_df[perf_df['sector'] == sector].copy()
            sector_data = sector_data.sort_values('date')
            
            # Calculate cumulative return
            sector_data['cumulative_return'] = (1 + sector_data['avg_return'] / 100).cumprod() - 1
            sector_data['cumulative_return'] *= 100  # Convert to percentage
            
            sector_data = sector_data.set_index('date')
            sector_timeseries[sector] = sector_data
        
        return sector_timeseries
    
    def get_sector_rankings(self,
                          level: str,
                          date: Optional[str] = None,
                          metric: str = 'avg_return',
                          top_n: int = 10) -> pd.DataFrame:
        """
        Get ranked list of top/bottom performing sectors
        
        Args:
            level: 'category', 'subcategory', or 'segment'
            date: Specific date to rank (default: most recent)
            metric: Metric to rank by ('avg_return', 'momentum', 'breadth_pct')
            top_n: Number of top performers to return
            
        Returns:
            DataFrame with top and bottom performers
        """
        perf_df = self.aggregate_sector_performance(level=level)
        
        if perf_df.empty:
            return pd.DataFrame()
        
        # Get specific date or most recent
        if date is None:
            date = perf_df['date'].max()
        
        date_data = perf_df[perf_df['date'] == date].copy()
        
        if date_data.empty:
            return pd.DataFrame()
        
        # Sort by metric
        date_data = date_data.sort_values(metric, ascending=False)
        
        # Get top and bottom performers
        top_performers = date_data.head(top_n)
        bottom_performers = date_data.tail(top_n)
        
        top_performers['rank_type'] = 'Top'
        bottom_performers['rank_type'] = 'Bottom'
        
        return pd.concat([top_performers, bottom_performers])
    
    def calculate_sector_correlations(self,
                                     level: str,
                                     lookback_days: int = 90,
                                     min_overlap: int = 30) -> pd.DataFrame:
        """
        Calculate correlation matrix between sectors
        
        Args:
            level: Hierarchy level
            lookback_days: Number of days for correlation calculation
            min_overlap: Minimum number of overlapping data points required
            
        Returns:
            DataFrame correlation matrix
        """
        # Get sector timeseries
        timeseries = self.create_sector_timeseries(level, lookback_days)
        
        if not timeseries:
            return pd.DataFrame()
        
        # Create wide-format DataFrame
        returns_dict = {}
        for sector, df in timeseries.items():
            returns_dict[sector] = df['avg_return']
        
        returns_df = pd.DataFrame(returns_dict)
        
        # Calculate correlation
        corr_matrix = returns_df.corr(min_periods=min_overlap)
        
        return corr_matrix


if __name__ == "__main__":
    # Example usage
    from data_loader import DataLoader
    
    loader = DataLoader(
        csv_directory="/tmp",
        sector_classification_path="/mnt/user-data/uploads/SYMBOLS_SECTORS_MERGED_Final.csv",
        timeframe="1d"
    )
    
    # Load data
    loader.load_all_coins()
    
    # Create aggregator
    aggregator = SectorAggregator(loader)
    
    # Test subcategory performance
    print("\n=== Subcategory Performance ===")
    perf = aggregator.aggregate_sector_performance(level='subcategory')
    print(f"Generated {len(perf)} data points across {perf['sector'].nunique()} subcategories")
    
    # Show recent top performers
    print("\n=== Top Performers (Most Recent) ===")
    rankings = aggregator.get_sector_rankings(level='subcategory', top_n=5)
    print(rankings[['sector', 'avg_return', 'breadth_pct', 'coin_count']])
