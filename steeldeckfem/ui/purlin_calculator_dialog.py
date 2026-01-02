# -*- coding: utf-8 -*-
"""
Purlin Calculator Dialog - Industrial Buildings Module
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QLineEdit, QComboBox, QPushButton,
                             QTextEdit, QGridLayout, QTabWidget, QWidget)
from PyQt5.QtCore import Qt
from steeldeckfem.core import PurlinCalculator, get_wind_pressure, get_all_locations
from steeldeckfem.core.data_models import CalculationInput, PurlinParams, WindParams, GeometryParams


class PurlinCalculatorDialog(QDialog):
    """GUI for purlin design calculator"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🏗️ Purlin Calculator - Tính Xà Gồ")
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
        calc_btn = QPushButton("⚡ TÍNH TOÁN XÀ GỒ")
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        calc_btn.clicked.connect(self.calculate_purlin)
        layout.addWidget(calc_btn)
        
    def create_input_tab(self):
        """Create input tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Geometry group
        geo_group = QGroupBox("📐 Geometry - Hình học")
        geo_layout = QGridLayout()
        
        self.span_input = QLineEdit("6.0")
        self.spacing_input = QLineEdit("1.5")
        self.roof_slope_input = QLineEdit("10.0")
        
        geo_layout.addWidget(QLabel("Span - Nhịp (m):"), 0, 0)
        geo_layout.addWidget(self.span_input, 0, 1)
        geo_layout.addWidget(QLabel("Spacing - Khoảng cách (m):"), 1, 0)
        geo_layout.addWidget(self.spacing_input, 1, 1)
        geo_layout.addWidget(QLabel("Roof Slope - Độ dốc mái (°):"), 2, 0)
        geo_layout.addWidget(self.roof_slope_input, 2, 1)
        
        geo_group.setLayout(geo_layout)
        layout.addWidget(geo_group)
        
        # Profile selection
        profile_group = QGroupBox("🔩 Purlin Profile - Tiết diện xà gồ")
        profile_layout = QHBoxLayout()
        
        self.profile_combo = QComboBox()
        profiles = ["Z15015", "Z15020", "Z17515", "Z17520", "Z20015", "Z20020",
                   "C15015", "C15020", "C17515", "C17520", "C20015", "C20020"]
        self.profile_combo.addItems(profiles)
        
        profile_layout.addWidget(QLabel("Select Profile:"))
        profile_layout.addWidget(self.profile_combo)
        profile_group.setLayout(profile_layout)
        layout.addWidget(profile_group)
        
        # Loads group
        loads_group = QGroupBox("⚖️ Loads - Tải trọng")
        loads_layout = QGridLayout()
        
        self.dead_load_input = QLineEdit("25.0")
        self.live_load_input = QLineEdit("30.0")
        
        # Wind location
        self.location_combo = QComboBox()
        self.location_combo.addItems(get_all_locations())
        self.location_combo.setCurrentText("Hà Nội")
        self.location_combo.currentTextChanged.connect(self.update_wind_pressure)
        
        self.wind_pressure_label = QLabel("95 kg/m²")
        
        loads_layout.addWidget(QLabel("Dead Load - Tĩnh tải (kg/m²):"), 0, 0)
        loads_layout.addWidget(self.dead_load_input, 0, 1)
        loads_layout.addWidget(QLabel("Live Load - Hoạt tải (kg/m²):"), 1, 0)
        loads_layout.addWidget(self.live_load_input, 1, 1)
        loads_layout.addWidget(QLabel("Wind Location - Địa điểm:"), 2, 0)
        loads_layout.addWidget(self.location_combo, 2, 1)
        loads_layout.addWidget(QLabel("Wind Pressure - Áp lực gió:"), 3, 0)
        loads_layout.addWidget(self.wind_pressure_label, 3, 1)
        
        loads_group.setLayout(loads_layout)
        layout.addWidget(loads_group)
        
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
    
    def update_wind_pressure(self, location):
        """Update wind pressure based on location"""
        wind_data = get_wind_pressure(location)
        if wind_data:
            self.wind_pressure_label.setText(f"{wind_data['Wo']} kg/m² (Zone {wind_data['zone']})")
    
    def calculate_purlin(self):
        """Calculate purlin design"""
        try:
            # Create input data
            input_data = CalculationInput()
            
            # Purlin parameters
            input_data.purlin = PurlinParams(
                profile_name=self.profile_combo.currentText(),
                span=float(self.span_input.text()),
                spacing=float(self.spacing_input.text()),
                roof_slope=float(self.roof_slope_input.text()),
                dead_load=float(self.dead_load_input.text()),
                live_load=float(self.live_load_input.text())
            )
            
            # Wind parameters
            location = self.location_combo.currentText()
            wind_data = get_wind_pressure(location)
            input_data.wind = WindParams(
                zone=wind_data['zone'],
                Wo=wind_data['Wo'],
                terrain_category='B',
                height=6.0
            )
            
            # Calculate
            calculator = PurlinCalculator()
            result = calculator.check_purlin(input_data)
            
            # Display results
            self.display_results(result)
            
        except Exception as e:
            self.results_text.setText(f"❌ ERROR: {str(e)}\n\nPlease check your inputs.")
    
    def display_results(self, result):
        """Display calculation results"""
        output = []
        output.append("=" * 60)
        output.append("PURLIN CALCULATION RESULTS - KẾT QUẢ TÍNH XÀ GỒ")
        output.append("=" * 60)
        output.append("")
        
        # Profile info
        output.append(f"Profile: {result.get('profile', 'N/A')}")
        output.append(f"Span: {result.get('span', 0):.2f} m")
        output.append(f"Spacing: {result.get('spacing', 0):.2f} m")
        output.append("")
        
        # Stage 1 check
        output.append("--- STAGE 1: Preliminary Check (without self-weight) ---")
        stage1 = result.get('stage1', {})
        output.append(f"Moment: {stage1.get('moment', 0):.2f} kN·m")
        output.append(f"Shear: {stage1.get('shear', 0):.2f} kN")
        output.append(f"Unity Check: {stage1.get('unity', 0):.3f}")
        output.append(f"Status: {stage1.get('status', 'N/A')}")
        output.append("")
        
        # Stage 2 check
        output.append("--- STAGE 2: Final Check (with self-weight) ---")
        stage2 = result.get('stage2', {})
        output.append(f"Moment: {stage2.get('moment', 0):.2f} kN·m")
        output.append(f"Shear: {stage2.get('shear', 0):.2f} kN")
        output.append(f"Unity Check: {stage2.get('unity', 0):.3f}")
        output.append(f"Status: {stage2.get('status', 'N/A')}")
        output.append("")
        
        # Deflection check
        output.append("--- DEFLECTION CHECK ---")
        defl = result.get('deflection', {})
        output.append(f"Max Deflection: {defl.get('value', 0):.2f} mm")
        output.append(f"Limit (L/150): {defl.get('limit', 0):.2f} mm")
        output.append(f"Status: {defl.get('status', 'N/A')}")
        output.append("")
        
        # Overall result
        overall_status = result.get('overall_status', 'UNKNOWN')
        symbol = "✅" if overall_status == "OK" else "❌"
        output.append("=" * 60)
        output.append(f"{symbol} OVERALL STATUS: {overall_status}")
        output.append("=" * 60)
        
        self.results_text.setText("\n".join(output))
    
    def export_report(self):
        """Export HTML report"""
        from PyQt5.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Report", "", "HTML Files (*.html)"
        )
        
        if filename:
            # TODO: Generate proper HTML report
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"<html><body><pre>{self.results_text.toPlainText()}</pre></body></html>")
            
            self.results_text.append(f"\n✅ Report saved to: {filename}")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = PurlinCalculatorDialog()
    dialog.show()
    sys.exit(app.exec_())
