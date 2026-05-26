"""
Data Loader Module for Crypto Sector Rotation Analysis

Loads OHLCV data from local CSV files and merges with CF DACS sector classifications.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class DataLoader:
    """Loads and organizes crypto OHLCV data with sector classifications"""
    
    def __init__(self, 
                 csv_directory: str,
                 sector_classification_path: str,
                 timeframe: str = '1d'):
        """
        Initialize the data loader
        
        Args:
            csv_directory: Path to directory containing CSV files
            sector_classification_path: Path to SYMBOLS_SECTORS_MERGED_Final.csv
            timeframe: '1d' for daily, '4h' for 4-hour data
        """
        self.csv_directory = Path(csv_directory)
        self.sector_classification_path = Path(sector_classification_path)
        self.timeframe = timeframe
        
        # Load sector classifications
        self.sectors_df = self._load_sector_classifications()
        
        # Storage for loaded data
        self.data_cache = {}
        self.sector_hierarchy = {}
        
    def _load_sector_classifications(self) -> pd.DataFrame:
        """Load and parse the CF DACS sector classification file"""
        df = pd.read_csv(self.sector_classification_path, header=None)
        df.columns = ['symbol', 'category', 'subcategory', 'segment']
        
        # Clean up any whitespace
        for col in df.columns:
            df[col] = df[col].str.strip()
        
        return df
    
    def _extract_symbol_from_filename(self, filename: str) -> Optional[str]:
        """
        Extract base symbol from filename like 'BTCUSDT_1d.csv'
        
        Args:
            filename: Name of CSV file
            
        Returns:
            Symbol without USDT suffix, or None if invalid format
        """
        try:
            # Remove .csv extension
            name = filename.replace('.csv', '')
            
            # Split by underscore to get symbol part
            symbol_part = name.split('_')[0]
            
            # Remove USDT suffix
            if symbol_part.endswith('USDT'):
                symbol = symbol_part[:-4]  # Remove 'USDT'
                return symbol
            
            return None
        except:
            return None
    
    def load_single_coin(self, filepath: Path) -> Optional[pd.DataFrame]:
        """
        Load OHLCV data for a single coin
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            DataFrame with datetime index and OHLCV columns, or None if error
        """
        try:
            df = pd.read_csv(filepath)
            
            # Convert timestamp to datetime
            df['datetime'] = pd.to_datetime(df['open_time_dt'])
            df = df.set_index('datetime')
            
            # Keep only OHLCV columns
            df = df[['open', 'high', 'low', 'close', 'volume']]
            
            # Convert to numeric (handle any string issues)
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Drop any rows with NaN values
            df = df.dropna()
            
            # Sort by date
            df = df.sort_index()
            
            return df
            
        except Exception as e:
            print(f"Error loading {filepath.name}: {e}")
            return None
    
    def load_all_coins(self, reload: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Load all coin data from CSV directory
        
        Args:
            reload: If True, reload even if cached
            
        Returns:
            Dictionary mapping symbol -> DataFrame
        """
        if self.data_cache and not reload:
            return self.data_cache
        
        print(f"Loading CSV files from {self.csv_directory}...")
        
        # Find all CSV files matching the timeframe
        pattern = f"*USDT_{self.timeframe}.csv"
        csv_files = list(self.csv_directory.glob(pattern))
        
        print(f"Found {len(csv_files)} files matching pattern '{pattern}'")
        
        loaded_count = 0
        for filepath in csv_files:
            symbol = self._extract_symbol_from_filename(filepath.name)
            
            if symbol is None:
                continue
            
            df = self.load_single_coin(filepath)
            
            if df is not None and len(df) > 0:
                self.data_cache[symbol] = df
                loaded_count += 1
        
        print(f"Successfully loaded {loaded_count} coins")
        
        return self.data_cache
    
    def get_sector_for_symbol(self, symbol: str) -> Optional[Dict[str, str]]:
        """
        Get sector classification for a symbol
        
        Args:
            symbol: Coin symbol (e.g., 'BTC')
            
        Returns:
            Dict with 'category', 'subcategory', 'segment' or None
        """
        row = self.sectors_df[self.sectors_df['symbol'] == symbol]
        
        if row.empty:
            return None
        
        return {
            'category': row.iloc[0]['category'],
            'subcategory': row.iloc[0]['subcategory'],
            'segment': row.iloc[0]['segment']
        }
    
    def build_sector_hierarchy(self) -> Dict[str, Dict]:
        """
        Build a hierarchical mapping of all sectors
        
        Returns:
            Nested dictionary: category -> subcategory -> segment -> [symbols]
        """
        if self.sector_hierarchy:
            return self.sector_hierarchy
        
        hierarchy = {}
        
        for symbol in self.data_cache.keys():
            sector_info = self.get_sector_for_symbol(symbol)
            
            if sector_info is None:
                continue
            
            cat = sector_info['category']
            subcat = sector_info['subcategory']
            seg = sector_info['segment']
            
            # Skip NA entries
            if cat == 'NA' or subcat == 'NA' or seg == 'NA':
                continue
            
            # Build hierarchy
            if cat not in hierarchy:
                hierarchy[cat] = {}
            
            if subcat not in hierarchy[cat]:
                hierarchy[cat][subcat] = {}
            
            if seg not in hierarchy[cat][subcat]:
                hierarchy[cat][subcat][seg] = []
            
            hierarchy[cat][subcat][seg].append(symbol)
        
        self.sector_hierarchy = hierarchy
        return hierarchy
    
    def get_symbols_in_sector(self, 
                              level: str,
                              sector_name: str) -> List[str]:
        """
        Get all symbols belonging to a specific sector at given hierarchy level
        
        Args:
            level: 'category', 'subcategory', or 'segment'
            sector_name: Name of the sector
            
        Returns:
            List of symbols in that sector
        """
        if not self.sector_hierarchy:
            self.build_sector_hierarchy()
        
        symbols = []
        
        if level == 'category':
            if sector_name in self.sector_hierarchy:
                for subcat in self.sector_hierarchy[sector_name].values():
                    for seg in subcat.values():
                        symbols.extend(seg)
        
        elif level == 'subcategory':
            for cat in self.sector_hierarchy.values():
                if sector_name in cat:
                    for seg in cat[sector_name].values():
                        symbols.extend(seg)
        
        elif level == 'segment':
            for cat in self.sector_hierarchy.values():
                for subcat in cat.values():
                    if sector_name in subcat:
                        symbols.extend(subcat[sector_name])
        
        return symbols
    
    def get_coverage_report(self) -> pd.DataFrame:
        """
        Generate a report showing data coverage by sector
        
        Returns:
            DataFrame with sector hierarchy and coin counts
        """
        report_data = []
        
        for symbol, df in self.data_cache.items():
            sector_info = self.get_sector_for_symbol(symbol)
            
            if sector_info and sector_info['category'] != 'NA':
                report_data.append({
                    'symbol': symbol,
                    'category': sector_info['category'],
                    'subcategory': sector_info['subcategory'],
                    'segment': sector_info['segment'],
                    'data_points': len(df),
                    'start_date': df.index.min(),
                    'end_date': df.index.max()
                })
        
        report_df = pd.DataFrame(report_data)
        
        if not report_df.empty:
            # Summary by subcategory
            summary = report_df.groupby(['category', 'subcategory']).agg({
                'symbol': 'count',
                'data_points': ['min', 'max', 'mean'],
                'start_date': 'min',
                'end_date': 'max'
            }).round(0)
            
            summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
            return summary
        
        return report_df


if __name__ == "__main__":
    # Example usage
    loader = DataLoader(
        csv_directory="/tmp",
        sector_classification_path="/mnt/user-data/uploads/SYMBOLS_SECTORS_MERGED_Final.csv",
        timeframe="1d"
    )
    
    # Load all data
    data = loader.load_all_coins()
    print(f"\nLoaded {len(data)} coins with sector classifications")
    
    # Build hierarchy
    hierarchy = loader.build_sector_hierarchy()
    print(f"\nSector hierarchy built:")
    print(f"  Categories: {len(hierarchy)}")
    for cat, subcats in hierarchy.items():
        print(f"    {cat}: {len(subcats)} subcategories")
    
    # Show coverage
    print("\nData Coverage by Sector:")
    print(loader.get_coverage_report())
