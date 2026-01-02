# -*- coding: utf-8 -*-
"""
QS-Smart Python - Session Dialog
Hạng mục/Phân đoạn (Session/Section management)
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QSpinBox, QPushButton,
    QGroupBox, QMessageBox, QComboBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.session import Session


class SessionDialog(QDialog):
    """
    Dialog for managing sessions/sections
    Based on frmSession.cs
    
    Features:
    - Create new session
    - Edit session name
    - Set session order
    """
    
    def __init__(self, parent=None, session: Session = None, existing_sessions: list = None):
        super().__init__(parent)
        self.session = session or Session()
        self.existing_sessions = existing_sessions or []
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        self.setWindowTitle("Hạng mục / Phân đoạn")
        self.setMinimumSize(400, 250)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Main group
        main_group = QGroupBox("Thông tin hạng mục")
        main_layout = QFormLayout(main_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("VD: Móng tầng hầm, Kết cấu tầng 1...")
        main_layout.addRow("Tên hạng mục:", self.name_edit)
        
        self.order_spin = QSpinBox()
        self.order_spin.setRange(0, 1000)
        main_layout.addRow("Thứ tự:", self.order_spin)
        
        self.parent_combo = QComboBox()
        self.parent_combo.addItem("-- Không có --", 0)
        for s in self.existing_sessions:
            if s.id != self.session.id:
                self.parent_combo.addItem(s.label, s.id)
        main_layout.addRow("Thuộc hạng mục:", self.parent_combo)
        
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
        
    def load_data(self):
        if self.session.id > 0:
            self.name_edit.setText(self.session.label)
            self.order_spin.setValue(self.session.order_id)
            
    def on_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Lỗi", "Tên hạng mục không được để trống!")
            self.name_edit.setFocus()
            return
        self.accept()
        
    def get_session(self) -> Session:
        self.session.label = self.name_edit.text().strip()
        self.session.order_id = self.order_spin.value()
        self.session.parent_id = self.parent_combo.currentData() or 0
        return self.session


class SessionSelectDialog(QDialog):
    """
    Dialog for selecting a session
    Based on frmSession_Select.cs
    """
    
    def __init__(self, parent=None, sessions: list = None):
        super().__init__(parent)
        self.sessions = sessions or []
        self.selected_session = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Chọn hạng mục")
        self.setMinimumSize(350, 400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Session list
        self.session_list = QListWidget()
        for session in self.sessions:
            item = QListWidgetItem(session.label)
            item.setData(Qt.UserRole, session)
            self.session_list.addItem(item)
        self.session_list.itemDoubleClicked.connect(self.on_double_click)
        layout.addWidget(self.session_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("Chọn")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.on_accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        
    def on_double_click(self, item):
        self.selected_session = item.data(Qt.UserRole)
        self.accept()
        
    def on_accept(self):
        current = self.session_list.currentItem()
        if current:
            self.selected_session = current.data(Qt.UserRole)
            self.accept()
        else:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một hạng mục!")
            
    def get_selected(self) -> Session:
        return self.selected_session
