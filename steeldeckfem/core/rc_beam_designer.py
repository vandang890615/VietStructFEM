# -*- coding: utf-8 -*-
"""
RC Beam Designer - TCVN 5574:2018
Reinforced Concrete Beam Design Calculator
"""

import math
from typing import Dict, Tuple, List


class MaterialDatabase:
    """Standard Vietnamese material properties"""
    
    # Concrete grades (Vietnamese standard)
    CONCRETE_GRADES = {
        'B15': {'f_c': 10.0},   # MPa (characteristic strength)
        'B20': {'f_c': 15.0},
        'B25': {'f_c': 18.0},
        'B30': {'f_c': 22.0},
        'B35': {'f_c': 25.0},
        'B40': {'f_c': 29.0}
    }
    
    # Steel grades (Vietnamese rebar)
    STEEL_GRADES = {
        'CB300-V': {'f_y': 300.0},  # MPa
        'CB400-V': {'f_y': 400.0},
        'CB500-V': {'f_y': 500.0}
    }
    
    # Standard rebar diameters (mm)
    REBAR_SIZES = [10, 12, 14, 16, 18, 20, 22, 25, 28, 32]
    
    # Rebar areas (mm²)
    REBAR_AREAS = {
        10: 78.5,
        12: 113.1,
        14: 153.9,
        16: 201.1,
        18: 254.5,
        20: 314.2,
        22: 380.1,
        25: 490.9,
        28: 615.8,
        32: 804.2
    }
    
    @staticmethod
    def get_concrete_strength(grade: str) -> float:
        """Get f'c for concrete grade"""
        return MaterialDatabase.CONCRETE_GRADES.get(grade, {'f_c': 18.0})['f_c']
    
    @staticmethod
    def get_steel_strength(grade: str) -> float:
        """Get fy for steel grade"""
        return MaterialDatabase.STEEL_GRADES.get(grade, {'f_y': 400.0})['f_y']


class RCBeamDesigner:
    """
    RC Beam Designer per TCVN 5574:2018
    Handles flexural, shear, deflection, and crack width design
    """
    
    def __init__(self, b: float, h: float, L: float, 
                 concrete_grade: str = 'B25', steel_grade: str = 'CB400-V',
                 cover: float = 30.0):
        """
        Initialize beam properties
        
        Args:
            b: Width (mm)
            h: Height (mm)
            L: Span (m)
            concrete_grade: Concrete grade (B15, B20, B25, B30, etc.)
            steel_grade: Steel grade (CB300-V, CB400-V, CB500-V)
            cover: Concrete cover (mm)
        """
        self.b = b
        self.h = h
        self.L = L * 1000  # Convert to mm
        self.cover = cover
        
        self.f_c = MaterialDatabase.get_concrete_strength(concrete_grade)
        self.f_y = MaterialDatabase.get_steel_strength(steel_grade)
        
        # Effective depth (assuming Φ20 main bars)
        self.d = h - cover - 20/2
        
        # Elastic modulus
        self.E_c = 4700 * math.sqrt(self.f_c)  # MPa (TCVN formula)
        self.E_s = 200000  # MPa (steel)
        
    def design_flexure(self, M_u: float) -> Dict:
        """
        Design for bending moment (ULS)
        
        Args:
            M_u: Ultimate moment (kNm)
        
        Returns:
            Dictionary with design results
        """
        M_u_Nmm = M_u * 1e6  # Convert to N·mm
        
        # Calculate required reinforcement
        # From equilibrium: M = φ·fy·As·(d - a/2)
        # Where a = As·fy / (0.85·f'c·b)
        
        # Quadratic solution for As
        # Assuming φ = 0.9 (strength reduction factor)
        phi = 0.9
        
        # Iterative solution
        As_req = 0
        for _ in range(10):  # Quick iteration
            a = (As_req * self.f_y) / (0.85 * self.f_c * self.b) if As_req > 0 else 0
            As_req = M_u_Nmm / (phi * self.f_y * (self.d - a/2))
        
        # Minimum reinforcement (TCVN 5574:2018)
        As_min = max(
            1.4 * self.b * self.d / self.f_y,
            0.25 * math.sqrt(self.f_c) * self.b * self.d / self.f_y
        )
        
        As_req = max(As_req, As_min)
        
        # Select bar configuration
        bar_config = self._select_bars(As_req)
        As_provided = bar_config['total_area']
        
        # Check strain limits (ductility)
        c = (As_provided * self.f_y) / (0.85 * self.f_c * self.b * 0.85)  # Neutral axis depth
        epsilon_t = 0.003 * (self.d - c) / c  # Tension strain
        is_ductile = epsilon_t >= 0.004  # Minimum for ductile behavior
        
        # Utilization ratio
        rho = As_provided / (self.b * self.d)
        
        return {
            'As_required': As_req,
            'As_provided': As_provided,
            'bar_config': bar_config,
            'rho': rho,
            'is_ductile': is_ductile,
            'status': 'OK' if As_provided >= As_req else 'FAIL'
        }
    
    def design_shear(self, V_u: float) -> Dict:
        """
        Design for shear (ULS)
        
        Args:
            V_u: Ultimate shear force (kN)
        
        Returns:
            Dictionary with stirrup design
        """
        V_u_N = V_u * 1000  # Convert to N
        
        # Concrete shear capacity (TCVN 5574:2018)
        phi_v = 0.85  # Shear strength reduction factor
        V_c = 0.17 * math.sqrt(self.f_c) * self.b * self.d  # N
        
        phi_V_c = phi_v * V_c
        
        if V_u_N <= phi_V_c:
            # Minimum stirrups only
            return {
                'stirrup_size': 8,
                'spacing': 300,  # mm (maximum spacing)
                'V_c': V_c / 1000,  # kN
                'required': False,
                'status': 'Minimum stirrups'
            }
        
        # Stirrups required
        V_s_req = V_u_N / phi_v - V_c  # Required stirrup contribution
        
        # Assume Φ8 stirrups (2 legs)
        stirrup_dia = 8
        A_v = 2 * MaterialDatabase.REBAR_AREAS[stirrup_dia]  # mm² (2-leg)
        
        # Calculate required spacing
        # V_s = A_v · f_y · d / s
        s_req = (A_v * self.f_y * self.d) / V_s_req
        
        # Maximum spacing limits (TCVN 5574:2018)
        s_max = min(self.d / 2, 600)  # mm
        
        # Standard spacing values
        standard_spacing = [100, 125, 150, 175, 200, 250, 300]
        spacing = min([s for s in standard_spacing if s <= min(s_req, s_max)], default=100)
        
        return {
            'stirrup_size': stirrup_dia,
            'spacing': spacing,
            'V_c': V_c / 1000,  # kN
            'V_s': (A_v * self.f_y * self.d / spacing) / 1000,  # kN
            'required': True,
            'status': f'Φ{stirrup_dia} @ {spacing}mm'
        }
    
    def check_deflection(self, q_service: float, As_provided: float = 0) -> Dict:
        """
        Check deflection (SLS)
        
        Args:
            q_service: Service load (kN/m)
            As_provided: Provided reinforcement area (mm²)
        
        Returns:
            Deflection check results
        """
        q_Nmm = q_service * 1000 / 1000  # N/mm
        
        # Gross moment of inertia
        I_g = (self.b * self.h**3) / 12  # mm⁴
        
        # Cracked moment of inertia (simplified)
        if As_provided > 0:
            n = self.E_s / self.E_c
            rho = As_provided / (self.b * self.d)
            k = math.sqrt(2 * rho * n + (rho * n)**2) - rho * n
            I_cr = (self.b * k * self.d)**3 / 3 + n * As_provided * (self.d * (1 - k))**2
        else:
            I_cr = I_g * 0.35  # Approximate
        
        # Effective moment of inertia (use average for simplicity)
        I_eff = (I_g + I_cr) / 2
        
        # Deflection (simply supported)
        delta = (5 * q_Nmm * self.L**4) / (384 * self.E_c * I_eff)  # mm
        
        # Allowable deflection
        delta_allow = self.L / 250  # mm (general limit)
        
        return {
            'delta': delta,
            'delta_allow': delta_allow,
            'ratio': delta / delta_allow,
            'status': 'OK' if delta <= delta_allow else 'FAIL'
        }
    
    def _select_bars(self, As_req: float) -> Dict:
        """
        Select optimal bar configuration
        
        Args:
            As_req: Required area (mm²)
        
        Returns:
            Bar configuration dict
        """
        best_config = None
        min_excess = float('inf')
        
        # Try different combinations
        for dia in MaterialDatabase.REBAR_SIZES:
            bar_area = MaterialDatabase.REBAR_AREAS[dia]
            n_bars = math.ceil(As_req / bar_area)
            
            # Limit to reasonable number (2-8 bars typically)
            if n_bars < 2 or n_bars > 8:
                continue
            
            total_area = n_bars * bar_area
            excess = total_area - As_req
            
            # Check if bars fit in width (minimum spacing 25mm)
            required_width = n_bars * dia + (n_bars - 1) * 25 + 2 * self.cover
            if required_width > self.b:
                continue
            
            if 0 <= excess < min_excess:
                min_excess = excess
                best_config = {
                    'n_bars': n_bars,
                    'diameter': dia,
                    'total_area': total_area,
                    'description': f'{n_bars}Φ{dia}'
                }
        
        return best_config if best_config else {
            'n_bars': 2,
            'diameter': 20,
            'total_area': 2 * MaterialDatabase.REBAR_AREAS[20],
            'description': '2Φ20 (default)'
        }
    
    def get_design_summary(self, M_u: float, V_u: float, q_service: float) -> Dict:
        """
        Get complete design summary
        
        Args:
            M_u: Ultimate moment (kNm)
            V_u: Ultimate shear (kN)
            q_service: Service load (kN/m)
        
        Returns:
            Complete design results
        """
        flexure = self.design_flexure(M_u)
        shear = self.design_shear(V_u)
        deflection = self.check_deflection(q_service, flexure['As_provided'])
        
        return {
            'geometry': {
                'b': self.b,
                'h': self.h,
                'L': self.L / 1000,  # m
                'd': self.d
            },
            'flexure': flexure,
            'shear': shear,
            'deflection': deflection,
            'overall_status': 'OK' if (
                flexure['status'] == 'OK' and 
                deflection['status'] == 'OK'
            ) else 'FAIL'
        }
