# -*- coding: utf-8 -*-
"""
Cantilever/Balcony Designer - TCVN 5574:2018
"""

from typing import Dict
from steeldeckfem.core.rc_beam_designer import RCBeamDesigner


class CantileverDesigner:
    """Cantilever/Balcony Designer"""
    
    @staticmethod
    def design_cantilever_slab(length: float, thickness: float, q: float, 
                               concrete: str = 'B25', steel: str = 'CB400-V') -> Dict:
        """
        Design cantilever slab
        
        Args:
            length: Cantilever length (m)
            thickness: Slab thickness (mm)
            q: Load (kN/m²)
            concrete: Concrete grade
            steel: Steel grade
        
        Returns: Design results
        """
        # Moment at root
        M = q * 1.0 * length**2 / 2  # kNm/m (per meter width)
        
        # Use beam designer for 1m width strip
        beam = RCBeamDesigner(1000, thickness, length, concrete, steel)
        
        d = thickness - 25
        M_Nmm = M * 1e6
        As_req = M_Nmm / (0.9 * beam.f_y * 0.9 * d)
        
        # Select bars
        spacing = (1000 * 113) / As_req  # Φ12
        spacing = min([s for s in [100, 125, 150, 175, 200] if s <= spacing], default=100)
        
        # Deflection check (cantilever: delta = qL^4 / 8EI)
        E = 29000  # MPa (approximate for concrete)
        I = (1000 * thickness**3) / 12
        delta = (q * 1000 / 1000 * (length * 1000)**4) / (8 * E * I)
        delta_allow = length * 1000 / 125  # L/125 for cantilever
        
        return {
            'moment': M,
            'As_required': As_req,
            'bar_spacing': spacing,
            'deflection': delta,
            'deflection_limit': delta_allow,
            'deflection_ok': delta <= delta_allow,
            'status': 'OK' if delta <= delta_allow else 'FAIL - Increase thickness'
        }
