# -*- coding: utf-8 -*-
"""
QS-Smart Python - Section MongBang Dialog
Đoạn móng băng (Strip footing section)
Based on frmSection_MongBang.cs
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QDoubleSpinBox, QPushButton,
    QGroupBox, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt


class SectionMongBangDialog(QDialog):
    """
    Dialog for Strip Footing Section definition
    
    Parameters similar to frmSection_Beam but for strip footings
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_data = {}
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Đoạn móng băng")
        self.setMinimumSize(520, 350)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Main group
        main_group = QGroupBox()
        main_layout = QGridLayout(main_group)
        
        # Section type
        main_layout.addWidget(QLabel("Loại tiết diện:"), 0, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItem("Tiết diện chữ T", "T")
        self.type_combo.addItem("Tiết diện chữ nhật", "RECT")
        self.type_combo.addItem("Tiết diện bậc thang", "STEP")
        self.type_combo.currentIndexChanged.connect(self.update_fields)
        main_layout.addWidget(self.type_combo, 0, 1)
        
        # Width B
        main_layout.addWidget(QLabel("Bề rộng B (m):"), 1, 0)
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(0.1, 10)
        self.width_spin.setDecimals(3)
        self.width_spin.setValue(1.0)
        main_layout.addWidget(self.width_spin, 1, 1)
        
        # Height H
        main_layout.addWidget(QLabel("Chiều cao H (m):"), 2, 0)
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0.1, 5)
        self.height_spin.setDecimals(3)
        self.height_spin.setValue(0.5)
        main_layout.addWidget(self.height_spin, 2, 1)
        
        # Sub-width B1 (for T-section)
        main_layout.addWidget(QLabel("Bề rộng B1 (m):"), 3, 0)
        self.width1_spin = QDoubleSpinBox()
        self.width1_spin.setRange(0, 5)
        self.width1_spin.setDecimals(3)
        self.width1_spin.setValue(0.4)
        main_layout.addWidget(self.width1_spin, 3, 1)
        
        # Sub-height H1 (for T-section)
        main_layout.addWidget(QLabel("Chiều cao H1 (m):"), 4, 0)
        self.height1_spin = QDoubleSpinBox()
        self.height1_spin.setRange(0, 3)
        self.height1_spin.setDecimals(3)
        self.height1_spin.setValue(0.3)
        main_layout.addWidget(self.height1_spin, 4, 1)
        
        # Length formula
        main_layout.addWidget(QLabel("Chiều dài:"), 5, 0)
        self.length_edit = QLineEdit()
        self.length_edit.setText("10.5 - 2*0.5")
        self.length_edit.setPlaceholderText("Công thức chiều dài")
        main_layout.addWidget(self.length_edit, 5, 1)
        
        layout.addWidget(main_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Hủy bỏ")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("Hoàn thành")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.on_accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        
    def update_fields(self, index):
        """Enable/disable fields based on section type"""
        section_type = self.type_combo.currentData()
        is_t_section = section_type == "T"
        self.width1_spin.setEnabled(is_t_section or section_type == "STEP")
        self.height1_spin.setEnabled(is_t_section or section_type == "STEP")
        
    def on_accept(self):
        if not self.length_edit.text().strip():
            QMessageBox.warning(self, "Lỗi", "Chiều dài không được để trống!")
            return
            
        self.result_data = {
            'section_type': self.type_combo.currentData(),
            'width': self.width_spin.value(),
            'height': self.height_spin.value(),
            'width1': self.width1_spin.value(),
            'height1': self.height1_spin.value(),
            'length_formula': self.length_edit.text().strip()
        }
        self.accept()
        
    def get_data(self) -> dict:
        return self.result_data
