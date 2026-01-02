"""
Advanced structural analysis module for column stability, buckling, and second-order effects.
Implements TCVN 5575-2012 specifications for steel structure design.
"""

import math
from dataclasses import dataclass
from typing import Tuple, Dict
from src.logic.data_models import Section, Material


@dataclass
class StabilityResult:
    """Results from stability calculations"""
    lambda_x: float  # Slenderness ratio about x-axis
    lambda_y: float  # Slenderness ratio about y-axis
    lambda_critical: float  # Critical slenderness ratio
    phi_x: float  # Buckling coefficient x-axis
    phi_y: float  # Buckling coefficient y-axis
    phi_critical: float  # Critical buckling coefficient
    n_allow: float  # Allowable axial force
    status: str  # "OK" or "FAIL"
    details: str  # HTML formatted details


class StabilityCalculator:
    """
    Calculates column stability per TCVN 5575-2012.
    Includes slenderness checks, buckling analysis, and second-order effects.
    """
    
    def __init__(self):
        # TCVN 5575 buckling curve coefficients
        self.buckling_curves = {
            'a': {'alpha': 0.21, 'lambda_0': 0.2},  # Rolled sections, h/b ≤ 1.2
            'b': {'alpha': 0.34, 'lambda_0': 0.2},  # Rolled sections, h/b > 1.2
            'c': {'alpha': 0.49, 'lambda_0': 0.2},  # Welded sections
        }
    
    def calculate_slenderness(self, section: Section, L_eff_x: float, L_eff_y: float, 
                             material: Material) -> Tuple[float, float]:
        """
        Calculate slenderness ratios λ = L_eff / r
        
        Args:
            section: Cross-section properties
            L_eff_x: Effective length about x-axis (cm)
            L_eff_y: Effective length about y-axis (cm)
            material: Material properties
            
        Returns:
            (lambda_x, lambda_y): Slenderness ratios for both axes
        """
        # Radius of gyration (already in cm from section properties)
        rx = section.rx if hasattr(section, 'rx') else math.sqrt(section.jx / section.area)
        ry = section.ry if hasattr(section, 'ry') else math.sqrt(section.jy / section.area)
        
        lambda_x = L_eff_x / rx
        lambda_y = L_eff_y / ry
        
        return lambda_x, lambda_y
    
    def calculate_critical_slenderness(self, material: Material, stress_level: float = 1.0) -> float:
        """
        Calculate critical slenderness λ_cr = π√(E/Ry)
        
        Args:
            material: Material properties
            stress_level: Stress level factor (default 1.0)
            
        Returns:
            Critical slenderness ratio
        """
        # E in kg/cm², Rk in kg/cm²
        E = material.e_modulus
        Ry = material.rk * stress_level
        
        lambda_cr = math.pi * math.sqrt(E / Ry)
        return lambda_cr
    
    def calculate_buckling_coefficient(self, lambda_ratio: float, curve_type: str = 'b') -> float:
        """
        Calculate buckling reduction coefficient φ using TCVN 5575 formulae.
        
        φ = 1 / [Φ + √(Φ² - λ̄²)]
        where Φ = 0.5[1 + α(λ̄ - λ₀) + λ̄²]
        λ̄ = λ / λcr (normalized slenderness)
        
        Args:
            lambda_ratio: Normalized slenderness λ̄ = λ/λcr
            curve_type: Buckling curve ('a', 'b', or 'c')
            
        Returns:
            Buckling coefficient φ
        """
        curve = self.buckling_curves.get(curve_type, self.buckling_curves['b'])
        alpha = curve['alpha']
        lambda_0 = curve['lambda_0']
        
        # For λ̄ ≤ 0.2, no reduction
        if lambda_ratio <= 0.2:
            return 1.0
        
        # Calculate Φ
        Phi_cap = 0.5 * (1 + alpha * (lambda_ratio - lambda_0) + lambda_ratio**2)
        
        # Calculate φ
        discriminant = Phi_cap**2 - lambda_ratio**2
        if discriminant < 0:
            # Extremely slender - use minimum value
            return 0.1
        
        phi = 1.0 / (Phi_cap + math.sqrt(discriminant))
        
        # Limit φ to reasonable range
        return max(0.1, min(1.0, phi))
    
    def check_column_stability(self, section: Section, material: Material, 
                               N_design: float, L_x: float, L_y: float,
                               k_x: float = 1.0, k_y: float = 1.0,
                               curve_type: str = 'b') -> StabilityResult:
        """
        Complete stability check for compression member.
        
        Args:
            section: Cross-section properties
            material: Material properties
            N_design: Design axial force (kg, positive = compression)
            L_x: Unbraced length about x-axis (cm)
            L_y: Unbraced length about y-axis (cm)
            k_x: Effective length factor for x-axis (default 1.0)
            k_y: Effective length factor for y-axis (default 1.0)
            curve_type: Buckling curve type
            
        Returns:
            StabilityResult with all calculation details
        """
        # 1. Effective lengths
        L_eff_x = k_x * L_x
        L_eff_y = k_y * L_y
        
        # 2. Slenderness ratios
        lambda_x, lambda_y = self.calculate_slenderness(section, L_eff_x, L_eff_y, material)
        lambda_critical = self.calculate_critical_slenderness(material)
        
        # 3. Normalized slenderness
        lambda_bar_x = lambda_x / lambda_critical
        lambda_bar_y = lambda_y / lambda_critical
        
        # 4. Buckling coefficients
        phi_x = self.calculate_buckling_coefficient(lambda_bar_x, curve_type)
        phi_y = self.calculate_buckling_coefficient(lambda_bar_y, curve_type)
        
        # 5. Critical buckling coefficient (minimum)
        phi_critical = min(phi_x, phi_y)
        critical_axis = 'x' if phi_x < phi_y else 'y'
        lambda_critical_axis = lambda_x if critical_axis == 'x' else lambda_y
        
        # 6. Allowable axial force
        # N_allow = φ × A × Ry
        N_allow = phi_critical * section.area * material.rk
        
        # 7. Check status
        utilization = N_design / N_allow if N_allow > 0 else 999
        status = "OK" if utilization <= 1.0 else "FAIL"
        
        # 8. Generate detailed HTML report
        details = self._generate_stability_html(
            section, material, N_design, L_x, L_y, k_x, k_y,
            L_eff_x, L_eff_y, lambda_x, lambda_y, lambda_critical,
            lambda_bar_x, lambda_bar_y, phi_x, phi_y, phi_critical,
            critical_axis, N_allow, utilization, status
        )
        
        return StabilityResult(
            lambda_x=lambda_x,
            lambda_y=lambda_y,
            lambda_critical=lambda_critical,
            phi_x=phi_x,
            phi_y=phi_y,
            phi_critical=phi_critical,
            n_allow=N_allow,
            status=status,
            details=details
        )
    
    def _generate_stability_html(self, section, material, N_design, L_x, L_y, k_x, k_y,
                                 L_eff_x, L_eff_y, lambda_x, lambda_y, lambda_cr,
                                 lambda_bar_x, lambda_bar_y, phi_x, phi_y, phi_critical,
                                 critical_axis, N_allow, utilization, status) -> str:
        """Generate detailed HTML report for stability calculations"""
        
        color = "green" if status == "OK" else "red"
        
        html = f"""
        <h4>Kiểm tra ổn định cho cấu kiện chịu nén: {section.name}</h4>
        
        <h5>1. Thông số đầu vào:</h5>
        <ul>
            <li>Lực nén tính toán: N = <b>{N_design:.2f} kg</b></li>
            <li>Chiều dài không giằng: L<sub>x</sub> = {L_x/100:.2f} m, L<sub>y</sub> = {L_y/100:.2f} m</li>
            <li>Hệ số chiều dài tính toán: k<sub>x</sub> = {k_x}, k<sub>y</sub> = {k_y}</li>
        </ul>
        
        <h5>2. Chiều dài tính toán:</h5>
        <ul>
            <li>L<sub>eff,x</sub> = k<sub>x</sub> × L<sub>x</sub> = {k_x} × {L_x/100:.2f} = <b>{L_eff_x/100:.2f} m</b></li>
            <li>L<sub>eff,y</sub> = k<sub>y</sub> × L<sub>y</sub> = {k_y} × {L_y/100:.2f} = <b>{L_eff_y/100:.2f} m</b></li>
        </ul>
        
        <h5>3. Độ mảnh:</h5>
        <ul>
            <li>r<sub>x</sub> = √(I<sub>x</sub>/A) = <b>{section.rx:.2f} cm</b></li>
            <li>r<sub>y</sub> = √(I<sub>y</sub>/A) = <b>{section.ry:.2f} cm</b></li>
            <li>λ<sub>x</sub> = L<sub>eff,x</sub> / r<sub>x</sub> = {L_eff_x:.1f} / {section.rx:.2f} = <b>{lambda_x:.2f}</b></li>
            <li>λ<sub>y</sub> = L<sub>eff,y</sub> / r<sub>y</sub> = {L_eff_y:.1f} / {section.ry:.2f} = <b>{lambda_y:.2f}</b></li>
            <li>λ<sub>cr</sub> = π√(E/R<sub>y</sub>) = π√({material.e_modulus}/{material.rk}) = <b>{lambda_cr:.2f}</b></li>
        </ul>
        
        <h5>4. Độ mảnh tương đối:</h5>
        <ul>
            <li>λ̄<sub>x</sub> = λ<sub>x</sub> / λ<sub>cr</sub> = {lambda_x:.2f} / {lambda_cr:.2f} = <b>{lambda_bar_x:.3f}</b></li>
            <li>λ̄<sub>y</sub> = λ<sub>y</sub> / λ<sub>cr</sub> = {lambda_y:.2f} / {lambda_cr:.2f} = <b>{lambda_bar_y:.3f}</b></li>
        </ul>
        
        <h5>5. Hệ số ổn định (TCVN 5575):</h5>
        <ul>
            <li>φ<sub>x</sub> = <b>{phi_x:.4f}</b> (theo đường cong uốn dọc)</li>
            <li>φ<sub>y</sub> = <b>{phi_y:.4f}</b> (theo đường cong uốn dọc)</li>
            <li>φ<sub>min</sub> = min(φ<sub>x</sub>, φ<sub>y</sub>) = <b>{phi_critical:.4f}</b></li>
            <li>Trục nguy hiểm: <b>{critical_axis.upper()}</b></li>
        </ul>
        
        <h5>6. Kiểm tra khả năng chịu lực:</h5>
        <ul>
            <li>Lực nén cho phép: N<sub>allow</sub> = φ × A × R<sub>y</sub></li>
            <li>N<sub>allow</sub> = {phi_critical:.4f} × {section.area:.2f} × {material.rk} = <b>{N_allow:.2f} kg</b></li>
            <li>Hệ số sử dụng: η = N / N<sub>allow</sub> = {N_design:.2f} / {N_allow:.2f} = <b>{utilization:.3f}</b></li>
            <li>Kết luận: <span style="color:{color}; font-weight:bold; font-size:1.1em;">{status}</span></li>
        </ul>
        
        <hr>
        """
        
        return html


class LateralTorsionalBuckling:
    """
    Lateral-torsional buckling analysis for beams (TCVN 5575).
    """
    
    @staticmethod
    def calculate_critical_moment(I_y: float, I_w: float, G: float, E: float, 
                                  L: float, C1: float = 1.0) -> float:
        """
        Calculate critical lateral-torsional buckling moment.
        
        M_cr = C1 × (π²EI_y / L²) × √(GI_w / (π²EI_y / L²) + 1)
        
        Simplified for typical I-sections:
        M_cr ≈ C1 × √(π²EI_y × GI_t) / L
        """
        # Simplified formula for typical cases
        M_cr = C1 * math.sqrt(math.pi**2 * E * I_y * G * I_w) / L
        return M_cr
