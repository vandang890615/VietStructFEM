# -*- coding: utf-8 -*-
"""
QS-Smart Python - Task OpChanTuong Dialog
Ốp gạch chân tường (Wall base tile task)
Based on frmAdd_Task_OpChanTuong.cs
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton,
    QGroupBox, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt


class TaskOpChanTuongDialog(QDialog):
    """
    Dialog for adding wall base tile task
    Based on frmAdd_Task_OpChanTuong.cs
    
    Parameters:
    - txtL: Length formula
    - cboLoaiGachOp: Tile type selection
    """
    
    # Common tile types for wall base
    TILE_TYPES = [
        "Gạch ốp ceramic 200x300",
        "Gạch ốp ceramic 250x400", 
        "Gạch ốp ceramic 300x450",
        "Gạch ốp granite 300x600",
        "Gạch ốp granite 400x800",
        "Gạch men 200x250",
        "Gạch men 250x400",
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_data = {}
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Thêm công tác Ốp gạch chân tường")
        self.setMinimumSize(560, 220)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Main group
        main_group = QGroupBox()
        main_layout = QFormLayout(main_group)
        
        # Length formula with link-like label
        length_layout = QHBoxLayout()
        self.length_edit = QLineEdit()
        self.length_edit.setText("12 - 2*0.22")
        self.length_edit.setPlaceholderText("Công thức chiều dài (VD: 12 - 2*0.22)")
        length_layout.addWidget(self.length_edit)
        
        length_link = QPushButton("📏")
        length_link.setFixedWidth(30)
        length_link.setToolTip("Lấy chiều dài từ element")
        length_link.clicked.connect(self.get_length_from_element)
        length_layout.addWidget(length_link)
        
        main_layout.addRow("Chiều dài:", length_layout)
        
        # Tile type
        self.tile_combo = QComboBox()
        self.tile_combo.addItems(self.TILE_TYPES)
        main_layout.addRow("Loại gạch:", self.tile_combo)
        
        # Height (optional)
        self.height_edit = QLineEdit()
        self.height_edit.setText("0.1")
        self.height_edit.setPlaceholderText("Chiều cao ốp (m)")
        main_layout.addRow("Chiều cao:", self.height_edit)
        
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
        
    def get_length_from_element(self):
        # Placeholder - in real app would get from parent element
        QMessageBox.information(self, "Thông báo", "Tính năng lấy chiều dài từ element")
        
    def check_input(self) -> bool:
        length_text = self.length_edit.text().strip()
        if not length_text:
            QMessageBox.warning(self, "Lỗi", "Chiều dài không được để trống!")
            return False
        
        try:
            # Try to evaluate the formula
            result = eval(length_text.replace('x', '*').replace('×', '*'))
            if result <= 0:
                QMessageBox.warning(self, "Lỗi", "Kiểm tra lại công thức nhập!")
                return False
        except:
            QMessageBox.warning(self, "Lỗi", "Công thức không hợp lệ!")
            return False
            
        return True
        
    def on_accept(self):
        if not self.check_input():
            return
            
        self.result_data = {
            'length_formula': self.length_edit.text().strip(),
            'tile_type': self.tile_combo.currentText(),
            'tile_index': self.tile_combo.currentIndex(),
            'height': float(self.height_edit.text() or 0.1)
        }
        self.accept()
        
    def get_data(self) -> dict:
        return self.result_data
