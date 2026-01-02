# -*- coding: utf-8 -*-
"""
QS-Smart Python - Quick Start Dialog
Mirrors frmQuickStart from C# source
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from config import APP_NAME


class QuickStartDialog(QDialog):
    """
    Quick start dialog shown on app launch
    Options: New project, Open project, Recent projects
    """
    
    RESULT_NEW = 1
    RESULT_OPEN = 2
    RESULT_RECENT = 3
    RESULT_EXIT = 99
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_action = 0
        self.selected_project_path = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle(f"Chào mừng - {APP_NAME}")
        self.setFixedSize(600, 400)
        self.setWindowModality(Qt.ApplicationModal)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel(f"🏗️ {APP_NAME}")
        header.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        subtitle = QLabel("Phần mềm bóc khối lượng xây dựng")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)
        
        # Buttons frame
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setSpacing(20)
        
        # New project button
        new_btn = QPushButton("📄 Dự án mới")
        new_btn.setMinimumSize(150, 60)
        new_btn.setFont(QFont("Segoe UI", 11))
        new_btn.clicked.connect(self.new_project)
        btn_layout.addWidget(new_btn)
        
        # Open project button
        open_btn = QPushButton("📂 Mở dự án")
        open_btn.setMinimumSize(150, 60)
        open_btn.setFont(QFont("Segoe UI", 11))
        open_btn.clicked.connect(self.open_project)
        btn_layout.addWidget(open_btn)
        
        layout.addWidget(btn_frame)
        
        # Recent projects label
        recent_label = QLabel("Dự án gần đây:")
        recent_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout.addWidget(recent_label)
        
        # Recent projects table
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(2)
        self.recent_table.setHorizontalHeaderLabels(["Tên dự án", "Đường dẫn"])
        self.recent_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.recent_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.recent_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recent_table.doubleClicked.connect(self.open_recent)
        layout.addWidget(self.recent_table)
        
        # Load recent projects
        self.load_recent_projects()
        
    def load_recent_projects(self):
        """Load list of recent projects"""
        # TODO: Implement recent projects tracking
        self.recent_table.setRowCount(0)
        
    def new_project(self):
        self.result_action = self.RESULT_NEW
        self.accept()
        
    def open_project(self):
        self.result_action = self.RESULT_OPEN
        self.accept()
        
    def open_recent(self, index):
        # Get selected project path
        row = index.row()
        if row >= 0:
            self.selected_project_path = self.recent_table.item(row, 1).text()
            self.result_action = self.RESULT_RECENT
            self.accept()
