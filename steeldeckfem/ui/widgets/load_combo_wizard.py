# -*- coding: utf-8 -*-
"""
Load Combination Wizard - UI Widget
Provides user interface for TCVN 2737:2023 load combinations
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QFormLayout, QLineEdit, QRadioButton, QButtonGroup,
                             QTableWidget, QTableWidgetItem, QPushButton, QLabel,
                             QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from steeldeckfem.core.load_combination_engine import (
    LoadType, LimitState, LoadCombinationEngine
)


class LoadCombinationWizard(QWidget):
    """
    Reusable widget for load combination calculation
    Emits governingCaseSelected signal when user picks a combination
    """
    
    # Signal emitted when user selects a governing case
    governingCaseSelected = pyqtSignal(float, str)  # (value, formula)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_results = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the wizard UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🔢 TỔ HỢP TẢI TRỌNG (TCVN 2737:2023)")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #34495e; color: white; padding: 10px; border-radius: 5px;")
        layout.addWidget(title)
        
        # Input Group
        gb_input = QGroupBox("Nhập Tải Trọng (Loads)")
        form = QFormLayout()
        
        self.inp_dead = QLineEdit("0.0")
        self.inp_dead.setPlaceholderText("kN or kN/m²")
        self.inp_live = QLineEdit("0.0")
        self.inp_live.setPlaceholderText("kN or kN/m²")
        self.inp_wind = QLineEdit("0.0")
        self.inp_wind.setPlaceholderText("kN or kN/m²")
        self.inp_seismic = QLineEdit("0.0")
        self.inp_seismic.setPlaceholderText("kN or kN/m²")
        self.inp_crane = QLineEdit("0.0")
        self.inp_crane.setPlaceholderText("kN")
        
        form.addRow("Tĩnh tải (D - Dead):", self.inp_dead)
        form.addRow("Hoạt tải (L - Live):", self.inp_live)
        form.addRow("Gió (W - Wind):", self.inp_wind)
        form.addRow("Động đất (E - Seismic):", self.inp_seismic)
        form.addRow("Cầu trục (C - Crane):", self.inp_crane)
        
        gb_input.setLayout(form)
        layout.addWidget(gb_input)
        
        # Limit State Selection
        gb_ls = QGroupBox("Trạng Thái Giới Hạn (Limit State)")
        hbox_ls = QHBoxLayout()
        
        self.btn_uls = QRadioButton("ULS (Cường độ)")
        self.btn_sls = QRadioButton("SLS (Sử dụng)")
        self.btn_uls.setChecked(True)
        
        self.ls_group = QButtonGroup()
        self.ls_group.addButton(self.btn_uls)
        self.ls_group.addButton(self.btn_sls)
        
        hbox_ls.addWidget(self.btn_uls)
        hbox_ls.addWidget(self.btn_sls)
        hbox_ls.addStretch()
        
        gb_ls.setLayout(hbox_ls)
        layout.addWidget(gb_ls)
        
        # Calculate Button
        btn_calc = QPushButton("⚡ TÍNH TỔ HỢP")
        btn_calc.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                font-size: 14px; font-weight: bold; padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        btn_calc.clicked.connect(self.calculate_combinations)
        layout.addWidget(btn_calc)
        
        # Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Tổ Hợp", "Công Thức", "Giá Trị"])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # Governing Case Display
        self.lbl_governing = QLabel("<i>Chưa có kết quả. Nhấn 'Tính tổ hợp' để bắt đầu.</i>")
        self.lbl_governing.setAlignment(Qt.AlignCenter)
        self.lbl_governing.setStyleSheet("padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        layout.addWidget(self.lbl_governing)
        
        # Action Buttons
        hbox_actions = QHBoxLayout()
        
        btn_use = QPushButton("✓ Sử dụng Giá Trị Nguy Hiểm")
        btn_use.setStyleSheet("background-color: #2980b9; color: white; padding: 8px; font-weight: bold;")
        btn_use.clicked.connect(self.use_governing_case)
        
        btn_copy = QPushButton("📋 Copy Bảng")
        btn_copy.clicked.connect(self.copy_to_clipboard)
        
        hbox_actions.addWidget(btn_use)
        hbox_actions.addWidget(btn_copy)
        
        layout.addLayout(hbox_actions)
        
    def get_loads(self):
        """Get current load values from inputs"""
        try:
            return {
                LoadType.DEAD: float(self.inp_dead.text() or 0),
                LoadType.LIVE: float(self.inp_live.text() or 0),
                LoadType.WIND: float(self.inp_wind.text() or 0),
                LoadType.SEISMIC: float(self.inp_seismic.text() or 0),
                LoadType.CRANE: float(self.inp_crane.text() or 0)
            }
        except ValueError:
            return None
    
    def calculate_combinations(self):
        """Calculate and display all load combinations"""
        loads = self.get_loads()
        if loads is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập số hợp lệ cho tất cả các tải trọng.")
            return
        
        # Get limit state
        limit_state = LimitState.ULS if self.btn_uls.isChecked() else LimitState.SLS
        
        # Calculate all combinations
        self.current_results = LoadCombinationEngine.calculate_all(loads, limit_state)
        
        # Find governing case
        gov_combo, gov_value = LoadCombinationEngine.get_governing_case(loads, limit_state)
        
        # Populate table
        self.table.setRowCount(len(self.current_results))
        
        for i, (combo, value) in enumerate(self.current_results):
            # Name
            item_name = QTableWidgetItem(combo.name.split(":")[0])
            item_name.setTextAlignment(Qt.AlignCenter)
            
            # Formula
            item_formula = QTableWidgetItem(combo.get_formula())
            
            # Value
            item_value = QTableWidgetItem(f"{value:.2f}")
            item_value.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Highlight governing case
            if combo.name == gov_combo.name:
                for item in [item_name, item_formula, item_value]:
                    item.setBackground(QColor("#27ae60"))
                    item.setForeground(QColor("white"))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
            
            self.table.setItem(i, 0, item_name)
            self.table.setItem(i, 1, item_formula)
            self.table.setItem(i, 2, item_value)
        
        # Update governing label
        self.lbl_governing.setText(f"""
            <b style='color: #27ae60; font-size: 14px;'>
                ⚠️ TỔ HỢP NGUY HIỂM NHẤT: {gov_combo.name}
            </b><br>
            <span style='font-size: 12px;'>
                Công thức: {gov_combo.get_formula()} = <b>{gov_value:.2f}</b>
            </span>
        """)
        
    def use_governing_case(self):
        """Emit signal with governing case value"""
        if not self.current_results:
            QMessageBox.information(self, "Thông báo", "Vui lòng tính toán trước.")
            return
        
        loads = self.get_loads()
        limit_state = LimitState.ULS if self.btn_uls.isChecked() else LimitState.SLS
        gov_combo, gov_value = LoadCombinationEngine.get_governing_case(loads, limit_state)
        
        self.governingCaseSelected.emit(gov_value, gov_combo.get_formula())
        QMessageBox.information(self, "Thành công", 
                              f"Đã chọn giá trị nguy hiểm: {gov_value:.2f}\n"
                              f"Công thức: {gov_combo.get_formula()}")
    
    def copy_to_clipboard(self):
        """Copy table contents to clipboard"""
        if self.table.rowCount() == 0:
            return
        
        text = "Tổ Hợp\tCông Thức\tGiá Trị\n"
        for i in range(self.table.rowCount()):
            row = []
            for j in range(3):
                item = self.table.item(i, j)
                row.append(item.text() if item else "")
            text += "\t".join(row) + "\n"
        
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        QMessageBox.information(self, "Đã Copy", "Bảng tổ hợp đã được copy vào clipboard.")
    
    def set_loads(self, dead=0, live=0, wind=0, seismic=0, crane=0):
        """Programmatically set load values"""
        self.inp_dead.setText(str(dead))
        self.inp_live.setText(str(live))
        self.inp_wind.setText(str(wind))
        self.inp_seismic.setText(str(seismic))
        self.inp_crane.setText(str(crane))
