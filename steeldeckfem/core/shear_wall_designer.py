# -*- coding: utf-8 -*-
"""
Shear Wall Designer - TCVN 5574:2018
RC Shear Wall Design (leverages column logic)
"""

import math
from typing import Dict
from steeldeckfem.core.rc_column_designer import RCColumnDesigner


class ShearWallDesigner:
    """RC Shear Wall Designer - extends column logic for walls"""
    
    def __init__(self, length: float, thickness: float, height: float, 
                 concrete: str = 'B25', steel: str = 'CB400-V'):
        """
        Args:
            length: Wall length (mm)
            thickness: Wall thickness (mm)  
            height: Wall height (mm)
            concrete: Concrete grade
            steel: Steel grade
        """
        self.L = length
        self.t = thickness
        self.h = height
        
        # Use column designer for rectangular wall section
        self.column_designer = RCColumnDesigner(thickness, length, concrete, steel)
    
    def check_shear_wall(self, P: float, M: float, V: float) -> Dict:
        """Check shear wall under P, M, V"""
        # Use column P-M interaction
        pm_result = self.column_designer.design_pm_interaction(P, M)
        
        # Shear check (simplified - wall shear)
        A_wall = self.L * self.t  # mm²
        v = (V * 1000) / A_wall  # MPa (V in kN)
        v_allow = 0.1 * self.column_designer.f_c  # Simplified allowable
        
        shear_status = 'OK' if v <= v_allow else 'FAIL'
        
        return {
            'pm_check': pm_result,
            'shear_stress': v,
            'shear_allow': v_allow,
            'shear_status': shear_status,
            'overall': 'OK' if (pm_result['status'] == 'OK' and shear_status == 'OK') else 'FAIL'
        }
