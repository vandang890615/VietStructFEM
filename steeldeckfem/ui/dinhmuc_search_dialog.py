# -*- coding: utf-8 -*-
"""
QS-Smart Python - DinhMuc Search Dialog
Tra cứu định mức (Work item standards search)
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.dinhmuc_loader import DinhMucLoader
from models.task import DinhMuc


class DinhMucSearchDialog(QDialog):
    """
    Dialog for searching and selecting định mức (work item standards)
    
    Features:
    - Search by code or name
    - Filter by category
    - View details
    - Select and add to element
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.loader = DinhMucLoader()
        self.selected_dinhmuc = None
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        self.setWindowTitle("Tra cứu Định mức")
        self.setMinimumSize(900, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Search section
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel("Tìm kiếm:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Nhập mã hoặc tên công việc...")
        self.search_edit.textChanged.connect(self.on_search)
        self.search_edit.setMinimumWidth(400)
        search_layout.addWidget(self.search_edit)
        
        # Category filter
        search_layout.addWidget(QLabel("Nhóm:"))
        self.category_combo = QComboBox()
        self.category_combo.addItem("Tất cả", "")
        self.category_combo.addItem("Đào đất - AA", "AA")
        self.category_combo.addItem("Bê tông - AB", "AB")
        self.category_combo.addItem("Cốt thép - AC", "AC")
        self.category_combo.addItem("Ván khuôn - AD", "AD")
        self.category_combo.addItem("Xây - AE", "AE")
        self.category_combo.addItem("Trát - AK", "AK")
        self.category_combo.addItem("Lát, ốp - AL", "AL")
        self.category_combo.currentIndexChanged.connect(self.on_search)
        search_layout.addWidget(self.category_combo)
        
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Results count
        self.count_label = QLabel("0 kết quả")
        layout.addWidget(self.count_label)
        
        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Mã công việc", "Tên công việc", "Đơn vị", "Số lần dùng"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.on_double_click)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Đóng")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        select_btn = QPushButton("Chọn định mức")
        select_btn.setDefault(True)
        select_btn.clicked.connect(self.on_select)
        btn_layout.addWidget(select_btn)
        
        layout.addLayout(btn_layout)
        
    def load_data(self):
        """Load định mức data from file"""
        from config import DEFAULT_DINHMUC_FILE
        
        # Try to load from default file
        if os.path.exists(DEFAULT_DINHMUC_FILE):
            self.loader.load(DEFAULT_DINHMUC_FILE)
        else:
            # Try alternative paths
            alt_paths = [
                os.path.join(os.path.dirname(__file__), '..', 'data', 'dinhmuc.txt'),
                os.path.join(os.path.dirname(__file__), '..', 'data dinhmuc.txt'),
                r'c:\QS-Smart\data dinhmuc.txt'
            ]
            for path in alt_paths:
                if os.path.exists(path):
                    self.loader.load(path)
                    break
        
        self.refresh_table()
        
    def refresh_table(self, items=None):
        """Refresh the table with items"""
        if items is None:
            items = self.loader.items
        
        self.table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(item.ma_cong_viec))
            self.table.setItem(row, 1, QTableWidgetItem(item.get_display_name()))
            self.table.setItem(row, 2, QTableWidgetItem(item.don_vi))
            self.table.setItem(row, 3, QTableWidgetItem(str(item.count)))
        
        self.count_label.setText(f"{len(items)} kết quả")
        
    def on_search(self):
        """Handle search input change"""
        keyword = self.search_edit.text().strip()
        category = self.category_combo.currentData()
        
        if not keyword and not category:
            self.refresh_table()
            return
        
        results = []
        for item in self.loader.items:
            # Check category filter
            if category and not item.ma_cong_viec.startswith(category):
                continue
            
            # Check keyword
            if keyword:
                keyword_lower = keyword.lower()
                if (keyword_lower not in item.ma_cong_viec.lower() and
                    keyword_lower not in item.ten_cong_viec.lower()):
                    continue
            
            results.append(item)
        
        self.refresh_table(results)
        
    def on_double_click(self, index):
        """Handle double-click on row"""
        self.on_select()
        
    def on_select(self):
        """Handle select button click"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một định mức!")
            return
        
        # Get the selected item
        ma_cv = self.table.item(row, 0).text()
        self.selected_dinhmuc = self.loader.get_by_code(ma_cv)
        
        if self.selected_dinhmuc:
            self.accept()
        
    def get_selected(self) -> DinhMuc:
        """Get the selected định mức"""
        return self.selected_dinhmuc
