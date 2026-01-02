# -*- coding: utf-8 -*-
"""
Foundation Module - UI
Móng - Vietnamese Foundation Design Interface
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QFormLayout, QLineEdit, QComboBox, QPushButton, 
                             QLabel, QTabWidget, QTextBrowser, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from steeldeckfem.core.foundation_designer import IsolatedFootingDesigner, PileFoundationDesigner, SoilDatabase


class FoundationModule(QWidget):
    """Foundation Designer Module"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.footing_designer = None
        self.pile_designer = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Isolated Footing
        self.tabs.addTab(self.create_footing_panel(), "🔲 MÓNG ĐƠN (Footing)")
        
        # Tab 2: Pile Foundation
        self.tabs.addTab(self.create_pile_panel(), "🔩 MÓNG CỌC (Pile)")
        
        main_layout.addWidget(self.tabs)
        
    def create_footing_panel(self):
        """Create isolated footing panel"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Left: Inputs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Title
        title = QLabel("🔲 MÓNG ĐƠN (TCVN 9362:2012)")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #795548; color: white; padding: 10px; border-radius: 5px;")
        left_layout.addWidget(title)
        
        # Loads
        gb_loads = QGroupBox("TẢI TRỌNG")
        form_loads = QFormLayout()
        
        self.ft_inp_P = QLineEdit("500")
        self.ft_inp_M = QLineEdit("50")
        
        form_loads.addRow("Tải trọng dọc P (kN):", self.ft_inp_P)
        form_loads.addRow("Moment M (kNm):", self.ft_inp_M)
        gb_loads.setLayout(form_loads)
        left_layout.addWidget(gb_loads)
        
        # Soil
        gb_soil = QGroupBox("ĐỊA CHẤT")
        form_soil = QFormLayout()
        
        self.ft_cbo_soil = QComboBox()
        self.ft_cbo_soil.addItems(list(SoilDatabase.SOIL_TYPES.keys()))
        self.ft_cbo_soil.setCurrentText('Sand - Medium')
        
        self.ft_inp_depth = QLineEdit("1.5")
        
        form_soil.addRow("Loại đất:", self.ft_cbo_soil)
        form_soil.addRow("Độ sâu chôn D (m):", self.ft_inp_depth)
        
        lbl_note = QLabel("<i>💡 Để cập nhật database đất, xem file missing_data.md</i>")
        lbl_note.setWordWrap(True)
        form_soil.addRow("", lbl_note)
        
        gb_soil.setLayout(form_soil)
        left_layout.addWidget(gb_soil)
        
        # Column
        gb_col = QGroupBox("CỘT")
        form_col = QFormLayout()
        
        self.ft_inp_col = QLineEdit("400")
        
        form_col.addRow("Kích thước cột (mm):", self.ft_inp_col)
        gb_col.setLayout(form_col)
        left_layout.addWidget(gb_col)
        
        # Design Button
        btn_design = QPushButton("⚡ THIẾT KẾ MÓNG ĐƠN")
        btn_design.setStyleSheet("""
            QPushButton {
                background-color: #795548; color: white;
                font-size: 14px; font-weight: bold; padding: 15px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #8d6e63; }
        """)
        btn_design.clicked.connect(self.design_footing)
        left_layout.addWidget(btn_design)
        
        left_layout.addStretch()
        
        # Right: Results
        self.ft_txt_results = QTextBrowser()
        
        layout.addWidget(left_panel)
        layout.addWidget(self.ft_txt_results, 1)
        
        return panel
        
    def create_pile_panel(self):
        """Create pile foundation panel"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Left: Inputs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Title
        title = QLabel("🔩 MÓNG CỌC (TCVN 10304:2014)")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #5d4037; color: white; padding: 10px; border-radius: 5px;")
        left_layout.addWidget(title)
        
        # Pile Properties
        gb_pile = QGroupBox("THÔNG SỐ CỌC")
        form_pile = QFormLayout()
        
        self.pl_inp_D = QLineEdit("400")
        self.pl_inp_L = QLineEdit("12.0")
        
        form_pile.addRow("Đường kính cọc D (mm):", self.pl_inp_D)
        form_pile.addRow("Chiều dài cọc L (m):", self.pl_inp_L)
        gb_pile.setLayout(form_pile)
        left_layout.addWidget(gb_pile)
        
        # Soil (simplified)
        gb_soil = QGroupBox("ĐỊA CHẤT (Đơn giản)")
        form_soil = QFormLayout()
        
        self.pl_cbo_soil = QComboBox()
        self.pl_cbo_soil.addItems(['Clay - Medium', 'Sand - Dense', 'Mixed Soil'])
        
        lbl_note = QLabel("<i>⚠️ Tính toán đơn giản hóa. Cần SPT data cho chính xác.</i>")
        lbl_note.setWordWrap(True)
        
        form_soil.addRow("Loại đất:", self.pl_cbo_soil)
        form_soil.addRow("", lbl_note)
        gb_soil.setLayout(form_soil)
        left_layout.addWidget(gb_soil)
        
        # Pile Group
        gb_group = QGroupBox("NHÓM CỌC")
        form_group = QFormLayout()
        
        self.pl_inp_n = QLineEdit("4")
        self.pl_inp_spacing = QLineEdit("3.0")
        
        form_group.addRow("Số lượng cọc:", self.pl_inp_n)
        form_group.addRow("Khoảng cách cọc s (m):", self.pl_inp_spacing)
        gb_group.setLayout(form_group)
        left_layout.addWidget(gb_group)
        
        # Design Button
        btn_design = QPushButton("⚡ THIẾT KẾ MÓNG CỌC")
        btn_design.setStyleSheet("""
            QPushButton {
                background-color: #5d4037; color: white;
                font-size: 14px; font-weight: bold; padding: 15px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #6d4c41; }
        """)
        btn_design.clicked.connect(self.design_pile)
        left_layout.addWidget(btn_design)
        
        left_layout.addStretch()
        
        # Right: Results
        self.pl_txt_results = QTextBrowser()
        
        layout.addWidget(left_panel)
        layout.addWidget(self.pl_txt_results, 1)
        
        return panel
        
    def design_footing(self):
        """Design isolated footing"""
        try:
            P = float(self.ft_inp_P.text())
            M = float(self.ft_inp_M.text())
            soil_type = self.ft_cbo_soil.currentText()
            depth = float(self.ft_inp_depth.text())
            col_size = float(self.ft_inp_col.text())
            
            # Create designer
            self.footing_designer = IsolatedFootingDesigner(P, M, soil_type, depth)
            
            # Design footing size
            size_result = self.footing_designer.design_footing_size()
            
            B = size_result['B']
            
            # Check punching shear (assume h = B/4, min 300mm)
            h = max(B / 4 * 1000, 300)
            punch_result = self.footing_designer.check_punching_shear(B, col_size, h)
            
            # Design reinforcement
            rebar_result = self.footing_designer.design_reinforcement(B, col_size)
            
            # Display results
            self.display_footing_results(size_result, punch_result, rebar_result)
            
        except ValueError as e:
            QMessageBox.warning(self, "Lỗi", f"Kiểm tra số liệu nhập:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi thiết kế:\n{str(e)}")
            
    def display_footing_results(self, size, punch, rebar):
        """Display footing results"""
        status_color = "green" if (size['status'] == 'OK' and punch['status'] == 'OK') else "red"
        
        html = f"""
        <h2 style='color: {status_color};'>KẾT QUẢ THIẾT KẾ MÓNG ĐƠN</h2>
        
        <h3>1. Kích thước móng:</h3>
        <ul>
            <li>Sức chịu tải cực hạn q<sub>ult</sub> = {size['q_ult']:.1f} kPa</li>
            <li>Sức chịu tải cho phép q<sub>allow</sub> = {size['q_allow']:.1f} kPa</li>
            <li><b>Kích thước: B × L = {size['B']:.2f} × {size['L']:.2f} m</b></li>
            <li>Diện tích A = {size['A']:.2f} m²</li>
            <li>Áp lực thực tế q = {size['q_actual']:.1f} kPa</li>
            <li>Hệ số an toàn FS = {size['FS']:.2f} {'✓' if size['status'] == 'OK' else '✗'}</li>
        </ul>
        
        <h3>2. Kiểm tra chọc thủng:</h3>
        <ul>
            <li>Lực chọc thủng P<sub>punch</sub> = {punch['P_punch']:.1f} kN</li>
            <li>Ứng suất chọc thủng v<sub>u</sub> = {punch['v_u']:.2f} MPa</li>
            <li>Cho phép v<sub>c</sub> = {punch['v_c']:.2f} MPa</li>
            <li>Tỷ lệ: {punch['ratio']:.2f} {'✓' if punch['status'] == 'OK' else '✗'}</li>
        </ul>
        
        <h3>3. Cốt thép:</h3>
        <ul>
            <li>Chiều dày móng đề xuất h = {rebar['h_recommended']:.0f} mm</li>
            <li>Chiều cao hữu ích d = {rebar['d']:.0f} mm</li>
            <li>Moment M = {rebar['M']:.2f} kNm/m</li>
            <li>Cốt thép cần A<sub>s</sub> = {rebar['As_required']:.0f} mm²/m</li>
            <li><b>Bố trí: {rebar['bar_config']}</b></li>
            <li>Cung cấp A<sub>s</sub> = {rebar['As_provided']:.0f} mm²/m ✓</li>
        </ul>
        
        <p><i>💡 Lưu ý: Kết quả dựa trên database đất chuẩn. Cần thí nghiệm địa chất chính xác cho công trình thực tế.</i></p>
        """
        
        self.ft_txt_results.setHtml(html)
        
    def design_pile(self):
        """Design pile foundation"""
        try:
            D = float(self.pl_inp_D.text())
            L = float(self.pl_inp_L.text())
            n_piles = int(self.pl_inp_n.text())
            spacing = float(self.pl_inp_spacing.text())
            soil_type = self.pl_cbo_soil.currentText()
            
            # Create simplified soil layer
            soil_layers = [{'depth': L, 'soil_type': soil_type, 'N_SPT': 20}]
            
            # Create designer
            self.pile_designer = PileFoundationDesigner(D, L, soil_layers)
            
            # Calculate single pile
            single_result = self.pile_designer.calculate_single_pile_capacity()
            
            # Design pile group
            group_result = self.pile_designer.design_pile_group(n_piles, spacing)
            
            # Display results
            self.display_pile_results(single_result, group_result)
            
        except ValueError as e:
            QMessageBox.warning(self, "Lỗi", f"Kiểm tra số liệu nhập:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi thiết kế:\n{str(e)}")
            
    def display_pile_results(self, single, group):
        """Display pile results"""
        status_color = "green" if group['status'] == 'OK' else "orange"
        
        html = f"""
        <h2 style='color: {status_color};'>KẾT QUẢ THIẾT KẾ MÓNG CỌC</h2>
        
        <h3>1. Sức chịu tải đơn cọc:</h3>
        <ul>
            <li>Sức kháng mũi Q<sub>base</sub> = {single['Q_base']:.1f} kN</li>
            <li>Sức kháng thân Q<sub>shaft</sub> = {single['Q_shaft']:.1f} kN</li>
            <li>Sức chịu tải cực hạn Q<sub>ult</sub> = {single['Q_ult']:.1f} kN</li>
            <li><b>Sức chịu tải cho phép Q<sub>allow</sub> = {single['Q_allow']:.1f} kN</b></li>
            <li>Hệ số an toàn FS = {single['FS']:.1f}</li>
        </ul>
        
        <h3>2. Nhóm cọc:</h3>
        <ul>
            <li>Số lượng cọc: {group['n_piles']}</li>
            <li>Khoảng cách: {group['spacing']:.1f} m</li>
            <li>Hệ số hiệu quả nhóm η = {group['efficiency']:.3f}</li>
            <li><b>Sức chịu tải nhóm cọc Q<sub>group</sub> = {group['Q_group']:.1f} kN</b></li>
            <li>Tải trọng/cọc = {group['Q_per_pile']:.1f} kN</li>
            <li>{group['status']}</li>
        </ul>
        
        <p><i>⚠️ CHÚ Ý: {single['note']}</i></p>
        <p><i>💡 Để tính toán chính xác, cần cung cấp:</i></p>
        <ul>
            <li>Profile địa chất với N-SPT theo độ sâu</li>
            <li>Thông số đất chi tiết (φ, c, γ theo lớp)</li>
        </ul>
        """
        
        self.pl_txt_results.setHtml(html)
