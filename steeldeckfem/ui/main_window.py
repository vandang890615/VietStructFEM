# -*- coding: utf-8 -*-
"""
VietStructFEM - Structural Engineering Platform
Main Window Shell
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QLabel, QApplication, QHBoxLayout, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

# Module Imports
from steeldeckfem.ui.modules.steel_deck_module import SteelDeckModule
from steeldeckfem.ui.modules.rc_column_module import RCColumnModule
from steeldeckfem.ui.modules.frame_analysis_module import FrameAnalysisModule
from steeldeckfem.ui.modules.opensees_module import OpenSeesModule
from steeldeckfem.ui.modules.warehouse_module import WarehouseModule
from steeldeckfem.ui.widgets.load_combo_wizard import LoadCombinationWizard
from steeldeckfem.ui.modules.rc_beam_module import RCBeamModule
from steeldeckfem.ui.modules.foundation_module import FoundationModule
from steeldeckfem.ui.modules.steel_module import SteelMemberModule
from steeldeckfem.ui.modules.connection_module import ConnectionModule
from steeldeckfem.ui.modules.deflection_module import DeflectionModule
from steeldeckfem.ui.modules.utility_modules import UtilityModulesWidget


class MainWindow(QMainWindow):
    """
    Main Application Window
    Hosting multiple structural engineering modules
    """
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("VietStructFEM - NỀN TẢNG KỸ THUẬT KẾT CẤU VIỆT NAM")
        self.resize(1800, 1000)
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main Layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Header
        self.create_header()
        
        # 2. Module Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #C2C7CB; top: -1px; }
            QTabBar::tab {
                background: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: bold;
                color: #2c3e50;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
                color: #2980b9;
            }
        """)
        self.main_layout.addWidget(self.tabs)
        
        # 3. Add Modules
        self.init_modules()
        
        # 4. Footer
        self.create_footer()
        
    def create_header(self):
        """Create Application Header"""
        header = QWidget()
        header.setStyleSheet("background-color: #2c3e50; color: white;")
        layout = QHBoxLayout(header)
        
        title = QLabel("🏗 VietStructFEM")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        
        subtitle = QLabel("  |  Structural Analysis Platform")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setStyleSheet("color: #bdc3c7;")
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        
        # About button
        btn_about = QPushButton("Giới thiệu")
        btn_about.setStyleSheet("""
            QPushButton {
                background-color: transparent; border: 1px solid white; 
                border-radius: 4px; padding: 5px 15px; color: white;
            }
            QPushButton:hover { background-color: #34495e; }
        """)
        btn_about.clicked.connect(self.show_about)
        layout.addWidget(btn_about)
        
        self.main_layout.addWidget(header)
        
    def init_modules(self):
        """Initialize and add modules"""
        
        # Module 1: Steel Deck (Existing)
        self.steel_deck_module = SteelDeckModule()
        self.tabs.addTab(self.steel_deck_module, "🏢 SÀN DECK LIÊN HỢP")
        
        # Module 2: RC Column
        self.rc_column_module = RCColumnModule()
        self.tabs.addTab(self.rc_column_module, "🏛 CỘT BTCT (RC Column)")
        
        # Module 3: 2D Frame
        self.frame_module = FrameAnalysisModule()
        self.tabs.addTab(self.frame_module, "🕸 KHUNG 2D (Frame Analysis)")
        
        # Tab 4: OpenSees Modal Analysis
        self.opensees_module = OpenSeesModule()
        self.tabs.addTab(self.opensees_module, "🌊 ĐỘNG ĐẤT (OPEN-SEES)")
        
        # Tab 5: Industrial Warehouse (Temporarily disabled - needs fixes)
        # self.warehouse_module = WarehouseModule()
        # self.tabs.addTab(self.warehouse_module, "🏭 NHÀ CÔNG NGHIỆP")
        
        # Tab 6: Load Combination Wizard (NEW - Phase 14)
        self.loadcombo_wizard = LoadCombinationWizard()
        self.tabs.addTab(self.loadcombo_wizard, "🔢 TỔ HỢP TẢI TRỌNG")
        
        # Tab 7: RC Beam Designer (NEW - Phase 15)
        self.rcbeam_module = RCBeamModule()
        self.tabs.addTab(self.rcbeam_module, "🏗 DẦM BTCT")
        
        # Tab 8: Foundation Designer (NEW - Phase 16)
        self.foundation_module = FoundationModule()
        self.tabs.addTab(self.foundation_module, "🔲 MÓNG")
        
        # Tab 9: Steel Members (NEW - Phase 17)
        self.steel_module = SteelMemberModule()
        self.tabs.addTab(self.steel_module, "⚙️ THÉP")
        
        # Tab 10: Steel Connections (NEW - Phase 18)
        self.connection_module = ConnectionModule()
        self.tabs.addTab(self.connection_module, "🔩 LIÊN KẾT")
        
        # Tab 11: Deflection Check (NEW - Phase 22)
        self.deflection_module = DeflectionModule()
        self.tabs.addTab(self.deflection_module, "📏 KIỂM TRA VÕNG")
        
        # Tab 12: Utility Modules (NEW - Phases 20-24)
        self.utility_modules = UtilityModulesWidget()
        self.tabs.addTab(self.utility_modules, "🛠️ TIỆN ÍCH")
        
    def create_footer(self):
        """Create Application Footer"""
        footer = QWidget()
        footer.setStyleSheet("background-color: #ecf0f1; border-top: 1px solid #bdc3c7;")
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(10, 5, 10, 5)
        
        lbl_copyright = QLabel("© 2025 VietStructFEM - Open Source")
        lbl_copyright.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        
        layout.addWidget(lbl_copyright)
        layout.addStretch()
        
        self.main_layout.addWidget(footer)
        
    def show_about(self):
        QMessageBox.about(self, "Về VietStructFEM", 
                          "<h3>VietStructFEM Platform</h3>"
                          "<p>Phần mềm tính toán kết cấu xây dựng Việt Nam</p>"
                          "<p>Tích hợp: PyNite, concreteproperties, anastruct, handcalcs</p>"
                          "<p>Phiên bản: 2.0 (Modular)</p>")


# Entry point for the application
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set global font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
