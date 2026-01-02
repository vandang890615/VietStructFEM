# -*- coding: utf-8 -*-
"""
Deflection Check Utility - TCVN 2737:2023
Simple beam deflection calculator with standard limits
"""

import math
from typing import Dict


class DeflectionCalculator:
    """
    Deflection calculator for common beam configurations
    Per TCVN 2737:2023 deflection limits
    """
    
    # Standard deflection limits
    DEFLECTION_LIMITS = {
        'beam_general': lambda L: L / 250,  # L/250
        'beam_brittle_finish': lambda L: L / 360,  # L/360
        'cantilever': lambda L: L / 125,  # L/125
        'roof_beam': lambda L: L / 180,  # L/180
        'floor_beam': lambda L: L / 300,  # L/300
    }
    
    @staticmethod
    def calculate_deflection(beam_type: str, L: float, E: float, I: float, load_type: str, **load_params) -> Dict:
        """
        Calculate deflection for various beam and load configurations
        
        Args:
            beam_type: 'simply_supported', 'fixed_fixed', 'cantilever'
            L: Span length (m)
            E: Young's modulus (MPa)
            I: Moment of inertia (mm⁴)
            load_type: 'uniform', 'point_center', 'point_any'
            **load_params: Load parameters (q for uniform, P for point, a for location)
        
        Returns:
            Deflection results with status
        """
        L_mm = L * 1000  # Convert to mm
        
        # Calculate deflection based on configuration
        if beam_type == 'simply_supported':
            if load_type == 'uniform':
                q = load_params.get('q', 0)  # N/mm
                delta = (5 * q * L_mm**4) / (384 * E * I)
            elif load_type == 'point_center':
                P = load_params.get('P', 0) * 1000  # kN to N
                delta = (P * L_mm**3) / (48 * E * I)
            else:
                delta = 0
                
        elif beam_type == 'fixed_fixed':
            if load_type == 'uniform':
                q = load_params.get('q', 0)
                delta = (q * L_mm**4) / (384 * E * I)
            elif load_type == 'point_center':
                P = load_params.get('P', 0) * 1000
                delta = (P * L_mm**3) / (192 * E * I)
            else:
                delta = 0
                
        elif beam_type == 'cantilever':
            if load_type == 'uniform':
                q = load_params.get('q', 0)
                delta = (q * L_mm**4) / (8 * E * I)
            elif load_type == 'point_end':
                P = load_params.get('P', 0) * 1000
                delta = (P * L_mm**3) / (3 * E * I)
            else:
                delta = 0
        else:
            delta = 0
        
        # Get limit
        limit_type = load_params.get('limit_type', 'beam_general')
        delta_limit = DeflectionCalculator.DEFLECTION_LIMITS[limit_type](L_mm)
        
        ratio = delta / delta_limit if delta_limit > 0 else 0
        
        return {
            'deflection_mm': delta,
            'limit_mm': delta_limit,
            'ratio': ratio,
            'actual_L_ratio': L_mm / delta if delta > 0 else float('inf'),
            'status': 'OK' if ratio <= 1.0 else 'FAIL'
        }
