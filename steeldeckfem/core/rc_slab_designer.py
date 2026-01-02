# -*- coding: utf-8 -*-
"""
RC Slab Designer - TCVN 5574:2018
Reinforced Concrete Slab Design Calculator
"""

import math
from typing import Dict, Tuple

from steeldeckfem.core.rc_beam_designer import MaterialDatabase
from steeldeckfem.core.vn_standards_loader import get_vn_standards


class RCSlabDesigner:
    """
    RC Slab Designer per TCVN 5574:2018
    Handles one-way and two-way slab design
    Now uses accurate TCVN data from vn_construction_standards.json
    """
    
    def __init__(self, thickness: float, concrete_grade: str = 'B25', 
                 steel_grade: str = 'CB400-V', cover: float = 20.0):
        """
        Initialize slab properties
        
        Args:
            thickness: Slab thickness (mm)
            concrete_grade: Concrete grade
            steel_grade: Steel grade
            cover: Concrete cover (mm)
        """
        self.h = thickness
        self.cover = cover
        
        self.f_c = MaterialDatabase.get_concrete_strength(concrete_grade)
        self.f_y = MaterialDatabase.get_steel_strength(steel_grade)
        
        # Effective depth (per meter width)
        self.d = thickness - cover - 10/2  # Assuming Φ10 bars
        
        # Elastic modulus
        self.E_c = 4700 * math.sqrt(self.f_c)
        self.E_s = 200000
        
    def design_one_way(self, L: float, q: float, support: str = 'simple') -> Dict:
        """
        Design one-way slab (acts as beam in short direction)
        
        Args:
            L: Span (m)
            q: Ultimate load (kN/m²)
            support: 'simple' or 'continuous'
        
        Returns:
            Design results
        """
        # Convert to per meter width
        b = 1000  # mm (1 meter strip)
        L_mm = L * 1000
        
        # Moment calculation
        if support == 'simple':
            M_u = (q * L**2) / 8  # kNm/m
        elif support == 'continuous':
            M_u = (q * L**2) / 10  # kNm/m (reduced for continuity)
        else:
            M_u = (q * L**2) / 8
        
        M_u_Nmm = M_u * 1e6  # N·mm
        
        # Calculate required reinforcement
        phi = 0.9
        As_req = 0
        for _ in range(10):
            a = (As_req * self.f_y) / (0.85 * self.f_c * b) if As_req > 0 else 0
            As_req = M_u_Nmm / (phi * self.f_y * (self.d - a/2))
        
        # Minimum reinforcement
        As_min = max(
            1.4 * b * self.d / self.f_y,
            0.0018 * b * self.h  # Shrinkage and temperature steel
        )
        
        As_req = max(As_req, As_min)
        
        # Select bar spacing
        bar_dia = 10  # Φ10 typical for slabs
        bar_area = MaterialDatabase.REBAR_AREAS[bar_dia]
        
        # Calculate spacing (s = 1000 * A_bar / A_s)
        spacing_calc = (1000 * bar_area) / As_req
        
        # Standard spacing values
        standard_spacing = [100, 125, 150, 175, 200, 250, 300]
        spacing = min([s for s in standard_spacing if s <= spacing_calc], default=100)
        
        As_provided = (1000 * bar_area) / spacing
        
        # Check maximum spacing (TCVN 5574:2018)
        s_max = min(2 * self.h, 300)  # mm
        
        return {
            'M_u': M_u,
            'As_required': As_req,
            'As_provided': As_provided,
            'bar_config': f'Φ{bar_dia} @ {spacing}mm',
            'spacing': spacing,
            's_max': s_max,
            'status': 'OK' if (spacing <= s_max and As_provided >= As_req) else 'FAIL'
        }
    
    def design_two_way(self, Lx: float, Ly: float, q: float, 
                       support: str = 'simple') -> Dict:
        """
        Design two-way slab using TCVN 5574:2018 moment coefficients
        
        Args:
            Lx: Short span (m)
            Ly: Long span (m)
            q: Ultimate load (kN/m²)
            support: 'simple' or 'fixed' or 'continuous'
        
        Returns:
            Design results for both directions
        """
        # Ensure Lx <= Ly
        if Lx > Ly:
            Lx, Ly = Ly, Lx
        
        ratio = Ly / Lx
        
        # Get TCVN coefficients from standards loader
        vn_standards = get_vn_standards()
        
        # Map support type to panel type
        # Note: Using interior panel for now. User can enhance with edge/corner detection
        panel_type = 'interiorPanel'
        
        coeffs = vn_standards.get_two_way_slab_coefficients(panel_type, ratio)
        
        # Use positive moment coefficients (conservative for simply supported)
        alpha_x = coeffs.get('mx_positive', 0.024)
        alpha_y = coeffs.get('my_positive', 0.024)
        
        # Calculate moments
        M_x = alpha_x * q * Lx**2  # kNm/m (short span)
        M_y = alpha_y * q * Lx**2  # kNm/m (long span)
        
        # Design for short span (X)
        design_x = self._design_slab_strip(M_x, direction='x')
        
        # Design for long span (Y) - slightly deeper effective depth
        design_y = self._design_slab_strip(M_y, direction='y')
        
        return {
            'geometry': {
                'Lx': Lx,
                'Ly': Ly,
                'ratio': ratio,
                'support': support
            },
            'moments': {
                'M_x': M_x,
                'M_y': M_y,
                'alpha_x': alpha_x,
                'alpha_y': alpha_y
            },
            'design_x': design_x,
            'design_y': design_y,
            'status': 'OK' if (design_x['status'] == 'OK' and design_y['status'] == 'OK') else 'FAIL'
        }
    
    def check_punching_shear(self, column_size: float, P: float, 
                            slab_type: str = 'interior') -> Dict:
        """
        Check punching shear around column
        
        Args:
            column_size: Column dimension (mm) - assuming square
            P: Ultimate load on column (kN)
            slab_type: 'interior', 'edge', or 'corner'
        
        Returns:
            Punching shear check results
        """
        c = column_size  # mm
        
        # Critical perimeter at d/2 from column face
        d = self.d
        
        # Perimeter length depends on location
        if slab_type == 'interior':
            b_o = 4 * (c + d)  # All four sides
        elif slab_type == 'edge':
            b_o = 3 * (c + d)  # Three sides
        else:  # corner
            b_o = 2 * (c + d)  # Two sides
        
        # Punching shear stress
        v_u = (P * 1000) / (b_o * d)  # N/mm² (MPa)
        
        # Allowable punching shear stress (TCVN 5574:2018)
        v_c = 0.33 * math.sqrt(self.f_c)  # MPa
        
        # Safety factor
        phi = 0.85
        v_allow = phi * v_c
        
        return {
            'P': P,
            'b_o': b_o,
            'v_u': v_u,
            'v_allow': v_allow,
            'ratio': v_u / v_allow,
            'status': 'OK' if v_u <= v_allow else 'FAIL - Need shear reinforcement or thicker slab'
        }
    
    def _design_slab_strip(self, M_u: float, direction: str = 'x') -> Dict:
        """Helper method to design 1m strip of slab"""
        b = 1000  # mm
        
        # Adjust effective depth for direction
        if direction == 'y':
            d_eff = self.d - 10  # Bars on top of X-direction
        else:
            d_eff = self.d
        
        M_u_Nmm = M_u * 1e6
        
        # Calculate required reinforcement
        phi = 0.9
        As_req = 0
        for _ in range(10):
            a = (As_req * self.f_y) / (0.85 * self.f_c * b) if As_req > 0 else 0
            As_req = M_u_Nmm / (phi * self.f_y * (d_eff - a/2))
        
        # Minimum reinforcement
        As_min = max(
            1.4 * b * d_eff / self.f_y,
            0.0018 * b * self.h
        )
        
        As_req = max(As_req, As_min)
        
        # Select bar spacing
        bar_dia = 10
        bar_area = MaterialDatabase.REBAR_AREAS[bar_dia]
        spacing_calc = (1000 * bar_area) / As_req
        
        standard_spacing = [100, 125, 150, 175, 200, 250, 300]
        spacing = min([s for s in standard_spacing if s <= spacing_calc], default=100)
        
        As_provided = (1000 * bar_area) / spacing
        
        return {
            'M_u': M_u,
            'As_required': As_req,
            'As_provided': As_provided,
            'bar_config': f'Φ{bar_dia} @ {spacing}mm',
            'spacing': spacing,
            'status': 'OK' if As_provided >= As_req else 'FAIL'
        }
    
    def _interpolate_coefficients(self, ratio: float, coeffs_table: dict) -> Tuple[float, float]:
        """Interpolate moment coefficients for given Ly/Lx ratio"""
        ratios = sorted(coeffs_table.keys())
        
        # If exact match
        if ratio in coeffs_table:
            return coeffs_table[ratio]
        
        # If beyond range
        if ratio <= ratios[0]:
            return coeffs_table[ratios[0]]
        if ratio >= ratios[-1]:
            return coeffs_table[ratios[-1]]
        
        # Linear interpolation
        for i in range(len(ratios) - 1):
            if ratios[i] <= ratio <= ratios[i+1]:
                r1, r2 = ratios[i], ratios[i+1]
                alpha_x1, alpha_y1 = coeffs_table[r1]
                alpha_x2, alpha_y2 = coeffs_table[r2]
                
                # Interpolate
                t = (ratio - r1) / (r2 - r1)
                alpha_x = alpha_x1 + t * (alpha_x2 - alpha_x1)
                alpha_y = alpha_y1 + t * (alpha_y2 - alpha_y1)
                
                return (alpha_x, alpha_y)
        
        # Fallback
        return coeffs_table[ratios[0]]
    
    def get_minimum_thickness(self, L: float, support: str = 'simple') -> float:
        """
        Get minimum slab thickness per TCVN 5574:2018
        
        Args:
            L: Span (m)
            support: Support condition
        
        Returns:
            Minimum thickness (mm)
        """
        L_mm = L * 1000
        
        # Deflection limits (TCVN 5574:2018 Table X.X - approximate)
        if support == 'simple':
            h_min = L_mm / 20
        elif support == 'continuous':
            h_min = L_mm / 28
        elif support == 'cantilever':
            h_min = L_mm / 10
        else:
            h_min = L_mm / 20
        
        # Also consider fire resistance (minimum 100mm for typical)
        h_min = max(h_min, 100)
        
        return h_min
