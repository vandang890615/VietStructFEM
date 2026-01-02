# -*- coding: utf-8 -*-
"""
QS-Smart Python - Section Slab Dialog
Ô sàn (Slab section with dimensions)
Based on frmSection_Slab.cs
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QDoubleSpinBox, QPushButton,
    QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt


class SectionSlabDialog(QDialog):
    """
    Dialog for Slab Section definition
    Based on frmSection_Slab.cs
    
    Parameters:
    - txtNotes: Notes (e.g., "Trừ thang")
    - txtKichThuoc: Dimensions formula (e.g., "12.25 - 2*0.25")
    - txtThickness: Slab thickness
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_data = {}
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Ô sàn")
        self.setMinimumSize(520, 280)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Main group
        main_group = QGroupBox()
        main_layout = QFormLayout(main_group)
        
        # Notes
        self.notes_edit = QLineEdit()
        self.notes_edit.setText("Trừ thang")
        self.notes_edit.setPlaceholderText("VD: Trừ lỗ thang, giếng trời...")
        main_layout.addRow("Ghi chú:", self.notes_edit)
        
        # Dimensions formula
        self.dimensions_edit = QLineEdit()
        self.dimensions_edit.setText("12.25 - 2*0.25 - 3*0.3")
        self.dimensions_edit.setPlaceholderText("Kích thước sàn (công thức)")
        main_layout.addRow("Kích thước:", self.dimensions_edit)
        
        # Thickness
        self.thickness_spin = QDoubleSpinBox()
        self.thickness_spin.setRange(0.05, 1.0)
        self.thickness_spin.setDecimals(3)
        self.thickness_spin.setSuffix(" m")
        self.thickness_spin.setValue(0.12)
        main_layout.addRow("Chiều dày:", self.thickness_spin)
        
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
        if not self.dimensions_edit.text().strip():
            QMessageBox.warning(self, "Lỗi", "Kích thước không được để trống!")
            return False
        return True
        
    def on_accept(self):
        if not self.check_input():
            return
            
        self.result_data = {
            'notes': self.notes_edit.text().strip(),
            'dimensions': self.dimensions_edit.text().strip(),
            'thickness': self.thickness_spin.value()
        }
        self.accept()
        
    def get_data(self) -> dict:
        return self.result_data
