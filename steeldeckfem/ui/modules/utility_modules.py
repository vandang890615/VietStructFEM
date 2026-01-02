# -*- coding: utf-8 -*-
"""
Utility Modules - Combined UI for Phases 20-24
Includes: Shear Wall, Staircase, Strip Footing, Cantilever
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget)
from PyQt5.QtWidgets import QLabel, QMessageBox
from PyQt5.QtGui import QFont


class UtilityModulesWidget(QWidget):
    """Combined utility modules"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI with placeholder tabs"""
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        
        # Phase 20: Shear Wall
        wall_tab = QWidget()
        wall_layout = QVBoxLayout(wall_tab)
        label = QLabel("🧱 VÁCH CHỊU CẮT\n\nTính toán vách BTCT chịu cắt theo TCVN 5574:2018\n\n"
                      "Module đã sẵn sàng. UI chi tiết sẽ bổ sung trong phiên bản tiếp theo.")
        label.setFont(QFont("Arial", 10))
        label.setAlignment(0x84)
        wall_layout.addWidget(label)
        tabs.addTab(wall_tab, "🧱 Vách")
        
        # Phase 21: Staircase
        stair_tab = QWidget()
        stair_layout = QVBoxLayout(stair_tab)
        label = QLabel("🪜 CẦU THANG\n\nThiết kế cầu thang BTCT theo TCVN 5574:2018\n\n"
                      "Module đã sẵn sàng. UI chi tiết sẽ bổ sung trong phiên bản tiếp theo.")
        label.setFont(QFont("Arial", 10))
        label.setAlignment(0x84)
        stair_layout.addWidget(label)
        tabs.addTab(stair_tab, "🪜 Cầu thang")
        
        # Phase 23: Strip Footing
        strip_tab = QWidget()
        strip_layout = QVBoxLayout(strip_tab)
        label = QLabel("📏 MÓNG BĂNG\n\nThiết kế móng băng liên tục theo TCVN 9362:2012\n\n"
                      "Module đã sẵn sàng. UI chi tiết sẽ bổ sung trong phiên bản tiếp theo.")
        label.setFont(QFont("Arial", 10))
        label.setAlignment(0x84)
        strip_layout.addWidget(label)
        tabs.addTab(strip_tab, "📏 Móng băng")
        
        # Phase 24: Cantilever
        cant_tab = QWidget()
        cant_layout = QVBoxLayout(cant_tab)
        label = QLabel("🏗️ CÔNG XÔN / BAN CÔNG\n\nThiết kế cấu kiện công xôn theo TCVN 5574:2018\n\n"
                      "Module đã sẵn sàng. UI chi tiết sẽ bổ sung trong phiên bản tiếp theo.")
        label.setFont(QFont("Arial", 10))
        label.setAlignment(0x84)
        cant_layout.addWidget(label)
        tabs.addTab(cant_tab, "🏗️ Công xôn")
        
        layout.addWidget(tabs)
