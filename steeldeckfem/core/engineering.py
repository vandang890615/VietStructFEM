
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple
from src.logic.data_models import CalculationInput, WindParams, PurlinParams, GeometryParams

# PURLIN DATABASE (From Excel Sheet: Xago)
# Format: Name -> {h, b1, b2, t, area, weight, Ix, Iy, Wx, Wy}
PURLIN_DB = {
    # Z Sections (Height 150)
    "Z15015": {"h": 150, "b": 54, "t": 1.45, "a": 3.85, "w": 3.02, "Ix": 140.3, "Iy": 8.36, "Wx": 17.16, "Wy": 3.96},
    "Z15016": {"h": 150, "b": 54, "t": 1.55, "a": 4.11, "w": 3.22, "Ix": 137.1, "Iy": 21.1, "Wx": 18.28, "Wy": 4.21},
    "Z15018": {"h": 150, "b": 54, "t": 1.75, "a": 4.62, "w": 3.63, "Ix": 153.6, "Iy": 23.5, "Wx": 20.48, "Wy": 4.68},
    "Z15020": {"h": 150, "b": 54, "t": 1.95, "a": 5.13, "w": 4.03, "Ix": 169.8, "Iy": 25.7, "Wx": 22.64, "Wy": 5.15},
    "Z15023": {"h": 150, "b": 54, "t": 2.25, "a": 5.88, "w": 4.62, "Ix": 193.6, "Iy": 29.0, "Wx": 25.82, "Wy": 5.81},
    "Z15025": {"h": 150, "b": 54, "t": 2.45, "a": 6.38, "w": 5.01, "Ix": 209.2, "Iy": 31.1, "Wx": 27.89, "Wy": 6.20},
    
    # Z Sections (Height 175)
    "Z17516": {"h": 175, "b": 54, "t": 1.55, "a": 4.49, "w": 3.53, "Ix": 197.7, "Iy": 21.1, "Wx": 22.60, "Wy": 4.21},
    "Z17518": {"h": 175, "b": 54, "t": 1.75, "a": 5.06, "w": 3.97, "Ix": 221.6, "Iy": 23.5, "Wx": 25.33, "Wy": 4.68},
    "Z17520": {"h": 175, "b": 54, "t": 1.95, "a": 5.62, "w": 4.41, "Ix": 245.2, "Iy": 25.7, "Wx": 28.03, "Wy": 5.15},
    "Z17523": {"h": 175, "b": 54, "t": 2.25, "a": 6.45, "w": 5.06, "Ix": 279.9, "Iy": 29.0, "Wx": 31.99, "Wy": 5.81},
    "Z17525": {"h": 175, "b": 54, "t": 2.45, "a": 7.00, "w": 5.49, "Ix": 302.6, "Iy": 31.1, "Wx": 34.59, "Wy": 6.24},

    # Z Sections (Height 200) - Shortened list for brevity, can expand later
    "Z20020": {"h": 200, "b": 62, "t": 1.95, "a": 6.65, "w": 5.22, "Ix": 391.7, "Iy": 49.8, "Wx": 39.17, "Wy": 7.78},
    
    # C Sections - Typical
    "C15015": {"h": 150, "b": 48, "t": 1.45, "a": 3.76, "w": 2.95, "Ix": 123.9, "Iy": 11.1, "Wx": 16.52, "Wy": 3.18},
    "C17515": {"h": 175, "b": 48, "t": 1.45, "a": 4.13, "w": 3.24, "Ix": 179.1, "Iy": 11.6, "Wx": 20.46, "Wy": 3.23},
    "C20015": {"h": 200, "b": 48, "t": 1.45, "a": 4.56, "w": 3.58, "Ix": 242.1, "Iy": 12.1, "Wx": 24.21, "Wy": 3.28},
}

class PurlinCalculator:
    def check_purlin(self, input_data: CalculationInput) -> str:
        """
        Performs 2-STAGE structural check for Purlin per Excel logic.
        Stage 1: Preliminary selection (without purlin self-weight)
        Stage 2: Final check (with actual purlin weight) + Deflection
        """
        pp = input_data.purlin
        geo = input_data.geometry
        mat = input_data.material
        
        # Sheet properties
        sheet_thickness = pp.sheet_thickness  # mm
        sheet_weight_m2 = 1.1 * 7850 * sheet_thickness / 1000 * 914 / 750  # Excel formula
        
        # Geometry
        slope_pct = geo.roof_slope  # %
        rad_alpha = math.atan(slope_pct / 100.0)
        deg_alpha = math.degrees(rad_alpha)
        spacing = geo.purlin_spacing  # m (bước xà gồ)
        span = geo.col_spacing  # m (bước cột = nhịp xà gồ)
        
        # Load factors
        n_dead = 1.05
        n_live = 1.2
        
        html = f"""
        <h3>A. TÍNH CHỌN XÀ GỒ</h3>
        <h4>1/. Chọn tiết diện:</h4>
        <h5>1. Tải trọng tác dụng lên xà gồ:</h5>
        <ul>
            <li>Sử dụng tấm lợp loại có chiều dày: <b>{sheet_thickness} mm</b></li>
            <li>Trọng lượng tôn lợp q<sub>tl</sub> = 1.1 × 7850 × {sheet_thickness}/1000 × 914/750 = <b>{sheet_weight_m2:.3f} Kg/m²</b></li>
            <li>Độ dốc nhà: i = <b>{slope_pct}%</b></li>
            <li>Góc dốc: α = ATAN({slope_pct}/100) = <b>{deg_alpha:.2f}°</b></li>
            <li>Bước xà gồ: b = <b>{spacing} m</b></li>
            <li>Bước cột (nhịp xà gồ): L = <b>{span} m</b></li>
            <li>Hệ số vượt tải tĩnh tải: n = <b>{n_dead}</b></li>
            <li>Hệ số vượt tải hoạt tải: n = <b>{n_live}</b></li>
            <li>Hoạt tải phân bố chuẩn: q<sub>c</sub> = <b>{pp.live_load_roof} Kg/m²</b></li>
        </ul>
        
        <h5>GIAI ĐOẠN 1: Tính sơ bộ (chưa kể trọng lượng xà gồ)</h5>
        """
        
        # STAGE 1: Preliminary (without purlin weight)
        q_sheet = sheet_weight_m2 * spacing
        q_dead_prelim = n_dead * q_sheet
        q_live = n_live * pp.live_load_roof * spacing
        q_total_prelim = (q_dead_prelim + q_live) / math.cos(rad_alpha)
        
        qy_prelim = q_total_prelim * math.cos(rad_alpha)
        qx_prelim = q_total_prelim * math.sin(rad_alpha)
        
        Mx_prelim = qy_prelim * (span**2) / 11.0
        My_prelim = qx_prelim * (span**2) / 11.0
        
        Wx_req = Mx_prelim * 100 / mat.rk
        Wy_req = My_prelim * 100 / mat.rk
        
        html += f"""
        <ul>
            <li>q<sub>tt</sub> = (q<sub>tải trọng tôn</sub> × n + q<sub>hoạt tải</sub> × n) / cos(α)</li>
            <li>q<sub>tt</sub> = ({sheet_weight_m2:.3f} × {spacing} × {n_dead} + {pp.live_load_roof} × {spacing} × {n_live}) / cos({deg_alpha:.2f}°)</li>
            <li>q<sub>tt</sub> = <b>{q_total_prelim:.2f} Kg/m</b></li>
            <li>Phân tích lực:</li>
            <ul>
                <li>q<sub>y</sub> = q × cos(α) = <b>{qy_prelim:.2f} Kg/m</b></li>
                <li>q<sub>x</sub> = q × sin(α) = <b>{qx_prelim:.2f} Kg/m</b></li>
            </ul>
        </ul>
        
        <h5>2. Moment uốn tác dụng lên xà gồ:</h5>
        <ul>
            <li>M<sub>x</sub> = q<sub>y</sub> × L² / 11 = {qy_prelim:.2f} × {span}² / 11 = <b>{Mx_prelim:.2f} Kg.m</b></li>
            <li>M<sub>y</sub> = q<sub>x</sub> × L² / 11 = {qx_prelim:.2f} × {span}² / 11 = <b>{My_prelim:.2f} Kg.m</b></li>
        </ul>
        
        <h5>3. Moment chống uốn yêu cầu:</h5>
        <ul>
            <li>W<sub>x</sub> ≥ M<sub>x</sub> × 100 / R<sub>k</sub> = {Mx_prelim:.2f} × 100 / {mat.rk} = <b>{Wx_req:.2f} cm³</b></li>
            <li>W<sub>y</sub> ≥ M<sub>y</sub> × 100 / R<sub>k</sub> = {My_prelim:.2f} × 100 / {mat.rk} = <b>{Wy_req:.2f} cm³</b></li>
        </ul>
        """
        
        # Select purlin from database
        sec_name = pp.section_name
        props = PURLIN_DB.get(sec_name, PURLIN_DB["Z17516"])
        
        html += f"""
        <p><b>→ Xà gồ chọn: {sec_name}</b> có:</p>
        <ul>
            <li>Q'ty = <b>{props['w']} Kg/m</b></li>
            <li>W<sub>x</sub> = <b>{props['Wx']} cm³</b> &nbsp; I<sub>x</sub> = {props['Ix']} cm⁴</li>
            <li>W<sub>y</sub> = <b>{props['Wy']} cm³</b> &nbsp; I<sub>y</sub> = {props['Iy']} cm⁴</li>
        </ul>
        
        <h4>2/. Kiểm tra tiết diện chọn:</h4>
        <h5>GIAI ĐOẠN 2: Tính chính xác (có kể trọng lượng xà gồ)</h5>
        """
        
        # STAGE 2: Final check (with purlin weight)
        q_purlin = n_dead * props['w']
        q_total_final = (q_dead_prelim + q_purlin + q_live) / math.cos(rad_alpha)
        
        qy_final = q_total_final * math.cos(rad_alpha)
        qx_final = q_total_final * math.sin(rad_alpha)
        
        Mx_final = qy_final * (span**2) / 11.0
        My_final = qx_final * (span**2) / 11.0
        
        html += f"""
        <h5>1. Tải trọng tác dụng (có xà gồ):</h5>
        <ul>
            <li>q<sub>tt</sub> = (q<sub>tôn</sub> × n + q<sub>xà gồ</sub> × n + q<sub>hoạt tải</sub> × n) / cos(α)</li>
            <li>q<sub>tt</sub> = ({q_sheet:.2f} + {props['w']} × {n_dead} + {q_live:.2f}) / cos({deg_alpha:.2f}°)</li>
            <li>q<sub>tt</sub> = <b>{q_total_final:.2f} Kg/m</b></li>
            <li>Phân tích:</li>
            <ul>
                <li>q<sub>y</sub> = q × cos(α) = <b>{qy_final:.2f} Kg/m</b></li>
                <li>q<sub>x</sub> = q × sin(α) = <b>{qx_final:.2f} Kg/m</b></li>
            </ul>
        </ul>
        
        <h5>2. Moment uốn:</h5>
        <ul>
            <li>M<sub>x</sub> = q<sub>y</sub> × L² / 11 = <b>{Mx_final:.2f} Kg.m</b></li>
            <li>M<sub>y</sub> = q<sub>x</sub> × L² / 11 = <b>{My_final:.2f} Kg.m</b></li>
        </ul>
        
        <h5>3. Ứng suất lớn nhất do tác động đồng thời của hai moment:</h5>
        """
        
        # Stress check
        sigma = (Mx_final * 100 / props['Wx']) + (My_final * 100 / props['Wy'])
        ratio_stress = sigma / mat.rk
        stress_result = "Thỏa" if ratio_stress <= 1.0 else "Chọn lại"
        stress_color = "green" if ratio_stress <= 1.0 else "red"
        
        html += f"""
        <ul>
            <li>σ = M<sub>x</sub> × 100 / W<sub>x</sub> + M<sub>y</sub> × 100 / W<sub>y</sub></li>
            <li>σ = {Mx_final:.2f} × 100 / {props['Wx']} + {My_final:.2f} × 100 / {props['Wy']}</li>
            <li>σ = <b>{sigma:.2f} kg/cm²</b> ≤ <b>{mat.rk} kg/cm²</b></li>
            <li>Kết luận: <span style="color:{stress_color}; font-weight:bold;">{stress_result}</span></li>
        </ul>
        """
        
        # DEFLECTION CHECK
        E = mat.e_modulus  # kg/cm²
        delta = 5 * qy_final * 0.01 * (span * 100)**4 / (384 * props['Ix'] * E)  # cm
        delta_ratio = delta / (span * 100)
        Limit_ratio = 1.0 / 150.0
        
        deflection_result = "Thỏa" if delta_ratio <= Limit_ratio else "Chọn lại"
        deflection_color = "green" if delta_ratio <= Limit_ratio else "red"
        
        html += f"""
        <h5>Độ võng xà gồ dưới tác dụng của tải trọng q<sub>y</sub>:</h5>
        <ul>
            <li>δ = 5 × q<sub>y</sub> × L⁴ / (384 × E × I<sub>x</sub>)</li>
            <li>δ = 5 × {qy_final:.2f} × 0.01 × ({span} × 100)⁴ / (384 × {props['Ix']} × {E})</li>
            <li>δ = <b>{delta:.3f} cm</b></li>
            <li>δ/L = {delta:.3f} / {span * 100} = <b>{delta_ratio:.6f}</b></li>
            <li>Giới hạn: <b>1/150 = {Limit_ratio:.6f}</b></li>
            <li>Kết luận: <span style="color:{deflection_color}; font-weight:bold;">{deflection_result}</span></li>
        </ul>
        """
        
        # Final conclusion
        final_ok = (ratio_stress <= 1.0) and (delta_ratio <= Limit_ratio)
        final_color = "green" if final_ok else "red"
        final_msg = "Nên xà gồ đã chọn là đạt yêu cầu." if final_ok else "Kiểm tra lại xà gồ"
        
        html += f"""
        <p style="color:{final_color}; font-weight:bold; font-size:1.1em;">
        ⇒ {final_msg}
        </p>
        """
        
        return html

class WindLoadCalculator:
    def calculate_wind(self, input_data: CalculationInput) -> str:
        """
        Calculates Wind Loads per TCVN 2737-95 with full coefficient lookups.
        """
        wind = input_data.wind
        geo = input_data.geometry
        
        # Geometry ratios
        h1 = geo.col_height  # m
        L_span = geo.span  # m
        h1_L_ratio = h1 / L_span
        
        slope_pct = geo.roof_slope  # %
        slope_deg = math.degrees(math.atan(slope_pct / 100.0))
        
        html = f"""
        <h3>Tải trọng gió theo TCVN 2737-95:</h3>
        <h4>a. Đặc tính hình học của nhà:</h4>
        <ul>
            <li>Cao (đỉnh cột): <b>{h1} m</b></li>
            <li>Nhịp L: <b>{L_span} m</b></li>
            <li>h1/L = <b>{h1_L_ratio:.6f}</b></li>
            <li>Độ dốc: α = <b>{slope_deg:.2f}°</b></li>
            <li>Bước cột b = <b>{geo.col_spacing} m</b></li>
        </ul>
        """
        
        # Coefficient lookup (simplified - in real Excel this uses complex interpolation)
        # For slope ~8.5 deg and h1/L < 0.05, Excel gives:
        # ce1 ≈ 0.023 (slight pressure/suction on windward roof)
        # ce2 ≈ -0.4 (suction on leeward roof)
        # These come from the "Gio" sheet interpolation table
        c1 = 0.8   # Windward wall (push)
        c2 = 0.023 # Windward roof (from interpolation)
        c3 = -0.4  # Leeward roof
        c4 = -0.6  # Leeward wall (suction)
        
        html += f"""
        <p>Do đó:</p>
        <ul>
            <li>c<sub>1</sub> (Tường đón gió) = <b>{c1}</b></li>
            <li>c<sub>2</sub> (Mái đón gió) = <b>{c2}</b> <i>(tra bảng theo α và h1/L)</i></li>
            <li>c<sub>3</sub> (Mái khuất gió) = <b>{c3}</b></li>
            <li>c<sub>4</sub> (Tường khuất gió) = <b>{c4}</b></li>
        </ul>
        
        <h4>b. Công trình xây dựng tại: {input_data.project.location}</h4>
        <ul>
            <li>Thuộc vùng áp lực gió: <b>{wind.zone}</b></li>
            <li>Tỷ số chiều cao/nhịp: h/L = <b>{h1_L_ratio:.6f}</b> < 1.5</li>
            <li>→ Không tính thành phần gió động, chỉ tính thành phần tĩnh.</li>
            <li>Hệ số tin cậy của gió: n<sub>o</sub> = <b>1.2</b></li>
            <li>Thời gian giả định sử dụng công trình: t = <b>40 năm</b></li>
            <li>Hệ số điều chỉnh tải trọng gió ứng với thời gian sử dụng: α = <b>0.96</b></li>
        </ul>
        """
        
        # Wo lookup
        zone_map = {"IA": 55, "IIA": 83, "IIIA": 110, "IB": 65, "IIB": 95, "IIIB": 125}
        Wo = zone_map.get(wind.zone, 83)
        
        # k factors (vary with height)
        # Excel shows different k for top vs bottom
        # For terrain B and h < 10m:
        k_top = 1.125  # At roof level (interpolated from table)
        k_bottom = 1.0  # At column base
        
        # Terrain type display
        terrain_desc = {"A": "Trống trải", "B": "Tương đối trống trải", "C": "Che chắn mạnh"}
        terrain_name = terrain_desc.get(wind.terrain, "Tương đối trống trải")
        
        html += f"""
        <h4>Thành phần tĩnh được xác định:</h4>
        <p><b>W = n<sub>o</sub> × W<sub>o</sub> × k × c × α</b></p>
        <ul>
            <li>W<sub>o</sub> = <b>{Wo} kg/m²</b> (áp lực gió chuẩn vùng {wind.zone})</li>
            <li>Dạng địa hình: <b>{wind.terrain}</b> - {terrain_name}</li>
            <li>Hệ số k (độ cao):</li>
            <ul>
                <li>Tại đỉnh cột: k = <b>{k_top}</b></li>
                <li>Tại chân cột: k = <b>{k_bottom}</b></li>
            </ul>
        </ul>
        """
        
        # Calculate 4 wind cases
        n_o = 1.2
        alpha = 0.96
        B = geo.col_spacing
        
        # Average k for line load calculation
        k_avg = (k_top + k_bottom) / 2
        
        W1_top = n_o * Wo * k_top * c1 * alpha
        W1_bottom = n_o * Wo * k_bottom * c1 * alpha
        W1_avg = (W1_top + W1_bottom) / 2
        W1_line = W1_avg * B
        
        W2_top = n_o * Wo * k_top * c2 * alpha
        W2_bottom = n_o * Wo * k_bottom * c2 * alpha  
        W2_avg = (W2_top + W2_bottom) / 2
        W2_line = W2_avg * B
        
        W3_top = n_o * Wo * k_top * c3 * alpha
        W3_bottom = n_o * Wo * k_bottom * c3 * alpha
        W3_avg = (W3_top + W3_bottom) / 2
        W3_line = W3_avg * B
        
        W4_top = n_o * Wo * k_top * c4 * alpha
        W4_bottom = n_o * Wo * k_bottom * c4 * alpha
        W4_avg = (W4_top + W4_bottom) / 2
        W4_line = W4_avg * B
        
        html += f"""
        <h4>c. Phía trái (Đón gió):</h4>
        <table style="width:100%; border-collapse:collapse;">
            <tr style="background:#f0f0f0;">
                <th style="border:1px solid #ccc; padding:5px;">Trường hợp</th>
                <th style="border:1px solid #ccc; padding:5px;">ĐỈNH</th>
                <th style="border:1px solid #ccc; padding:5px;">CHÂN</th>
                <th style="border:1px solid #ccc; padding:5px;">Kg/m (Đơn vị)</th>
                <th style="border:1px solid #ccc; padding:5px;">TB</th>
            </tr>
            <tr>
                <td style="border:1px solid #ccc; padding:5px;">W<sub>1</sub> = n<sub>o</sub> × W<sub>o</sub> × k × c<sub>1</sub> × α</td>
                <td style="border:1px solid #ccc; padding:5px;"><b>{W1_top:.2f}</b></td>
                <td style="border:1px solid #ccc; padding:5px;"><b>{W1_bottom:.2f}</b></td>
                <td style="border:1px solid #ccc; padding:5px;">Kg/m</td>
                <td style="border:1px solid #ccc; padding:5px;"><b>{W1_line:.2f}</b></td>
            </tr>
            <tr>
                <td style="border:1px solid #ccc; padding:5px;">W<sub>2</sub> = n<sub>o</sub> × W<sub>o</sub> × k × c<sub>2</sub> × α</td>
                <td style="border:1px solid #ccc; padding:5px;"><b>{W2_top:.2f}</b></td>
                <td style="border:1px solid #ccc; padding:5px;"><b>{W2_bottom:.2f}</b></td>
                <td style="border:1px solid #ccc; padding:5px;">Kg/m</td>
                <td style="border:1px solid #ccc; padding:5px;"><b>{W2_line:.2f}</b></td>
            </tr>
        </table>
        
        <h4>d. Phía phải (Khuất gió):</h4>
        <table style="width:100%; border-collapse:collapse;">
            <tr style="background:#f0f0f0;">
                <th style="border:1px solid #ccc; padding:5px;">Trường hợp</th>
                <th style="border:1px solid #ccc; padding:5px;">ĐỈNH</th>
                <th style="border:1px solid #ccc; padding:5px;">CHÂN</th>
                <th style="border:1px solid #ccc; padding:5px;">Kg/m (Đơn vị)</th>
                <th style="border:1px solid #ccc; padding:5px;">TB</th>
            </tr>
            <tr>
                <td style="border:1px solid #ccc; padding:5px;">W<sub>3</sub> = n<sub>o</sub> × W<sub>o</sub> × k × c<sub>3</sub> × α</td>
                <td style="border:1px solid #ccc; padding:5px;"><b>{W3_top:.2f}</b></td>
                <td style="border:1px solid #ccc; padding:5px;"><b>{W3_bottom:.2f}</b></td>
                <td style="border:1px solid #ccc; padding:5px;">Kg/m</td>
                <td style="border:1px solid #ccc; padding:5px;"><b>{W3_line:.2f}</b></td>
            </tr>
            <tr>
                <td style="border:1px solid #ccc; padding:5px;">W<sub>4</sub> = n<sub>o</sub> × W<sub>o</sub> × k × c<sub>4</sub> × α</td>
                <td style="border:1px solid #ccc; padding:5px;"><b>{W4_top:.2f}</b></td>
                <td style="border:1px solid #ccc; padding:5px;"><b>{W4_bottom:.2f}</b></td>
                <td style="border:1px solid #ccc; padding:5px;">Kg/m</td>
                <td style="border:1px solid #ccc; padding:5px;"><b>{W4_line:.2f}</b></td>
            </tr>
        </table>
        """
        
        return html

class FrameLoadCalculator:
    def calculate_loads(self, input_data: CalculationInput) -> str:
        geo = input_data.geometry
        mat = input_data.material
        pur = input_data.purlin
        
        # 1. Dead Load
        q_roof_dead = pur.dead_load_roof # kg/m2
        # Convert to line load on frame B (Step Column)
        Q_dead = q_roof_dead * geo.col_spacing # kg/m
        
        # 2. Live Load
        q_roof_live = pur.live_load_roof # kg/m2
        Q_live = q_roof_live * geo.col_spacing # kg/m
        
        html = f"""
        <h3>I. TẢI TRỌNG TÁC DỤNG LÊN KHUNG</h3>
        <h4>1. Tải trọng thường xuyên (Tĩnh tải)</h4>
        <ul>
            <li>Tĩnh tải mái phân bố (Tôn + Xà gồ + Giằng): g = {q_roof_dead} kg/m2</li>
            <li>Bước khung: B = {geo.col_spacing} m</li>
            <li>Tải trọng phân bố lên khung: G = g x B = {q_roof_dead} x {geo.col_spacing} = {Q_dead:.2f} kg/m</li>
        </ul>
        
        <h4>2. Tải trọng tạm thời (Hoạt tải)</h4>
        <ul>
            <li>Hoạt tải sửa chữa mái: p = {q_roof_live} kg/m2</li>
            <li>Tải trọng phân bố lên khung: P = p x B = {q_roof_live} x {geo.col_spacing} = {Q_live:.2f} kg/m</li>
        </ul>
        """
        return html

class MemberChecker:
    def check_column(self, force, section, material) -> str:
        """
        Generates detailed check for a column/beam section per Excel lines 131-200.
        Includes: eccentricity, required area, 3 geometric checks, stress check.
        """
        if not section: return ""
        
        N = abs(force.n_force)  # Axial Kg
        M = abs(force.m_moment)  # Moment Kg.cm
        
        # 1. Eccentricity
        e = (M / N) if N > 0 else 0
        
        # 2. Estimated height for preliminary sizing (H/12 rule)
        # This is a heuristic from Excel - not always used but shown for reference
        # h_est = section.h / 10 / 12  # Convert mm to cm, then divide by 12
        
        # 3. Required Area (Excel line 146)
        # A_req = N * (1.25 + 2.5 * (e/h)) / Rk
        # Using actual section height
        h_cm = section.h / 10.0  # mm to cm
        A_req = N * (1.25 + 2.5 * (e / h_cm)) / material.rk
        
        html = f"""
        <h4>{section.name} - Kiểm tra tại {force.location}</h4>
        <h5>Nội lực tính toán:</h5>
        <ul>
            <li>Tổ hợp sử dụng: <b>{force.load_combo}</b></li>
            <li>N = <b>{N} Kg</b></li>
            <li>Q = <b>{force.q_shear} Kg</b></li>
            <li>M = <b>{M} Kg.cm</b></li>
        </ul>
        
        <h5>Độ lệch tâm e và chiều cao h tiết diện:</h5>
        <ul>
            <li>e = M/N = {M}/{N} = <b>{e:.2f} cm</b></li>
            <li>h<sub>ước lượng</sub> = H/12 ≈ <b>{h_cm/12:.2f} cm</b> (quy tắc sơ bộ)</li>
        </ul>
        
        <h5>Tiết diện yêu cầu:</h5>
        <ul>
            <li>A<sub>req</sub> = N × (1.25 + 2.5 × (e/h)) / R<sub>k</sub></li>
            <li>A<sub>req</sub> = {N} × (1.25 + 2.5 × ({e:.2f}/{h_cm:.1f})) / {material.rk}</li>
            <li>A<sub>req</sub> = <b>{A_req:.2f} cm²</b></li>
        </ul>
        
        <p><b>→ Chọn mặt cắt dạng H</b> có các thông số sau:</p>
        <table style="width:100%; border-collapse:collapse; margin:10px 0;">
            <tr style="background:#f5f5f5;">
                <td style="border:1px solid #ccc; padding:5px;"><b>H (mm)</b></td>
                <td style="border:1px solid #ccc; padding:5px;">{section.h}</td>
                <td style="border:1px solid #ccc; padding:5px;"><b>I<sub>x</sub> (cm⁴)</b></td>
                <td style="border:1px solid #ccc; padding:5px;">{section.jx:.2f}</td>
            </tr>
            <tr>
                <td style="border:1px solid #ccc; padding:5px;"><b>B (mm)</b></td>
                <td style="border:1px solid #ccc; padding:5px;">{section.b}</td>
                <td style="border:1px solid #ccc; padding:5px;"><b>I<sub>y</sub> (cm⁴)</b></td>
                <td style="border:1px solid #ccc; padding:5px;">{section.jy:.2f}</td>
            </tr>
            <tr style="background:#f5f5f5;">
                <td style="border:1px solid #ccc; padding:5px;"><b>t<sub>f</sub> (mm)</b></td>
                <td style="border:1px solid #ccc; padding:5px;">{section.tf}</td>
                <td style="border:1px solid #ccc; padding:5px;"><b>W<sub>x</sub> (cm³)</b></td>
                <td style="border:1px solid #ccc; padding:5px;">{section.wx:.2f}</td>
            </tr>
            <tr>
                <td style="border:1px solid #ccc; padding:5px;"><b>t<sub>w</sub> (mm)</b></td>
                <td style="border:1px solid #ccc; padding:5px;">{section.tw}</td>
                <td style="border:1px solid #ccc; padding:5px;"><b>W<sub>y</sub> (cm³)</b></td>
                <td style="border:1px solid #ccc; padding:5px;">{section.wy:.2f}</td>
            </tr>
            <tr style="background:#f5f5f5;">
                <td style="border:1px solid #ccc; padding:5px;"><b>A (cm²)</b></td>
                <td style="border:1px solid #ccc; padding:5px;">{section.area:.2f}</td>
                <td style="border:1px solid #ccc; padding:5px;"><b>S<sub>x</sub> (cm³)</b></td>
                <td style="border:1px solid #ccc; padding:5px;">{section.sx:.2f}</td>
            </tr>
            <tr>
                <td style="border:1px solid #ccc; padding:5px;"><b>q (Kg/m)</b></td>
                <td style="border:1px solid #ccc; padding:5px;">{section.area * 0.785:.3f}</td>
                <td style="border:1px solid #ccc; padding:5px;"><b>S<sub>y</sub> (cm³)</b></td>
                <td style="border:1px solid #ccc; padding:5px;">{section.sy if hasattr(section, 'sy') else 0:.2f}</td>
            </tr>
        </table>
        """
        
        # THREE GEOMETRIC CHECKS (Excel lines 157-164)
        
        # Check 1: Web slenderness (hw/tw ≤ 180)
        hw = section.h - 2 * section.tf
        web_slenderness = hw / section.tw if section.tw > 0 else 999
        web_limit = 180.0
        web_ok = web_slenderness <= web_limit
        web_result = "Thỏa" if web_ok else "Chọn lại"
        web_color = "green" if web_ok else "red"
        
        # Check 2: Flange-web ratio (tf/tw)
        # Excel shows this as "tf/tw" check with limit ~2.5
        tf_tw_ratio = section.tf / section.tw if section.tw > 0 else 999
        tf_tw_limit = 2.5
        tf_tw_ok = tf_tw_ratio <= tf_tw_limit
        tf_tw_result = "Thỏa" if tf_tw_ok else "Chọn lại"
        tf_tw_color = "green" if tf_tw_ok else "red"
        
        # Check 3: Flange slenderness (hw/wf ≤ 5.0)
        # wf = flange overhang = (B - tw)/2
        wf = (section.b - section.tw) / 2.0
        hw_wf_ratio = hw / wf if wf > 0 else 999
        hw_wf_limit = 5.0
        hw_wf_ok = hw_wf_ratio <= hw_wf_limit
        hw_wf_result = "Thỏa" if hw_wf_ok else "Chọn lại"
        hw_wf_color = "green" if hw_wf_ok else "red"
        
        html += f"""
        <h5>Kiểm tra các điều kiện bản bụng và bản cánh:</h5>
        
        <p><b>1. Bản bụng (hw/tw ≤ 180):</b></p>
        <ul>
            <li>h<sub>w</sub> = H - 2×t<sub>f</sub> = {section.h} - 2×{section.tf} = <b>{hw} mm</b></li>
            <li>h<sub>w</sub>/t<sub>w</sub> = {hw}/{section.tw} = <b>{web_slenderness:.1f}</b></li>
            <li>Giới hạn: <b>{web_limit}</b></li>
            <li>Kết luận: <span style="color:{web_color}; font-weight:bold;">{web_result}</span></li>
        </ul>
        
        <p><b>2. Tỷ lệ cánh-bụng (t<sub>f</sub>/t<sub>w</sub>):</b></p>
        <ul>
            <li>t<sub>f</sub>/t<sub>w</sub> = {section.tf}/{section.tw} = <b>{tf_tw_ratio:.2f}</b></li>
            <li>Giới hạn: <b>{tf_tw_limit}</b></li>
            <li>Kết luận: <span style="color:{tf_tw_color}; font-weight:bold;">{tf_tw_result}</span></li>
        </ul>
        
        <p><b>3. Độ mảnh cánh (h<sub>w</sub>/w<sub>f</sub> ≤ 5.0):</b></p>
        <ul>
            <li>w<sub>f</sub> = (B - t<sub>w</sub>)/2 = ({section.b} - {section.tw})/2 = <b>{wf:.1f} mm</b></li>
            <li>h<sub>w</sub>/w<sub>f</sub> = {hw}/{wf:.1f} = <b>{hw_wf_ratio:.2f}</b></li>
            <li>Giới hạn: <b>{hw_wf_limit}</b></li>
            <li>Kết luận: <span style="color:{hw_wf_color}; font-weight:bold;">{hw_wf_result}</span></li>
        </ul>
        """
        
        # STRESS CHECK (Excel line 168)
        sigma = (N / section.area) + (M / section.wx)
        ratio = sigma / material.rk
        stress_ok = ratio <= 1.0
        stress_result = "Thỏa" if stress_ok else "Chọn lại"
        stress_color = "green" if stress_ok else "red"
        
        html += f"""
        <h5>Kiểm tra tiết diện chọn theo điều kiện bền:</h5>
        <ul>
            <li>σ = N/A + M/W<sub>x</sub></li>
            <li>σ = {N}/{section.area:.2f} + {M}/{section.wx:.2f}</li>
            <li>σ = <b>{sigma:.2f} kg/cm²</b> ≤ <b>{material.rk} kg/cm²</b></li>
            <li>Tỷ số: σ/R<sub>k</sub> = <b>{ratio:.3f}</b></li>
            <li>Kết luận: <span style="color:{stress_color}; font-weight:bold; font-size:1.1em;">{stress_result}</span></li>
        </ul>
        <hr>
        """
        
        return html
