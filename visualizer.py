"""
Visualization Module

Creates interactive and static visualizations for sector rotation analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from typing import Dict, List, Optional
import warnings

# Try to import plotly - optional dependency
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    warnings.warn("Plotly not available. Interactive visualizations will be limited.")

# Try to import networkx - optional dependency  
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    warnings.warn("NetworkX not available. Network graphs will be disabled.")

try:
    from .sector_aggregator import SectorAggregator
    from .rotation_analyzer import RotationAnalyzer
except ImportError:
    from sector_aggregator import SectorAggregator
    from rotation_analyzer import RotationAnalyzer


class SectorVisualizer:
    """Creates visualizations for sector rotation analysis"""
    
    def __init__(self, 
                 aggregator: SectorAggregator,
                 analyzer: RotationAnalyzer):
        """
        Initialize visualizer
        
        Args:
            aggregator: SectorAggregator instance
            analyzer: RotationAnalyzer instance
        """
        self.aggregator = aggregator
        self.analyzer = analyzer
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def plot_sector_heatmap(self,
                           level: str,
                           lookback_days: int = 90,
                           interactive: bool = True,
                           save_path: Optional[str] = None):
        """
        Create animated heatmap showing sector performance over time
        
        Args:
            level: Hierarchy level
            lookback_days: Days to display
            interactive: If True, create Plotly interactive; else matplotlib static
            save_path: Path to save figure
        """
        # Get sector timeseries
        timeseries = self.aggregator.create_sector_timeseries(level, lookback_days)
        
        if not timeseries:
            print("No data available for heatmap")
            return
        
        # Create wide-format DataFrame
        data_dict = {}
        for sector, df in timeseries.items():
            data_dict[sector] = df['avg_return']
        
        df_wide = pd.DataFrame(data_dict)
        df_wide = df_wide.fillna(0)
        
        if interactive:
            if not PLOTLY_AVAILABLE:
                print("Plotly not available. Creating static matplotlib version instead.")
                interactive = False
            else:
                # Plotly interactive heatmap
                fig = go.Figure(data=go.Heatmap(
                    z=df_wide.T.values,
                    x=df_wide.index,
                    y=df_wide.columns,
                    colorscale='RdYlGn',
                    zmid=0,
                    text=df_wide.T.values.round(2),
                    texttemplate='%{text}%',
                    textfont={"size": 8},
                    colorbar=dict(title="Daily Return (%)")
                ))
                
                fig.update_layout(
                    title=f'Sector Performance Heatmap - {level.title()} Level',
                    xaxis_title='Date',
                    yaxis_title='Sector',
                    height=max(600, len(df_wide.columns) * 25),
                    hovermode='closest'
                )
                
                if save_path:
                    fig.write_html(save_path)
                    print(f"Saved to {save_path}")
                    return
                else:
                    fig.show()
                    return
        
        if not interactive:
            # Plotly interactive heatmap
            fig = go.Figure(data=go.Heatmap(
                z=df_wide.T.values,
                x=df_wide.index,
                y=df_wide.columns,
                colorscale='RdYlGn',
                zmid=0,
                text=df_wide.T.values.round(2),
                texttemplate='%{text}%',
                textfont={"size": 8},
                colorbar=dict(title="Daily Return (%)")
            ))
            
            fig.update_layout(
                title=f'Sector Performance Heatmap - {level.title()} Level',
                xaxis_title='Date',
                yaxis_title='Sector',
                height=max(600, len(df_wide.columns) * 25),
                hovermode='closest'
            )
            
            if save_path:
                fig.write_html(save_path)
            else:
                fig.show()
        
        else:
            # Matplotlib static heatmap
            fig, ax = plt.subplots(figsize=(16, max(8, len(df_wide.columns) * 0.4)))
            
            sns.heatmap(
                df_wide.T,
                cmap='RdYlGn',
                center=0,
                cbar_kws={'label': 'Daily Return (%)'},
                ax=ax,
                linewidths=0.5
            )
            
            ax.set_title(f'Sector Performance Heatmap - {level.title()} Level', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Sector', fontsize=12)
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=120, bbox_inches='tight')
            else:
                plt.show()
    
    def plot_cumulative_performance(self,
                                   level: str,
                                   lookback_days: int = 90,
                                   top_n: Optional[int] = None,
                                   save_path: Optional[str] = None):
        """
        Plot cumulative returns for all sectors as racing lines
        
        Args:
            level: Hierarchy level
            lookback_days: Days to display
            top_n: If set, only show top N performers
            save_path: Path to save figure
        """
        # Get sector timeseries
        timeseries = self.aggregator.create_sector_timeseries(level, lookback_days)
        
        if not timeseries:
            print("No data available")
            return
        
        # Calculate final cumulative returns for each sector
        final_returns = {sector: df['cumulative_return'].iloc[-1] 
                        for sector, df in timeseries.items() 
                        if len(df) > 0}
        
        # Sort and optionally filter to top N
        sorted_sectors = sorted(final_returns.items(), key=lambda x: x[1], reverse=True)
        
        if top_n:
            sorted_sectors = sorted_sectors[:top_n]
        
        sectors_to_plot = [s[0] for s in sorted_sectors]
        
        # Create Plotly line chart
        fig = go.Figure()
        
        for sector in sectors_to_plot:
            df = timeseries[sector]
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['cumulative_return'],
                mode='lines',
                name=sector,
                line=dict(width=2),
                hovertemplate=f'<b>{sector}</b><br>' +
                             'Date: %{x}<br>' +
                             'Return: %{y:.2f}%<extra></extra>'
            ))
        
        fig.update_layout(
            title=f'Cumulative Sector Performance - {level.title()} Level',
            xaxis_title='Date',
            yaxis_title='Cumulative Return (%)',
            height=600,
            hovermode='x unified',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.01
            )
        )
        
        if save_path:
            fig.write_html(save_path)
        else:
            fig.show()
    
    def plot_rotation_network(self,
                             level: str,
                             min_flow_strength: float = 10.0,
                             save_path: Optional[str] = None):
        """
        Create network graph showing capital rotation flows between sectors
        
        Args:
            level: Hierarchy level
            min_flow_strength: Minimum flow strength to include
            save_path: Path to save figure
        """
        # Get rotation flows
        flows = self.analyzer.get_strongest_rotations(level=level, n_flows=50)
        
        if flows.empty:
            print("No rotation flows detected")
            return
        
        # Filter by minimum strength
        flows = flows[flows['total_flow'] >= min_flow_strength]
        
        if flows.empty:
            print(f"No flows above threshold {min_flow_strength}")
            return
        
        # Create network graph
        G = nx.DiGraph()
        
        for _, row in flows.iterrows():
            G.add_edge(
                row['from_sector'],
                row['to_sector'],
                weight=row['total_flow'],
                occurrences=row['occurrences']
            )
        
        # Calculate layout
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Extract edge information for Plotly
        edge_trace = []
        
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            weight = edge[2]['weight']
            
            edge_trace.append(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=weight/10, color='rgba(125,125,125,0.5)'),
                hoverinfo='none',
                showlegend=False
            ))
        
        # Extract node information
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Calculate node size based on in/out degree
            in_flows = sum([G[u][node]['weight'] for u in G.predecessors(node)])
            out_flows = sum([G[node][v]['weight'] for v in G.successors(node)])
            total_flows = in_flows + out_flows
            
            node_size.append(20 + total_flows / 2)
            node_text.append(f"{node}<br>In: {in_flows:.1f}<br>Out: {out_flows:.1f}")
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            marker=dict(
                size=node_size,
                color='lightblue',
                line=dict(width=2, color='darkblue')
            ),
            text=[n for n in G.nodes()],
            textposition="top center",
            hovertext=node_text,
            hoverinfo='text',
            showlegend=False
        )
        
        # Create figure
        fig = go.Figure(data=edge_trace + [node_trace])
        
        fig.update_layout(
            title=f'Sector Rotation Network - {level.title()} Level<br>' +
                  '<sub>Arrow thickness = flow strength | Node size = total capital flow</sub>',
            showlegend=False,
            hovermode='closest',
            height=700,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        if save_path:
            fig.write_html(save_path)
        else:
            fig.show()
    
    def plot_lead_lag_matrix(self,
                            level: str,
                            max_lag_days: int = 7,
                            save_path: Optional[str] = None):
        """
        Visualize lead-lag correlation matrix
        
        Args:
            level: Hierarchy level
            max_lag_days: Maximum lag to calculate
            save_path: Path to save figure
        """
        # Calculate lead-lag correlations
        lead_lag = self.analyzer.calculate_lead_lag_correlation(
            level=level,
            max_lag_days=max_lag_days
        )
        
        if lead_lag.empty:
            print("No lead-lag correlations found")
            return
        
        # Create pivot table for heatmap (showing optimal lag for each pair)
        # Get the lag with highest absolute correlation for each pair
        idx = lead_lag.groupby(['sector_lead', 'sector_lag'])['correlation'].apply(
            lambda x: x.abs().idxmax()
        )
        
        best_lags = lead_lag.loc[idx].copy()
        
        # Create pivot showing correlation strength
        pivot_corr = best_lags.pivot(
            index='sector_lead',
            columns='sector_lag',
            values='correlation'
        )
        
        # Create pivot showing optimal lag
        pivot_lag = best_lags.pivot(
            index='sector_lead',
            columns='sector_lag',
            values='lag_days'
        )
        
        # Plot correlation heatmap
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        
        # Correlation heatmap
        sns.heatmap(
            pivot_corr,
            cmap='RdBu_r',
            center=0,
            annot=True,
            fmt='.2f',
            cbar_kws={'label': 'Correlation'},
            ax=ax1
        )
        ax1.set_title(f'Lead-Lag Correlations - {level.title()} Level', 
                     fontsize=14, fontweight='bold')
        ax1.set_xlabel('Lagging Sector', fontsize=12)
        ax1.set_ylabel('Leading Sector', fontsize=12)
        
        # Lag days heatmap
        sns.heatmap(
            pivot_lag,
            cmap='YlOrRd',
            annot=True,
            fmt='.0f',
            cbar_kws={'label': 'Optimal Lag (days)'},
            ax=ax2
        )
        ax2.set_title(f'Optimal Lag Days - {level.title()} Level', 
                     fontsize=14, fontweight='bold')
        ax2.set_xlabel('Lagging Sector', fontsize=12)
        ax2.set_ylabel('Leading Sector', fontsize=12)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=120, bbox_inches='tight')
        else:
            plt.show()
    
    def plot_sector_rankings_race(self,
                                 level: str,
                                 lookback_days: int = 90,
                                 save_path: Optional[str] = None):
        """
        Create animated bar chart race showing sector rankings over time
        
        Args:
            level: Hierarchy level
            lookback_days: Days to animate
            save_path: Path to save HTML
        """
        # Get performance data
        perf_df = self.aggregator.aggregate_sector_performance(level=level)
        
        if perf_df.empty:
            print("No performance data available")
            return
        
        # Filter to lookback period
        end_date = perf_df['date'].max()
        start_date = end_date - pd.Timedelta(days=lookback_days)
        perf_df = perf_df[perf_df['date'] >= start_date]
        
        # Calculate cumulative returns for each sector
        cumulative_data = []
        
        for sector in perf_df['sector'].unique():
            sector_data = perf_df[perf_df['sector'] == sector].copy()
            sector_data = sector_data.sort_values('date')
            sector_data['cumulative_return'] = (
                (1 + sector_data['avg_return'] / 100).cumprod() - 1
            ) * 100
            cumulative_data.append(sector_data)
        
        df_cum = pd.concat(cumulative_data)
        
        # Create animated bar chart
        fig = px.bar(
            df_cum,
            x='cumulative_return',
            y='sector',
            animation_frame='date',
            color='sector',
            orientation='h',
            range_x=[df_cum['cumulative_return'].min() - 5, 
                    df_cum['cumulative_return'].max() + 5],
            title=f'Sector Performance Race - {level.title()} Level'
        )
        
        fig.update_layout(
            xaxis_title='Cumulative Return (%)',
            yaxis_title='Sector',
            showlegend=False,
            height=max(600, len(df_cum['sector'].unique()) * 40)
        )
        
        if save_path:
            fig.write_html(save_path)
        else:
            fig.show()


if __name__ == "__main__":
    # Example usage
    from data_loader import DataLoader
    from sector_aggregator import SectorAggregator
    from rotation_analyzer import RotationAnalyzer
    
    print("Initializing visualization system...")
    
    loader = DataLoader(
        csv_directory="/tmp",
        sector_classification_path="/mnt/user-data/uploads/SYMBOLS_SECTORS_MERGED_Final.csv",
        timeframe="1d"
    )
    
    loader.load_all_coins()
    aggregator = SectorAggregator(loader)
    analyzer = RotationAnalyzer(aggregator)
    visualizer = SectorVisualizer(aggregator, analyzer)
    
    print("\nGenerating visualizations...")
    
    # Create all visualizations
    visualizer.plot_sector_heatmap(level='subcategory', lookback_days=60)
    visualizer.plot_cumulative_performance(level='subcategory', top_n=10)
    visualizer.plot_rotation_network(level='subcategory')
