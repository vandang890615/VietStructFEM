# -*- coding: utf-8 -*-
"""
QS-Smart Python - Section RCWall Dialog
Đoạn vách BTCT (RC Wall section)
Based on frmSection_RCWall.cs
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QDoubleSpinBox, QPushButton,
    QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt


class SectionRCWallDialog(QDialog):
    """
    Dialog for RC Wall Section definition
    
    Parameters:
    - Wall thickness
    - Height
    - Length formula
    - Openings (optional)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_data = {}
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Đoạn vách BTCT")
        self.setMinimumSize(520, 320)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Main group
        main_group = QGroupBox()
        main_layout = QFormLayout(main_group)
        
        # Wall thickness
        self.thickness_spin = QDoubleSpinBox()
        self.thickness_spin.setRange(0.1, 1.0)
        self.thickness_spin.setDecimals(3)
        self.thickness_spin.setSuffix(" m")
        self.thickness_spin.setValue(0.2)
        main_layout.addRow("Chiều dày:", self.thickness_spin)
        
        # Height
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0.5, 10)
        self.height_spin.setDecimals(3)
        self.height_spin.setSuffix(" m")
        self.height_spin.setValue(3.3)
        main_layout.addRow("Chiều cao:", self.height_spin)
        
        # Length formula
        self.length_edit = QLineEdit()
        self.length_edit.setText("12.5 - 2*0.3")
        self.length_edit.setPlaceholderText("Công thức chiều dài")
        main_layout.addRow("Chiều dài:", self.length_edit)
        
        # Openings
        openings_group = QGroupBox("Lỗ mở (trừ)")
        openings_layout = QGridLayout(openings_group)
        
        openings_layout.addWidget(QLabel("Số lỗ:"), 0, 0)
        self.opening_count_spin = QDoubleSpinBox()
        self.opening_count_spin.setRange(0, 20)
        self.opening_count_spin.setDecimals(0)
        self.opening_count_spin.setValue(0)
        openings_layout.addWidget(self.opening_count_spin, 0, 1)
        
        openings_layout.addWidget(QLabel("Kích thước (BxH):"), 1, 0)
        self.opening_size_edit = QLineEdit()
        self.opening_size_edit.setPlaceholderText("VD: 1.2*2.0")
        openings_layout.addWidget(self.opening_size_edit, 1, 1)
        
        main_layout.addRow(openings_group)
        
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
        
    def on_accept(self):
        if not self.length_edit.text().strip():
            QMessageBox.warning(self, "Lỗi", "Chiều dài không được để trống!")
            return
            
        self.result_data = {
            'thickness': self.thickness_spin.value(),
            'height': self.height_spin.value(),
            'length_formula': self.length_edit.text().strip(),
            'opening_count': int(self.opening_count_spin.value()),
            'opening_size': self.opening_size_edit.text().strip()
        }
        self.accept()
        
    def get_data(self) -> dict:
        return self.result_data
