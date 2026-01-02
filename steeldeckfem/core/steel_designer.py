# -*- coding: utf-8 -*-
"""
Steel Member Designer - TCVN 5575:2024
I-Beam and Box Column Design
Now uses Vietnamese steel section database from vn_construction_standards.json
"""

import math
from typing import Dict

from steeldeckfem.core.vn_standards_loader import get_vn_standards


class SteelSectionDatabase:
    """
    Steel section properties database
    Now loads from vn_construction_standards.json
    """
    
    @staticmethod
    def get_all_h_beams():
        """Get all available H-beam section names"""
        vn_standards = get_vn_standards()
        return vn_standards.get_all_h_beam_sections()
    
    @staticmethod
    def get_all_box_sections():
        """Get all available box section names"""
        vn_standards = get_vn_standards()
        return vn_standards.get_all_box_sections()
    
    # Sample I-Beams (for backward compatibility - now loads from JSON)
    I_BEAMS = None  # Loaded dynamically
    BOX_SECTIONS = None  # Loaded dynamically
    
    # Steel grades (Vietnamese standard)
    STEEL_GRADES = {
        'SS400': {'Fy': 235, 'Fu': 400},  # MPa
        'SM490': {'Fy': 315, 'Fu': 490},
        'SM570': {'Fy': 450, 'Fu': 570},
    }


class SteelIBeamDesigner:
    """
    Steel I-Beam Designer per TCVN 5575:2024
    Dầm thép chữ I
    """
    
    def __init__(self, section_name: str, steel_grade: str = 'SS400'):
        """
        Initialize steel beam using Vietnamese section database
        
        Args:
            section_name: Section name from database (e.g., 'H200x200x8x12')
            steel_grade: Steel grade
        """
        # Load from Vietnamese standards database
        vn_standards = get_vn_standards()
        
        try:
            section = vn_standards.get_steel_section_properties(section_name)
        except ValueError:
            raise ValueError(f"Section {section_name} not found in Vietnamese database. "
                           f"Available sections: {', '.join(SteelSectionDatabase.get_all_h_beams())}")
        
        self.section_name = section_name
        self.h = section['h_mm']
        self.b = section['b_mm']
        self.t_w = section['tw_mm']
        self.t_f = section['tf_mm']
        self.A = section['A']
        self.Ix = section['Ix']
        self.Iy = section['Iy']
        self.Wx = section['Wx']
        self.Wy = section['Wy']
        self.rx = section['rx']
        self.ry = section['ry']
        
        # Steel properties
        steel = SteelSectionDatabase.STEEL_GRADES.get(steel_grade, SteelSectionDatabase.STEEL_GRADES['SS400'])
        self.Fy = steel['Fy']
        self.Fu = steel['Fu']
        
        self.E = 200000  # MPa (Young's modulus)
        
    def check_bending(self, M_x: float, M_y: float = 0) -> Dict:
        """
        Check bending capacity
        
        Args:
            M_x: Moment about strong axis (kNm)
            M_y: Moment about weak axis (kNm)
        
        Returns:
            Bending check results
        """
        # Nominal moment capacity
        M_nx = self.Fy * self.Wx / 1e6  # kNm (Wx in mm³)
        M_ny = self.Fy * self.Wy / 1e6  # kNm
        
        # Design strength (φ = 0.9)
        phi = 0.9
        phi_M_nx = phi * M_nx
        phi_M_ny = phi * M_ny
        
        # Unity check
        ratio = (M_x / phi_M_nx) + (M_y / phi_M_ny) if M_y > 0 else (M_x / phi_M_nx)
        
        return {
            'M_nx': M_nx,
            'M_ny': M_ny,
            'phi_M_nx': phi_M_nx,
            'phi_M_ny': phi_M_ny,
            'M_x': M_x,
            'M_y': M_y,
            'ratio': ratio,
            'status': 'OK' if ratio <= 1.0 else 'FAIL'
        }
    
    def check_shear(self, V: float) -> Dict:
        """
        Check shear capacity
        
        Args:
            V: Shear force (kN)
        
        Returns:
            Shear check results
        """
        # Web shear capacity
        d = self.h - 2 * self.t_f  # Web depth
        A_w = d * self.t_w  # Web area
        
        # Nominal shear strength
        V_n = 0.6 * self.Fy * A_w / 1000  # kN
        
        # Design strength (φ = 0.9)
        phi = 0.9
        phi_V_n = phi * V_n
        
        ratio = V / phi_V_n
        
        return {
            'V_n': V_n,
            'phi_V_n': phi_V_n,
            'V': V,
            'ratio': ratio,
            'status': 'OK' if ratio <= 1.0 else 'FAIL'
        }
    
    def check_deflection(self, L: float, q: float) -> Dict:
        """
        Check deflection
        
        Args:
            L: Span (m)
            q: Service load (kN/m)
        
        Returns:
            Deflection check results
        """
        L_mm = L * 1000
        q_Nmm = q * 1000 / 1000  # N/mm
        
        # Deflection (simply supported)
        delta = (5 * q_Nmm * L_mm**4) / (384 * self.E * self.Ix)  # mm
        
        # Limit
        delta_allow = L_mm / 360  # L/360 (typical for beams)
        
        return {
            'delta': delta,
            'delta_allow': delta_allow,
            'ratio': delta / delta_allow,
            'status': 'OK' if delta <= delta_allow else 'FAIL'
        }


class SteelBoxColumnDesigner:
    """
    Steel Box Column Designer per TCVN 5575:2024
    Cột thép hộp
    """
    
    def __init__(self, section_name: str, steel_grade: str = 'SS400', L: float = 4.0, K: float = 1.0):
        """
        Initialize steel column using Vietnamese section database
        
        Args:
            section_name: Section name from database (e.g., 'BOX200x200x6')
            steel_grade: Steel grade
            L: Unbraced length (m)
            K: Effective length factor
        """
        # Load from Vietnamese standards database
        vn_standards = get_vn_standards()
        
        try:
            section = vn_standards.get_steel_section_properties(section_name)
        except ValueError:
            raise ValueError(f"Section {section_name} not found in Vietnamese database. "
                           f"Available sections: {', '.join(SteelSectionDatabase.get_all_box_sections())}")
        
        self.section_name = section_name
        self.h = section['h_mm']
        self.b = section['b_mm']
        self.t = section['t_mm']
        self.A = section['A']
        self.Ix = section['Ix']
        self.Iy = section['Iy']
        self.Wx = section['Wx']
        self.Wy = section['Wy']
        self.rx = section['rx']
        self.ry = section['ry']
        
        self.L = L * 1000  # mm
        self.K = K
        
        # Steel properties
        steel = SteelSectionDatabase.STEEL_GRADES.get(steel_grade, SteelSectionDatabase.STEEL_GRADES['SS400'])
        self.Fy = steel['Fy']
        self.Fu = steel['Fu']
        
        self.E = 200000  # MPa
        
    def check_axial_compression(self, P: float) -> Dict:
        """
        Check axial compression capacity
        
        Args:
            P: Axial load (kN)
        
        Returns:
            Compression check results
        """
        # Slenderness ratio
        r = min(self.rx, self.ry)
        lambda_r = (self.K * self.L) / r
        
        # Critical stress (Euler)
        lambda_c = math.sqrt((2 * math.pi**2 * self.E) / self.Fy)
        
        if lambda_r <= lambda_c:
            # Inelastic buckling
            F_cr = self.Fy * (1 - 0.5 * (lambda_r / lambda_c)**2)
        else:
            # Elastic buckling
            F_cr = (math.pi**2 * self.E) / lambda_r**2
        
        # Nominal axial strength
        P_n = F_cr * self.A / 1000  # kN
        
        # Design strength (φ = 0.9)
        phi = 0.9
        phi_P_n = phi * P_n
        
        ratio = P / phi_P_n
        
        return {
            'lambda': lambda_r,
            'F_cr': F_cr,
            'P_n': P_n,
            'phi_P_n': phi_P_n,
            'P': P,
            'ratio': ratio,
            'status': 'OK' if ratio <= 1.0 else 'FAIL'
        }
    
    def check_combined_loading(self, P: float, M_x: float, M_y: float = 0) -> Dict:
        """
        Check P-M interaction
        
        Args:
            P: Axial load (kN)
            M_x: Moment about strong axis (kNm)
            M_y: Moment about weak axis (kNm)
        
        Returns:
            Interaction check results
        """
        # Compression capacity
        comp_result = self.check_axial_compression(P)
        phi_P_n = comp_result['phi_P_n']
        
        # Moment capacity
        M_nx = self.Fy * self.Wx / 1e6  # kNm
        M_ny = self.Fy * self.Wy / 1e6  # kNm
        
        phi = 0.9
        phi_M_nx = phi * M_nx
        phi_M_ny = phi * M_ny
        
        # Interaction equation
        P_ratio = P / phi_P_n
        
        if P_ratio >= 0.2:
            # Full interaction
            ratio = P_ratio + (8/9) * ((M_x / phi_M_nx) + (M_y / phi_M_ny))
        else:
            # Simplified interaction
            ratio = (P_ratio / 2) + ((M_x / phi_M_nx) + (M_y / phi_M_ny))
        
        return {
            'phi_P_n': phi_P_n,
            'phi_M_nx': phi_M_nx,
            'phi_M_ny': phi_M_ny,
            'P': P,
            'M_x': M_x,
            'M_y': M_y,
            'ratio': ratio,
            'status': 'OK' if ratio <= 1.0 else 'FAIL'
        }
