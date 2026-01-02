# -*- coding: utf-8 -*-
"""
VietStruct FEM - Core Package
Steel structure analysis for Vietnamese engineers
"""

# Helpers
from .helpers import remove_diacritics, format_number

# FEM Analysis
from .fem_analyzer import FloorSystemFEMAnalyzer

# Wind zones
from .wind_zones import WIND_ZONES, CITY_WIND_ZONES, get_wind_pressure, get_all_locations

# Floor system calculators
from .complete_floor_system import CompleteFloorSystemCalculator, FloorSystemLayout, ColumnSpec, BeamSpec
from .floor_deck import SteelDeckCalculator, DeckDesignResult, CompositeBeamResult, FloorLoadDistributor

# Engineering (Industrial buildings - purlin, portal frames)
from .engineering import PurlinCalculator, WindLoadCalculator, FrameLoadCalculator, MemberChecker

# Stability analysis
from .stability import StabilityCalculator, StabilityResult, LateralTorsionalBuckling

# Plotly visualization
from .plotly_charts import StructuralDiagramCreator

__all__ = [
    # Helpers
    'remove_diacritics', 'format_number',
    # FEM
    'FloorSystemFEMAnalyzer',
    # Wind
    'WIND_ZONES', 'CITY_WIND_ZONES', 'get_wind_pressure', 'get_all_locations',
    # Floor system
    'CompleteFloorSystemCalculator', 'FloorSystemLayout', 'ColumnSpec', 'BeamSpec',
    'SteelDeckCalculator', 'DeckDesignResult', 'CompositeBeamResult', 'FloorLoadDistributor',
    # Industrial buildings
    'PurlinCalculator', 'WindLoadCalculator', 'FrameLoadCalculator', 'MemberChecker',
    # Stability
    'StabilityCalculator', 'StabilityResult', 'LateralTorsionalBuckling',
    # Visualization
    'StructuralDiagramCreator',
]

