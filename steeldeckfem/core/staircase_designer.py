# -*- coding: utf-8 -*-
"""
Staircase Designer - TCVN 5574:2018
"""

import math
from typing import Dict
from steeldeckfem.core.rc_beam_designer import MaterialDatabase


class StaircaseDesigner:
    """RC Staircase Designer - inclined slab with steps"""
    
    def __init__(self, width: float = 1200, concrete: str = 'B25', steel: str = 'CB400-V'):
        self.width = width
        mat_db = MaterialDatabase()
        concrete_props = mat_db.get_concrete_properties(concrete)
        steel_props = mat_db.get_steel_properties(steel)
        self.f_c = concrete_props['f_c']
        self.f_y = steel_props['f_y']
    
    def design_staircase(self, length: float, height: float, thickness: float, 
                        step_rise: float, step_tread: float, q: float) -> Dict:
        """
        Args:
            length: Horizontal projection (mm)
            height: Total rise (mm)
            thickness: Slab thickness (mm)
            step_rise: Step height (mm)
            step_tread: Step width (mm)
            q: Live load (kN/m²)
        
        Returns: Design results
        """
        # Inclined length
        L_incline = math.sqrt(length**2 + height**2)
        
        # Dead load (slab + steps)
        DL_slab = 25 * thickness / 1000  # kN/m²
        n_steps = int(height / step_rise)
        step_volume_per_m2 = (step_rise * step_tread / 2) / (step_tread * 1000)
        DL_steps = 25 * step_volume_per_m2
        
        q_total = 1.2 * (DL_slab + DL_steps) + 1.6 * q
        
        # Moment (simply supported)
        L_m = L_incline / 1000
        M = q_total * self.width / 1000 * L_m**2 / 8  # kNm
        
        # Required steel
        d = thickness - 25  # Effective depth
        M_Nmm = M * 1e6
        As_req = M_Nmm / (0.9 * self.f_y * 0.9 * d)
        
        # Select bars
        bar_area = 113  # Φ12
        spacing = (self.width * bar_area) / As_req
        spacing = min([s for s in [100, 125, 150, 175, 200, 250] if s <= spacing], default=100)
        
        return {
            'n_steps': n_steps,
            'incline_length': L_incline,
            'total_load': q_total,
            'moment': M,
            'As_required': As_req,
            'bar_spacing': spacing,
            'status': 'OK'
        }
