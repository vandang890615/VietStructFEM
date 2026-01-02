# -*- coding: utf-8 -*-
"""
Steel Connections Module - UI
Liên Kết Thép - Vietnamese Steel Connection Design Interface
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QFormLayout, QLineEdit, QComboBox, QPushButton, 
                             QLabel, QTabWidget, QTextBrowser, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from steeldeckfem.core.connection_designer import ConnectionDesigner


class ConnectionModule(QWidget):
    """Steel Connection Designer Module"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Bolted Connection
        self.tabs.addTab(self.create_bolt_panel(), "🔩 BU LÔNG (Bolted)")
        
        # Tab 2: Welded Connection
        self.tabs.addTab(self.create_weld_panel(), "⚡ HÀN (Welded)")
        
        # Tab 3: Base Plate
        self.tabs.addTab(self.create_baseplate_panel(), "🔲 CHÂN CỘT (Base Plate)")
        
        main_layout.addWidget(self.tabs)
        
    def create_bolt_panel(self):
        """Create bolted connection panel"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Left: Inputs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Title
        title = QLabel("🔩 LIÊN KẾT BU LÔNG (TCVN 5575:2024)")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #37474f; color: white; padding: 10px; border-radius: 5px;")
        left_layout.addWidget(title)
        
        # Bolt properties
        gb_bolt = QGroupBox("THÔNG SỐ BU LÔNG")
        form_bolt = QFormLayout()
        
        self.bolt_inp_n = QLineEdit("4")
        self.bolt_cbo_dia = QComboBox()
        self.bolt_cbo_dia.addItems(['M12', 'M16', 'M20', 'M22', 'M24', 'M27', 'M30'])
        self.bolt_cbo_dia.setCurrentText('M20')
        
        self.bolt_cbo_grade = QComboBox()
        self.bolt_cbo_grade.addItems(list(ConnectionDesigner.BOLT_GRADES.keys()))
        
        form_bolt.addRow("Số bu lông:", self.bolt_inp_n)
        form_bolt.addRow("Đường kính:", self.bolt_cbo_dia)
        form_bolt.addRow("Cấp bu lông:", self.bolt_cbo_grade)
        gb_bolt.setLayout(form_bolt)
        left_layout.addWidget(gb_bolt)
        
        # Plate
        gb_plate = QGroupBox("TẤM THÉP")
        form_plate = QFormLayout()
        
        self.bolt_inp_t = QLineEdit("10")
        self.bolt_inp_Fu = QLineEdit("400")
        
        form_plate.addRow("Chiều dày t (mm):", self.bolt_inp_t)
        form_plate.addRow("Fu (MPa):", self.bolt_inp_Fu)
        gb_plate.setLayout(form_plate)
        left_layout.addWidget(gb_plate)
        
        # Forces
        gb_force = QGroupBox("NỘI LỰC")
        form_force = QFormLayout()
        
        self.bolt_inp_V = QLineEdit("50")
        self.bolt_inp_T = QLineEdit("0")
        
        form_force.addRow("Lực cắt V (kN):", self.bolt_inp_V)
        form_force.addRow("Lực kéo T (kN):", self.bolt_inp_T)
        gb_force.setLayout(form_force)
        left_layout.addWidget(gb_force)
        
        # Check Button
        btn_check = QPushButton("⚡ KIỂM TRA LIÊN KẾT")
        btn_check.setStyleSheet("""
            QPushButton {
                background-color: #37474f; color: white;
                font-size: 14px; font-weight: bold; padding: 15px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #455a64; }
        """)
        btn_check.clicked.connect(self.check_bolt)
        left_layout.addWidget(btn_check)
        
        left_layout.addStretch()
        
        # Right: Results
        self.bolt_txt_results = QTextBrowser()
        
        layout.addWidget(left_panel)
        layout.addWidget(self.bolt_txt_results, 1)
        
        return panel
        
    def create_weld_panel(self):
        """Create welded connection panel"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Left: Inputs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Title
        title = QLabel("⚡ LIÊN KẾT HÀN (TCVN 5575:2024)")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #263238; color: white; padding: 10px; border-radius: 5px;")
        left_layout.addWidget(title)
        
        # Weld properties
        gb_weld = QGroupBox("THÔNG SỐ HÀN")
        form_weld = QFormLayout()
        
        self.weld_cbo_type = QComboBox()
        self.weld_cbo_type.addItems(['fillet (Hàn góc)', 'groove (Hàn giáp mối)'])
        
        self.weld_inp_size = QLineEdit("6")
        self.weld_inp_length = QLineEdit("200")
        
        self.weld_cbo_electrode = QComboBox()
        self.weld_cbo_electrode.addItems(['E60', 'E70', 'E80'])
        self.weld_cbo_electrode.setCurrentText('E70')
        
        form_weld.addRow("Loại hàn:", self.weld_cbo_type)
        form_weld.addRow("Kích thước a (mm):", self.weld_inp_size)
        form_weld.addRow("Chiều dài L (mm):", self.weld_inp_length)
        form_weld.addRow("Que hàn:", self.weld_cbo_electrode)
        gb_weld.setLayout(form_weld)
        left_layout.addWidget(gb_weld)
        
        # Force
        gb_force = QGroupBox("NỘI LỰC")
        form_force = QFormLayout()
        
        self.weld_inp_V = QLineEdit("50")
        
        form_force.addRow("Lực tác dụng V (kN):", self.weld_inp_V)
        gb_force.setLayout(form_force)
        left_layout.addWidget(gb_force)
        
        # Check Button
        btn_check = QPushButton("⚡ KIỂM TRA HÀN")
        btn_check.setStyleSheet("""
            QPushButton {
                background-color: #263238; color: white;
                font-size: 14px; font-weight: bold; padding: 15px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #37474f; }
        """)
        btn_check.clicked.connect(self.check_weld)
        left_layout.addWidget(btn_check)
        
        left_layout.addStretch()
        
        # Right: Results
        self.weld_txt_results = QTextBrowser()
        
        layout.addWidget(left_panel)
        layout.addWidget(self.weld_txt_results, 1)
        
        return panel
        
    def create_baseplate_panel(self):
        """Create base plate panel"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Left: Inputs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Title
        title = QLabel("🔲 CHÂN CỘT (Base Plate)")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #424242; color: white; padding: 10px; border-radius: 5px;")
        left_layout.addWidget(title)
        
        # Column
        gb_col = QGroupBox("CỘT")
        form_col = QFormLayout()
        
        self.bp_inp_col = QLineEdit("300")
        
        form_col.addRow("Kích thước cột (mm):", self.bp_inp_col)
        gb_col.setLayout(form_col)
        left_layout.addWidget(gb_col)
        
        # Forces
        gb_force = QGroupBox("NỘI LỰC")
        form_force = QFormLayout()
        
        self.bp_inp_P = QLineEdit("500")
        self.bp_inp_M = QLineEdit("50")
        
        form_force.addRow("Lực nén P (kN):", self.bp_inp_P)
        form_force.addRow("Moment M (kNm):", self.bp_inp_M)
        gb_force.setLayout(form_force)
        left_layout.addWidget(gb_force)
        
        # Materials
        gb_mat = QGroupBox("VẬT LIỆU")
        form_mat = QFormLayout()
        
        self.bp_inp_fc = QLineEdit("20")
        self.bp_inp_Fy = QLineEdit("235")
        
        form_mat.addRow("Bê tông f'c (MPa):", self.bp_inp_fc)
        form_mat.addRow("Thép tấm Fy (MPa):", self.bp_inp_Fy)
        gb_mat.setLayout(form_mat)
        left_layout.addWidget(gb_mat)
        
        # Design Button
        btn_design = QPushButton("⚡ THIẾT KẾ CHÂN CỘT")
        btn_design.setStyleSheet("""
            QPushButton {
                background-color: #424242; color: white;
                font-size: 14px; font-weight: bold; padding: 15px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #616161; }
        """)
        btn_design.clicked.connect(self.design_baseplate)
        left_layout.addWidget(btn_design)
        
        left_layout.addStretch()
        
        # Right: Results
        self.bp_txt_results = QTextBrowser()
        
        layout.addWidget(left_panel)
        layout.addWidget(self.bp_txt_results, 1)
        
        return panel
        
    def check_bolt(self):
        """Check bolted connection"""
        try:
            n = int(self.bolt_inp_n.text())
            dia_text = self.bolt_cbo_dia.currentText()
            dia = int(dia_text.replace('M', ''))
            grade = self.bolt_cbo_grade.currentText()
            t = float(self.bolt_inp_t.text())
            Fu = float(self.bolt_inp_Fu.text())
            V = float(self.bolt_inp_V.text())
            T = float(self.bolt_inp_T.text())
            
            # Check
            result = ConnectionDesigner.check_bolted_connection(n, dia, grade, V, T, t, Fu)
            
            # Display
            status_color = "green" if result['status'] == 'OK' else "red"
            
            html = f"""
            <h2 style='color: {status_color};'>KẾT QUẢ KIỂM TRA BU LÔNG: {result['status']}</h2>
            
            <h3>1. Thông số:</h3>
            <ul>
                <li>{result['n_bolts']} bu lông {result['bolt_dia']}mm {result['bolt_grade']}</li>
            </ul>
            
            <h3>2. Kiểm tra Cắt:</h3>
            <ul>
                <li>Sức kháng cắt φRn = {result['phi_Rn_shear']:.1f} kN</li>
                <li>Lực cắt V = {result['V']:.1f} kN</li>
                <li><b>Tỷ lệ: {result['V_ratio']:.3f}</b> {'✓' if result['V_ratio'] <= 1.0 else '✗'}</li>
            </ul>
            
            <h3>3. Kiểm tra Bearing (Ép mặt):</h3>
            <ul>
                <li>Sức kháng ép φRn = {result['phi_Rn_bearing']:.1f} kN</li>
                <li><b>Tỷ lệ: {result['bearing_ratio']:.3f}</b> {'✓' if result['bearing_ratio'] <= 1.0 else '✗'}</li>
            </ul>
            """
            
            if result['T_ratio'] is not None:
                html += f"""
                <h3>4. Tương tác Cắt-Kéo:</h3>
                <ul>
                    <li>Tỷ lệ kéo: {result['T_ratio']:.3f}</li>
                    <li><b>Tương tác: {result['interaction']:.3f}</b> {'✓' if result['interaction'] <= 1.0 else '✗'}</li>
                </ul>
                """
            
            self.bolt_txt_results.setHtml(html)
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
            
    def check_weld(self):
        """Check welded connection"""
        try:
            type_text = self.weld_cbo_type.currentText()
            weld_type = 'fillet' if 'fillet' in type_text else 'groove'
            size = float(self.weld_inp_size.text())
            length = float(self.weld_inp_length.text())
            electrode = self.weld_cbo_electrode.currentText()
            V = float(self.weld_inp_V.text())
            
            # Check
            result = ConnectionDesigner.check_welded_connection(length, size, V, weld_type, electrode)
            
            # Display
            status_color = "green" if result['status'] == 'OK' else "red"
            
            html = f"""
            <h2 style='color: {status_color};'>KẾT QUẢ KIỂM TRA HÀN: {result['status']}</h2>
            
            <h3>1. Thông số hàn:</h3>
            <ul>
                <li>Loại: {result['weld_type']}</li>
                <li>Kích thước: {result['weld_size']} mm</li>
                <li>Chiều dài: {result['weld_length']} mm</li>
                <li>Chiều dày cổ hàn: {result['throat']:.1f} mm</li>
            </ul>
            
            <h3>2. Sức kháng:</h3>
            <ul>
                <li>Sức kháng danh định Rn = {result['Rn']:.1f} kN</li>
                <li>Sức kháng thiết kế φRn = {result['phi_Rn']:.1f} kN</li>
            </ul>
            
            <h3>3. Kiểm tra:</h3>
            <ul>
                <li>Lực tác dụng V = {result['V']:.1f} kN</li>
                <li><b>Tỷ lệ: {result['ratio']:.3f}</b> {'✓' if result['status'] == 'OK' else '✗'}</li>
            </ul>
            """
            
            self.weld_txt_results.setHtml(html)
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
            
    def design_baseplate(self):
        """Design base plate"""
        try:
            col = float(self.bp_inp_col.text())
            P = float(self.bp_inp_P.text())
            M = float(self.bp_inp_M.text())
            fc = float(self.bp_inp_fc.text())
            Fy = float(self.bp_inp_Fy.text())
            
            # Design
            result = ConnectionDesigner.design_base_plate(P, M, col, fc, Fy)
            
            # Display
            status_color = "green" if result['status'] == 'OK' else "red"
            
            html = f"""
            <h2 style='color: {status_color};'>KẾT QUẢ THIẾT KẾ CHÂN CỘT</h2>
            
            <h3>1. Kích thước tấm đế:</h3>
            <ul>
                <li><b>B × L = {result['B']} × {result['L']} mm</b></li>
                <li><b>Chiều dày t = {result['t']} mm</b></li>
            </ul>
            
            <h3>2. Kiểm tra Ép bê tông:</h3>
            <ul>
                <li>Áp lực tối đa q = {result['q_max']:.2f} MPa</li>
                <li>Cho phép fp = {result['fp_allow']:.2f} MPa</li>
                <li><b>Tỷ lệ: {result['bearing_ratio']:.3f}</b> {'✓' if result['status'] == 'OK' else '✗'}</li>
            </ul>
            
            <h3>3. Bu lông neo:</h3>
            <ul>
                <li><b>{result['anchor_bolts']}</b></li>
                <li><i>💡 Cần kiểm tra chi tiết bu lông neo riêng</i></li>
            </ul>
            
            <p><i>{result['status']}</i></p>
            """
            
            self.bp_txt_results.setHtml(html)
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
