# -*- coding: utf-8 -*-
"""
QS-Smart Python - Add Task Dialog
Thêm công tác (Add work task)
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QDoubleSpinBox, QPushButton,
    QGroupBox, QMessageBox, QComboBox, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.task import Task


class AddTaskDialog(QDialog):
    """
    Dialog for adding work tasks
    Based on frmAdd_Task.cs
    
    Fields:
    - txtMa_Cong_Viec: Work code (MSCV)
    - txtTen_Cong_Viec: Work name
    - txtKhoi_Luong: Quantity formula
    - cboDonVi: Unit (m3, m2, m, etc.)
    - txtGhiChu: Notes
    """
    
    UNITS = ["m3", "m2", "m", "100m3", "100m2", "100m", "tấn", "kg", "cái", "bộ"]
    
    def __init__(self, parent=None, task: Task = None, element_id: int = 0):
        super().__init__(parent)
        self.task = task or Task()
        self.element_id = element_id
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        self.setWindowTitle("Công tác")
        self.setMinimumSize(700, 400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Main group
        main_group = QGroupBox()
        main_layout = QGridLayout(main_group)
        
        # Work code
        main_layout.addWidget(QLabel("MSCV:"), 0, 0)
        self.code_edit = QLineEdit()
        self.code_edit.setFont(QFont("Microsoft Sans Serif", 12))
        self.code_edit.setPlaceholderText("VD: AB.11111, AC.12345...")
        main_layout.addWidget(self.code_edit, 0, 1)
        
        # Work name
        main_layout.addWidget(QLabel("Tên công việc:"), 1, 0, Qt.AlignTop)
        self.name_edit = QTextEdit()
        self.name_edit.setMaximumHeight(80)
        self.name_edit.setPlaceholderText("Nhập tên công việc theo định mức...")
        main_layout.addWidget(self.name_edit, 1, 1, 1, 3)
        
        # Notes
        main_layout.addWidget(QLabel("Ghi chú:"), 2, 0)
        self.notes_edit = QLineEdit()
        main_layout.addWidget(self.notes_edit, 2, 1, 1, 3)
        
        # Quantity formula
        main_layout.addWidget(QLabel("Khối lượng:"), 3, 0)
        self.quantity_edit = QLineEdit()
        self.quantity_edit.setPlaceholderText("VD: 12.25 - 2*0.25 - 3*0.3")
        main_layout.addWidget(self.quantity_edit, 3, 1, 1, 2)
        
        # Unit
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(self.UNITS)
        main_layout.addWidget(self.unit_combo, 3, 3)
        
        # Quick links
        link_layout = QHBoxLayout()
        
        length_link = QPushButton("📏 Nhập chiều dài")
        length_link.setFlat(True)
        length_link.clicked.connect(self.insert_length)
        link_layout.addWidget(length_link)
        
        area_link = QPushButton("📐 Nhập diện tích")
        area_link.setFlat(True)
        area_link.clicked.connect(self.insert_area)
        link_layout.addWidget(area_link)
        
        bracket_link = QPushButton("( ) Thêm ngoặc")
        bracket_link.setFlat(True)
        bracket_link.clicked.connect(self.insert_brackets)
        link_layout.addWidget(bracket_link)
        
        link_layout.addStretch()
        main_layout.addLayout(link_layout, 4, 1, 1, 3)
        
        layout.addWidget(main_group)
        
        # Save change option
        self.save_check = QCheckBox("Cập nhật tên công việc cho mã công việc")
        layout.addWidget(self.save_check)
        
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
        if self.task.id > 0:
            self.code_edit.setText(self.task.ma_cong_viec)
            self.name_edit.setPlainText(self.task.ten_cong_viec)
            self.quantity_edit.setText(self.task.cong_thuc)
            self.notes_edit.setText(self.task.ghi_chu)
            if self.task.don_vi in self.UNITS:
                self.unit_combo.setCurrentText(self.task.don_vi)
                
    def insert_length(self):
        current = self.quantity_edit.text()
        self.quantity_edit.setText(current + " + L")
        
    def insert_area(self):
        current = self.quantity_edit.text()
        self.quantity_edit.setText(current + " + A")
        
    def insert_brackets(self):
        cursor_pos = self.quantity_edit.cursorPosition()
        current = self.quantity_edit.text()
        self.quantity_edit.setText(current[:cursor_pos] + "()" + current[cursor_pos:])
        self.quantity_edit.setCursorPosition(cursor_pos + 1)
        
    def check_input(self) -> bool:
        if not self.code_edit.text().strip():
            QMessageBox.warning(self, "Lỗi", "Mã công việc không được để trống!")
            self.code_edit.setFocus()
            return False
        if not self.name_edit.toPlainText().strip():
            QMessageBox.warning(self, "Lỗi", "Tên công việc không được để trống!")
            self.name_edit.setFocus()
            return False
        if not self.quantity_edit.text().strip():
            QMessageBox.warning(self, "Lỗi", "Khối lượng không được để trống!")
            self.quantity_edit.setFocus()
            return False
        return True
        
    def on_accept(self):
        if not self.check_input():
            return
        self.accept()
        
    def get_task(self) -> Task:
        self.task.ma_cong_viec = self.code_edit.text().strip()
        self.task.ten_cong_viec = self.name_edit.toPlainText().strip()
        self.task.cong_thuc = self.quantity_edit.text().strip()
        self.task.don_vi = self.unit_combo.currentText()
        self.task.ghi_chu = self.notes_edit.text().strip()
        self.task.element_id = self.element_id
        
        # Calculate quantity from formula
        try:
            self.task.khoi_luong = eval(self.task.cong_thuc.replace('x', '*').replace('×', '*'))
        except:
            self.task.khoi_luong = 0
            
        return self.task
