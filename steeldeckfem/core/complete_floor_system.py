"""
Complete Floor System Module - Full Structural Hierarchy
Includes: Columns → Main Beams → Secondary Beams → Deck Floor
With comprehensive spacing calculations and load distribution
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict
import math


@dataclass
class ColumnSpec:
    """Column specifications"""
    section_type: str  # "H", "I", "Box", "Circular"
    name: str
    h: float  # Height (mm)
    b: float  # Width (mm)
    tf: float = 0  # Flange thickness
    tw: float = 0  # Web thickness
    diameter: float = 0  # For circular
    area: float = 0  # cm2
    ix: float = 0  # cm4
    wx: float = 0  # cm3
    column_height: float = 0  # m


@dataclass
class BeamSpec:
    """Beam specifications (Main or Secondary)"""
    beam_type: str  # "Main" or "Secondary"
    section_type: str  # "I", "H", "Box", "C"
    name: str
    h: float  # mm
    b: float  # mm
    tf: float = 0
    tw: float = 0
    area: float = 0  # cm2
    ix: float = 0  # cm4
    wx: float = 0  # cm3
    span: float = 0  # m
    spacing: float = 0  # m (distance between parallel beams)


@dataclass
class FloorSystemLayout:
    """Complete floor system layout"""
    # Overall dimensions
    length: float  # Building length (m)
    width: float  # Building width (m)
    floor_height: float  # Floor to floor height (m)
    
    # Column grid
    column_spacing_x: float  # Column spacing in X direction (m)
    column_spacing_y: float  # Column spacing in Y direction (m)
    
    # Main beams (typically spanning between columns)
    main_beam_direction: str  # "X" or "Y"
    main_beam_spec: BeamSpec = None
    
    # Secondary beams (spanning between main beams)
    secondary_beam_spacing: float = 0  # m
    secondary_beam_spec: BeamSpec = None
    
    # Deck
    deck_profile: str = "DECK_75"
    deck_thickness: float = 1.0  # mm
    concrete_depth: float = 120  # mm
    
    # Column
    column_spec: ColumnSpec = None


class CompleteFloorSystemCalculator:
    """
    Comprehensive floor system calculator with full structural hierarchy
    """
    
    def __init__(self):
        self.E_steel = 200000  # MPa
        self.fy_steel = 350  # MPa (Grade 50)
        
    def design_complete_system(self, layout: FloorSystemLayout, 
                              live_load: float = 400,  # kg/m2
                              dead_load_finish: float = 30) -> Dict:
        """
        Design complete floor system from deck to columns
        
        Returns comprehensive analysis results
        """
        
        results = {
            'deck': None,
            'secondary_beams': None,
            'main_beams': None,
            'columns': None,
            'load_summary': None
        }
        
        # 1. DECK DESIGN
        # Deck spans between secondary beams
        deck_span = layout.secondary_beam_spacing
        from src.logic.floor_deck import SteelDeckCalculator
        deck_calc = SteelDeckCalculator()
        
        deck_result = deck_calc.design_deck(
            profile_name=layout.deck_profile,
            thickness=layout.deck_thickness,
            span=deck_span,
            concrete_thickness=layout.concrete_depth,
            construction_load=150,
            live_load=live_load
        )
        results['deck'] = deck_result
        
        # 2. SECONDARY BEAM DESIGN
        # Secondary beams carry deck load and span between main beams
        sec_beam = layout.secondary_beam_spec
        
        # Load per meter on secondary beam
        q_deck_dead = deck_result.construction_capacity  # kg/m2
        q_total_dead = q_deck_dead + dead_load_finish
        q_live = live_load
        
        # Tributary width = deck span (secondary beam spacing)
        tributary = layout.secondary_beam_spacing
        q_dead_beam = q_total_dead * tributary  # kg/m
        q_live_beam = q_live * tributary  # kg/m
        
        # Secondary beam span = distance between main beams
        if layout.main_beam_direction == "X":
            sec_beam_span = layout.column_spacing_x
        else:
            sec_beam_span = layout.column_spacing_y
        
        sec_beam_analysis = self.analyze_beam(
            beam=sec_beam,
            span=sec_beam_span,
            q_dead=q_dead_beam,
            q_live=q_live_beam,
            beam_name="Secondary Beam"
        )
        results['secondary_beams'] = sec_beam_analysis
        
        # 3. MAIN BEAM DESIGN
        # Main beams carry reactions from secondary beams
        main_beam = layout.main_beam_spec
        
        # Number of secondary beams on main beam
        if layout.main_beam_direction == "X":
            main_beam_span = layout.column_spacing_y
            num_sec_beams = int(layout.column_spacing_x / layout.secondary_beam_spacing) + 1
        else:
            main_beam_span = layout.column_spacing_x
            num_sec_beams = int(layout.column_spacing_y / layout.secondary_beam_spacing) + 1
        
        # Point loads from secondary beams
        P_dead = sec_beam_analysis['reaction_dead']  # kg
        P_live = sec_beam_analysis['reaction_live']  # kg
        
        # Convert to equivalent uniform load on main beam
        total_load_dead = P_dead * num_sec_beams
        total_load_live = P_live * num_sec_beams
        q_main_dead = total_load_dead / main_beam_span  # kg/m
        q_main_live = total_load_live / main_beam_span  # kg/m
        
        main_beam_analysis = self.analyze_beam(
            beam=main_beam,
            span=main_beam_span,
            q_dead=q_main_dead,
            q_live=q_main_live,
            beam_name="Main Beam"
        )
        results['main_beams'] = main_beam_analysis
        
        # 4. COLUMN DESIGN
        # Columns carry main beam reactions
        column = layout.column_spec
        
        # Load on column = main beam reactions
        # For interior column: 2 main beams
        # For edge column: 1 main beam
        # Assuming interior column (worst case)
        
        num_floors = 1  # Single floor for now
        
        P_dead_column = main_beam_analysis['reaction_dead'] * 2 * num_floors
        P_live_column = main_beam_analysis['reaction_live'] * 2 * num_floors
        
        column_analysis = self.analyze_column(
            column=column,
            P_dead=P_dead_column,
            P_live=P_live_column,
            height=layout.floor_height
        )
        results['columns'] = column_analysis
        
        # 5. LOAD SUMMARY
        results['load_summary'] = {
            'deck_load': f"{q_deck_dead:.1f} kg/m²",
            'live_load': f"{live_load:.1f} kg/m²",
            'secondary_beam_load': f"{q_dead_beam + q_live_beam:.1f} kg/m",
            'main_beam_load': f"{q_main_dead + q_main_live:.1f} kg/m",
            'column_load': f"{P_dead_column + P_live_column:.1f} kg",
        }
        
        return results
    
    def analyze_beam(self, beam: BeamSpec, span: float, 
                    q_dead: float, q_live: float, beam_name: str) -> Dict:
        """Analyze beam under uniform load"""
        
        # Load combination
        q_total = 1.2 * q_dead + 1.6 * q_live  # kg/m
        
        # Moment and shear
        M_max = q_total * span**2 / 8  # kg.m
        V_max = q_total * span / 2  # kg
        
        # Convert to kN.m for steel design
        M_kNm = M_max / 100  # Approximate
        
        # Stress check
        M_kgcm = M_max * 100  # kg.cm
        sigma = M_kgcm / beam.wx if beam.wx > 0 else 999999
        fy_kgcm2 = self.fy_steel * 100  # Convert MPa to kg/cm2
        
        stress_ok = sigma <= fy_kgcm2
        
        # Deflection check (L/360)
        E_kgcm2 = self.E_steel * 10  # MPa to kg/cm2
        delta = (5 * q_dead * 0.01 * (span * 100)**4) / (384 * beam.ix * E_kgcm2)  # cm
        delta_limit = span * 100 / 360  # cm
        deflection_ok = delta <= delta_limit
        
        # Reactions
        reaction_dead = q_dead * span / 2  # kg
        reaction_live = q_live * span / 2  # kg
        
        return {
            'beam_name': beam_name,
            'section': beam.name,
            'span': span,
            'moment': M_max,
            'shear': V_max,
            'stress': sigma,
            'stress_limit': fy_kgcm2,
            'stress_ok': stress_ok,
            'deflection': delta,
            'deflection_limit': delta_limit,
            'deflection_ok': deflection_ok,
            'reaction_dead': reaction_dead,
            'reaction_live': reaction_live,
            'status': 'ĐẠT' if (stress_ok and deflection_ok) else 'KHÔNG ĐẠT'
        }
    
    def analyze_column(self, column: ColumnSpec, P_dead: float, 
                      P_live: float, height: float) -> Dict:
        """Analyze column under axial load"""
        
        # Load combination
        P_total = 1.2 * P_dead + 1.6 * P_live  # kg
        
        # Axial stress
        sigma = P_total / column.area if column.area > 0 else 999999
        fy_kgcm2 = self.fy_steel * 100
        
        # Slenderness check (simplified)
        # λ = L/r, where r = sqrt(I/A)
        r = math.sqrt(column.ix / column.area) if column.area > 0 else 1
        lambda_ratio = (height * 100) / r
        
        # Euler buckling (simplified)
        E_kgcm2 = self.E_steel * 10
        P_cr = (math.pi**2 * E_kgcm2 * column.ix) / ((height * 100)**2)
        
        # Allowable stress with buckling reduction
        if lambda_ratio < 100:
            reduction = 1.0
        else:
            reduction = 0.8
        
        sigma_allow = fy_kgcm2 * reduction
        stress_ok = sigma <= sigma_allow
        
        return {
            'section': column.name,
            'height': height,
            'axial_load': P_total,
            'stress': sigma,
            'stress_allow': sigma_allow,
            'slenderness': lambda_ratio,
            'buckling_load': P_cr,
            'stress_ok': stress_ok,
            'status': 'ĐẠT' if stress_ok else 'KHÔNG ĐẠT'
        }
    
    def calculate_beam_spacing(self, deck_span_max: float, 
                              total_width: float) -> List[float]:
        """
        Calculate optimal secondary beam spacing
        
        Args:
            deck_span_max: Maximum allowable deck span (m)
            total_width: Total width to be spanned (m)
            
        Returns:
            List of beam positions
        """
        
        # Number of spaces
        num_spaces = math.ceil(total_width / deck_span_max)
        
        # Equal spacing
        spacing = total_width / num_spaces
        
        # Beam positions
        positions = [i * spacing for i in range(num_spaces + 1)]
        
        return positions, spacing
    
    def generate_system_report(self, layout: FloorSystemLayout, 
                              results: Dict) -> str:
        """Generate comprehensive HTML report for complete system"""
        
        html = f"""
        <h2>HỆ THỐNG SÀN HOÀN CHỈNH - PHÂN TÍCH TỔNG THỂ</h2>
        
        <h3>I. LAYOUT HỆ THỐNG</h3>
        <table>
            <tr><th>Thông số</th><th>Giá trị</th></tr>
            <tr><td>Kích thước tổng thể</td><td>{layout.length}m × {layout.width}m</td></tr>
            <tr><td>Chiều cao tầng</td><td>{layout.floor_height}m</td></tr>
            <tr><td>Lưới cột</td><td>{layout.column_spacing_x}m × {layout.column_spacing_y}m</td></tr>
            <tr><td>Hướng dầm chính</td><td>{layout.main_beam_direction}</td></tr>
            <tr><td>Bước dầm phụ</td><td>{layout.secondary_beam_spacing}m</td></tr>
        </table>
        
        <h3>II. PHÂN CẤP KẾT CẤU</h3>
        <p><b>Deck → Dầm phụ → Dầm chính → Cột</b></p>
        
        <h3>III. KẾT QUẢ TÍNH TOÁN</h3>
        
        <h4>1. SÀN DECK</h4>
        <ul>
            <li>Profile: <b>{results['deck'].profile_name}</b></li>
            <li>Nhịp: <b>{results['deck'].max_span}m</b></li>
            <li>Trạng thái: <b style="color:{'green' if results['deck'].status == 'ĐẠT' else 'red'};">{results['deck'].status}</b></li>
        </ul>
        
        <h4>2. DẦM PHỤ (Secondary Beams)</h4>
        <ul>
            <li>Tiết diện: <b>{results['secondary_beams']['section']}</b></li>
            <li>Nhịp: <b>{results['secondary_beams']['span']}m</b></li>
            <li>Moment: <b>{results['secondary_beams']['moment']:.2f} kg.m</b></li>
            <li>Độ võng: <b>{results['secondary_beams']['deflection']:.2f}mm / {results['secondary_beams']['deflection_limit']:.2f}mm</b></li>
            <li>Trạng thái: <b style="color:{'green' if results['secondary_beams']['status'] == 'ĐẠT' else 'red'};">{results['secondary_beams']['status']}</b></li>
        </ul>
        
        <h4>3. DẦM CHÍNH (Main Beams)</h4>
        <ul>
            <li>Tiết diện: <b>{results['main_beams']['section']}</b></li>
            <li>Nhịp: <b>{results['main_beams']['span']}m</b></li>
            <li>Moment: <b>{results['main_beams']['moment']:.2f} kg.m</b></li>
            <li>Độ võng: <b>{results['main_beams']['deflection']:.2f}mm / {results['main_beams']['deflection_limit']:.2f}mm</b></li>
            <li>Trạng thái: <b style="color:{'green' if results['main_beams']['status'] == 'ĐẠT' else 'red'};">{results['main_beams']['status']}</b></li>
        </ul>
        
        <h4>4. CỘT (Columns)</h4>
        <ul>
            <li>Tiết diện: <b>{results['columns']['section']}</b></li>
            <li>Chiều cao: <b>{results['columns']['height']}m</b></li>
            <li>Lực nén: <b>{results['columns']['axial_load']:.2f} kg</b></li>
            <li>Ứng suất: <b>{results['columns']['stress']:.2f} / {results['columns']['stress_allow']:.2f} kg/cm²</b></li>
            <li>Trạng thái: <b style="color:{'green' if results['columns']['status'] == 'ĐẠT' else 'red'};">{results['columns']['status']}</b></li>
        </ul>
        
        <h3>IV. TÓM TẮT TẢI TRỌNG</h3>
        <table>
            <tr><th>Cấu kiện</th><th>Tải trọng</th></tr>
            <tr><td>Sàn deck</td><td>{results['load_summary']['deck_load']}</td></tr>
            <tr><td>Hoạt tải</td><td>{results['load_summary']['live_load']}</td></tr>
            <tr><td>Dầm phụ</td><td>{results['load_summary']['secondary_beam_load']}</td></tr>
            <tr><td>Dầm chính</td><td>{results['load_summary']['main_beam_load']}</td></tr>
            <tr><td>Cột</td><td>{results['load_summary']['column_load']}</td></tr>
        </table>
        """
        
        return html
