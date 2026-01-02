# -*- coding: utf-8 -*-
"""
Data Models for VietStruct FEM
Common data structures used across modules
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List


@dataclass
class Section:
    """Steel section properties"""
    name: str
    h: float  # Height (mm or cm depending on usage)
    b: float  # Width (mm or cm)
    tf: float = 0.0  # Flange thickness
    tw: float = 0.0  # Web thickness
    area: float = 0.0  # Cross-sectional area (cm²)
    ix: float = 0.0  # Moment of inertia about x-axis (cm⁴)  
    iy: float = 0.0  # Moment of inertia about y-axis (cm⁴)
    wx: float = 0.0  # Section modulus about x-axis (cm³)
    wy: float = 0.0  # Section modulus about y-axis (cm³)
    rx: float = 0.0  # Radius of gyration about x-axis (cm)
    ry: float = 0.0  # Radius of gyration about y-axis (cm)
    weight: float = 0.0  # Weight per unit length (kg/m)


@dataclass
class Material:
    """Material properties"""
    name: str = "Steel Grade 50"
    E: float = 200000  # Young's modulus (MPa)
    G: float = 77000  # Shear modulus (MPa)
    fy: float = 350  # Yield strength (MPa)
    fu: float = 490  # Ultimate strength (MPa)
    density: float = 7850  # Density (kg/m³)
    nu: float = 0.3  # Poisson's ratio


@dataclass
class GeometryParams:
    """Geometry parameters for industrial buildings"""
    span: float = 0.0  # Span length (m)
    length: float = 0.0  # Building length (m)
    height_eave: float = 0.0  # Eave height (m)
    roof_slope: float = 0.0  # Roof slope (degrees)
    purlin_spacing: float = 0.0  # Purlin spacing (m)
    frame_spacing: float = 0.0  # Frame spacing (m)


@dataclass
class WindParams:
    """Wind load parameters per TCVN 2737"""
    zone: str = "I"  # Wind zone
    Wo: float = 95  # Basic wind pressure (kg/m²)
    terrain_category: str = "B"  # A, B, C, D
    height: float = 10.0  # Reference height (m)
    k_factor: float = 1.0  # Terrain factor
    beta_factor: float = 1.0  # Dynamic factor


@dataclass
class PurlinParams:
    """Purlin design parameters"""
    profile_name: str = "Z15015"  # Purlin profile
    span: float = 0.0  # Span between frames (m)
    spacing: float = 0.0  # Purlin spacing (m)
    roof_slope: float = 0.0  # Roof slope (degrees)
    dead_load: float = 0.0  # Dead load (kg/m²)
    live_load: float = 0.0  # Live load (kg/m²)


@dataclass
class LoadCombination:
    """Load combination factor"""
    name: str = "1.2D + 1.6L"
    dead_factor: float = 1.2
    live_factor: float = 1.6
    wind_factor: float = 0.0
    seismic_factor: float = 0.0


@dataclass
class CalculationInput:
    """Complete calculation input for industrial building design"""
    geometry: GeometryParams = field(default_factory=GeometryParams)
    wind: WindParams = field(default_factory=WindParams)
    purlin: PurlinParams = field(default_factory=PurlinParams)
    material: Material = field(default_factory=Material)
    load_combination: LoadCombination = field(default_factory=LoadCombination)
    
    # Additional loads
    dead_load_roof: float = 25.0  # kg/m² (roofing + insulation)
    live_load_roof: float = 30.0  # kg/m² (maintenance)
    snow_load: float = 0.0  # kg/m²
    crane_load: float = 0.0  # kg (if applicable)


@dataclass  
class DesignResult:
    """Generic design result"""
    status: str = "OK"  # OK, WARNING, FAILED
    unity_check: float = 0.0  # Utilization ratio (should be ≤ 1.0)
    capacity: float = 0.0  # Member capacity
    demand: float = 0.0  # Load demand
    details: Dict = field(default_factory=dict)
    html_report: str = ""


__all__ = [
    'Section', 'Material', 'GeometryParams', 'WindParams', 'PurlinParams',
    'LoadCombination', 'CalculationInput', 'DesignResult'
]
