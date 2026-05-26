"""
Rotation Analyzer Module

Detects sector rotation patterns, lead-lag relationships, and capital flow dynamics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy.stats import pearsonr
try:
    from .sector_aggregator import SectorAggregator
except ImportError:
    from sector_aggregator import SectorAggregator


class RotationAnalyzer:
    """Analyzes sector rotation patterns and capital flows"""
    
    def __init__(self, aggregator: SectorAggregator):
        """
        Initialize with a sector aggregator
        
        Args:
            aggregator: Initialized SectorAggregator instance
        """
        self.aggregator = aggregator
    
    def calculate_lead_lag_correlation(self,
                                      level: str,
                                      max_lag_days: int = 14,
                                      lookback_days: int = 90) -> pd.DataFrame:
        """
        Calculate lead-lag correlations between all sector pairs
        
        Args:
            level: Hierarchy level ('category', 'subcategory', 'segment')
            max_lag_days: Maximum number of days to test for lag
            lookback_days: Number of days of history to use
            
        Returns:
            DataFrame with columns: [sector_lead, sector_lag, lag_days, correlation, p_value]
        """
        # Get sector timeseries
        timeseries = self.aggregator.create_sector_timeseries(level, lookback_days)
        
        if len(timeseries) < 2:
            return pd.DataFrame()
        
        sectors = list(timeseries.keys())
        results = []
        
        print(f"\nCalculating lead-lag correlations for {len(sectors)} sectors...")
        
        # Test all pairs
        for i, sector_a in enumerate(sectors):
            for sector_b in sectors[i+1:]:  # Avoid duplicates
                
                # Get aligned returns
                df_a = timeseries[sector_a]['avg_return'].dropna()
                df_b = timeseries[sector_b]['avg_return'].dropna()
                
                # Find common dates
                common_dates = df_a.index.intersection(df_b.index)
                
                if len(common_dates) < 30:  # Need minimum data
                    continue
                
                df_a_aligned = df_a.loc[common_dates]
                df_b_aligned = df_b.loc[common_dates]
                
                # Test different lags
                for lag in range(0, max_lag_days + 1):
                    if lag == 0:
                        # Contemporaneous correlation
                        if len(df_a_aligned) > 10:
                            corr, p_val = pearsonr(df_a_aligned, df_b_aligned)
                            
                            results.append({
                                'sector_lead': sector_a,
                                'sector_lag': sector_b,
                                'lag_days': 0,
                                'correlation': corr,
                                'p_value': p_val,
                                'direction': 'contemporaneous'
                            })
                    else:
                        # Test A leading B
                        if len(df_a_aligned) > lag + 10:
                            a_lead = df_a_aligned[:-lag].values
                            b_lag = df_b_aligned[lag:].values
                            
                            if len(a_lead) == len(b_lag):
                                corr, p_val = pearsonr(a_lead, b_lag)
                                
                                results.append({
                                    'sector_lead': sector_a,
                                    'sector_lag': sector_b,
                                    'lag_days': lag,
                                    'correlation': corr,
                                    'p_value': p_val,
                                    'direction': f'{sector_a}_leads'
                                })
                        
                        # Test B leading A
                        if len(df_b_aligned) > lag + 10:
                            b_lead = df_b_aligned[:-lag].values
                            a_lag = df_a_aligned[lag:].values
                            
                            if len(b_lead) == len(a_lag):
                                corr, p_val = pearsonr(b_lead, a_lag)
                                
                                results.append({
                                    'sector_lead': sector_b,
                                    'sector_lag': sector_a,
                                    'lag_days': lag,
                                    'correlation': corr,
                                    'p_value': p_val,
                                    'direction': f'{sector_b}_leads'
                                })
        
        if results:
            results_df = pd.DataFrame(results)
            # Filter to significant correlations
            results_df = results_df[results_df['p_value'] < 0.05]
            results_df = results_df.sort_values('correlation', ascending=False, key=abs)
            return results_df
        
        return pd.DataFrame()
    
    def detect_rotation_sequence(self,
                                level: str,
                                lookback_days: int = 90,
                                window_days: int = 7) -> List[Tuple[str, float, str]]:
        """
        Detect the sequence of sector rotation based on momentum peaks
        
        Args:
            level: Hierarchy level
            lookback_days: Days to analyze
            window_days: Rolling window for momentum calculation
            
        Returns:
            List of tuples: (sector_name, peak_date, peak_momentum)
        """
        # Get performance data
        perf_df = self.aggregator.aggregate_sector_performance(level=level)
        
        if perf_df.empty:
            return []
        
        # Filter to lookback period
        end_date = perf_df['date'].max()
        start_date = end_date - pd.Timedelta(days=lookback_days)
        perf_df = perf_df[perf_df['date'] >= start_date]
        
        rotation_sequence = []
        
        for sector in perf_df['sector'].unique():
            sector_data = perf_df[perf_df['sector'] == sector].copy()
            sector_data = sector_data.sort_values('date')
            
            # Calculate rolling momentum
            sector_data['rolling_momentum'] = sector_data['avg_return'].rolling(window_days).mean()
            
            # Find peak momentum
            if len(sector_data) > 0:
                peak_idx = sector_data['rolling_momentum'].idxmax()
                peak_row = sector_data.loc[peak_idx]
                
                rotation_sequence.append((
                    sector,
                    peak_row['date'],
                    peak_row['rolling_momentum']
                ))
        
        # Sort by peak date
        rotation_sequence.sort(key=lambda x: x[1])
        
        return rotation_sequence
    
    def calculate_capital_flow(self,
                              level: str,
                              threshold: float = 2.0,
                              lookback_days: int = 30) -> pd.DataFrame:
        """
        Estimate capital flow between sectors based on momentum divergence
        
        When one sector's momentum drops significantly while another rises,
        estimate capital is rotating from sector A to sector B.
        
        Args:
            level: Hierarchy level
            threshold: Minimum momentum change to consider a flow
            lookback_days: Period to analyze
            
        Returns:
            DataFrame with: [date, from_sector, to_sector, flow_strength]
        """
        # Get performance data
        perf_df = self.aggregator.aggregate_sector_performance(level=level)
        
        if perf_df.empty:
            return pd.DataFrame()
        
        # Filter to recent period
        end_date = perf_df['date'].max()
        start_date = end_date - pd.Timedelta(days=lookback_days)
        perf_df = perf_df[perf_df['date'] >= start_date]
        
        # Calculate momentum change for each sector
        flows = []
        
        dates = sorted(perf_df['date'].unique())
        
        for i in range(1, len(dates)):
            prev_date = dates[i-1]
            curr_date = dates[i]
            
            prev_data = perf_df[perf_df['date'] == prev_date]
            curr_data = perf_df[perf_df['date'] == curr_date]
            
            # Merge to calculate changes
            merged = prev_data.merge(
                curr_data,
                on='sector',
                suffixes=('_prev', '_curr')
            )
            
            merged['momentum_change'] = merged['momentum_curr'] - merged['momentum_prev']
            
            # Find sectors with declining momentum
            declining = merged[merged['momentum_change'] < -threshold].copy()
            # Find sectors with rising momentum
            rising = merged[merged['momentum_change'] > threshold].copy()
            
            # Estimate flows
            for _, dec_row in declining.iterrows():
                for _, ris_row in rising.iterrows():
                    # Flow strength based on magnitude of changes
                    flow_strength = abs(dec_row['momentum_change']) + abs(ris_row['momentum_change'])
                    
                    flows.append({
                        'date': curr_date,
                        'from_sector': dec_row['sector'],
                        'to_sector': ris_row['sector'],
                        'flow_strength': flow_strength,
                        'from_momentum_change': dec_row['momentum_change'],
                        'to_momentum_change': ris_row['momentum_change']
                    })
        
        if flows:
            flows_df = pd.DataFrame(flows)
            # Sort by flow strength
            flows_df = flows_df.sort_values('flow_strength', ascending=False)
            return flows_df
        
        return pd.DataFrame()
    
    def identify_cycle_phase(self,
                            level: str,
                            sector_name: str,
                            lookback_days: int = 90) -> str:
        """
        Identify what phase of the cycle a sector is in
        
        Phases:
        - Accumulation: Low volatility, positive breadth, rising momentum
        - Markup: High momentum, high breadth, rising prices
        - Distribution: Declining momentum, mixed breadth, high volatility
        - Markdown: Negative returns, low breadth, declining momentum
        
        Args:
            level: Hierarchy level
            sector_name: Name of sector to analyze
            lookback_days: Days to analyze
            
        Returns:
            Phase name as string
        """
        # Get sector timeseries
        timeseries = self.aggregator.create_sector_timeseries(level, lookback_days)
        
        if sector_name not in timeseries:
            return "Unknown"
        
        df = timeseries[sector_name]
        
        if len(df) < 14:
            return "Insufficient Data"
        
        # Get recent metrics (last 14 days)
        recent = df.tail(14)
        
        avg_return = recent['avg_return'].mean()
        momentum = recent['momentum'].mean()
        breadth = recent['breadth_pct'].mean()
        volatility = recent['volatility'].mean()
        
        # Classify phase
        if momentum > 0 and breadth > 60 and avg_return > 1:
            return "Markup"
        elif momentum < 0 and breadth < 40 and avg_return < -1:
            return "Markdown"
        elif abs(momentum) < 0.5 and breadth > 50 and volatility < volatility:
            return "Accumulation"
        elif momentum < 0 and breadth < 60:
            return "Distribution"
        else:
            return "Transitional"
    
    def get_strongest_rotations(self,
                               level: str,
                               n_flows: int = 10) -> pd.DataFrame:
        """
        Get the strongest capital rotation flows
        
        Args:
            level: Hierarchy level
            n_flows: Number of top flows to return
            
        Returns:
            DataFrame with strongest rotation flows
        """
        flows = self.calculate_capital_flow(level=level)
        
        if flows.empty:
            return pd.DataFrame()
        
        # Aggregate by sector pair (sum all flows between same pair)
        aggregated = flows.groupby(['from_sector', 'to_sector']).agg({
            'flow_strength': 'sum',
            'date': 'count'
        }).reset_index()
        
        aggregated.columns = ['from_sector', 'to_sector', 'total_flow', 'occurrences']
        
        # Sort by total flow
        aggregated = aggregated.sort_values('total_flow', ascending=False)
        
        return aggregated.head(n_flows)


if __name__ == "__main__":
    # Example usage
    from data_loader import DataLoader
    from sector_aggregator import SectorAggregator
    
    loader = DataLoader(
        csv_directory="/tmp",
        sector_classification_path="/mnt/user-data/uploads/SYMBOLS_SECTORS_MERGED_Final.csv",
        timeframe="1d"
    )
    
    loader.load_all_coins()
    aggregator = SectorAggregator(loader)
    analyzer = RotationAnalyzer(aggregator)
    
    print("\n=== Analyzing Sector Rotation Patterns ===")
    
    # Test lead-lag correlations
    print("\n1. Lead-Lag Correlations (Subcategory):")
    lead_lag = analyzer.calculate_lead_lag_correlation(level='subcategory', max_lag_days=7)
    if not lead_lag.empty:
        print(lead_lag.head(10)[['sector_lead', 'sector_lag', 'lag_days', 'correlation']])
    
    # Test rotation sequence
    print("\n2. Rotation Sequence (order of momentum peaks):")
    sequence = analyzer.detect_rotation_sequence(level='subcategory', lookback_days=60)
    for sector, date, momentum in sequence[:10]:
        print(f"  {sector}: peaked on {date.strftime('%Y-%m-%d')} (momentum: {momentum:.2f}%)")
    
    # Test capital flows
    print("\n3. Strongest Capital Rotation Flows:")
    flows = analyzer.get_strongest_rotations(level='subcategory', n_flows=5)
    if not flows.empty:
        print(flows)
