# -*- coding: utf-8 -*-
"""
QS-Smart Python - Config BeTongLot Dialog
Thiết lập bê tông lót (Lean concrete configuration)
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QDoubleSpinBox, QPushButton,
    QGroupBox, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ConfigBeTongLotDialog(QDialog):
    """
    Dialog for BeTongLot configuration
    Based on frmConfig_BeTongLot.cs
    
    Settings:
    - chkIsHave: Enable/disable lean concrete
    - txtT_Value: Thickness T (m)
    - txtB_Value: Extension B (m)
    - chkBoBeTongLotMongLech: Skip lean concrete on eccentric footing
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_data = {}
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Thiết lập bê tông lót")
        self.setMinimumSize(420, 280)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Enable checkbox
        self.enable_check = QCheckBox("Tính bê tông lót")
        self.enable_check.setChecked(True)
        self.enable_check.stateChanged.connect(self.toggle_config)
        layout.addWidget(self.enable_check)
        
        # Config group
        self.config_group = QGroupBox("Thông số BT lót")
        config_layout = QFormLayout(self.config_group)
        
        self.thickness_spin = QDoubleSpinBox()
        self.thickness_spin.setRange(0, 1)
        self.thickness_spin.setDecimals(3)
        self.thickness_spin.setSuffix(" m")
        self.thickness_spin.setValue(0.1)
        config_layout.addRow("Chiều dày T:", self.thickness_spin)
        
        self.extension_spin = QDoubleSpinBox()
        self.extension_spin.setRange(0, 1)
        self.extension_spin.setDecimals(3)
        self.extension_spin.setSuffix(" m")
        self.extension_spin.setValue(0.1)
        config_layout.addRow("Phần mở rộng B:", self.extension_spin)
        
        self.skip_eccentric_check = QCheckBox("Bỏ BT lót một bên khi móng lệch")
        self.skip_eccentric_check.setChecked(True)
        config_layout.addRow(self.skip_eccentric_check)
        
        layout.addWidget(self.config_group)
        
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
        
    def toggle_config(self, state):
        self.config_group.setEnabled(state == Qt.Checked)
        
    def on_accept(self):
        self.result_data = {
            'enabled': self.enable_check.isChecked(),
            'thickness': self.thickness_spin.value(),
            'extension': self.extension_spin.value(),
            'skip_eccentric': self.skip_eccentric_check.isChecked()
        }
        self.accept()
        
    def get_config(self) -> dict:
        return self.result_data
