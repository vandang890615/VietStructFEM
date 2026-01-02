"""
Steel Deck FEM Calculator
Open source finite element analysis for steel deck floor systems
"""

__version__ = '1.0.0'
__author__ = 'Steel Deck FEM Contributors'
__license__ = 'MIT'

from steeldeckfem.core.fem_analyzer import FloorSystemFEMAnalyzer
from steeldeckfem.core.wind_zones import get_wind_pressure, WIND_ZONES, CITY_WIND_ZONES

__all__ = [
    'FloorSystemFEMAnalyzer',
    'get_wind_pressure',
    'WIND_ZONES',
    'CITY_WIND_ZONES'
]
