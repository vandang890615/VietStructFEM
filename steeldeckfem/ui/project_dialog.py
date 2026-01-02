# -*- coding: utf-8 -*-
"""
QS-Smart Python - Project Dialog
Mirrors frmProject_Editor from C# source
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from models.project import ProjectInfo


class ProjectDialog(QDialog):
    """
    Dialog for creating/editing project info
    Fields: Project name, description
    """
    
    def __init__(self, parent=None, project_info: ProjectInfo = None):
        super().__init__(parent)
        self.project_info = project_info or ProjectInfo()
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        self.setWindowTitle("Thông tin dự án")
        self.setMinimumSize(500, 300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Form layout
        form = QFormLayout()
        form.setSpacing(10)
        
        # Project name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nhập tên dự án...")
        self.name_edit.setMinimumHeight(30)
        form.addRow("Tên dự án:", self.name_edit)
        
        # Description
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Mô tả dự án (không bắt buộc)...")
        self.desc_edit.setMaximumHeight(100)
        form.addRow("Mô tả:", self.desc_edit)
        
        layout.addLayout(form)
        
        # Spacer
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Hủy")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("Tạo dự án")
        ok_btn.setMinimumWidth(100)
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        
    def load_data(self):
        """Load existing project info"""
        if self.project_info:
            self.name_edit.setText(self.project_info.name)
            self.desc_edit.setPlainText(self.project_info.description)
            
    def get_project_info(self) -> ProjectInfo:
        """Get project info from dialog"""
        from datetime import datetime
        
        return ProjectInfo(
            id=self.project_info.id,
            name=self.name_edit.text().strip(),
            description=self.desc_edit.toPlainText().strip(),
            user_id=0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
