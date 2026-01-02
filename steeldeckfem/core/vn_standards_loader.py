# -*- coding: utf-8 -*-
"""
Vietnamese Construction Standards Data Loader
Loads and provides access to TCVN standard data from JSON file
"""

import json
import os
from typing import Dict, Any


class VNStandardsLoader:
    """
    Singleton class to load and cache Vietnamese construction standards data
    """
    _instance = None
    _data = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._data is None:
            self._load_data()
    
    def _load_data(self):
        """Load JSON data from file"""
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Go up two levels to get to project root
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        json_path = os.path.join(project_root, 'vn_construction_standards.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Could not find vn_construction_standards.json at {json_path}. "
                "Please ensure the file is in the project root directory."
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in vn_construction_standards.json: {str(e)}")
    
    def get_two_way_slab_coefficients(self, panel_type: str, ratio: float) -> Dict[str, float]:
        """
        Get moment coefficients for two-way slab
        
        Args:
            panel_type: 'interiorPanel', 'edgePanel_oneEdgeContinuous', 
                       'edgePanel_twoEdgesContinuous', 'cornerPanel'
            ratio: Ly/Lx ratio
        
        Returns:
            Dictionary with mx_negative, mx_positive, my_negative, my_positive
        """
        slab_data = self._data['slabDesign']['twoWaySlabMomentCoefficients']['coefficients']
        
        # Map panel type to data structure
        if 'interior' in panel_type.lower():
            coeffs = slab_data['interiorPanel']
        elif 'corner' in panel_type.lower():
            coeffs = slab_data['cornerPanel']
        elif 'edge' in panel_type.lower():
            if 'one' in panel_type.lower():
                coeffs = slab_data['edgePanel']['oneEdgeContinuous']
            else:
                coeffs = slab_data['edgePanel']['twoEdgesContinuous']
        else:
            coeffs = slab_data['interiorPanel']
        
        # Find closest ratio
        ratio_key = self._find_closest_ratio_key(ratio, coeffs)
        
        return coeffs[ratio_key]
    
    def _find_closest_ratio_key(self, ratio: float, coeffs: dict) -> str:
        """Find the closest ratio key in the coefficients dictionary"""
        # Extract ratios from keys like "Ly_Lx_1_5" -> 1.5
        available_ratios = {}
        for key in coeffs.keys():
            parts = key.split('_')
            if len(parts) >= 4:
                try:
                    ratio_val = float(parts[2] + '.' + parts[3])
                    available_ratios[ratio_val] = key
                except ValueError:
                    continue
        
        if not available_ratios:
            return list(coeffs.keys())[0]
        
        # Find closest ratio
        closest = min(available_ratios.keys(), key=lambda x: abs(x - ratio))
        return available_ratios[closest]
    
    def get_bearing_capacity_factors(self, phi_degrees: float) -> Dict[str, float]:
        """
        Get Nc, Nq, Nγ factors for given friction angle
        
        Args:
            phi_degrees: Friction angle in degrees
        
        Returns:
            Dictionary with Nc, Nq, Nγ
        """
        factors_data = self._data['geotechnicalEngineering']['bearingCapacity']['bearingCapacityFactors']
        
        # Find closest phi value
        phi_rounded = round(phi_degrees / 5) * 5  # Round to nearest 5
        phi_key = f'phi_{phi_rounded}'
        
        if phi_key in factors_data:
            return factors_data[phi_key]
        else:
            # Default to phi_30 if not found
            return factors_data.get('phi_30', {'Nc': 30.14, 'Nq': 18.40, 'Nγ': 18.08})
    
    def get_vietnamese_soil_properties(self, soil_type: str) -> Dict[str, Any]:
        """
        Get Vietnamese soil properties
        
        Args:
            soil_type: e.g., 'sét', 'cát_pha', 'cát_sỏi'
        
        Returns:
            Dictionary with phi, c, γ, qa_typical
        """
        soil_data = self._data['geotechnicalEngineering']['bearingCapacity']['vietnameseSoilTypes']
        
        return soil_data.get(soil_type, soil_data['cát_pha'])  # Default to mixed soil
    
    def get_steel_section_properties(self, section_name: str) -> Dict[str, float]:
        """
        Get Vietnamese steel section properties
        
        Args:
            section_name: e.g., 'H200x200x8x12', 'BOX200x200x6'
        
        Returns:
            Dictionary with section properties (h, b, t, A, Ix, Iy, etc.)
        """
        steel_data = self._data['steelDesign']['vietnameseSteelSections']
        
        # Try H-beams
        if section_name in steel_data['H_beams']:
            props = steel_data['H_beams'][section_name].copy()
            # Convert cm units to mm
            props['A'] = props['A_cm2'] * 100  # cm² to mm²
            props['Ix'] = props['Ix_cm4'] * 10000  # cm⁴ to mm⁴
            props['Iy'] = props['Iy_cm4'] * 10000
            props['Wx'] = props['Wx_cm3'] * 1000  # cm³ to mm³
            props['Wy'] = props['Wy_cm3'] * 1000
            props['rx'] = props['rx_cm'] * 10  # cm to mm
            props['ry'] = props['ry_cm'] * 10
            return props
        
        # Try Box sections
        if section_name in steel_data['box_sections']:
            props = steel_data['box_sections'][section_name].copy()
            props['A'] = props['A_cm2'] * 100
            props['Ix'] = props['Ix_cm4'] * 10000
            props['Iy'] = props['Iy_cm4'] * 10000
            props['Wx'] = props['Wx_cm3'] * 1000
            props['Wy'] = props['Wy_cm3'] * 1000
            props['rx'] = props['rx_cm'] * 10
            props['ry'] = props['ry_cm'] * 10
            return props
        
        raise ValueError(f"Section {section_name} not found in Vietnamese database")
    
    def get_all_h_beam_sections(self) -> list:
        """Get list of all available H-beam section names"""
        return list(self._data['steelDesign']['vietnameseSteelSections']['H_beams'].keys())
    
    def get_all_box_sections(self) -> list:
        """Get list of all available box section names"""
        return list(self._data['steelDesign']['vietnameseSteelSections']['box_sections'].keys())
    
    def get_wind_terrain_factor(self, terrain_type: str, height_m: float) -> float:
        """
        Get wind terrain exposure factor Ce
        
        Args:
            terrain_type: 'terrainA', 'terrainB', 'terrainC', 'terrainD'
            height_m: Height above ground (m)
        
        Returns:
            Ce factor
        """
        terrain_data = self._data['windLoads']['terrainFactors'][terrain_type]
        heights = terrain_data['heights']
        
        # Find closest height
        height_str = str(int(height_m)) + 'm'
        
        if height_str in heights:
            return heights[height_str]
        
        # Interpolate if exact height not found
        available_heights = sorted([int(h.replace('m', '')) for h in heights.keys()])
        
        if height_m <= available_heights[0]:
            return heights[f'{available_heights[0]}m']
        if height_m >= available_heights[-1]:
            return heights[f'{available_heights[-1]}m']
        
        # Linear interpolation
        for i in range(len(available_heights) - 1):
            h1 = available_heights[i]
            h2 = available_heights[i + 1]
            if h1 <= height_m <= h2:
                Ce1 = heights[f'{h1}m']
                Ce2 = heights[f'{h2}m']
                Ce = Ce1 + (Ce2 - Ce1) * (height_m - h1) / (h2 - h1)
                return Ce
        
        return 1.0  # Fallback
    
    def get_wind_aerodynamic_coefficient(self, element_type: str, **kwargs) -> float:
        """
        Get wind aerodynamic coefficient Cd
        
        Args:
            element_type: e.g., 'rectangular_windward', 'pitched_roof_windward'
            **kwargs: Additional parameters (e.g., slope for roofs)
        
        Returns:
            Cd coefficient
        """
        aero_data = self._data['windLoads']['aerodynamicCoefficients']['buildings']
        
        if element_type in aero_data:
            if isinstance(aero_data[element_type], dict):
                return aero_data[element_type].get('Cd', 0.8)
            else:
                return aero_data[element_type]
        
        return 0.8  # Default windward
    
    def get_crack_width_limit(self, environment: str) -> float:
        """
        Get crack width limit for given exposure environment
        
        Args:
            environment: 'normalEnvironment', 'humidEnvironment', etc.
        
        Returns:
            Crack width limit in mm
        """
        crack_data = self._data['slabDesign']['crackWidthLimits']['limits']
        
        return crack_data.get(environment, crack_data['normalEnvironment'])['value_mm']
    
    def get_reinforcement_development_length(self, phi_mm: int, concrete_grade: str = 'C25') -> float:
        """
        Get basic development length for rebar
        
        Args:
            phi_mm: Rebar diameter (mm)
            concrete_grade: Concrete grade
        
        Returns:
            Development length in mm
        """
        dev_data = self._data['slabDesign']['reinforcementDevelopment']['commonDiameters']
        
        phi_key = f'φ{phi_mm}'
        if phi_key in dev_data:
            return dev_data[phi_key]['lb_C25_mm']
        
        # Calculate if not in table
        # Simplified: lb ≈ 36 × φ for C25
        return 36 * phi_mm


# Global singleton instance
_vn_standards = None

def get_vn_standards() -> VNStandardsLoader:
    """Get the global VN standards loader instance"""
    global _vn_standards
    if _vn_standards is None:
        _vn_standards = VNStandardsLoader()
    return _vn_standards
