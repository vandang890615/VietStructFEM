# -*- coding: utf-8 -*-
"""
Steel Connection Designer - TCVN 5575:2024
Bolted, Welded, and Base Plate Connections
"""

import math
from typing import Dict


class ConnectionDesigner:
    """Steel Connection Design Library"""
    
    # Bolt grades (ASTM equivalents - TODO: Vietnamese standards)
    BOLT_GRADES = {
        'A325': {'Fnt': 620, 'Fnv': 372},  # MPa (Tension, Shear)
        'A490': {'Fnt': 780, 'Fnv': 468},
    }
    
    # Bolt areas (nominal diameter in mm)
    BOLT_AREAS = {
        12: 113,   # mm²
        16: 201,
        20: 314,
        22: 380,
        24: 452,
        27: 573,
        30: 707,
    }
    
    @staticmethod
    def check_bolted_connection(n_bolts: int, bolt_dia: int, bolt_grade: str,
                                V: float, T: float = 0, 
                                bearing_thickness: float = 10, 
                                Fu_plate: float = 400) -> Dict:
        """
        Check bolted connection
        
        Args:
            n_bolts: Number of bolts
            bolt_dia: Bolt diameter (mm)
            bolt_grade: Bolt grade ('A325', 'A490')
            V: Shear force (kN)
            T: Tension force (kN)
            bearing_thickness: Plate thickness (mm)
            Fu_plate: Ultimate strength of plate (MPa)
        
        Returns:
            Connection check results
        """
        # Get bolt properties
        bolt = ConnectionDesigner.BOLT_GRADES.get(bolt_grade, ConnectionDesigner.BOLT_GRADES['A325'])
        Ab = ConnectionDesigner.BOLT_AREAS.get(bolt_dia, 314)  # mm²
        
        # Shear capacity per bolt
        Fnv = bolt['Fnv']
        
        # Check shear
        phi_v = 0.75
        Rn_v = Fnv * Ab / 1000  # kN (per bolt)
        phi_Rn_v = phi_v * Rn_v * n_bolts
        
        V_ratio = V / phi_Rn_v if phi_Rn_v > 0 else 999
        
        # Check bearing on plate
        Lc = 1.5 * bolt_dia  # Edge distance (assumed)
        Rn_bearing = 2.4 * bolt_dia * bearing_thickness * Fu_plate / 1000  # kN per bolt
        phi_b = 0.75
        phi_Rn_bearing = phi_b * Rn_bearing * n_bolts
        
        bearing_ratio = V / phi_Rn_bearing if phi_Rn_bearing > 0 else 999
        
        # Check tension (if present)
        if T > 0:
            Fnt = bolt['Fnt']
            phi_t = 0.75
            Rn_t = Fnt * Ab / 1000  # kN per bolt
            phi_Rn_t = phi_t * Rn_t * n_bolts
            T_ratio = T / phi_Rn_t
            
            # Combined shear-tension interaction
            # (V/Vn)² + (T/Tn)² ≤ 1.0 (simplified)
            interaction = V_ratio**2 + T_ratio**2
        else:
            T_ratio = 0
            interaction = V_ratio
        
        # Overall status
        status = 'OK' if (V_ratio <= 1.0 and bearing_ratio <= 1.0 and interaction <= 1.0) else 'FAIL'
        
        return {
            'n_bolts': n_bolts,
            'bolt_dia': bolt_dia,
            'bolt_grade': bolt_grade,
            'phi_Rn_shear': phi_Rn_v,
            'phi_Rn_bearing': phi_Rn_bearing,
            'V': V,
            'V_ratio': V_ratio,
            'bearing_ratio': bearing_ratio,
            'T_ratio': T_ratio if T > 0 else None,
            'interaction': interaction if T > 0 else None,
            'status': status
        }
    
    @staticmethod
    def check_welded_connection(weld_length: float, weld_size: float, 
                                V: float, weld_type: str = 'fillet',
                                electrode: str = 'E70') -> Dict:
        """
        Check welded connection
        
        Args:
            weld_length: Total weld length (mm)
            weld_size: Weld size/leg (mm)
            V: Force (kN)
            weld_type: 'fillet' or 'groove'
            electrode: Electrode type
        
        Returns:
            Weld check results
        """
        # Electrode strength
        FEXX = {'E60': 415, 'E70': 485, 'E80': 550}.get(electrode, 485)  # MPa
        
        if weld_type == 'fillet':
            # Fillet weld capacity
            throat = 0.707 * weld_size  # mm
            Aw = throat * weld_length  # mm²
            
            # Nominal strength (TCVN/AISC)
            Fnw = 0.6 * FEXX  # MPa
            
            phi = 0.75
            Rn = Fnw * Aw / 1000  # kN
            phi_Rn = phi * Rn
            
        else:  # groove weld
            Aw = weld_size * weld_length  # mm² (full penetration)
            Fnw = 0.9 * FEXX
            
            phi = 0.9
            Rn = Fnw * Aw / 1000  # kN
            phi_Rn = phi * Rn
        
        ratio = V / phi_Rn if phi_Rn > 0 else 999
        
        return {
            'weld_type': weld_type,
            'weld_size': weld_size,
            'weld_length': weld_length,
            'throat': throat if weld_type == 'fillet' else weld_size,
            'Rn': Rn,
            'phi_Rn': phi_Rn,
            'V': V,
            'ratio': ratio,
            'status': 'OK' if ratio <= 1.0 else 'FAIL'
        }
    
    @staticmethod
    def design_base_plate(P: float, M: float, column_size: float,
                         f_c: float = 20, Fy_plate: float = 235) -> Dict:
        """
        Design base plate under column
        
        Args:
            P: Axial load (kN)
            M: Moment (kNm)
            column_size: Column width (mm) - assumed square
            f_c: Concrete strength (MPa)
            Fy_plate: Plate yield strength (MPa)
        
        Returns:
            Base plate design results
        """
        c = column_size  # mm
        
        # Required plate area (bearing pressure check)
        # Allowable bearing pressure on concrete
        fp = 0.85 * f_c  # MPa (simplified)
        
        # Eccentricity
        e = (M * 1e6) / (P * 1000) if P > 0 else 0  # mm
        
        # Required plate dimensions (conservative - square plate)
        # Account for eccentricity with factor
        if e == 0:
            A_req = (P * 1000) / fp  # mm²
        else:
            # Simplified approach - increase area by eccentricity factor
            A_req = (P * 1000) / fp * 1.5
        
        B = math.sqrt(A_req)
        
        # Round up to nearest 50mm
        B = math.ceil(B / 50) * 50
        
        # Plate thickness (simplified)
        # Maximum bearing pressure
        q_max = (P * 1000) / (B * B)  # MPa
        
        # Cantilever distance from column face
        m = (B - c) / 2  # mm
        
        # Bending moment in plate
        M_plate = q_max * m**2 / 2  # N·mm/mm width
        
        # Required plate thickness
        # t = sqrt(6M / (Fy * b)) where b = 1mm width
        t_req = math.sqrt((6 * M_plate) / Fy_plate)
        
        # Round up to standard thickness
        standard_thicknesses = [10, 12, 16, 20, 25, 30, 40, 50]
        t = min([th for th in standard_thicknesses if th >= t_req], default=50)
        
        # Anchor bolts (placeholder - simplified)
        n_bolts = 4  # Typical
        bolt_dia = 20  # mm (M20 typical)
        
        return {
            'B': B,
            'L': B,
            't': t,
            'q_max': q_max,
            'fp_allow': fp,
            'bearing_ratio': q_max / fp,
            'anchor_bolts': f'{n_bolts}M{bolt_dia}',
            'status': 'OK' if q_max <= fp else 'FAIL - Increase plate size'
        }
