# -*- coding: utf-8 -*-
"""
QS-Smart Python - Config DaoMong Dialog
Thiết lập đào đất móng (Excavation configuration)
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QDoubleSpinBox, QPushButton,
    QGroupBox, QMessageBox, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ConfigDaoMongDialog(QDialog):
    """
    Dialog for Excavation configuration
    Based on frmConfig_DaoMong.cs
    
    Settings:
    - Excavation slope angle
    - Working space width
    - Excavation depth
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_data = {}
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Thiết lập đào đất móng")
        self.setMinimumSize(450, 350)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Enable checkbox
        self.enable_check = QCheckBox("Tính khối lượng đào đất")
        self.enable_check.setChecked(True)
        self.enable_check.stateChanged.connect(self.toggle_config)
        layout.addWidget(self.enable_check)
        
        # Config group
        self.config_group = QGroupBox("Thông số đào đất")
        config_layout = QFormLayout(self.config_group)
        
        # Excavation type
        self.type_combo = QComboBox()
        self.type_combo.addItem("Đào thủ công", "manual")
        self.type_combo.addItem("Đào máy", "machine")
        self.type_combo.addItem("Đào hỗn hợp", "mixed")
        config_layout.addRow("Phương pháp đào:", self.type_combo)
        
        # Slope angle
        self.slope_spin = QDoubleSpinBox()
        self.slope_spin.setRange(0, 90)
        self.slope_spin.setSuffix(" °")
        self.slope_spin.setValue(0)
        config_layout.addRow("Góc mái dốc:", self.slope_spin)
        
        # Working space
        self.workspace_spin = QDoubleSpinBox()
        self.workspace_spin.setRange(0, 2)
        self.workspace_spin.setDecimals(3)
        self.workspace_spin.setSuffix(" m")
        self.workspace_spin.setValue(0.3)
        config_layout.addRow("Khoảng cách làm việc:", self.workspace_spin)
        
        # Extra depth
        self.extra_depth_spin = QDoubleSpinBox()
        self.extra_depth_spin.setRange(0, 1)
        self.extra_depth_spin.setDecimals(3)
        self.extra_depth_spin.setSuffix(" m")
        self.extra_depth_spin.setValue(0.1)
        config_layout.addRow("Đào thêm dưới đáy:", self.extra_depth_spin)
        
        # Soil type
        self.soil_combo = QComboBox()
        self.soil_combo.addItem("Đất cấp I", 1)
        self.soil_combo.addItem("Đất cấp II", 2)
        self.soil_combo.addItem("Đất cấp III", 3)
        self.soil_combo.addItem("Đất cấp IV", 4)
        config_layout.addRow("Loại đất:", self.soil_combo)
        
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
            'method': self.type_combo.currentData(),
            'slope_angle': self.slope_spin.value(),
            'workspace': self.workspace_spin.value(),
            'extra_depth': self.extra_depth_spin.value(),
            'soil_class': self.soil_combo.currentData()
        }
        self.accept()
        
    def get_config(self) -> dict:
        return self.result_data
