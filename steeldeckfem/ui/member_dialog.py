# -*- coding: utf-8 -*-
"""
QS-Smart Python - Member Dialog
Quản lý thành viên (Member management)
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QMessageBox, QHeaderView, QComboBox
)
from PyQt5.QtCore import Qt


class MemberDialog(QDialog):
    """
    Dialog for managing project members
    Based on frmMember.cs
    
    Features:
    - List members
    - Add/remove members
    - Set permissions
    """
    
    ROLES = ["Xem", "Chỉnh sửa", "Quản trị"]
    
    def __init__(self, parent=None, members: list = None):
        super().__init__(parent)
        self.members = members or []
        self.setup_ui()
        self.load_members()
        
    def setup_ui(self):
        self.setWindowTitle("Quản lý thành viên")
        self.setMinimumSize(550, 450)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Add member form
        add_group = QGroupBox("Thêm thành viên")
        add_layout = QHBoxLayout(add_group)
        
        add_layout.addWidget(QLabel("Email:"))
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("email@example.com")
        add_layout.addWidget(self.email_edit)
        
        add_layout.addWidget(QLabel("Quyền:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(self.ROLES)
        add_layout.addWidget(self.role_combo)
        
        add_btn = QPushButton("➕ Thêm")
        add_btn.clicked.connect(self.add_member)
        add_layout.addWidget(add_btn)
        
        layout.addWidget(add_group)
        
        # Members table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Tên", "Email", "Quyền", "Xóa"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("Lưu thay đổi")
        save_btn.clicked.connect(self.save_changes)
        btn_layout.addWidget(save_btn)
        
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
    def load_members(self):
        self.table.setRowCount(len(self.members))
        for i, member in enumerate(self.members):
            self.table.setItem(i, 0, QTableWidgetItem(member.get('name', '')))
            self.table.setItem(i, 1, QTableWidgetItem(member.get('email', '')))
            
            role_combo = QComboBox()
            role_combo.addItems(self.ROLES)
            role_combo.setCurrentText(member.get('role', 'Xem'))
            self.table.setCellWidget(i, 2, role_combo)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.clicked.connect(lambda _, row=i: self.delete_member(row))
            self.table.setCellWidget(i, 3, delete_btn)
            
    def add_member(self):
        email = self.email_edit.text().strip()
        if not email:
            QMessageBox.warning(self, "Lỗi", "Email không được để trống!")
            return
        if '@' not in email:
            QMessageBox.warning(self, "Lỗi", "Email không hợp lệ!")
            return
            
        member = {
            'name': email.split('@')[0],
            'email': email,
            'role': self.role_combo.currentText()
        }
        self.members.append(member)
        self.load_members()
        self.email_edit.clear()
        
    def delete_member(self, row: int):
        if 0 <= row < len(self.members):
            del self.members[row]
            self.load_members()
            
    def save_changes(self):
        # Update roles from table
        for i in range(self.table.rowCount()):
            role_combo = self.table.cellWidget(i, 2)
            if role_combo and i < len(self.members):
                self.members[i]['role'] = role_combo.currentText()
        QMessageBox.information(self, "Thông báo", "Đã lưu thay đổi!")
        
    def get_members(self) -> list:
        return self.members
