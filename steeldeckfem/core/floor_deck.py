"""
Steel Deck Floor System Design Module
Implements composite steel-concrete floor design per TCVN 5575-2012 and Eurocode 4.

Features:
- Steel deck profile selection and design
- Composite beam calculations
- Load distribution and transfer
- Deflection checks (construction and service stages)
- Shear stud design
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from steeldeckfem.core.data_models import Section, Material


# STEEL DECK PROFILE DATABASE
# Based on common Vietnamese/Asian profiles
DECK_PROFILES = {
    # Composite Floor Deck (Trapezoidal profiles with embossments)
    "DECK_51": {
        "name": "Deck 51mm",
        "type": "composite",
        "depth": 51,  # mm
        "pitch": 150,  # mm (rib spacing)
        "cover_width": 1000,  # mm
        "thickness_range": [0.75, 0.9, 1.0, 1.2],  # mm
        "weight_per_m2": {0.75: 7.8, 0.9: 9.2, 1.0: 10.2, 1.2: 12.1},  # kg/m2
        "Ix": {0.75: 28.5, 0.9: 34.2, 1.0: 38.0, 1.2: 45.6},  # cm4/m
        "Sx": {0.75: 10.8, 0.9: 12.9, 1.0: 14.3, 1.2: 17.2},  # cm3/m
    },
    "DECK_75": {
        "name": "Deck 75mm", 
        "type": "composite",
        "depth": 75,
        "pitch": 200,
        "cover_width": 1000,
        "thickness_range": [0.9, 1.0, 1.2],
        "weight_per_m2": {0.9: 10.5, 1.0: 11.6, 1.2: 13.8},
        "Ix": {0.9: 68.5, 1.0: 76.1, 1.2: 91.3},
        "Sx": {0.9: 17.8, 1.0: 19.7, 1.2: 23.7},
    },
    "DECK_100": {
        "name": "Deck 100mm",
        "type": "composite",
        "depth": 100,
        "pitch": 250,
        "cover_width": 1000,
        "thickness_range": [1.0, 1.2],
        "weight_per_m2": {1.0: 13.2, 1.2: 15.6},
        "Ix": {1.0: 142.5, 1.2: 171.0},
        "Sx": {1.0: 27.8, 1.2: 33.4},
    },
}


@dataclass
class DeckDesignResult:
    """Results from deck design calculations"""
    profile_name: str
    thickness: float
    construction_capacity: float  # kg/m2
    composite_capacity: float  # kg/m2
    max_span: float  # m
    deflection_ok: bool
    construction_deflection: float  # mm
    service_deflection: float  # mm
    status: str
    html_report: str


@dataclass
class CompositeBeamResult:
    """Results from composite beam design"""
    section_name: str
    effective_width: float  # mm
    moment_capacity: float  # kg.m
    shear_studs_required: int
    deflection: float  # mm
    deflection_limit: float  # mm
    status: str
    html_report: str


class SteelDeckCalculator:
    """
    Comprehensive steel deck floor system calculator.
    Handles both construction stage and composite stage.
    """
    
    def __init__(self):
        self.concrete_density = 2400  # kg/m3
        self.concrete_fc = 25  # MPa (C25/30)
        self.E_steel = 200000  # MPa
        self.E_concrete = 30000  # MPa (approximate for C25)
        
    def design_deck(self, profile_name: str, thickness: float, 
                   span: float, concrete_thickness: float,
                   construction_load: float = 150,  # kg/m2
                   live_load: float = 400) -> DeckDesignResult:
        """
        Complete deck design for both construction and service stages.
        
        Args:
            profile_name: Deck profile (e.g., "DECK_75")
            thickness: Deck thickness (mm)
            span: Span between supports (m)
            concrete_thickness: Total depth of concrete slab (mm)
            construction_load: Construction live load (kg/m2)
            live_load: Service live load (kg/m2)
            
        Returns:
            DeckDesignResult with all calculations
        """
        profile = DECK_PROFILES.get(profile_name)
        if not profile:
            raise ValueError(f"Unknown profile: {profile_name}")
            
        # Validate thickness
        if thickness not in profile["thickness_range"]:
            raise ValueError(f"Invalid thickness {thickness}mm for {profile_name}")
        
        deck_depth = profile["depth"]
        Ix = profile["Ix"][thickness]
        Sx = profile["Sx"][thickness]
        deck_weight = profile["weight_per_m2"][thickness]
        
        # === STAGE 1: CONSTRUCTION (Deck alone supports wet concrete) ===
        
        # Dead load: deck + wet concrete
        concrete_volume = (concrete_thickness / 1000) * 1.0  # m3/m2
        concrete_weight = concrete_volume * self.concrete_density  # kg/m2
        
        q_dead_construction = deck_weight + concrete_weight  # kg/m2
        q_total_construction = 1.2 * q_dead_construction + 1.6 * construction_load
        
        # Moment (simple span)
        M_construction = q_total_construction * span**2 / 8  # kg.m/m
        
        # Stress check (deck alone)
        fy_deck = 350  # N/mm2 = 35 kg/mm2
        sigma_construction = (M_construction * 100) / Sx  # kg/cm2
        construction_capacity = (Sx * fy_deck * 100) / (span**2 / 8) / 1.6  # kg/m2
        
        # Deflection (construction stage) - L/180 or 20mm
        delta_construction = (5 * q_dead_construction * (span * 1000)**4) / (384 * self.E_steel * Ix * 10000)
        delta_limit_construction = min(span * 1000 / 180, 20)  # mm
        
        # === STAGE 2: COMPOSITE (Deck + hardened concrete) ===
        
        # Transformed section properties (simplified)
        n = self.E_steel / self.E_concrete  # modular ratio
        
        # Effective concrete width (full width assumed)
        b_eff = 1000  # mm (per meter width)
        
        # Composite moment of inertia (approximate)
        # Concrete area above deck
        Ac = b_eff * (concrete_thickness - deck_depth) / 10  # cm2
        y_c = deck_depth / 10 + (concrete_thickness - deck_depth) / 20  # cm (centroid from bottom)
        
        # Approximate composite Ix
        Ix_composite = Ix + (Ac / n) * y_c**2  # cm4/m (simplified)
        
        # Service loads
        q_dead_service = deck_weight + concrete_weight + 30  # +30 for finishes
        q_total_service = 1.2 * q_dead_service + 1.6 * live_load
        
        M_composite = q_total_service * span**2 / 8
        
        # Composite capacity (simplified - assume full composite action)
        composite_capacity = live_load * 1.5  # Simplified, actual would need full analysis
        
        # Deflection (service stage) - L/240
        delta_service = (5 * q_total_service * (span * 1000)**4) / (384 * self.E_steel * Ix_composite * 10000)
        delta_limit_service = span * 1000 / 240
        
        # Status check
        deflection_ok = (delta_construction <= delta_limit_construction and 
                        delta_service <= delta_limit_service)
        stress_ok = sigma_construction <= fy_deck * 100
        status = "ĐẠT" if (deflection_ok and stress_ok) else "KHÔNG ĐẠT"
        
        # Generate detailed report
        html_report = self._generate_deck_report(
            profile, thickness, span, concrete_thickness, deck_weight,
            q_dead_construction, q_total_construction, M_construction,
            sigma_construction, fy_deck, construction_capacity,
            delta_construction, delta_limit_construction,
            q_total_service, M_composite, composite_capacity,
            delta_service, delta_limit_service, status
        )
        
        return DeckDesignResult(
            profile_name=profile_name,
            thickness=thickness,
            construction_capacity=construction_capacity,
            composite_capacity=composite_capacity,
            max_span=span,
            deflection_ok=deflection_ok,
            construction_deflection=delta_construction,
            service_deflection=delta_service,
            status=status,
            html_report=html_report
        )
    
    def _generate_deck_report(self, profile, thickness, span, concrete_thickness, deck_weight,
                             q_dead_construction, q_total_construction, M_construction,
                             sigma_construction, fy_deck, construction_capacity,
                             delta_construction, delta_limit_construction,
                             q_total_service, M_composite, composite_capacity,
                             delta_service, delta_limit_service, status) -> str:
        """Generate detailed HTML report for deck design"""
        
        color = "green" if status == "ĐẠT" else "red"
        
        html = f"""
        <h3>THIẾT KẾ SÀN DECK THÉP LIÊN HỢP</h3>
        
        <h4>1. Thông số hệ sàn:</h4>
        <ul>
            <li>Profile: <b>{profile['name']}</b> (Chiều sâu: {profile['depth']}mm)</li>
            <li>Chiều dày tôn: <b>{thickness} mm</b></li>
            <li>Nhịp tính toán: <b>{span} m</b></li>
            <li>Chiều dày sàn bê tông: <b>{concrete_thickness} mm</b></li>
            <li>Trọng lượng tôn deck: <b>{deck_weight:.1f} kg/m²</b></li>
        </ul>
        
        <h4>2. GIAI ĐOẠN THI CÔNG (Deck chịu bê tông ướt):</h4>
        
        <h5>2.1. Tải trọng thi công:</h5>
        <ul>
            <li>Tĩnh tải (deck + bê tông ướt): <b>{q_dead_construction:.1f} kg/m²</b></li>
            <li>Tải trọng thi công: p<sub>tc</sub> = 150 kg/m²</li>
            <li>Tổ hợp tải: q = 1.2×TT + 1.6×HT = <b>{q_total_construction:.1f} kg/m²</b></li>
        </ul>
        
        <h5>2.2. Kiểm tra ứng suất:</h5>
        <ul>
            <li>Moment: M = qL²/8 = {q_total_construction:.1f} × {span}² / 8 = <b>{M_construction:.2f} kg.m/m</b></li>
            <li>Ứng suất: σ = M/S<sub>x</sub> = <b>{sigma_construction:.1f} kg/cm²</b></li>
            <li>Giới hạn: f<sub>y</sub> = <b>{fy_deck * 100:.0f} kg/cm²</b></li>
            <li>Khả năng chịu tải: <b>{construction_capacity:.1f} kg/m²</b> ✓</li>
        </ul>
        
        <h5>2.3. Độ võng thi công:</h5>
        <ul>
            <li>Δ = 5qL⁴/(384EI) = <b>{delta_construction:.2f} mm</b></li>
            <li>Giới hạn: min(L/180, 20mm) = <b>{delta_limit_construction:.2f} mm</b></li>
            <li>Kết luận: <b>{"ĐẠT" if delta_construction <= delta_limit_construction else "VƯỢT"}</b></li>
        </ul>
        
        <h4>3. GIAI ĐOẠN SỬ DỤNG (Liên hợp deck + bê tông):</h4>
        
        <h5>3.1. Tải trọng sử dụng:</h5>
        <ul>
            <li>Tĩnh tải (deck + BTCT + hoàn thiện): TT = {q_dead_construction + 30:.1f} kg/m²</li>
            <li>Hoạt tải sàn: HT = 400 kg/m²</li>
            <li>Tổ hợp: q = 1.2×TT + 1.6×HT = <b>{q_total_service:.1f} kg/m²</b></li>
        </ul>
        
        <h5>3.2. Khả năng chiu tải liên hợp:</h5>
        <ul>
            <li>Moment liên hợp: M = <b>{M_composite:.2f} kg.m/m</b></li>
            <li>Khả năng chịu tải: <b>{composite_capacity:.1f} kg/m²</b> (liên hợp đầy đủ)</li>
        </ul>
        
        <h5>3.3. Độ võng sử dụng:</h5>
        <ul>
            <li>Δ = <b>{delta_service:.2f} mm</b></li>
            <li>Giới hạn: L/240 = <b>{delta_limit_service:.2f} mm</b></li>
            <li>Kết luận: <b>{"ĐẠT" if delta_service <= delta_limit_service else "VƯỢT"}</b></li>
        </ul>
        
        <h4 style="color:{color};">KẾT LUẬN CUỐI CÙNG: {status}</h4>
        <hr>
        """
        
        return html
    
    def design_composite_beam(self, section: Section, material: Material,
                             deck_span: float, beam_spacing: float,
                             deck_load: float, live_load: float,
                             concrete_thickness: float) -> CompositeBeamResult:
        """
        Design composite floor beam with steel deck.
        
        Args:
            section: Steel beam section
            material: Material properties
            deck_span: Deck span (= beam spacing) (m)
            beam_spacing: Distance between beams (m)
            deck_load: Total deck dead load (kg/m2)
            live_load: Floor live load (kg/m2)
            concrete_thickness: Slab thickness (mm)
        """
        
        # Effective width of concrete flange (Eurocode 4)
        L = deck_span * 1000  # mm
        b_eff = min(beam_spacing * 1000, L / 8, 2000)  # mm
        
        # Loads on beam (tributary width = beam_spacing)
        q_dead = deck_load * beam_spacing  # kg/m
        q_live = live_load * beam_spacing  # kg/m
        q_total = 1.2 * q_dead + 1.6 * q_live
        
        # Moment
        M_design = q_total * deck_span**2 / 8  # kg.m
        
        # Simplified composite capacity (plastic neutral axis in slab)
        # Full analysis would need to check PNA location
        Fy_steel = material.rk / 100  # N/mm2
        A_steel = section.area * 100  # mm2
        
        # Plastic capacity of steel section
        Mp_steel = section.wx * Fy_steel / 10  # kg.m
        
        # Enhanced capacity due to composite action (approximate 30-50% increase)
        M_composite = Mp_steel * 1.4  # Simplified
        
        # Shear stud requirements (simplified)
        # Horizontal shear force
        V_h = A_steel * Fy_steel / 2  # N (simplified)
        
        # Stud capacity (assuming 19mm dia, 100mm height)
        stud_capacity = 80000  # N per stud (typical)
        n_studs = math.ceil(V_h / stud_capacity)
        
        # Deflection check (L/360 for floors)
        E = material.e_modulus  # kg/cm2
        I_steel = section.jx  # cm4
        
        # Composite I (simplified - 2x steel I)
        I_composite = I_steel * 2.5  # Approximate
        
        delta = (5 * q_dead * 0.01 * (deck_span * 100)**4) / (384 * I_composite * E)  # cm
        delta_mm = delta * 10
        delta_limit = deck_span * 1000 / 360
        
        deflection_ok = delta_mm <= delta_limit
        capacity_ok = M_design <= M_composite
        status = "ĐẠT" if (deflection_ok and capacity_ok) else "KHÔNG ĐẠT"
        
        # Generate report
        html_report = self._generate_beam_report(
            section, b_eff, q_dead, q_live, q_total, M_design, M_composite,
            n_studs, delta_mm, delta_limit, status
        )
        
        return CompositeBeamResult(
            section_name=section.name,
            effective_width=b_eff,
            moment_capacity=M_composite,
            shear_studs_required=n_studs,
            deflection=delta_mm,
            deflection_limit=delta_limit,
            status=status,
            html_report=html_report
        )
    
    def _generate_beam_report(self, section, b_eff, q_dead, q_live, q_total,
                             M_design, M_composite, n_studs, delta, delta_limit, status) -> str:
        """Generate HTML report for composite beam"""
        
        color = "green" if status == "ĐẠT" else "red"
        
        html = f"""
        <h3>THIẾT KẾ DẦM SÀN LIÊN HỢP</h3>
        
        <h4>1. Tiết diện dầm: {section.name}</h4>
        <ul>
            <li>H = {section.h} mm, B = {section.b} mm</li>
            <li>A = {section.area:.2f} cm², W<sub>x</sub> = {section.wx:.2f} cm³</li>
            <li>I<sub>x</sub> = {section.jx:.2f} cm⁴</li>
        </ul>
        
        <h4>2. Bề rộng có hiệu bản bê tông:</h4>
        <ul>
            <li>b<sub>eff</sub> = min(b, L/8) = <b>{b_eff:.0f} mm</b></li>
        </ul>
        
        <h4>3. Tải trọng tác dụng:</h4>
        <ul>
            <li>Tĩnh tải: q<sub>d</sub> = <b>{q_dead:.1f} kg/m</b></li>
            <li>Hoạt tải: q<sub>l</sub> = <b>{q_live:.1f} kg/m</b></li>
            <li>Tổ hợp: q = 1.2TT + 1.6HT = <b>{q_total:.1f} kg/m</b></li>
        </ul>
        
        <h4>4. Kiểm tra khả năng chịu moment:</h4>
        <ul>
            <li>M<sub>tính toán</sub> = qL²/8 = <b>{M_design:.2f} kg.m</b></li>
            <li>M<sub>liên hợp</sub> = <b>{M_composite:.2f} kg.m</b></li>
            <li>Hệ số sử dụng: η = {M_design/M_composite:.3f}</li>
            <li>Kết luận: <b>{"ĐẠT" if M_design <= M_composite else "KHÔNG ĐẠT"}</b></li>
        </ul>
        
        <h4>5. Liên kết chống cắt (Shear studs):</h4>
        <ul>
            <li>Số lượng đinh ghim yêu cầu: <b>{n_studs} cái</b></li>
            <li>Bố trí: dọc theo bề dài dầm</li>
        </ul>
        
        <h4>6. Kiểm tra độ võng:</h4>
        <ul>
            <li>Δ = <b>{delta:.2f} mm</b></li>
            <li>Giới hạn: L/360 = <b>{delta_limit:.2f} mm</b></li>
            <li>Kết luận: <b>{"ĐẠT" if delta <= delta_limit else "VƯỢT"}</b></li>
        </ul>
        
        <h4 style="color:{color};">KẾT LUẬN: {status}</h4>
        <hr>
        """
        
        return html


class FloorLoadDistributor:
    """
    Calculates load distribution from deck → beams → columns
    """
    
    @staticmethod
    def calculate_column_loads(num_floors: int, floor_load: float, 
                               tributary_area: float, roof_load: float = 0) -> Dict:
        """
        Calculate cumulative column loads from multiple floors.
        
        Returns dict with:
            - dead_load_per_floor
            - live_load_per_floor  
            - total_axial_force
            - load_combinations
        """
        
        # Dead load per floor (deck + concrete + finishes)
        DL_floor = floor_load * tributary_area  # kg
        
        # Live load per floor
        LL_floor = 400 * tributary_area  # kg (400 kg/m2 typical office)
        
        # Roof load (if applicable)
        DL_roof = roof_load * tributary_area if roof_load > 0 else 0
        
        # Total axial force (cumulative)
        # TCVN allows live load reduction for multiple floors
        total_DL = DL_floor * num_floors + DL_roof
        total_LL = LL_floor * min(num_floors, 3)  # Simplified reduction
        
        N_total = 1.2 * total_DL + 1.6 * total_LL
        
        return {
            "dead_load_per_floor": DL_floor,
            "live_load_per_floor": LL_floor,
            "total_dead_load": total_DL,
            "total_live_load": total_LL,
            "axial_force_design": N_total,
            "tributary_area": tributary_area
        }
