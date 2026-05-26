"""
Crypto Sector Rotation Analyzer

A comprehensive toolkit for analyzing sector rotation patterns in cryptocurrency markets.
"""

__version__ = "1.0.0"
__author__ = "Human & Claude"

from .data_loader import DataLoader
from .sector_aggregator import SectorAggregator
from .rotation_analyzer import RotationAnalyzer
from .visualizer import SectorVisualizer
from .dashboard import SectorRotationDashboard

__all__ = [
    'DataLoader',
    'SectorAggregator',
    'RotationAnalyzer',
    'SectorVisualizer',
    'SectorRotationDashboard'
]
