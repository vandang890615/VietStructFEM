# -*- coding: utf-8 -*-
"""
Deflection Check Module - UI
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QFormLayout, QLineEdit, QComboBox, QPushButton, 
                             QLabel, QTextBrowser, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from steeldeckfem.core.deflection_utility import DeflectionCalculator


class DeflectionModule(QWidget):
    """Deflection Check Utility Module"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QHBoxLayout(self)
        
        # Left: Inputs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Title
        title = QLabel("📏 KIỂM TRA VÕNG (TCVN 2737:2023)")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #00796b; color: white; padding: 10px; border-radius: 5px;")
        left_layout.addWidget(title)
        
        # Beam Type
        gb_beam = QGroupBox("LOẠI DẦM")
        form_beam = QFormLayout()
        
        self.cbo_beam = QComboBox()
        self.cbo_beam.addItems(['Simply Supported (Tựa đơn)', 'Fixed-Fixed (Ngàm 2 đầu)', 'Cantilever (Công xôn)'])
        
        form_beam.addRow("Điều kiện tựa:", self.cbo_beam)
        gb_beam.setLayout(form_beam)
        left_layout.addWidget(gb_beam)
        
        # Geometry
        gb_geo = QGroupBox("HÌNH HỌC")
        form_geo = QFormLayout()
        
        self.inp_L = QLineEdit("6.0")
        self.inp_E = QLineEdit("200000")
        self.inp_I = QLineEdit("100000000")
        
        form_geo.addRow("Nhịp L (m):", self.inp_L)
        form_geo.addRow("E (MPa):", self.inp_E)
        form_geo.addRow("I (mm⁴):", self.inp_I)
        gb_geo.setLayout(form_geo)
        left_layout.addWidget(gb_geo)
        
        # Load
        gb_load = QGroupBox("TẢI TRỌNG")
        form_load = QFormLayout()
        
        self.cbo_load = QComboBox()
        self.cbo_load.addItems(['Uniform load (Phân bố đều)', 'Point load at center (Tập trung giữa nhịp)'])
        
        self.inp_q = QLineEdit("10.0")
        
        form_load.addRow("Loại tải:", self.cbo_load)
        form_load.addRow("q hoặc P (kN/m hoặc kN):", self.inp_q)
        gb_load.setLayout(form_load)
        left_layout.addWidget(gb_load)
        
        # Limit
        gb_limit = QGroupBox("GIỚI HẠN")
        form_limit = QFormLayout()
        
        self.cbo_limit = QComboBox()
        self.cbo_limit.addItems(['L/250 (General)', 'L/360 (Brittle finish)', 'L/180 (Roof)', 'L/300 (Floor)'])
        
        form_limit.addRow("Tiêu chuẩn võng:", self.cbo_limit)
        gb_limit.setLayout(form_limit)
        left_layout.addWidget(gb_limit)
        
        # Check Button
        btn_check = QPushButton("⚡ KIỂM TRA VÕNG")
        btn_check.setStyleSheet("""
            QPushButton {
                background-color: #00796b; color: white;
                font-size: 14px; font-weight: bold; padding: 15px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #009688; }
        """)
        btn_check.clicked.connect(self.check_deflection)
        left_layout.addWidget(btn_check)
        
        left_layout.addStretch()
        
        # Right: Results
        self.txt_results = QTextBrowser()
        
        layout.addWidget(left_panel)
        layout.addWidget(self.txt_results, 1)
        
    def check_deflection(self):
        """Check deflection"""
        try:
            L = float(self.inp_L.text())
            E = float(self.inp_E.text())
            I = float(self.inp_I.text())
            q_or_P = float(self.inp_q.text())
            
            # Get beam type
            beam_text = self.cbo_beam.currentText()
            if 'Simply' in beam_text:
                beam_type = 'simply_supported'
            elif 'Fixed' in beam_text:
                beam_type = 'fixed_fixed'
            else:
                beam_type = 'cantilever'
            
            # Get load type
            load_text = self.cbo_load.currentText()
            if 'Uniform' in load_text:
                load_type = 'uniform'
                load_params = {'q': q_or_P * 1000 / 1000}  # kN/m to N/mm
            else:
                if beam_type == 'cantilever':
                    load_type = 'point_end'
                else:
                    load_type = 'point_center'
                load_params = {'P': q_or_P}  # kN
            
            # Get limit type
            limit_text = self.cbo_limit.currentText()
            if 'L/360' in limit_text:
                limit_type = 'beam_brittle_finish'
            elif 'L/180' in limit_text:
                limit_type = 'roof_beam'
            elif 'L/300' in limit_text:
                limit_type = 'floor_beam'
            else:
                limit_type = 'beam_general'
            
            load_params['limit_type'] = limit_type
            
            # Calculate
            result = DeflectionCalculator.calculate_deflection(beam_type, L, E, I, load_type, **load_params)
            
            # Display
            status_color = "green" if result['status'] == 'OK' else "red"
            
            html = f"""
            <h2 style='color: {status_color};'>KẾT QUẢ KIỂM TRA VÕNG: {result['status']}</h2>
            
            <h3>Độ võng tính toán:</h3>
            <ul>
                <li><b>δ = {result['deflection_mm']:.2f} mm</b></li>
                <li>Tỷ lệ thực tế: L/{result['actual_L_ratio']:.0f}</li>
            </ul>
            
            <h3>Giới hạn cho phép:</h3>
            <ul>
                <li>[δ] = {result['limit_mm']:.2f} mm</li>
                <li>Tiêu chuẩn: {limit_text}</li>
            </ul>
            
            <h3>Đánh giá:</h3>
            <ul>
                <li><b>Tỷ lệ: {result['ratio']:.3f}</b> {'✓' if result['status'] == 'OK' else '✗'}</li>
                <li>{'Đạt yêu cầu' if result['status'] == 'OK' else 'Không đạt - cần tăng độ cứng'}</li>
            </ul>
            """
            
            self.txt_results.setHtml(html)
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
