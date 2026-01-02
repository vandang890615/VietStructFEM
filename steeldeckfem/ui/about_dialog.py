# -*- coding: utf-8 -*-
"""
QS-Smart Python - About Dialog
Giới thiệu ứng dụng
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap


class AboutDialog(QDialog):
    """
    About dialog showing application info
    Based on frmAbout.cs
    """
    
    VERSION = "1.0.0"
    APP_NAME = "QS-Smart Python"
    AUTHOR = "KetcauSoft Team"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Giới thiệu")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # App name
        name_label = QLabel(self.APP_NAME)
        name_label.setFont(QFont("Microsoft Sans Serif", 18, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # Version
        version_label = QLabel(f"Phiên bản: {self.VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)
        
        # Description
        desc_label = QLabel(
            "Phần mềm bóc tách khối lượng xây dựng\n"
            "Dựa trên QS-Smart của KetcauSoft\n"
            "Phiên bản Python - Mã nguồn mở"
        )
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # Author
        author_label = QLabel(f"Tác giả: {self.AUTHOR}")
        author_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(author_label)
        
        layout.addStretch()
        
        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton("Đóng")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
