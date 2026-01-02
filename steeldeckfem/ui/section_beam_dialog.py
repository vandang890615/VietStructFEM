# -*- coding: utf-8 -*-
"""
QS-Smart Python - Section_Beam Form Dialog
Đoạn dầm (Beam section with dimensions)
Based on frmSection_Beam.cs
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QDoubleSpinBox, QPushButton,
    QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class SectionBeamDialog(QDialog):
    """
    Dialog for Beam Section definition
    Based on frmSection_Beam.cs
    
    Parameters:
    - txtSection: Section dimensions (e.g., "0.22*0.5")
    - txtHF1, txtHF2: Height factors
    - txtCF1, txtCF2: Column factors
    - txtL: Length formula
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_data = {}
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Đoạn dầm")
        self.setMinimumSize(520, 320)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Main group
        main_group = QGroupBox()
        main_layout = QGridLayout(main_group)
        
        # Section
        main_layout.addWidget(QLabel("Tiết diện:"), 0, 0)
        self.section_edit = QLineEdit()
        self.section_edit.setText("0.22*0.5")
        self.section_edit.setPlaceholderText("b*h (VD: 0.22*0.5)")
        main_layout.addWidget(self.section_edit, 0, 1)
        
        # HF1, HF2 (Height factors)
        main_layout.addWidget(QLabel("HF1:"), 1, 0)
        self.hf1_spin = QDoubleSpinBox()
        self.hf1_spin.setRange(0, 10)
        self.hf1_spin.setDecimals(3)
        self.hf1_spin.setValue(0.12)
        main_layout.addWidget(self.hf1_spin, 1, 1)
        
        main_layout.addWidget(QLabel("HF2:"), 2, 0)
        self.hf2_spin = QDoubleSpinBox()
        self.hf2_spin.setRange(0, 10)
        self.hf2_spin.setDecimals(3)
        self.hf2_spin.setValue(0.12)
        main_layout.addWidget(self.hf2_spin, 2, 1)
        
        # CF1, CF2 (Column factors)
        main_layout.addWidget(QLabel("CF1:"), 1, 2)
        self.cf1_spin = QDoubleSpinBox()
        self.cf1_spin.setRange(0, 10)
        self.cf1_spin.setDecimals(3)
        self.cf1_spin.setValue(0)
        main_layout.addWidget(self.cf1_spin, 1, 3)
        
        main_layout.addWidget(QLabel("CF2:"), 2, 2)
        self.cf2_spin = QDoubleSpinBox()
        self.cf2_spin.setRange(0, 10)
        self.cf2_spin.setDecimals(3)
        self.cf2_spin.setValue(0)
        main_layout.addWidget(self.cf2_spin, 2, 3)
        
        # Length
        main_layout.addWidget(QLabel("Chiều dài:"), 3, 0)
        self.length_edit = QLineEdit()
        self.length_edit.setText("12.25 - 2*0.25 - 3*0.3")
        self.length_edit.setPlaceholderText("VD: 12.25 - 2*0.25")
        main_layout.addWidget(self.length_edit, 3, 1, 1, 3)
        
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
        
    def check_input(self) -> bool:
        try:
            # Validate section format
            section = self.section_edit.text().strip()
            if '*' not in section:
                raise ValueError("Invalid section format")
            parts = section.split('*')
            float(parts[0])
            float(parts[1])
        except:
            QMessageBox.warning(self, "Lỗi", "Tiết diện không hợp lệ! Định dạng: b*h")
            return False
        
        if not self.length_edit.text().strip():
            QMessageBox.warning(self, "Lỗi", "Chiều dài không được để trống!")
            return False
        
        return True
        
    def on_accept(self):
        if not self.check_input():
            return
            
        section = self.section_edit.text().strip()
        parts = section.split('*')
        
        self.result_data = {
            'section': section,
            'width': float(parts[0]),
            'height': float(parts[1]),
            'hf1': self.hf1_spin.value(),
            'hf2': self.hf2_spin.value(),
            'cf1': self.cf1_spin.value(),
            'cf2': self.cf2_spin.value(),
            'length_formula': self.length_edit.text().strip()
        }
        self.accept()
        
    def get_data(self) -> dict:
        return self.result_data
