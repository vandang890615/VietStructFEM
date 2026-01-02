# -*- coding: utf-8 -*-
"""
QS-Smart Python - Sync Dialog
Đồng bộ dữ liệu (Data synchronization)
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QProgressBar,
    QGroupBox, QMessageBox, QCheckBox, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer


class SyncDialog(QDialog):
    """
    Dialog for data synchronization
    Based on frmSync.cs
    
    Features:
    - Sync to cloud
    - Sync from cloud
    - Sync status log
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Đồng bộ dữ liệu")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Status group
        status_group = QGroupBox("Trạng thái")
        status_layout = QFormLayout(status_group)
        
        self.server_label = QLabel("Offline")
        self.server_label.setStyleSheet("color: #888;")
        status_layout.addRow("Máy chủ:", self.server_label)
        
        self.last_sync_label = QLabel("Chưa đồng bộ")
        status_layout.addRow("Đồng bộ cuối:", self.last_sync_label)
        
        layout.addWidget(status_group)
        
        # Options
        options_group = QGroupBox("Tùy chọn đồng bộ")
        options_layout = QVBoxLayout(options_group)
        
        self.sync_sessions = QCheckBox("Đồng bộ hạng mục")
        self.sync_sessions.setChecked(True)
        options_layout.addWidget(self.sync_sessions)
        
        self.sync_elements = QCheckBox("Đồng bộ cấu kiện")
        self.sync_elements.setChecked(True)
        options_layout.addWidget(self.sync_elements)
        
        self.sync_tasks = QCheckBox("Đồng bộ công tác")
        self.sync_tasks.setChecked(True)
        options_layout.addWidget(self.sync_tasks)
        
        layout.addWidget(options_group)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        # Log
        log_group = QGroupBox("Nhật ký")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.sync_up_btn = QPushButton("⬆️ Đẩy lên")
        self.sync_up_btn.clicked.connect(self.sync_upload)
        btn_layout.addWidget(self.sync_up_btn)
        
        self.sync_down_btn = QPushButton("⬇️ Tải về")
        self.sync_down_btn.clicked.connect(self.sync_download)
        btn_layout.addWidget(self.sync_down_btn)
        
        btn_layout.addStretch()
        
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
    def log(self, message: str):
        self.log_text.append(message)
        
    def sync_upload(self):
        self.log("▶ Bắt đầu đẩy dữ liệu lên...")
        self.progress.setValue(0)
        
        # Simulate sync (offline mode)
        QTimer.singleShot(500, lambda: self.progress.setValue(30))
        QTimer.singleShot(1000, lambda: self.progress.setValue(60))
        QTimer.singleShot(1500, lambda: self.progress.setValue(100))
        QTimer.singleShot(1500, lambda: self.log("✓ Hoàn thành (chế độ offline)"))
        
    def sync_download(self):
        self.log("▶ Bắt đầu tải dữ liệu về...")
        self.progress.setValue(0)
        
        # Simulate sync (offline mode)
        QTimer.singleShot(500, lambda: self.progress.setValue(30))
        QTimer.singleShot(1000, lambda: self.progress.setValue(60))
        QTimer.singleShot(1500, lambda: self.progress.setValue(100))
        QTimer.singleShot(1500, lambda: self.log("✓ Hoàn thành (chế độ offline)"))
