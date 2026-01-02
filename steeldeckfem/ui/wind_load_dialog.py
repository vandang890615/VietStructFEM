# -*- coding: utf-8 -*-
"""
Wind Load Calculator Dialog - TCVN 2737:2023
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QLineEdit, QComboBox, QPushButton,
                             QTextEdit, QGridLayout, QTabWidget, QWidget,
                             QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt
from steeldeckfem.core import WindLoadCalculator, get_wind_pressure, get_all_locations, WIND_ZONES
from steeldeckfem.core.data_models import CalculationInput, WindParams, GeometryParams


class WindLoadCalculatorDialog(QDialog):
    """GUI for wind load calculator per TCVN 2737"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🌪️ Wind Load Calculator - Tải Trọng Gió TCVN 2737")
        self.setMinimumSize(1000, 750)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_input_tab(), "📝 Input - Nhập liệu")
        tabs.addTab(self.create_results_tab(), "📊 Results - Kết quả")
        tabs.addTab(self.create_wind_cases_tab(), "🌪️ Wind Cases - Trường hợp gió")
        
        layout.addWidget(tabs)
        
        # Calculate button
        calc_btn = QPushButton("⚡ TÍNH TOÁN TẢI TRỌNG GIÓ")
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        calc_btn.clicked.connect(self.calculate_wind)
        layout.addWidget(calc_btn)
        
    def create_input_tab(self):
        """Create input tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Location selection
        location_group = QGroupBox("📍 Wind Zone - Vùng gió (TCVN 2737:2023)")
        location_layout = QVBoxLayout()
        
        loc_h = QHBoxLayout()
        self.location_combo = QComboBox()
        self.location_combo.addItem("--- Chọn theo thành phố ---")
        self.location_combo.addItems(get_all_locations())
        self.location_combo.currentTextChanged.connect(self.update_wind_zone)
        
        loc_h.addWidget(QLabel("Địa điểm:"))
        loc_h.addWidget(self.location_combo)
        location_layout.addLayout(loc_h)
        
        # Wind zone info display
        info_layout = QGridLayout()
        self.zone_label = QLabel("---")
        self.wo_label = QLabel("---")
        
        info_layout.addWidget(QLabel("Wind Zone - Vùng gió:"), 0, 0)
        info_layout.addWidget(self.zone_label, 0, 1)
        info_layout.addWidget(QLabel("Wo (kg/m²):"), 1, 0)
        info_layout.addWidget(self.wo_label, 1, 1)
        
        location_layout.addLayout(info_layout)
        location_group.setLayout(location_layout)
        layout.addWidget(location_group)
        
        # Building geometry
        geo_group = QGroupBox("🏗️ Building Geometry - Kích thước công trình")
        geo_layout = QGridLayout()
        
        self.length_input = QLineEdit("40.0")
        self.width_input = QLineEdit("20.0")
        self.height_input = QLineEdit("10.0")
        
        geo_layout.addWidget(QLabel("Length - Chiều dài (m):"), 0, 0)
        geo_layout.addWidget(self.length_input, 0, 1)
        geo_layout.addWidget(QLabel("Width - Chiều rộng (m):"), 1, 0)
        geo_layout.addWidget(self.width_input, 1, 1)
        geo_layout.addWidget(QLabel("Height - Chiều cao (m):"), 2, 0)
        geo_layout.addWidget(self.height_input, 2, 1)
        
        geo_group.setLayout(geo_layout)
        layout.addWidget(geo_group)
        
        # Terrain category
        terrain_group = QGroupBox("🌳 Terrain Category - Phân loại địa hình")
        terrain_layout = QVBoxLayout()
        
        self.terrain_combo = QComboBox()
        terrain_options = [
            "A - Ven biển, mặt nước",
            "B - Nông thôn, ít công trình",
            "C - Ngoại ô, nhiều công trình thấp",
            "D - Thành phố, công trình cao tầng"
        ]
        self.terrain_combo.addItems(terrain_options)
        self.terrain_combo.setCurrentIndex(1)  # Default to B
        
        terrain_layout.addWidget(QLabel("Select terrain:"))
        terrain_layout.addWidget(self.terrain_combo)
        
        # Terrain description
        desc = QTextEdit()
        desc.setReadOnly(True)
        desc.setMaximumHeight(100)
        desc.setHtml("""
        <b>A</b>: Ven biển, mặt nước<br>
        <b>B</b>: Nông thôn, ít công trình (k=1.0)<br>
        <b>C</b>: Ngoại ô, nhiều công trình thấp (k=1.2)<br>
        <b>D</b>: Thành phố, công trình cao (k=1.4)
        """)
        terrain_layout.addWidget(desc)
        
        terrain_group.setLayout(terrain_layout)
        layout.addWidget(terrain_group)
        
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
    
    def create_wind_cases_tab(self):
        """Create wind cases tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("<b>4 Wind Load Cases - Các trường hợp tải trọng gió</b>")
        layout.addWidget(label)
        
        # Table for wind cases
        self.wind_table = QTableWidget()
        self.wind_table.setColumnCount(6)
        self.wind_table.setHorizontalHeaderLabels([
            "Case", "Direction", "Pressure (kg/m²)", 
            "k Factor", "β Factor", "Description"
        ])
        self.wind_table.setRowCount(4)
        
        # Default data
        cases = [
            ("W1", "→ Gió ngang X+", "---", "---", "---", "Wind perpendicular to length"),
            ("W2", "← Gió ngang X-", "---", "---", "---", "Wind perpendicular to length (opposite)"),
            ("W3", "↑ Gió dọc Y+", "---", "---", "---", "Wind perpendicular to width"),
            ("W4", "↓ Gió dọc Y-", "---", "---", "---", "Wind perpendicular to width (opposite)"),
        ]
        
        for row, data in enumerate(cases):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.wind_table.setItem(row, col, item)
        
        self.wind_table.resizeColumnsToContents()
        layout.addWidget(self.wind_table)
        
        return widget
    
    def update_wind_zone(self, location):
        """Update wind zone info based on location"""
        if location and location != "--- Chọn theo thành phố ---":
            wind_data = get_wind_pressure(location)
            if wind_data:
                self.zone_label.setText(f"<b style='color: #e74c3c;'>Zone {wind_data['zone']}</b>")
                self.wo_label.setText(f"<b style='color: #e74c3c;'>{wind_data['Wo']} kg/m²</b>")
        else:
            self.zone_label.setText("---")
            self.wo_label.setText("---")
    
    def calculate_wind(self):
        """Calculate wind loads"""
        try:
            location = self.location_combo.currentText()
            if location == "--- Chọn theo thành phố ---":
                self.results_text.setText("❌ Vui lòng chọn địa điểm!")
                return
            
            # Get wind data
            wind_data = get_wind_pressure(location)
            
            # Get terrain category
            terrain_text = self.terrain_combo.currentText()
            terrain_code = terrain_text[0]  # A, B, C, or D
            
            # Create input data
            input_data = CalculationInput()
            
            input_data.geometry = GeometryParams(
                span=float(self.length_input.text()),
                length=float(self.length_input.text()),
                height_eave=float(self.height_input.text())
            )
            
            input_data.wind = WindParams(
                zone=wind_data['zone'],
                Wo=wind_data['Wo'],
                terrain_category=terrain_code,
                height=float(self.height_input.text())
            )
            
            # Calculate
            calculator = WindLoadCalculator()
            result = calculator.calculate_wind(input_data)
            
            # Display results
            self.display_results(result, wind_data, terrain_text)
            self.update_wind_cases_table(result)
            
        except Exception as e:
            self.results_text.setText(f"❌ ERROR: {str(e)}\n\nPlease check your inputs.")
    
    def display_results(self, result, wind_data, terrain):
        """Display calculation results"""
        output = []
        output.append("=" * 70)
        output.append("WIND LOAD CALCULATION - TÍNH TOÁN TẢI TRỌNG GIÓ TCVN 2737:2023")
        output.append("=" * 70)
        output.append("")
        
        # Location info
        output.append(f"📍 Location: {self.location_combo.currentText()}")
        output.append(f"   Wind Zone: {wind_data['zone']}")
        output.append(f"   Wo: {wind_data['Wo']} kg/m²")
        output.append("")
        
        # Building geometry
        output.append("🏗️ Building Geometry:")
        output.append(f"   Length: {self.length_input.text()} m")
        output.append(f"   Width: {self.width_input.text()} m")
        output.append(f"   Height: {self.height_input.text()} m")
        output.append("")
        
        # Terrain
        output.append(f"🌳 Terrain: {terrain}")
        output.append("")
        
        # Wind pressure calculations
        output.append("--- WIND PRESSURE CALCULATIONS ---")
        output.append(f"k Factor (terrain): {result.get('k_factor', 1.0):.2f}")
        output.append(f"β Factor (dynamic): {result.get('beta_factor', 1.0):.2f}")
        output.append(f"Ce Coefficient: {result.get('Ce', 1.0):.2f}")
        output.append(f"Cq Coefficient: {result.get('Cq', 1.0):.2f}")
        output.append("")
        
        # Design wind pressure
        Wd = result.get('Wd', 0)
        output.append(f"📊 Design Wind Pressure:")
        output.append(f"   Wd = Wo × k × β × Ce × Cq")
        output.append(f"   Wd = {wind_data['Wo']} × {result.get('k_factor', 1.0):.2f} × "
                     f"{result.get('beta_factor', 1.0):.2f} × {result.get('Ce', 1.0):.2f} × {result.get('Cq', 1.0):.2f}")
        output.append(f"   Wd = {Wd:.2f} kg/m²")
        output.append("")
        
        # Wind cases
        output.append("--- 4 WIND LOAD CASES ---")
        cases = result.get('wind_cases', {})
        for case_name, case_data in cases.items():
            output.append(f"{case_name}: {case_data.get('description', '')}")
            output.append(f"     Pressure: {case_data.get('pressure', 0):.2f} kg/m²")
            output.append(f"     Direction: {case_data.get('direction', '')}")
        
        output.append("")
        output.append("=" * 70)
        output.append("✅ Calculation Complete")
        output.append("=" * 70)
        
        self.results_text.setText("\n".join(output))
    
    def update_wind_cases_table(self, result):
        """Update wind cases table"""
        cases = result.get('wind_cases', {})
        
        case_names = ['W1', 'W2', 'W3', 'W4']
        for row, case_name in enumerate(case_names):
            if case_name in cases:
                case_data = cases[case_name]
                
                # Update pressure
                self.wind_table.setItem(row, 2, 
                    QTableWidgetItem(f"{case_data.get('pressure', 0):.2f}"))
                
                # Update k factor
                self.wind_table.setItem(row, 3, 
                    QTableWidgetItem(f"{result.get('k_factor', 1.0):.2f}"))
                
                # Update beta factor
                self.wind_table.setItem(row, 4, 
                    QTableWidgetItem(f"{result.get('beta_factor', 1.0):.2f}"))
    
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
    dialog = WindLoadCalculatorDialog()
    dialog.show()
    sys.exit(app.exec_())
