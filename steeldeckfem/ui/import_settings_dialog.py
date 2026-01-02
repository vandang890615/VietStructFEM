# -*- coding: utf-8 -*-
"""
QS-Smart Python - Import Settings Dialog
Nhập cấu hình từ file
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog,
    QGroupBox, QMessageBox, QCheckBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import json
import os


class ImportSettingsDialog(QDialog):
    """
    Dialog for importing settings from file
    Based on frmImport_Setting.cs
    
    Features:
    - Import DinhMuc configuration
    - Import Element types
    - Import calculation formulas
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = ""
        self.import_options = {}
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Thiết lập")
        self.setMinimumSize(500, 350)
        
        main_layout = QVBoxLayout(self)
        
        # General Settings Group (GroupBox1 in C#)
        gen_group = QGroupBox("Thiết lập chung")
        gen_layout = QGridLayout(gen_group)
        
        gen_layout.addWidget(QLabel("Bê tông:"), 0, 0)
        self.betong_combo = QComboBox()
        self.betong_combo.addItems(["C20", "C25", "C30", "C35"])
        gen_layout.addWidget(self.betong_combo, 0, 1)
        
        gen_layout.addWidget(QLabel("Ván khuôn:"), 1, 0)
        self.van_khuon_combo = QComboBox()
        self.van_khuon_combo.addItems(["Ván phủ phim", "Ván ép thường", "Thép"])
        gen_layout.addWidget(self.van_khuon_combo, 1, 1)
        
        self.chk_rebar_all = QCheckBox("Khối lượng Cốt thép đã nhân với số lượng cấu kiện")
        self.chk_rebar_all.setChecked(True)
        gen_layout.addWidget(self.chk_rebar_all, 2, 0, 1, 2)
        
        main_layout.addWidget(gen_group)
        
        # Beam Settings Group (GroupBox2 in C#)
        beam_group = QGroupBox("Dành cho phần dầm")
        beam_layout = QVBoxLayout(beam_group)
        
        self.chk_bottom_formwork = QCheckBox("Tính ván khuôn đáy dầm")
        self.chk_bottom_formwork.setChecked(True)
        beam_layout.addWidget(self.chk_bottom_formwork)
        
        self.chk_slab_less = QCheckBox("Trừ bê tông sàn")
        self.chk_slab_less.setChecked(True)
        beam_layout.addWidget(self.chk_slab_less)
        
        main_layout.addWidget(beam_group)
        
        # Buttons
        btns = QHBoxLayout()
        btns.addStretch()
        ok_btn = QPushButton("Hoàn thành")
        ok_btn.clicked.connect(self.on_accept)
        cancel_btn = QPushButton("Hủy bỏ")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        main_layout.addLayout(btns)

    def on_accept(self):
        # Save settings to global state (Class25 equivalents)
        self.accept()
        
    def get_options(self) -> dict:
        return self.import_options
