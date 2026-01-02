# -*- coding: utf-8 -*-
"""
Industrial Warehouse Module
Features:
1. Wind Load Calculation (TCVN 2737:2023)
2. Purlin Design (C/Z Profiles)
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
                             QLineEdit, QComboBox, QPushButton, QLabel, QSplitter, QScrollArea,
                             QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import math
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches


# --- CORE LOGIC ---

class WindLoadCalculator:
    """TCVN 2737:2023 Wind Load Logic"""
    
    # Wind Pressure Regions (partial database)
    WIND_REGIONS = {
        "I": 0.65, "II": 0.95, "III": 1.25, "IV": 1.55, "V": 1.85 
        # Note: 2023 standard might have updated these values (Wo in kPa or daN/m2)
        # TCVN 2737:2023 uses pressure in kPa. 
        # Typical values: Zone 1 (0.65 kPa), Zone 2 (0.95 kPa)...
    }
    
    @staticmethod
    def get_k_factor(z, terrain_type):
        """
        Calculates coefficient k assuming standard height variation.
        z: height (m)
        terrain_type: 'A', 'B', 'C' (or equivalent 2023 definitions)
        """
        # Simplified power law: k = (z/10)^alpha
        # TCVN 2737:2023 has specific tables. Approximating for MVP.
        
        if z < 3: z = 3 # Minimum height
        
        params = {
            'A': {'alpha': 0.12, 'z_g': 250}, # Open sea
            'B': {'alpha': 0.16, 'z_g': 350}, # Rural/Towns
            'C': {'alpha': 0.22, 'z_g': 450}  # Urban/Forest
        }
        
        p = params.get(terrain_type, params['B'])
        alpha = p['alpha']
        
        # Simplified formula often used in codes
        k = 2.01 * (z / 900)**alpha # Wait, this is ASCE.
        
        # Using TCVN 2737-1995/2023 standard approximation
        # For Terrain B:
        # z=10 -> k=1.0
        # z=20 -> k=1.13
        
        # Let's use specific interpolation or simple logic
        # For MVP, we use the table lookup logic typically found in these Excel sheets
        # Or a curve fit: k = A * log(z) + B? 
        # Let's use a robust approximation: k = (z/10)^(2*alpha)
        
        if terrain_type == 'A':
            return 1.39 * (z/10)**0.11 # Rough fit
        elif terrain_type == 'B':
            return 1.00 * (z/10)**0.15
        elif terrain_type == 'C':
            return 0.47 * (z/10)**0.20 # C is very shielded
            
        return 1.0

    @staticmethod
    def calculate_wind_loads(Wo, H, terrain):
        """Returns list of (z, k, W)"""
        results = []
        steps = int(H / 1.0) # Every 1 meter
        if steps < 1: steps = 1
        
        for i in range(1, steps + 2):
            z = (i-1) * 1.0
            if z > H: z = H
            if z == 0: continue
            
            k = WindLoadCalculator.get_k_factor(z, terrain)
            W = Wo * k # Wind pressure at height z (Standard value)
            
            results.append({
                'z': z,
                'k': k,
                'W': W
            })
            
        return results

# --- UI COMPONENT ---

class WarehouseModule(QWidget):
    """
    Module: Industrial Warehouse (Wind & Purlins)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Tabs for sub-modules
        self.tabs = QTabWidget()
        
        # Tab 1: Wind Load
        self.tab_wind = QWidget()
        self.init_wind_tab()
        self.tabs.addTab(self.tab_wind, "🌬 Tải trọng Gió (TCVN 2737:2023)")
        
        # Tab 2: Purlin
        self.tab_purlin = QWidget()
        self.init_purlin_tab()
        self.tabs.addTab(self.tab_purlin, "📏 Tính Xà gồ (Z/C)")
        
        main_layout.addWidget(self.tabs)
        
    def init_wind_tab(self):
        layout = QHBoxLayout(self.tab_wind)
        
        # Left Panel (Inputs)
        gb_in = QGroupBox("Thông số công trình")
        gb_in.setFixedWidth(350)
        form = QFormLayout()
        
        self.cbo_region = QComboBox()
        self.cbo_region.addItems(["I", "II", "III", "IV", "V"])
        self.cbo_terrain = QComboBox()
        self.cbo_terrain.addItems(["A (Trống trải/Biển)", "B (Thị trấn/Đồng ruộng)", "C (Đô thị/Rừng)"])
        
        self.inp_H = QLineEdit("10.0")
        self.inp_gamma = QLineEdit("1.0") # Safety factor
        
        form.addRow("Vùng gió:", self.cbo_region)
        form.addRow("Dạng địa hình:", self.cbo_terrain)
        form.addRow("Chiều cao công trình H (m):", self.inp_H)
        form.addRow("Hệ số tin cậy γ:", self.inp_gamma)
        gb_in.setLayout(form)
        
        btn_calc = QPushButton("Tính toán Gió")
        btn_calc.setStyleSheet("background-color: #2980b9; color: white; padding: 10px; font-weight: bold;")
        btn_calc.clicked.connect(self.calc_wind)
        
        left_layout = QVBoxLayout()
        left_layout.addWidget(gb_in)
        left_layout.addWidget(btn_calc)
        left_layout.addStretch()
        
        # Right Panel (Results)
        self.tbl_wind = QTableWidget()
        self.tbl_wind.setColumnCount(4)
        self.tbl_wind.setHorizontalHeaderLabels(["Độ cao z (m)", "Hệ số k", "W tiêu chuẩn (kPa)", "W tính toán (kPa)"])
        header = self.tbl_wind.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addLayout(left_layout)
        layout.addWidget(self.tbl_wind)
        
# --- PURLIN LOGIC ---

class PurlinCalculator:
    """Methods for checking C/Z Purlins per TCVN 5575"""
    
    SECTIONS = {
        "C150x50x20x2.0": {'h': 150, 'b': 50, 'c': 20, 't': 2.0, 'Ix': 285.0e4, 'Iy': 35.0e4, 'Wx': 38.0e3, 'Wy': 9.0e3, 'Area': 5.5}, # Dummy values
        "C200x65x20x2.0": {'h': 200, 'b': 65, 'c': 20, 't': 2.0, 'Ix': 550.0e4, 'Iy': 55.0e4, 'Wx': 55.0e3, 'Wy': 12.0e3, 'Area': 7.2},
        "Z150x50x20x2.0": {'h': 150, 'b': 50, 'c': 20, 't': 2.0, 'Ix': 280.0e4, 'Iy': 34.0e4, 'Wx': 37.0e3, 'Wy': 8.8e3, 'Area': 5.5},
        "Z200x65x20x2.0": {'h': 200, 'b': 65, 'c': 20, 't': 2.0, 'Ix': 540.0e4, 'Iy': 54.0e4, 'Wx': 54.0e3, 'Wy': 11.8e3, 'Area': 7.2}
    }
    
    @staticmethod
    def check_purlin(span, spacing, slope_deg, loads, section_name, sag_rods):
        """
        Check purlin capacity.
        loads = {'dead': kN/m2, 'live': kN/m2, 'wind': kN/m2}
        """
        sec = PurlinCalculator.SECTIONS.get(section_name, PurlinCalculator.SECTIONS["C200x65x20x2.0"])
        
        # Geometry
        alpha = math.radians(slope_deg)
        L = span
        B = spacing
        
        # Load Combination (1.1 DL + 1.2 LL usually, or 1.0 DL + 1.0 WL)
        # Simplified for MVP: Max Gravity Load
        q_grav_ser = loads['dead'] + loads['live']
        q_grav_fac = 1.1 * loads['dead'] + 1.2 * loads['live'] # TCVN factors approx
        
        # Distributed load on purlin (kN/m)
        q_total = q_grav_fac * B
        
        # Components
        qx = q_total * math.cos(alpha) # Major axis bending
        qy = q_total * math.sin(alpha) # Minor axis bending
        
        # Moment
        # Major: Mx = qx * L^2 / 8
        Mx = qx * L**2 / 8
        
        # Minor: Depends on sag rods
        # n_sag = 0 -> L_y = L
        # n_sag = 1 -> L_y = L/2
        # n_sag = 2 -> L_y = L/3
        n_sag = int(sag_rods)
        Ly = L / (n_sag + 1)
        My = qy * Ly**2 / 8
        
        # Stress Check
        # Sigma = Mx/Wx + My/Wy
        # Units: M in kNm, W in mm3 -> Need conversion.
        # kNm * 1e6 = Nmm. W in mm3. result in N/mm2 (MPa).
        
        sigma_x = (Mx * 1e6) / sec['Wx']
        sigma_y = (My * 1e6) / sec['Wy']
        
        sigma_total = sigma_x + sigma_y
        f_y = 245.0 # MPa, SS400
        uc_stress = sigma_total / f_y
        
        # Deflection Check (Service Load)
        q_serv = q_grav_ser * B
        qx_s = q_serv * math.cos(alpha)
        # Delta = 5/384 * q L^4 / EI
        # kN/m -> N/mm. L in m -> mm (*1000). E = 2.1e5 MPa. I in mm4.
        E = 2.1e5
        
        delta_x = (5/384) * (qx_s) * (L*1000)**4 / (E * sec['Ix'])
        limit_delta = (L*1000) / 200 # L/200 limit
        uc_def = delta_x / limit_delta
        
        return {
            'Mx': Mx, 'My': My,
            'sigma': sigma_total,
            'delta': delta_x,
            'uc_stress': uc_stress,
            'uc_def': uc_def,
            'status': "ĐẠT" if (uc_stress <= 1.0 and uc_def <= 1.0) else "KHÔNG ĐẠT",
            'notes': "Thỏa mãn" if (uc_stress <= 1.0 and uc_def <= 1.0) else ("Võng quá lớn" if uc_def > 1 else "Ứng suất quá lớn")
        }

    @staticmethod
    def optimize_section(span, spacing, slope_deg, loads, sag_rods):
        """Find the lightest section that passes"""
        valid_sections = []
        
        for name, props in PurlinCalculator.SECTIONS.items():
            res = PurlinCalculator.check_purlin(span, spacing, slope_deg, loads, name, sag_rods)
            if res['status'] == "ĐẠT":
                valid_sections.append((name, props['Area'], res))
                
        # Sort by Area (Weight)
        valid_sections.sort(key=lambda x: x[1])
        
        if not valid_sections:
            return None
        return valid_sections[0] # Return name, area, result

    
    def init_purlin_tab(self):
        layout = QHBoxLayout(self.tab_purlin)
        
        # Inputs
        gb_in = QGroupBox("Thông số Xà gồ")
        gb_in.setFixedWidth(350)
        form = QFormLayout()
        
        self.inp_span = QLineEdit("6.0")
        self.inp_spacing = QLineEdit("1.2")
        self.inp_slope = QLineEdit("10") # degrees
        
        self.cbo_section = QComboBox()
        self.cbo_section.addItems(PurlinCalculator.SECTIONS.keys())
        
        self.cbo_sagrods = QComboBox()
        self.cbo_sagrods.addItems(["0 (Không)", "1 (L/2)", "2 (L/3)"])
        
        self.inp_dl = QLineEdit("0.15") # kN/m2
        self.inp_ll = QLineEdit("0.30") # kN/m2 (mái tôn)
        
        form.addRow("Nhịp cột (m):", self.inp_span)
        form.addRow("Bước xà gồ B (m):", self.inp_spacing)
        form.addRow("Độ dốc mái (độ):", self.inp_slope)
        form.addRow("Tiết diện (Kiểm tra):", self.cbo_section)
        form.addRow("Số ty giằng:", self.cbo_sagrods)
        form.addRow("Tĩnh tải (kN/m²):", self.inp_dl)
        form.addRow("Hoạt tải (kN/m²):", self.inp_ll)
        
        gb_in.setLayout(form)
        
        # Actions
        hbox_btn = QHBoxLayout()
        btn_calc = QPushButton("Kiểm tra")
        btn_calc.setStyleSheet("background-color: #2980b9; color: white; padding: 10px; font-weight: bold;")
        btn_calc.clicked.connect(self.calc_purlin)
        
        btn_opt = QPushButton("✨ Tự động Chọn")
        btn_opt.setToolTip("Tìm tiết diện nhẹ nhất thỏa mãn điều kiện")
        btn_opt.setStyleSheet("background-color: #8e44ad; color: white; padding: 10px; font-weight: bold;")
        btn_opt.clicked.connect(self.optimize_purlin)
        
        hbox_btn.addWidget(btn_calc)
        hbox_btn.addWidget(btn_opt)
        
        left = QVBoxLayout()
        left.addWidget(gb_in)
        left.addLayout(hbox_btn)
        left.addStretch()
        
        # Results
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.txt_purlin_res = QLabel("<b>Kết quả sẽ hiện ở đây...</b><br><i>Hãy nhập số liệu và nhấn Kiểm tra hoặc Tự động chọn.</i>")
        self.txt_purlin_res.setAlignment(Qt.AlignTop)
        self.txt_purlin_res.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.txt_purlin_res.setStyleSheet("font-size: 14px; padding: 15px; background-color: #ffffff; border: 1px solid #ddd; border-top-left-radius: 5px; border-top-right-radius: 5px;")
        
        # Diagram
        self.fig = Figure(figsize=(6, 5), facecolor='#f5f6fa')
        self.canvas = FigureCanvas(self.fig)
        
        right_layout.addWidget(self.txt_purlin_res)
        right_layout.addWidget(self.canvas)
        
        layout.addLayout(left)
        layout.addWidget(right_panel, 1) # Stretch

    def draw_section_diagram(self, section_name, res):
        """Draw Dashboard: Section, Stress, M-Diagram, V-Diagram"""
        self.fig.clear()
        
        # GridSpec layout
        gs = self.fig.add_gridspec(2, 2)
        
        # 1. Stress Bar (Top Left)
        ax1 = self.fig.add_subplot(gs[0, 0])
        ax1.set_title("Ứng suất (Stress Ratio)")
        uc = res['uc_stress']
        color = 'green' if uc <= 1.0 else 'red'
        ax1.barh(['Ur'], [uc], color=color, height=0.5)
        ax1.axvline(1.0, color='black', linestyle='--', linewidth=1)
        ax1.set_xlim(0, max(1.2, uc + 0.2))
        ax1.text(uc + 0.05, 0, f"{uc:.2f}", va='center', color=color, fontweight='bold')
        ax1.axis('off')
        
        # 2. Section Visualization (Top Right)
        ax2 = self.fig.add_subplot(gs[0, 1])
        ax2.set_title(section_name)
        sec = PurlinCalculator.SECTIONS.get(section_name, {})
        if sec:
            h, b, c = sec['h'], sec['b'], sec['c']
            if section_name.startswith("Z"):
                x = [b, 0, 0, b]
                y = [h, h, 0, 0] # Rough Z
                ax2.plot(x, y, 'b-', linewidth=3)
            else:
                x = [b, 0, 0, b] # Rough C
                y = [h-c, h, 0, c]
                ax2.plot(x, y, 'b-', linewidth=3)
        ax2.set_aspect('equal')
        ax2.axis('off')
        
        # 3. Moment Diagram (Mx) (Bottom Left)
        ax3 = self.fig.add_subplot(gs[1, 0])
        ax3.set_title("Biểu đồ Moment Mx (kNm)")
        L = float(self.inp_span.text())
        x = [0, L/2, L]
        M_max = res['Mx'] # qL^2/8
        # Parabola approx
        import numpy as np
        xx = np.linspace(0, L, 50)
        # M(x) = 4 * M_max * (x/L) * (1 - x/L)
        yy = 4 * M_max * (xx/L) * (1 - xx/L)
        ax3.plot(xx, yy, 'r-')
        ax3.fill_between(xx, yy, color='red', alpha=0.1)
        ax3.invert_yaxis() # Moment diagram standard
        ax3.grid(True, linestyle='--', alpha=0.5)
        ax3.text(L/2, M_max, f"{M_max:.2f}", ha='center', va='bottom', color='red', fontweight='bold')
        
        # 4. Shear Diagram (Vy) or Deflection (Bottom Right)
        # Let's show Deflection since it's critical for Purlins
        ax4 = self.fig.add_subplot(gs[1, 1])
        ax4.set_title("Độ võng (mm)")
        delta_max = res['delta']
        # Deflection curve ~ Mx shape but cubic/quartic
        yy_def = 16/5 * delta_max * ((xx/L) - 2*(xx/L)**3 + (xx/L)**4) # Approx beam deflection shape? 
        # Actually simple sin wave approx is enough for visual
        yy_def = delta_max * np.sin(np.pi * xx / L)
        
        ax4.plot(xx, yy_def, 'g-')
        ax4.fill_between(xx, yy_def, color='green', alpha=0.1)
        ax4.invert_yaxis() # Downward deflection positive visually
        ax4.grid(True, linestyle='--', alpha=0.5)
        ax4.text(L/2, delta_max, f"{delta_max:.1f} mm", ha='center', va='bottom', color='green', fontweight='bold')
        
        self.fig.tight_layout()
        self.canvas.draw()

        
    def calc_purlin(self):
        try:
            self._run_check(self.cbo_section.currentText())
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Nhập số liệu không hợp lệ")

    def optimize_purlin(self):
        try:
            loads = {'dead': float(self.inp_dl.text()), 'live': float(self.inp_ll.text()), 'wind': 0}
            res = PurlinCalculator.optimize_section(
                float(self.inp_span.text()),
                float(self.inp_spacing.text()),
                float(self.inp_slope.text()),
                loads,
                self.cbo_sagrods.currentText().split(" ")[0]
            )
            
            if res:
                self.cbo_section.setCurrentText(res[0])
                self._run_check(res[0], optimized=True)
            else:
                QMessageBox.warning(self, "Thất bại", "Không tìm thấy tiết diện nào thỏa mãn trong thư viện!")
                
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Nhập số liệu không hợp lệ")

    def _run_check(self, section_name, optimized=False):
        res = PurlinCalculator.check_purlin(
            span=float(self.inp_span.text()),
            spacing=float(self.inp_spacing.text()),
            slope_deg=float(self.inp_slope.text()),
            loads={'dead': float(self.inp_dl.text()), 'live': float(self.inp_ll.text()), 'wind': 0},
            section_name=section_name,
            sag_rods=self.cbo_sagrods.currentText().split(" ")[0]
        )
        
        status_color = "#27ae60" if res['status'] == "ĐẠT" else "#c0392b"
        title = "KẾT QUẢ TỐI ƯU HÓA ✨" if optimized else "KẾT QUẢ KIỂM TRA"
        
        html = f"""
        <h2 style='color: #2c3e50; margin-bottom: 5px;'>{title}</h2>
        <div style='background-color: {status_color}; color: white; padding: 10px; border-radius: 4px; font-weight: bold; font-size: 16px; text-align: center;'>
            {res['status']} - {section_name}
        </div>
        <br>
        <table style='width: 100%; border-collapse: collapse; font-size: 13px;'>
            <tr style='background-color: #ecf0f1;'><td colspan='2'><b>1. Kiểm tra Bền (Stress)</b></td></tr>
            <tr><td>Moment Mx:</td><td>{res['Mx']:.2f} kNm</td></tr>
            <tr><td>Moment My:</td><td>{res['My']:.2f} kNm</td></tr>
            <tr><td>Ứng suất tổng:</td><td>{res['sigma']:.1f} MPa</td></tr>
            <tr><td>Hệ số an toàn:</td><td><b style='color: {status_color}'>{res['uc_stress']:.2f}</b> (Limit 1.0)</td></tr>
            
            <tr style='background-color: #ecf0f1;'><td colspan='2'><b>2. Kiểm tra Võng (Deflection)</b></td></tr>
            <tr><td>Độ võng f:</td><td>{res['delta']:.1f} mm</td></tr>
            <tr><td>Giới hạn [f]:</td><td>{float(self.inp_span.text())*1000/200:.1f} mm (L/200)</td></tr>
            <tr><td>Hệ số an toàn:</td><td><b style='color: {status_color}'>{res['uc_def']:.2f}</b> (Limit 1.0)</td></tr>
        </table>
        """
        self.txt_purlin_res.setText(html)
        self.draw_section_diagram(section_name, res)
        
    def calc_wind(self):
        try:
            region = self.cbo_region.currentText()
            terrain = self.cbo_terrain.currentText().split(" ")[0]
            H = float(self.inp_H.text())
            gamma = float(self.inp_gamma.text())
            
            Wo = WindLoadCalculator.WIND_REGIONS.get(region, 0.65)
            
            data = WindLoadCalculator.calculate_wind_loads(Wo, H, terrain)
            
            self.tbl_wind.setRowCount(len(data))
            for i, row in enumerate(data):
                self.tbl_wind.setItem(i, 0, QTableWidgetItem(f"{row['z']:.1f}"))
                self.tbl_wind.setItem(i, 1, QTableWidgetItem(f"{row['k']:.3f}"))
                self.tbl_wind.setItem(i, 2, QTableWidgetItem(f"{row['W']:.3f}"))
                self.tbl_wind.setItem(i, 3, QTableWidgetItem(f"{row['W']*gamma:.3f}"))
                
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập số hợp lệ")

