# -*- coding: utf-8 -*-
"""
Strip Footing Designer - TCVN 9362:2012
"""

import math
from typing import Dict
from steeldeckfem.core.foundation_designer import IsolatedFootingDesigner


class StripFootingDesigner(IsolatedFootingDesigner):
    """Strip (Continuous) Footing - extends isolated footing"""
    
    def design_strip_footing(self, q_wall: float, width_req: float = None) -> Dict:
        """
        Design strip footing
        
        Args:
            q_wall: Wall load per unit length (kN/m)
            width_req: Required width (m), if None will calculate
        
        Returns: Design results
        """
        q_allow = self._calculate_bearing_capacity() / 3.0  # FS=3
        
        # Required width
        if width_req is None:
            B = (q_wall * 1.2) / q_allow  # kN/m / kPa * 1000
            B = math.ceil(B * 10) / 10
        else:
            B = width_req
        
        # Pressure
        q_actual = q_wall / B
        
        return {
            'width': B,
            'q_allow': q_allow,
            'q_actual': q_actual,
            'status': 'OK' if q_actual <= q_allow else 'FAIL'
        }
