# -*- coding: utf-8 -*-
"""
Steel Members Module - UI
Kết Cấu Thép - Vietnamese Steel Design Interface
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QFormLayout, QLineEdit, QComboBox, QPushButton, 
                             QLabel, QTabWidget, QTextBrowser, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from steeldeckfem.core.steel_designer import SteelIBeamDesigner, SteelBoxColumnDesigner, SteelSectionDatabase


class SteelMemberModule(QWidget):
    """Steel Member Designer Module"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.beam_designer = None
        self.column_designer = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # Tab 1: I-Beam
        self.tabs.addTab(self.create_beam_panel(), "🔲 DẦM THÉP I (I-Beam)")
        
        # Tab 2: Box Column
        self.tabs.addTab(self.create_column_panel(), "⬛ CỘT THÉP HỘP (Box Column)")
        
        main_layout.addWidget(self.tabs)
        
    def create_beam_panel(self):
        """Create I-beam panel"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Left: Inputs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Title
        title = QLabel("🔲 DẦM THÉP I (TCVN 5575:2024)")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #607d8b; color: white; padding: 10px; border-radius: 5px;")
        left_layout.addWidget(title)
        
        # Section
        gb_section = QGroupBox("TIẾT DIỆN")
        form_section = QFormLayout()
        
        self.bm_cbo_section = QComboBox()
        # Load all Vietnamese H-beam sections
        from steeldeckfem.core.steel_designer import SteelSectionDatabase
        h_beams = SteelSectionDatabase.get_all_h_beams()
        self.bm_cbo_section.addItems(h_beams)
        
        self.bm_cbo_steel = QComboBox()
        self.bm_cbo_steel.addItems(list(SteelSectionDatabase.STEEL_GRADES.keys()))
        
        form_section.addRow("Tiết diện:", self.bm_cbo_section)
        form_section.addRow("Mác thép:", self.bm_cbo_steel)
        
        lbl_note = QLabel(f"<i>✅ Database có {len(h_beams)} tiết diện VN (TCVN 5575:2012)</i>")
        lbl_note.setWordWrap(True)
        form_section.addRow("", lbl_note)
        
        gb_section.setLayout(form_section)
        left_layout.addWidget(gb_section)
        
        # Loads
        gb_loads = QGroupBox("NỘI LỰC")
        form_loads = QFormLayout()
        
        self.bm_inp_Mx = QLineEdit("50")
        self.bm_inp_My = QLineEdit("0")
        self.bm_inp_V = QLineEdit("100")
        
        form_loads.addRow("Moment Mx (kNm):", self.bm_inp_Mx)
        form_loads.addRow("Moment My (kNm):", self.bm_inp_My)
        form_loads.addRow("Lực cắt V (kN):", self.bm_inp_V)
        gb_loads.setLayout(form_loads)
        left_layout.addWidget(gb_loads)
        
        # Deflection
        gb_defl = QGroupBox("KIỂM TRA VÕNG")
        form_defl = QFormLayout()
        
        self.bm_inp_L = QLineEdit("6.0")
        self.bm_inp_q = QLineEdit("10.0")
        
        form_defl.addRow("Nhịp L (m):", self.bm_inp_L)
        form_defl.addRow("Tải phục vụ q (kN/m):", self.bm_inp_q)
        gb_defl.setLayout(form_defl)
        left_layout.addWidget(gb_defl)
        
        # Design Button
        btn_design = QPushButton("⚡ KIỂM TRA DẦM")
        btn_design.setStyleSheet("""
            QPushButton {
                background-color: #607d8b; color: white;
                font-size: 14px; font-weight: bold; padding: 15px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #78909c; }
        """)
        btn_design.clicked.connect(self.check_beam)
        left_layout.addWidget(btn_design)
        
        left_layout.addStretch()
        
        # Right: Results
        self.bm_txt_results = QTextBrowser()
        
        layout.addWidget(left_panel)
        layout.addWidget(self.bm_txt_results, 1)
        
        return panel
        
    def create_column_panel(self):
        """Create box column panel"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Left: Inputs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Title
        title = QLabel("⬛ CỘT THÉP HỘP (TCVN 5575:2024)")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #455a64; color: white; padding: 10px; border-radius: 5px;")
        left_layout.addWidget(title)
        
        # Section
        gb_section = QGroupBox("TIẾT DIỆN")
        form_section = QFormLayout()
        
        self.col_cbo_section = QComboBox()
        # Load all Vietnamese box sections
        box_sections = SteelSectionDatabase.get_all_box_sections()
        self.col_cbo_section.addItems(box_sections)
        
        self.col_cbo_steel = QComboBox()
        self.col_cbo_steel.addItems(list(SteelSectionDatabase.STEEL_GRADES.keys()))
        
        form_section.addRow("Tiết diện:", self.col_cbo_section)
        form_section.addRow("Mác thép:", self.col_cbo_steel)
        gb_section.setLayout(form_section)
        left_layout.addWidget(gb_section)
        
        # Geometry
        gb_geo = QGroupBox("CHIỀU DÀI TÍNH TOÁN")
        form_geo = QFormLayout()
        
        self.col_inp_L = QLineEdit("4.0")
        self.col_inp_K = QLineEdit("1.0")
        
        form_geo.addRow("Chiều dài L (m):", self.col_inp_L)
        form_geo.addRow("Hệ số K:", self.col_inp_K)
        
        lbl_k = QLabel("<i>K=1.0 (ngàm-tự do), K=0.7 (ngàm-ngàm), K=0.5 (ngàm cứng)</i>")
        lbl_k.setWordWrap(True)
        form_geo.addRow("", lbl_k)
        
        gb_geo.setLayout(form_geo)
        left_layout.addWidget(gb_geo)
        
        # Loads
        gb_loads = QGroupBox("NỘI LỰC")
        form_loads = QFormLayout()
        
        self.col_inp_P = QLineEdit("500")
        self.col_inp_Mx = QLineEdit("50")
        self.col_inp_My = QLineEdit("0")
        
        form_loads.addRow("Lực nén P (kN):", self.col_inp_P)
        form_loads.addRow("Moment Mx (kNm):", self.col_inp_Mx)
        form_loads.addRow("Moment My (kNm):", self.col_inp_My)
        gb_loads.setLayout(form_loads)
        left_layout.addWidget(gb_loads)
        
        # Design Button
        btn_design = QPushButton("⚡ KIỂM TRA CỘT")
        btn_design.setStyleSheet("""
            QPushButton {
                background-color: #455a64; color: white;
                font-size: 14px; font-weight: bold; padding: 15px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #546e7a; }
        """)
        btn_design.clicked.connect(self.check_column)
        left_layout.addWidget(btn_design)
        
        left_layout.addStretch()
        
        # Right: Results
        self.col_txt_results = QTextBrowser()
        
        layout.addWidget(left_panel)
        layout.addWidget(self.col_txt_results, 1)
        
        return panel
        
    def check_beam(self):
        """Check I-beam"""
        try:
            section = self.bm_cbo_section.currentText()
            steel = self.bm_cbo_steel.currentText()
            
            Mx = float(self.bm_inp_Mx.text())
            My = float(self.bm_inp_My.text())
            V = float(self.bm_inp_V.text())
            L = float(self.bm_inp_L.text())
            q = float(self.bm_inp_q.text())
            
            # Create designer
            self.beam_designer = SteelIBeamDesigner(section, steel)
            
            # Check
            bend_result = self.beam_designer.check_bending(Mx, My)
            shear_result = self.beam_designer.check_shear(V)
            defl_result = self.beam_designer.check_deflection(L, q)
            
            # Display
            self.display_beam_results(bend_result, shear_result, defl_result)
            
        except ValueError as e:
            QMessageBox.warning(self, "Lỗi", f"Kiểm tra số liệu nhập:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi kiểm tra:\n{str(e)}")
            
    def display_beam_results(self, bend, shear, defl):
        """Display beam results"""
        overall_status = 'OK' if (bend['status'] == 'OK' and shear['status'] == 'OK' and defl['status'] == 'OK') else 'FAIL'
        status_color = "green" if overall_status == 'OK' else "red"
        
        html = f"""
        <h2 style='color: {status_color};'>KẾT QUẢ KIỂM TRA DẦM THÉP I: {overall_status}</h2>
        
        <h3>1. Kiểm tra Uốn (Bending):</h3>
        <ul>
            <li>Sức kháng uốn φM<sub>nx</sub> = {bend['phi_M_nx']:.1f} kNm</li>
            <li>Sức kháng uốn φM<sub>ny</sub> = {bend['phi_M_ny']:.1f} kNm</li>
            <li>Moment tác dụng M<sub>x</sub> = {bend['M_x']:.1f} kNm</li>
            <li>Moment tác dụng M<sub>y</sub> = {bend['M_y']:.1f} kNm</li>
            <li><b>Tỷ lệ: {bend['ratio']:.3f}</b> {'✓' if bend['status'] == 'OK' else '✗'}</li>
        </ul>
        
        <h3>2. Kiểm tra Cắt (Shear):</h3>
        <ul>
            <li>Sức kháng cắt φV<sub>n</sub> = {shear['phi_V_n']:.1f} kN</li>
            <li>Lực cắt tác dụng V = {shear['V']:.1f} kN</li>
            <li><b>Tỷ lệ: {shear['ratio']:.3f}</b> {'✓' if shear['status'] == 'OK' else '✗'}</li>
        </ul>
        
        <h3>3. Kiểm tra Võng (Deflection):</h3>
        <ul>
            <li>Độ võng tính toán δ = {defl['delta']:.2f} mm</li>
            <li>Giới hạn [δ] = {defl['delta_allow']:.2f} mm (L/360)</li>
            <li><b>Tỷ lệ: {defl['ratio']:.3f}</b> {'✓' if defl['status'] == 'OK' else '✗'}</li>
        </ul>
        """
        
        self.bm_txt_results.setHtml(html)
        
    def check_column(self):
        """Check box column"""
        try:
            section = self.col_cbo_section.currentText()
            steel = self.col_cbo_steel.currentText()
            L = float(self.col_inp_L.text())
            K = float(self.col_inp_K.text())
            
            P = float(self.col_inp_P.text())
            Mx = float(self.col_inp_Mx.text())
            My = float(self.col_inp_My.text())
            
            # Create designer
            self.column_designer = SteelBoxColumnDesigner(section, steel, L, K)
            
            # Check
            if Mx == 0 and My == 0:
                # Pure compression
                result = self.column_designer.check_axial_compression(P)
                self.display_column_axial_results(result)
            else:
                # Combined loading
                result = self.column_designer.check_combined_loading(P, Mx, My)
                self.display_column_combined_results(result)
            
        except ValueError as e:
            QMessageBox.warning(self, "Lỗi", f"Kiểm tra số liệu nhập:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi kiểm tra:\n{str(e)}")
            
    def display_column_axial_results(self, result):
        """Display pure axial results"""
        status_color = "green" if result['status'] == 'OK' else "red"
        
        html = f"""
        <h2 style='color: {status_color};'>KẾT QUẢ KIỂM TRA CỘT NÉN: {result['status']}</h2>
        
        <h3>1. Độ mảnh:</h3>
        <ul>
            <li>Tỷ số λ = KL/r = {result['lambda']:.1f}</li>
        </ul>
        
        <h3>2. Ổn định uốn dọc (Buckling):</h3>
        <ul>
            <li>Ứng suất tới hạn F<sub>cr</sub> = {result['F_cr']:.1f} MPa</li>
            <li>Sức kháng nén P<sub>n</sub> = {result['P_n']:.1f} kN</li>
            <li>Sức kháng thiết kế φP<sub>n</sub> = {result['phi_P_n']:.1f} kN</li>
        </ul>
        
        <h3>3. Kiểm tra:</h3>
        <ul>
            <li>Lực nén tác dụng P = {result['P']:.1f} kN</li>
            <li><b>Tỷ lệ: {result['ratio']:.3f}</b> {'✓' if result['status'] == 'OK' else '✗'}</li>
        </ul>
        """
        
        self.col_txt_results.setHtml(html)
        
    def display_column_combined_results(self, result):
        """Display combined loading results"""
        status_color = "green" if result['status'] == 'OK' else "red"
        
        html = f"""
        <h2 style='color: {status_color};'>KẾT QUẢ KIỂM TRA CỘT NÉN + UỐN: {result['status']}</h2>
        
        <h3>1. Sức kháng:</h3>
        <ul>
            <li>Sức kháng nén φP<sub>n</sub> = {result['phi_P_n']:.1f} kN</li>
            <li>Sức kháng uốn φM<sub>nx</sub> = {result['phi_M_nx']:.1f} kNm</li>
            <li>Sức kháng uốn φM<sub>ny</sub> = {result['phi_M_ny']:.1f} kNm</li>
        </ul>
        
        <h3>2. Nội lực tác dụng:</h3>
        <ul>
            <li>Lực nén P = {result['P']:.1f} kN</li>
            <li>Moment M<sub>x</sub> = {result['M_x']:.1f} kNm</li>
            <li>Moment M<sub>y</sub> = {result['M_y']:.1f} kNm</li>
        </ul>
        
        <h3>3. Tương tác P-M:</h3>
        <ul>
            <li><b>Tỷ lệ tương tác: {result['ratio']:.3f}</b> {'✓' if result['status'] == 'OK' else '✗'}</li>
            <li><i>Công thức: P/φP<sub>n</sub> + 8/9(M<sub>x</sub>/φM<sub>nx</sub> + M<sub>y</sub>/φM<sub>ny</sub>) ≤ 1.0</i></li>
        </ul>
        """
        
        self.col_txt_results.setHtml(html)
