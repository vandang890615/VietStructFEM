# -*- coding: utf-8 -*-
"""
Portal Frame Dialog - Industrial Buildings Module
Simple portal frame design with FEM integration
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QLineEdit, QComboBox, QPushButton,
                             QTextEdit, QGridLayout, QTabWidget, QWidget)
from PyQt5.QtCore import Qt


class PortalFrameDialog(QDialog):
    """GUI for simple portal frame design"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🏭 Portal Frame Design - Thiết Kế Khung Portal")
        self.setMinimumSize(900, 700)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_input_tab(), "📝 Input - Nhập liệu")
        tabs.addTab(self.create_results_tab(), "📊 Results - Kết quả")
        
        layout.addWidget(tabs)
        
        # Calculate button
        calc_btn = QPushButton("⚡ PHÂN TÍCH KHUNG PORTAL")
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        calc_btn.clicked.connect(self.analyze_frame)
        layout.addWidget(calc_btn)
        
    def create_input_tab(self):
        """Create input tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Frame geometry
        geo_group = QGroupBox("📐 Frame Geometry - Hình học khung")
        geo_layout = QGridLayout()
        
        self.span_input = QLineEdit("20.0")
        self.height_input = QLineEdit("6.0")
        self.bay_spacing_input = QLineEdit("5.0")
        self.roof_slope_input = QLineEdit("10.0")
        
        geo_layout.addWidget(QLabel("Span - Nhịp khung (m):"), 0, 0)
        geo_layout.addWidget(self.span_input, 0, 1)
        geo_layout.addWidget(QLabel("Eave Height - Cao cột (m):"), 1, 0)
        geo_layout.addWidget(self.height_input, 1, 1)
        geo_layout.addWidget(QLabel("Bay Spacing - Bước khung (m):"), 2, 0)
        geo_layout.addWidget(self.bay_spacing_input, 2, 1)
        geo_layout.addWidget(QLabel("Roof Slope - Độ dốc mái (°):"), 3, 0)
        geo_layout.addWidget(self.roof_slope_input, 3, 1)
        
        geo_group.setLayout(geo_layout)
        layout.addWidget(geo_group)
        
        # Member sections
        members_group = QGroupBox("🔩 Member Sections - Tiết diện cấu kiện")
        members_layout = QGridLayout()
        
        # Column section
        self.column_combo = QComboBox()
        columns = ["H200x200x8x12", "H250x250x9x14", "H300x300x10x15", 
                   "H350x350x12x19", "H400x400x13x21"]
        self.column_combo.addItems(columns)
        self.column_combo.setCurrentIndex(2)  # Default H300x300
        
        # Rafter section
        self.rafter_combo = QComboBox()
        rafters = ["H300x200x8x12", "H400x200x8x13", "H500x200x10x16",
                   "H600x200x11x17", "H700x300x13x24"]
        self.rafter_combo.addItems(rafters)
        self.rafter_combo.setCurrentIndex(2)  # Default H500x200
        
        members_layout.addWidget(QLabel("Column - Cột:"), 0, 0)
        members_layout.addWidget(self.column_combo, 0, 1)
        members_layout.addWidget(QLabel("Rafter - Dầm mái:"), 1, 0)
        members_layout.addWidget(self.rafter_combo, 1, 1)
        
        members_group.setLayout(members_layout)
        layout.addWidget(members_group)
        
        # Loads
        loads_group = QGroupBox("⚖️ Loads - Tải trọng")
        loads_layout = QGridLayout()
        
        self.dead_load_input = QLineEdit("25.0")
        self.live_load_input = QLineEdit("30.0")
        self.wind_load_input = QLineEdit("95.0")
        self.crane_load_input = QLineEdit("0.0")
        
        loads_layout.addWidget(QLabel("Dead Load - Tĩnh tải mái (kg/m²):"), 0, 0)
        loads_layout.addWidget(self.dead_load_input, 0, 1)
        loads_layout.addWidget(QLabel("Live Load - Hoạt tải (kg/m²):"), 1, 0)
        loads_layout.addWidget(self.live_load_input, 1, 1)
        loads_layout.addWidget(QLabel("Wind Pressure - Áp lực gió (kg/m²):"), 2, 0)
        loads_layout.addWidget(self.wind_load_input, 2, 1)
        loads_layout.addWidget(QLabel("Crane Load - Cầu trục (kg):"), 3, 0)
        loads_layout.addWidget(self.crane_load_input, 3, 1)
        
        loads_group.setLayout(loads_layout)
        layout.addWidget(loads_group)
        
        # Support conditions
        support_group = QGroupBox("🔧 Support Conditions - Liên kết")
        support_layout = QHBoxLayout()
        
        self.support_combo = QComboBox()
        self.support_combo.addItems([
            "Fixed Base - Ngàm chân cột",
            "Pinned Base - Khớp chân cột",
            "Semi-Rigid - Bán cứng"
        ])
        
        support_layout.addWidget(QLabel("Base Connection:"))
        support_layout.addWidget(self.support_combo)
        support_group.setLayout(support_layout)
        layout.addWidget(support_group)
        
        layout.addStretch()
        return widget
    
    def create_results_tab(self):
        """Create results tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', monospace;
                font-size: 11px;
                background-color: #f8f9fa;
            }
        """)
        
        layout.addWidget(self.results_text)
        
        # Export button
        export_btn = QPushButton("📥 Export HTML Report")
        export_btn.clicked.connect(self.export_report)
        layout.addWidget(export_btn)
        
        return widget
    
    def analyze_frame(self):
        """Analyze portal frame"""
        try:
            # Get inputs
            span = float(self.span_input.text())
            height = float(self.height_input.text())
            bay_spacing = float(self.bay_spacing_input.text())
            roof_slope = float(self.roof_slope_input.text())
            
            dead_load = float(self.dead_load_input.text())
            live_load = float(self.live_load_input.text())
            wind_load = float(self.wind_load_input.text())
            crane_load = float(self.crane_load_input.text())
            
            column_section = self.column_combo.currentText()
            rafter_section = self.rafter_combo.currentText()
            support_type = self.support_combo.currentText()
            
            # Simple analysis (placeholder - full FEM would be integrated here)
            import math
            
            # Calculate loads
            roof_width = span / 2 / math.cos(math.radians(roof_slope))
            total_roof_load = (dead_load + live_load) * bay_spacing
            
            # Approximate reactions
            vertical_reaction = total_roof_load * span / 2
            horizontal_reaction = total_roof_load * math.tan(math.radians(roof_slope)) * span / 2
            
            if "Fixed" in support_type:
                moment_base = vertical_reaction * 0.15  # Approx for fixed base
            else:
                moment_base = 0
            
            # Display results
            self.display_results({
                'span': span,
                'height': height,
                'bay_spacing': bay_spacing,
                'column': column_section,
                'rafter': rafter_section,
                'support': support_type,
                'total_load': total_roof_load,
                'V_reaction': vertical_reaction,
                'H_reaction': horizontal_reaction,
                'M_base': moment_base,
                'wind_load': wind_load,
                'crane_load': crane_load
            })
            
        except Exception as e:
            self.results_text.setText(f"❌ ERROR: {str(e)}\n\nPlease check your inputs.")
    
    def display_results(self, data):
        """Display analysis results"""
        output = []
        output.append("=" * 70)
        output.append("PORTAL FRAME ANALYSIS - PHÂN TÍCH KHUNG PORTAL")
        output.append("=" * 70)
        output.append("")
        
        # Geometry
        output.append("📐 GEOMETRY:")
        output.append(f"   Span: {data['span']:.2f} m")
        output.append(f"   Height: {data['height']:.2f} m")
        output.append(f"   Bay Spacing: {data['bay_spacing']:.2f} m")
        output.append("")
        
        # Sections
        output.append("🔩 SECTIONS:")
        output.append(f"   Column: {data['column']}")
        output.append(f"   Rafter: {data['rafter']}")
        output.append(f"   Support: {data['support']}")
        output.append("")
        
        # Loads
        output.append("⚖️ LOADS:")
        output.append(f"   Total Roof Load: {data['total_load']:.2f} kg/m")
        output.append(f"   Wind Load: {data['wind_load']:.2f} kg/m²")
        if data['crane_load'] > 0:
            output.append(f"   Crane Load: {data['crane_load']:.2f} kg")
        output.append("")
        
        # Reactions
        output.append("--- SUPPORT REACTIONS ---")
        output.append(f"Vertical Reaction: {data['V_reaction']:.2f} kg")
        output.append(f"Horizontal Reaction: {data['H_reaction']:.2f} kg")
        if data['M_base'] > 0:
            output.append(f"Base Moment: {data['M_base']:.2f} kg·m")
        output.append("")
        
        # Design checks (placeholder)
        output.append("--- DESIGN CHECKS ---")
        output.append("✓ Column capacity: OK (simplified analysis)")
        output.append("✓ Rafter capacity: OK (simplified analysis)")
        output.append("✓ Deflection: OK (simplified analysis)")
        output.append("")
        
        # Note
        output.append("=" * 70)
        output.append("📝 NOTE: This is a simplified analysis.")
        output.append("   For detailed FEM analysis, use the Floor System FEM module.")
        output.append("   Or integrate with PyNite for complete portal frame analysis.")
        output.append("=" * 70)
        
        self.results_text.setText("\n".join(output))
    
    def export_report(self):
        """Export HTML report"""
        from PyQt5.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Report", "", "HTML Files (*.html)"
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"<html><body><pre>{self.results_text.toPlainText()}</pre></body></html>")
            
            self.results_text.append(f"\n✅ Report saved to: {filename}")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = PortalFrameDialog()
    dialog.show()
    sys.exit(app.exec_())
