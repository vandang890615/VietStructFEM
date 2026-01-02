# -*- coding: utf-8 -*-
"""
RC Beam Module - UI
Reinforced Concrete Beam Designer Interface
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QFormLayout, QLineEdit, QComboBox, QPushButton, 
                             QLabel, QSplitter, QTextBrowser, QMessageBox,
                             QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches

from steeldeckfem.core.rc_beam_designer import RCBeamDesigner, MaterialDatabase
from steeldeckfem.core.rc_slab_designer import RCSlabDesigner
from steeldeckfem.core.load_combination_engine import LoadType, LimitState, LoadCombinationEngine


class RCBeamModule(QWidget):
    """RC Beam & Slab Designer Module"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.beam_designer = None
        self.slab_designer = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        
        # Create tabs for Beam and Slab
        self.main_tabs = QTabWidget()
        
        # Tab 1: Beam
        self.main_tabs.addTab(self.create_beam_panel(), "🔲 DẦM (Beam)")
        
        # Tab 2: Slab
        self.main_tabs.addTab(self.create_slab_panel(), "⬜ SÀN (Slab)")
        
        main_layout.addWidget(self.main_tabs)
        
    def create_beam_panel(self):
        """Create beam design panel"""
        panel = QWidget()
        main_layout = QHBoxLayout(panel)
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Inputs
        splitter.addWidget(self.create_beam_input_panel())
        
        # Right: Results
        splitter.addWidget(self.create_beam_output_panel())
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        return panel
        
    def create_beam_input_panel(self):
        """Create input panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("🏗 DẦM BTCT (TCVN 5574:2018)")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #d35400; color: white; padding: 10px; border-radius: 5px;")
        layout.addWidget(title)
        
        # Geometry
        gb_geo = QGroupBox("1. HÌNH HỌC")
        form_geo = QFormLayout()
        
        self.inp_b = QLineEdit("300")
        self.inp_h = QLineEdit("500")
        self.inp_L = QLineEdit("6.0")
        self.inp_cover = QLineEdit("30")
        
        form_geo.addRow("Bề rộng b (mm):", self.inp_b)
        form_geo.addRow("Chiều cao h (mm):", self.inp_h)
        form_geo.addRow("Nhịp L (m):", self.inp_L)
        form_geo.addRow("Lớp bảo vệ (mm):", self.inp_cover)
        gb_geo.setLayout(form_geo)
        layout.addWidget(gb_geo)
        
        # Materials
        gb_mat = QGroupBox("2. VẬT LIỆU")
        form_mat = QFormLayout()
        
        self.cbo_concrete = QComboBox()
        self.cbo_concrete.addItems(['B15', 'B20', 'B25', 'B30', 'B35', 'B40'])
        self.cbo_concrete.setCurrentText('B25')
        
        self.cbo_steel = QComboBox()
        self.cbo_steel.addItems(['CB300-V', 'CB400-V', 'CB500-V'])
        self.cbo_steel.setCurrentText('CB400-V')
        
        form_mat.addRow("Mác bê tông:", self.cbo_concrete)
        form_mat.addRow("Mác thép:", self.cbo_steel)
        gb_mat.setLayout(form_mat)
        layout.addWidget(gb_mat)
        
        # Loads
        gb_loads = QGroupBox("3. TẢI TRỌNG")
        form_loads = QFormLayout()
        
        self.inp_dead = QLineEdit("10.0")
        self.inp_live = QLineEdit("5.0")
        
        form_loads.addRow("Tĩnh tải (kN/m):", self.inp_dead)
        form_loads.addRow("Hoạt tải (kN/m):", self.inp_live)
        
        btn_load_combo = QPushButton("🔢 Mở Tổ hợp Tải trọng")
        btn_load_combo.clicked.connect(self.open_load_combo)
        form_loads.addRow("", btn_load_combo)
        
        gb_loads.setLayout(form_loads)
        layout.addWidget(gb_loads)
        
        # Design Button
        btn_design = QPushButton("⚡ THIẾT KẾ DẦM")
        btn_design.setStyleSheet("""
            QPushButton {
                background-color: #c0392b; color: white;
                font-size: 14px; font-weight: bold; padding: 15px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #e74c3c; }
        """)
        btn_design.clicked.connect(self.design_beam)
        layout.addWidget(btn_design)
        
        layout.addStretch()
        return panel
    
    def create_slab_panel(self):
        """Create slab design panel"""
        panel = QWidget()
        main_layout = QHBoxLayout(panel)
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Inputs
        splitter.addWidget(self.create_slab_input_panel())
        
        # Right: Results
        splitter.addWidget(self.create_slab_output_panel())
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        return panel
    
    def create_slab_input_panel(self):
        """Create slab input panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("⬜ SÀN BTCT (TCVN 5574:2018)")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #8e44ad; color: white; padding: 10px; border-radius: 5px;")
        layout.addWidget(title)
        
        # Slab Type
        gb_type = QGroupBox("LOẠI SÀN")
        form_type = QFormLayout()
        
        self.slab_cbo_type = QComboBox()
        self.slab_cbo_type.addItems(['1 phương (One-way)', '2 phương (Two-way)'])
        self.slab_cbo_type.currentTextChanged.connect(self.on_slab_type_changed)
        
        form_type.addRow("Loại:", self.slab_cbo_type)
        gb_type.setLayout(form_type)
        layout.addWidget(gb_type)
        
        # Geometry
        gb_geo = QGroupBox("HÌNH HỌC")
        form_geo = QFormLayout()
        
        self.slab_inp_h = QLineEdit("120")
        self.slab_inp_Lx = QLineEdit("4.0")
        self.slab_inp_Ly = QLineEdit("6.0")
        self.slab_inp_cover = QLineEdit("20")
        
        form_geo.addRow("Chiều dày h (mm):", self.slab_inp_h)
        form_geo.addRow("Nhịp ngắn Lx (m):", self.slab_inp_Lx)
        self.lbl_Ly = QLabel("Nhịp dài Ly (m):")
        form_geo.addRow(self.lbl_Ly, self.slab_inp_Ly)
        form_geo.addRow("Lớp bảo vệ (mm):", self.slab_inp_cover)
        gb_geo.setLayout(form_geo)
        layout.addWidget(gb_geo)
        
        # Materials
        gb_mat = QGroupBox("VẬT LIỆU")
        form_mat = QFormLayout()
        
        self.slab_cbo_concrete = QComboBox()
        self.slab_cbo_concrete.addItems(['B15', 'B20', 'B25', 'B30', 'B35', 'B40'])
        self.slab_cbo_concrete.setCurrentText('B25')
        
        self.slab_cbo_steel = QComboBox()
        self.slab_cbo_steel.addItems(['CB300-V', 'CB400-V', 'CB500-V'])
        self.slab_cbo_steel.setCurrentText('CB400-V')
        
        form_mat.addRow("Mác bê tông:", self.slab_cbo_concrete)
        form_mat.addRow("Mác thép:", self.slab_cbo_steel)
        gb_mat.setLayout(form_mat)
        layout.addWidget(gb_mat)
        
        # Support
        gb_support = QGroupBox("ĐIỀU KIỆN TỰA")
        form_support = QFormLayout()
        
        self.slab_cbo_support = QComboBox()
        self.slab_cbo_support.addItems(['simple (Tựa đơn)', 'fixed (Ngàm)', 'continuous (Liên tục)'])
        
        form_support.addRow("Loại tựa:", self.slab_cbo_support)
        gb_support.setLayout(form_support)
        layout.addWidget(gb_support)
        
        # Loads
        gb_loads = QGroupBox("TẢI TRỌNG")
        form_loads = QFormLayout()
        
        self.slab_inp_q = QLineEdit("15.0")
        
        form_loads.addRow("Tải tính toán q (kN/m²):", self.slab_inp_q)
        gb_loads.setLayout(form_loads)
        layout.addWidget(gb_loads)
        
        # Design Button
        btn_design = QPushButton("⚡ THIẾT KẾ SÀN")
        btn_design.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad; color: white;
                font-size: 14px; font-weight: bold; padding: 15px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #9b59b6; }
        """)
        btn_design.clicked.connect(self.design_slab)
        layout.addWidget(btn_design)
        
        layout.addStretch()
        return panel
    
    def create_slab_output_panel(self):
        """Create slab output panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        self.slab_txt_results = QTextBrowser()
        layout.addWidget(self.slab_txt_results)
        
        return panel
        
    def on_slab_type_changed(self, text):
        """Handle slab type change"""
        if '1 phương' in text:
            self.slab_inp_Ly.setEnabled(False)
            self.lbl_Ly.setEnabled(False)
        else:
            self.slab_inp_Ly.setEnabled(True)
            self.lbl_Ly.setEnabled(True)
        
    def design_slab(self):
        """Run slab design"""
        try:
            h = float(self.slab_inp_h.text())
            Lx = float(self.slab_inp_Lx.text())
            q = float(self.slab_inp_q.text())
            
            concrete = self.slab_cbo_concrete.currentText()
            steel = self.slab_cbo_steel.currentText()
            cover = float(self.slab_inp_cover.text())
            
            support_text = self.slab_cbo_support.currentText()
            support = 'simple' if 'simple' in support_text else ('fixed' if 'fixed' in support_text else 'continuous')
            
            # Create designer
            self.slab_designer = RCSlabDesigner(h, concrete, steel, cover)
            
            # Check type
            if '1 phương' in self.slab_cbo_type.currentText():
                # One-way slab
                result = self.slab_designer.design_one_way(Lx, q, support)
                self.display_oneway_results(result, Lx, h)
            else:
                # Two-way slab
                Ly = float(self.slab_inp_Ly.text())
                result = self.slab_designer.design_two_way(Lx, Ly, q, support)
                self.display_twoway_results(result, h)
                
        except ValueError as e:
            QMessageBox.warning(self, "Lỗi", f"Kiểm tra số liệu nhập:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi thiết kế:\n{str(e)}")
    
    def display_oneway_results(self, result, L, h):
        """Display one-way slab results"""
        status_color = "green" if result['status'] == 'OK' else "red"
        
        html = f"""
        <h2 style='color: {status_color};'>SÀN 1 PHƯƠNG: {result['status']}</h2>
        
        <h3>Thông số:</h3>
        <ul>
            <li>Nhịp L = {L} m</li>
            <li>Chiều dày h = {h} mm</li>
            <li>Chiều dày hữu ích d = {h - 20 - 5:.0f} mm</li>
        </ul>
        
        <h3>Thiết kế cốt thép:</h3>
        <ul>
            <li>Moment M<sub>u</sub> = {result['M_u']:.2f} kNm/m</li>
            <li>Cốt thép cần A<sub>s</sub> = {result['As_required']:.0f} mm²/m</li>
            <li><b>Bố trí: {result['bar_config']}</b></li>
            <li>Cung cấp A<sub>s</sub> = {result['As_provided']:.0f} mm²/m ✓</li>
            <li>Khoảng cách tối đa: {result['s_max']:.0f} mm</li>
        </ul>
        
        <p><i>Lưu ý: Cần bố trí thêm cốt thép phân bố theo phương vuông góc (0.2% diện tích bê tông)</i></p>
        """
        
        self.slab_txt_results.setHtml(html)
    
    def display_twoway_results(self, result, h):
        """Display two-way slab results"""
        status_color = "green" if result['status'] == 'OK' else "red"
        
        geo = result['geometry']
        mom = result['moments']
        dx = result['design_x']
        dy = result['design_y']
        
        html = f"""
        <h2 style='color: {status_color};'>SÀN 2 PHƯƠNG: {result['status']}</h2>
        
        <h3>Thông số:</h3>
        <ul>
            <li>Lx = {geo['Lx']} m, Ly = {geo['Ly']} m</li>
            <li>Tỷ lệ Ly/Lx = {geo['ratio']:.2f}</li>
            <li>Điều kiện tựa: {geo['support']}</li>
            <li>Chiều dày h = {h} mm</li>
        </ul>
        
        <h3>Hệ số moment:</h3>
        <ul>
            <li>α<sub>x</sub> = {mom['alpha_x']:.4f}</li>
            <li>α<sub>y</sub> = {mom['alpha_y']:.4f}</li>
        </ul>
        
        <h3>Thiết kế phương ngắn (X):</h3>
        <ul>
            <li>M<sub>x</sub> = {mom['M_x']:.2f} kNm/m</li>
            <li><b>Cốt thép: {dx['bar_config']}</b></li>
            <li>A<sub>s</sub> = {dx['As_provided']:.0f} mm²/m</li>
        </ul>
        
        <h3>Thiết kế phương dài (Y):</h3>
        <ul>
            <li>M<sub>y</sub> = {mom['M_y']:.2f} kNm/m</li>
            <li><b>Cốt thép: {dy['bar_config']}</b></li>
            <li>A<sub>s</sub> = {dy['As_provided']:.0f} mm²/m</li>
        </ul>
        """
        
        self.slab_txt_results.setHtml(html)
        
    def create_beam_output_panel(self):
        """Create output panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Results & Diagrams
        self.tab_results = QWidget()
        layout_res = QVBoxLayout(self.tab_results)
        
        # Matplotlib canvas
        self.fig = Figure(figsize=(8, 6), facecolor='#ffffff')
        self.canvas = FigureCanvas(self.fig)
        layout_res.addWidget(self.canvas)
        
        # Results text
        self.txt_results = QTextBrowser()
        self.txt_results.setMaximumHeight(200)
        layout_res.addWidget(self.txt_results)
        
        self.tabs.addTab(self.tab_results, "📊 Kết quả Thiết kế")
        
        layout.addWidget(self.tabs)
        return panel
        
    def open_load_combo(self):
        """Show message about load combination"""
        QMessageBox.information(self, "Tổ hợp Tải trọng", 
                              "Vui lòng mở tab 'TỔ HỢP TẢI TRỌNG' để tính toán tải trọng tổ hợp.\n"
                              "Sau đó nhập kết quả vào đây.")
        
    def design_beam(self):
        """Run beam design"""
        try:
            # Get inputs
            b = float(self.inp_b.text())
            h = float(self.inp_h.text())
            L = float(self.inp_L.text())
            cover = float(self.inp_cover.text())
            
            concrete = self.cbo_concrete.currentText()
            steel = self.cbo_steel.currentText()
            
            DL = float(self.inp_dead.text())
            LL = float(self.inp_live.text())
            
            # Create designer
            self.beam_designer = RCBeamDesigner(b, h, L, concrete, steel, cover)
            
            # Calculate loads using simple combination (1.1D + 1.3L for ULS)
            q_uls = 1.1 * DL + 1.3 * LL  # kN/m
            q_sls = DL + LL  # kN/m (serviceability)
            
            # Calculate moment and shear (simply supported)
            M_u = q_uls * L**2 / 8  # kNm
            V_u = q_uls * L / 2  # kN
            
            # Design
            summary = self.beam_designer.get_design_summary(M_u, V_u, q_sls)
            
            # Display results
            self.display_results(summary, M_u, V_u, q_uls)
            
        except ValueError as e:
            QMessageBox.warning(self, "Lỗi", f"Kiểm tra số liệu nhập:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi thiết kế:\n{str(e)}")
            
    def display_results(self, summary, M_u, V_u, q_uls):
        """Display design results"""
        
        # Draw diagrams
        self.draw_diagrams(summary, q_uls)
        
        # Format text results
        flex = summary['flexure']
        shear = summary['shear']
        defl = summary['deflection']
        
        status_color = "green" if summary['overall_status'] == 'OK' else "red"
        
        html = f"""
        <h2 style='color: {status_color};'>KẾT QUẢ THIẾT KẾ: {summary['overall_status']}</h2>
        
        <h3>1. Thiết kế Uốn (Bending)</h3>
        <ul>
            <li>Moment tính toán M<sub>u</sub> = {M_u:.2f} kNm</li>
            <li>Cốt thép cần thiết A<sub>s,req</sub> = {flex['As_required']:.0f} mm²</li>
            <li><b>Bố trí: {flex['bar_config']['description']} ({flex['As_provided']:.0f} mm²)</b></li>
            <li>Tỷ lệ cốt thép ρ = {flex['rho']:.4f}</li>
            <li>Tính dẻo: {'OK ✓' if flex['is_ductile'] else 'Cần kiểm tra'}</li>
        </ul>
        
        <h3>2. Thiết kế Cắt (Shear)</h3>
        <ul>
            <li>Lực cắt tính toán V<sub>u</sub> = {V_u:.2f} kN</li>
            <li>Khả năng bê tông V<sub>c</sub> = {shear['V_c']:.2f} kN</li>
            <li><b>Đai: {shear['status']}</b></li>
        </ul>
        
        <h3>3. Kiểm tra Võng (Deflection)</h3>
        <ul>
            <li>Độ võng tính toán δ = {defl['delta']:.1f} mm</li>
            <li>Giới hạn [δ] = {defl['delta_allow']:.1f} mm (L/250)</li>
            <li>Tỷ lệ: {defl['ratio']:.2f} {'✓' if defl['status'] == 'OK' else '✗'}</li>
        </ul>
        """
        
        self.txt_results.setHtml(html)
        
    def draw_diagrams(self, summary, q):
        """Draw beam cross-section and diagrams"""
        self.fig.clear()
        
        gs = self.fig.add_gridspec(2, 2)
        
        # 1. Cross-section (Top Left)
        ax1 = self.fig.add_subplot(gs[0, 0])
        ax1.set_title("Mặt cắt ngang")
        
        b = summary['geometry']['b']
        h = summary['geometry']['h']
        
        # Draw section
        rect = patches.Rectangle((0, 0), b, h, linewidth=2, 
                                 edgecolor='black', facecolor='lightgray')
        ax1.add_patch(rect)
        
        # Draw rebar (simplified)
        bar_config = summary['flexure']['bar_config']
        n_bars = bar_config['n_bars']
        for i in range(n_bars):
            x = (i + 1) * b / (n_bars + 1)
            y = 40  # Near bottom
            circle = patches.Circle((x, y), 10, color='red')
            ax1.add_patch(circle)
        
        ax1.text(b/2, h + 20, f"b = {b}mm", ha='center')
        ax1.text(-20, h/2, f"h = {h}mm", ha='right', va='center', rotation=90)
        ax1.text(b/2, 20, bar_config['description'], ha='center', 
                color='red', fontweight='bold')
        
        ax1.set_xlim(-50, b + 50)
        ax1.set_ylim(-20, h + 40)
        ax1.set_aspect('equal')
        ax1.axis('off')
        
        # 2. Moment Diagram (Top Right)
        ax2 = self.fig.add_subplot(gs[0, 1])
        ax2.set_title("Biểu đồ Moment")
        
        import numpy as np
        L = summary['geometry']['L'] * 1000  # mm
        x = np.linspace(0, L, 50)
        M = (q * (L/1000)**2 / 8) * (4 * (x/L) * (1 - x/L))  # kNm
        
        ax2.plot(x/1000, M, 'r-', linewidth=2)
        ax2.fill_between(x/1000, M, alpha=0.2, color='red')
        ax2.invert_yaxis()
        ax2.set_xlabel('x (m)')
        ax2.set_ylabel('M (kNm)')
        ax2.grid(True, alpha=0.3)
        
        # 3. Shear Diagram (Bottom Left)
        ax3 = self.fig.add_subplot(gs[1, 0])
        ax3.set_title("Biểu đồ Lực cắt")
        
        V = q * (L/1000) / 2 * (1 - 2*x/L)  # kN
        ax3.plot(x/1000, V, 'b-', linewidth=2)
        ax3.fill_between(x/1000, V, alpha=0.2, color='blue')
        ax3.axhline(0, color='black', linewidth=0.5)
        ax3.set_xlabel('x (m)')
        ax3.set_ylabel('V (kN)')
        ax3.grid(True, alpha=0.3)
        
        # 4. Status Summary (Bottom Right)
        ax4 = self.fig.add_subplot(gs[1, 1])
        ax4.set_title("Tổng kết")
        ax4.axis('off')
        
        flex_status = '✓' if summary['flexure']['status'] == 'OK' else '✗'
        defl_status = '✓' if summary['deflection']['status'] == 'OK' else '✗'
        
        summary_text = f"""
Thiết kế Uốn: {flex_status}
  {summary['flexure']['bar_config']['description']}
  
Thiết kế Cắt: ✓
  {summary['shear']['status']}
  
Kiểm tra Võng: {defl_status}
  δ = {summary['deflection']['delta']:.1f}mm
        """
        
        ax4.text(0.1, 0.5, summary_text, fontsize=11, 
                verticalalignment='center', family='monospace')
        
        self.fig.tight_layout()
        self.canvas.draw()
