# -*- coding: utf-8 -*-
"""
Foundation Designer - TCVN 9362:2012 & TCVN 10304:2014
Isolated Footing and Pile Foundation Design
Now uses accurate TCVN data from vn_construction_standards.json
"""

import math
from typing import Dict, Tuple

from steeldeckfem.core.vn_standards_loader import get_vn_standards


class SoilDatabase:
    """
    Standard soil properties
    TODO: User to provide Vietnamese soil classification database
    """
    
    # Default soil parameters (conservative estimates)
    SOIL_TYPES = {
        'Clay - Soft': {'phi': 0, 'c': 25, 'gamma': 17, 'qult_method': 'cohesive'},
        'Clay - Medium': {'phi': 0, 'c': 50, 'gamma': 18, 'qult_method': 'cohesive'},
        'Clay - Stiff': {'phi': 0, 'c': 100, 'gamma': 19, 'qult_method': 'cohesive'},
        'Sand - Loose': {'phi': 28, 'c': 0, 'gamma': 16, 'qult_method': 'cohesionless'},
        'Sand - Medium': {'phi': 32, 'c': 0, 'gamma': 17, 'qult_method': 'cohesionless'},
        'Sand - Dense': {'phi': 38, 'c': 0, 'gamma': 19, 'qult_method': 'cohesionless'},
        'Mixed Soil': {'phi': 25, 'c': 20, 'gamma': 18, 'qult_method': 'mixed'}
    }


class IsolatedFootingDesigner:
    """
    Isolated (Spread) Footing Designer per TCVN 9362:2012
    Móng Đơn - Vietnamese Standard
    """
    
    def __init__(self, P: float, M: float, soil_type: str, depth: float = 1.5):
        """
        Initialize footing
        
        Args:
            P: Axial load (kN)
            M: Moment (kNm)
            soil_type: Soil type from database
            depth: Depth of footing base from ground level (m)
        """
        self.P = P
        self.M = M
        self.D = depth
        
        # Get soil properties
        soil = SoilDatabase.SOIL_TYPES.get(soil_type, SoilDatabase.SOIL_TYPES['Mixed Soil'])
        self.phi = soil['phi']  # degrees
        self.c = soil['c']      # kPa
        self.gamma = soil['gamma']  # kN/m3
        
        # Concrete properties (default B20)
        self.f_c = 15.0  # MPa
        self.f_y = 400.0  # MPa (CB400-V)
        
    def design_footing_size(self, factor_of_safety: float = 3.0) -> Dict:
        """
        Determine required footing size based on bearing capacity
        
        Args:
            factor_of_safety: FS for bearing capacity
        
        Returns:
            Design results including footing dimensions
        """
        # Ultimate bearing capacity (Terzaghi formula)
        q_ult = self._calculate_bearing_capacity()
        
        # Allowable bearing capacity
        q_allow = q_ult / factor_of_safety
        
        # Required area (considering safety factor for design)
        # Add 20% for self-weight
        P_total = self.P * 1.2
        A_req = P_total / q_allow
        
        # Assume square footing
        B = math.sqrt(A_req)
        
        # Round up to nearest 0.1m
        B = math.ceil(B * 10) / 10
        
        # Check bearing pressure with actual size
        q_actual = P_total / (B * B)
        
        return {
            'q_ult': q_ult,
            'q_allow': q_allow,
            'B': B,
            'L': B,  # Square footing
            'A': B * B,
            'q_actual': q_actual,
            'FS': q_ult / q_actual,
            'status': 'OK' if q_actual <= q_allow else 'FAIL'
        }
    
    def check_punching_shear(self, B: float, column_size: float, thickness: float) -> Dict:
        """
        Check punching shear per TCVN 5574:2018
        
        Args:
            B: Footing width (m)
            column_size: Column dimension (mm)
            thickness: Footing thickness (mm)
        
        Returns:
            Punching shear check results
        """
        c = column_size  # mm
        h = thickness
        d = h - 50  # Effective depth (50mm cover)
        
        # Critical perimeter at d/2 from column face
        b_o = 4 * (c + d)  # mm
        
        # Punching force (total load minus area within critical section)
        A_punch = ((c + d) / 1000)**2  # m²
        P_punch = self.P * (1 - A_punch / (B * B))  # kN
        
        # Punching shear stress
        v_u = (P_punch * 1000) / (b_o * d)  # MPa
        
        # Allowable punching shear
        v_c = 0.33 * math.sqrt(self.f_c)  # MPa
        
        return {
            'P_punch': P_punch,
            'v_u': v_u,
            'v_c': v_c,
            'ratio': v_u / v_c,
            'status': 'OK' if v_u <= v_c else 'FAIL - Increase thickness'
        }
    
    def design_reinforcement(self, B: float, column_size: float) -> Dict:
        """
        Design flexural reinforcement
        
        Args:
            B: Footing width (m)
            column_size: Column dimension (mm)
        
        Returns:
            Reinforcement design results
        """
        # Critical section at face of column
        c = column_size / 1000  # m
        a = (B - c) / 2  # Cantilever length
        
        # Bearing pressure (simplified - uniform)
        q = self.P / (B * B)  # kN/m²
        
        # Moment per meter width
        M = q * a**2 / 2  # kNm/m
        
        # Required reinforcement (simplified)
        # Assume d = h - 50mm, use typical h = B/4 (rough rule)
        h = max(B / 4 * 1000, 300)  # mm, minimum 300mm
        d = h - 50  # mm
        
        # As = M / (0.9 * fy * 0.9d) - simplified
        M_Nmm = M * 1e6
        As_req = M_Nmm / (0.9 * self.f_y * 0.9 * d)  # mm²/m
        
        # Minimum reinforcement
        As_min = 0.0018 * 1000 * h  # mm²/m
        As_req = max(As_req, As_min)
        
        # Select bar spacing (Φ16 typical)
        bar_dia = 16
        bar_area = 201  # mm² for Φ16
        spacing = (1000 * bar_area) / As_req
        
        # Standard spacing
        standard_spacing = [100, 125, 150, 175, 200, 250, 300]
        spacing = min([s for s in standard_spacing if s <= spacing], default=100)
        As_provided = (1000 * bar_area) / spacing
        
        return {
            'h_recommended': h,
            'd': d,
            'M': M,
            'As_required': As_req,
            'As_provided': As_provided,
            'bar_config': f'Φ{bar_dia} @ {spacing}mm both ways',
            'status': 'OK' if As_provided >= As_req else 'FAIL'
        }
    
    def _calculate_bearing_capacity(self) -> float:
        """
        Calculate ultimate bearing capacity using Terzaghi equation with TCVN factors
        
        Returns:
            q_ult in kPa
        """
        # Get TCVN bearing capacity factors
        vn_standards = get_vn_standards()
        factors = vn_standards.get_bearing_capacity_factors(self.phi)
        
        Nc = factors['Nc']
        Nq = factors['Nq']
        Ng = factors['Nγ']
        
        # Effective width (assuming square footing, this is approximate)
        B_eff = 1.0  # Will be refined in actual design
        
        # Ultimate bearing capacity (Terzaghi formula)
        q_ult = self.c * Nc + self.gamma * self.D * Nq + 0.5 * self.gamma * B_eff * Ng
        
        return q_ult


class PileFoundationDesigner:
    """
    Pile Foundation Designer per TCVN 10304:2014
    Móng Cọc - Vietnamese Standard
    """
    
    def __init__(self, pile_diameter: float, pile_length: float, soil_layers: list):
        """
        Initialize pile foundation
        
        Args:
            pile_diameter: Pile diameter (mm)
            pile_length: Pile length (m)
            soil_layers: List of {depth, soil_type, N_SPT} dicts
                         TODO: User to provide proper soil profile format
        """
        self.D = pile_diameter  # mm
        self.L = pile_length    # m
        self.soil_layers = soil_layers
        
    def calculate_single_pile_capacity(self) -> Dict:
        """
        Calculate single pile capacity using simplified method
        
        Returns:
            Pile capacity results
        """
        # Simplified α-method for cohesive, β-method for cohesionless
        # TODO: Implement full TCVN 10304:2014 method when user provides soil data
        
        # For now, use very simplified approach
        # Assume average soil strength
        if not self.soil_layers:
            # Default conservative estimate
            q_base = 100  # kPa (very conservative)
            f_shaft = 20  # kPa
        else:
            # Use first layer as approximation
            layer = self.soil_layers[0]
            soil_type = layer.get('soil_type', 'Mixed Soil')
            
            if 'Clay' in soil_type:
                q_base = 200  # kPa
                f_shaft = 30
            else:
                q_base = 400  # kPa
                f_shaft = 50
        
        # Pile area
        A_base = math.pi * (self.D / 1000)**2 / 4  # m²
        
        # Pile perimeter
        P = math.pi * (self.D / 1000)  # m
        
        # Base resistance
        Q_base = q_base * A_base  # kN
        
        # Shaft resistance
        Q_shaft = f_shaft * P * self.L  # kN
        
        # Total capacity
        Q_ult = Q_base + Q_shaft
        
        # Allowable capacity (FS = 2.5 typical)
        Q_allow = Q_ult / 2.5
        
        return {
            'Q_base': Q_base,
            'Q_shaft': Q_shaft,
            'Q_ult': Q_ult,
            'Q_allow': Q_allow,
            'FS': 2.5,
            'note': 'Simplified calculation - Provide soil data for accurate design'
        }
    
    def design_pile_group(self, n_piles: int, spacing: float) -> Dict:
        """
        Design pile group
        
        Args:
            n_piles: Number of piles
            spacing: Center-to-center spacing (m)
        
        Returns:
            Pile group design results
        """
        # Single pile capacity
        single = self.calculate_single_pile_capacity()
        Q_single = single['Q_allow']
        
        # Group efficiency (simplified)
        # η = 1 - θ(n-1)√n / 90n
        # where θ = arctan(D/s)
        theta = math.degrees(math.atan(self.D / 1000 / spacing))
        eta = 1 - (theta * (n_piles - 1) * math.sqrt(n_piles)) / (90 * n_piles)
        eta = max(eta, 0.6)  # Minimum 0.6
        
        # Group capacity
        Q_group = eta * n_piles * Q_single
        
        return {
            'n_piles': n_piles,
            'spacing': spacing,
            'Q_single': Q_single,
            'efficiency': eta,
            'Q_group': Q_group,
            'Q_per_pile': Q_group / n_piles,
            'status': 'OK' if spacing >= 2.5 * (self.D / 1000) else 'WARNING - Spacing too small'
        }
