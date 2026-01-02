# -*- coding: utf-8 -*-
"""
Steel Deck Floor System Calculator with Advanced FEM Analysis
Professional structural analysis with PyNite + Plotly interactive diagrams
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
                             QLineEdit, QComboBox, QPushButton, QLabel, QTabWidget,
                             QTextBrowser, QMessageBox, QSplitter, QWidget, QScrollArea,
                             QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QFont
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False
    print("⚠ PyQtWebEngine not available. Plotly diagrams will not display.")

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Wind zones - always needed
try:
    from utils.wind_zones import WIND_ZONES, CITY_WIND_ZONES, get_wind_pressure, get_all_locations
except ImportError:
    # Fallback if wind_zones not found
    WIND_ZONES = {"Vùng I - Nội địa": {"zone": "I", "Wo": 95, "description": "Default", "cities": []}}
    CITY_WIND_ZONES = {"Hà Nội": {"zone": "I", "Wo": 95}}
    def get_wind_pressure(loc): return {"zone": "I", "Wo": 95}
    def get_all_locations(): return list(WIND_ZONES.keys())

# Advanced analysis features (optional)
try:
    from utils.fem_analyzer import FloorSystemFEMAnalyzer
    from utils.plotly_charts import StructuralDiagramCreator
    HAS_ADVANCED_FEATURES = True
    print("✓ Advanced features loaded successfully!")
except ImportError as e:
    HAS_ADVANCED_FEATURES = False
    import traceback
    print("⚠ Advanced features (PyNite/Plotly) not available.")
    print(f"Error: {e}")
    print("Traceback:")
    traceback.print_exc()
    print("\nInstall with: pip install PyNite plotly")


class FEMAnalysisThread(QThread):
    """Background thread for FEM analysis"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, layout, loads):
        super().__init__()
        self.layout = layout
        self.loads = loads
        
    def run(self):
        try:
            analyzer = FloorSystemFEMAnalyzer()
            analyzer.build_fem_model(self.layout, self.loads)
            results = analyzer.run_analysis(layout=self.layout)  # Pass layout for design checks
            results['html_report'] = analyzer.generate_fem_report()
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class SteelDeckCalculatorDialog(QDialog):
    """
    Steel Deck Floor System Calculator với:
    - FEM Analysis (PyNite)
    - Interactive Diagrams (Plotly)
    - 3D Visualization
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🏗 TÍNH TOÁN SÀN DECK LIÊN HỢP - PHÂN TÍCH FEM")
        self.resize(1600, 1000)
        
        self.fem_results = None
        self.layout_data = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QHBoxLayout(self)
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Inputs
        left_panel = self.create_input_panel()
        splitter.addWidget(left_panel)
        
        # Right: Outputs & Analysis
        right_panel = self.create_output_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        
    def create_input_panel(self):
        """Create input panel"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        panel = QWidget()
        layout = QVBoxLayout(panel)
        scroll.setWidget(panel)
        
        # Title
        title = QLabel("⚙ ĐẦU VÀO HỆ THỐNG")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #2980b9; color: white; padding: 10px; border-radius: 5px;")
        layout.addWidget(title)
        
        # System Layout
        gb_system = QGroupBox("1. BỐ TRÍ HỆ THỐNG")
        form_system = QFormLayout()
        
        # Location selector with wind zones
        self.cbo_location = QComboBox()
        self.cbo_location.addItems(["Chọn địa điểm..."] + ["--- VÙNG GIÓ ---"] + list(WIND_ZONES.keys()) + 
                                   ["--- THÀNH PHỐ ---"] + sorted(CITY_WIND_ZONES.keys()))
        self.cbo_location.currentTextChanged.connect(self.on_location_changed)
        
        self.lbl_wind_zone = QLabel("Chưa chọn")
        self.lbl_wind_zone.setStyleSheet("color: #7f8c8d; font-style: italic;")
        
        self.inp_length = QLineEdit("20")
        self.inp_width = QLineEdit("15")
        self.inp_height = QLineEdit("4.0")
        self.inp_col_x = QLineEdit("5.0")
        self.inp_col_y = QLineEdit("5.0")
        self.cbo_main_dir = QComboBox()
        self.cbo_main_dir.addItems(["X", "Y"])
        self.inp_sec_spacing = QLineEdit("2.5")
        
        form_system.addRow("🌍 Địa điểm:", self.cbo_location)
        form_system.addRow("📍 Vùng gió:", self.lbl_wind_zone)
        form_system.addRow("Chiều dài (m):", self.inp_length)
        form_system.addRow("Chiều rộng (m):", self.inp_width)
        form_system.addRow("Cao tầng (m):", self.inp_height)
        form_system.addRow("Lưới cột X (m):", self.inp_col_x)
        form_system.addRow("Lưới cột Y (m):", self.inp_col_y)
        form_system.addRow("Hướng dầm chính:", self.cbo_main_dir)
        form_system.addRow("Khoảng cách dầm phụ (m):", self.inp_sec_spacing)
        gb_system.setLayout(form_system)
        layout.addWidget(gb_system)
        
        # Columns
        gb_col = QGroupBox("2. CỘT")
        gb_col.setStyleSheet("QGroupBox { font-weight: bold; color: #27ae60; }")
        form_col = QFormLayout()
        
        self.inp_col_h = QLineEdit("300")
        self.inp_col_b = QLineEdit("300")
        self.inp_col_tf = QLineEdit("10")
        self.inp_col_tw = QLineEdit("15")
        
        form_col.addRow("H (mm):", self.inp_col_h)
        form_col.addRow("B (mm):", self.inp_col_b)
        form_col.addRow("tf (mm):", self.inp_col_tf)
        form_col.addRow("tw (mm):", self.inp_col_tw)
        gb_col.setLayout(form_col)
        layout.addWidget(gb_col)
        
        # Main Beams
        gb_main = QGroupBox("3. DẦM CHÍNH")
        gb_main.setStyleSheet("QGroupBox { font-weight: bold; color: #e74c3c; }")
        form_main = QFormLayout()
        
        self.inp_main_h = QLineEdit("500")
        self.inp_main_b = QLineEdit("200")
        self.inp_main_tf = QLineEdit("10")
        self.inp_main_tw = QLineEdit("8")
        
        form_main.addRow("H (mm):", self.inp_main_h)
        form_main.addRow("B (mm):", self.inp_main_b)
        form_main.addRow("tf (mm):", self.inp_main_tf)
        form_main.addRow("tw (mm):", self.inp_main_tw)
        gb_main.setLayout(form_main)
        layout.addWidget(gb_main)
        
        # Secondary Beams
        gb_sec = QGroupBox("4. DẦM PHỤ")
        gb_sec.setStyleSheet("QGroupBox { font-weight: bold; color: #3498db; }")
        form_sec = QFormLayout()
        
        self.inp_sec_h = QLineEdit("300")
        self.inp_sec_b = QLineEdit("150")
        self.inp_sec_tf = QLineEdit("8")
        self.inp_sec_tw = QLineEdit("6")
        
        form_sec.addRow("H (mm):", self.inp_sec_h)
        form_sec.addRow("B (mm):", self.inp_sec_b)
        form_sec.addRow("tf (mm):", self.inp_sec_tf)
        form_sec.addRow("tw (mm):", self.inp_sec_tw)
        gb_sec.setLayout(form_sec)
        layout.addWidget(gb_sec)
        
        # Loads
        gb_loads = QGroupBox("5. TẢI TRỌNG")
        form_loads = QFormLayout()
        
        self.inp_live = QLineEdit("400")
        self.inp_dead = QLineEdit("30")
        self.inp_wind = QLineEdit("95")
        self.inp_wind.setStyleSheet("background: #fff3cd;")
        self.inp_wind.setReadOnly(True)
        
        form_loads.addRow("Hoạt tải (kg/m²):", self.inp_live)
        form_loads.addRow("Tĩnh tải HT (kg/m²):", self.inp_dead)
        form_loads.addRow("🌪 Gió Wo (kg/m²):", self.inp_wind)
        gb_loads.setLayout(form_loads)
        layout.addWidget(gb_loads)
        
        # Calculate Button
        btn_calc = QPushButton("⚡ PHÂN TÍCH FEM")
        btn_calc.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_calc.clicked.connect(self.run_fem_analysis)
        layout.addWidget(btn_calc)
        
        layout.addStretch()
        
        return scroll
    
    def create_output_panel(self):
        """Create output panel with tabs"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        tabs = QTabWidget()
        
        # Tab 1: 3D View (Matplotlib)
        self.tab_3d = QWidget()
        self.init_3d_tab()
        tabs.addTab(self.tab_3d, "🎨 Mô hình 3D")
        
        # Tab 2: FEM Results
        self.tab_fem = QWidget()
        self.init_fem_tab()
        tabs.addTab(self.tab_fem, "🔬 Kết quả FEM")
        
        # Tab 3: Plotly Diagrams
        if HAS_ADVANCED_FEATURES:
            self.tab_plotly = QWidget()
            self.init_plotly_tab()
            tabs.addTab(self.tab_plotly, "📊 Biểu đồ Interactive")
        
        layout.addWidget(tabs)
        
        return panel
    
    def on_location_changed(self):
        """Handle location selection change"""
        location = self.cbo_location.currentText()
        
        if location in ["Chọn địa điểm...", "--- VÙNG GIÓ ---", "--- THÀNH PHỐ ---"]:
            return
        
        wind_data = get_wind_pressure(location)
        zone = wind_data.get('zone', 'I')
        wo = wind_data.get('Wo', 95)
        
        self.lbl_wind_zone.setText(f"Vùng {zone} - Wo = {wo} kg/m²")
        self.lbl_wind_zone.setStyleSheet("color: #27ae60; font-weight: bold;")
        self.inp_wind.setText(str(wo))
    
    def init_3d_tab(self):
        """Initialize 3D tab with component toggles"""
        layout = QVBoxLayout(self.tab_3d)
        
        self.fig_3d = Figure(figsize=(10, 8), facecolor='#f8f9fa')
        self.ax_3d = self.fig_3d.add_subplot(111, projection='3d')
        self.canvas_3d = FigureCanvas(self.fig_3d)
        
        layout.addWidget(self.canvas_3d)
        
        # Component visibility toggles
        toggle_layout = QHBoxLayout()
        toggle_layout.addWidget(QLabel("<b>Hiển thị:</b>"))
        
        self.chk_show_columns = QCheckBox("🟢 Cột")
        self.chk_show_columns.setChecked(True)
        self.chk_show_columns.stateChanged.connect(self.draw_3d_model)
        
        self.chk_show_main_beams = QCheckBox("🔴 Dầm chính")
        self.chk_show_main_beams.setChecked(True)
        self.chk_show_main_beams.stateChanged.connect(self.draw_3d_model)
        
        self.chk_show_sec_beams = QCheckBox("🔵 Dầm phụ")
        self.chk_show_sec_beams.setChecked(True)
        self.chk_show_sec_beams.stateChanged.connect(self.draw_3d_model)
        
        self.chk_show_deck = QCheckBox("⬜ Sàn deck")
        self.chk_show_deck.setChecked(True)
        self.chk_show_deck.stateChanged.connect(self.draw_3d_model)
        
        toggle_layout.addWidget(self.chk_show_columns)
        toggle_layout.addWidget(self.chk_show_main_beams)
        toggle_layout.addWidget(self.chk_show_sec_beams)
        toggle_layout.addWidget(self.chk_show_deck)
        toggle_layout.addStretch()
        
        layout.addLayout(toggle_layout)
        
        # View controls
        controls = QHBoxLayout()
        
        btn_top = QPushButton("Nhìn trên")
        btn_top.clicked.connect(lambda: self.ax_3d.view_init(90, -90) or self.canvas_3d.draw())
        
        btn_iso = QPushButton("Isometric")
        btn_iso.clicked.connect(lambda: self.ax_3d.view_init(30, 45) or self.canvas_3d.draw())
        
        btn_side = QPushButton("Nhìn nghiêng")
        btn_side.clicked.connect(lambda: self.ax_3d.view_init(0, 0) or self.canvas_3d.draw())
        
        controls.addWidget(btn_top)
        controls.addWidget(btn_iso)
        controls.addWidget(btn_side)
        controls.addStretch()
        
        layout.addLayout(controls)
        
        self.draw_3d_model()
    
    def init_fem_tab(self):
        """Initialize FEM results tab"""
        layout = QVBoxLayout(self.tab_fem)
        
        self.fem_browser = QTextBrowser()
        self.fem_browser.setHtml("<h3>Nhấn 'PHÂN TÍCH FEM' để chạy phân tích</h3>")
        layout.addWidget(self.fem_browser)
    
    def init_plotly_tab(self):
        """Initialize Plotly tab"""
        layout = QVBoxLayout(self.tab_plotly)
        
        if HAS_WEBENGINE:
            self.plotly_view = QWebEngineView()
        else:
            self.plotly_view = QTextBrowser()
            self.plotly_view.setHtml("<h3 style='color:red;'>⚠ Cần cài PyQtWebEngine để xem biểu đồ Plotly</h3><p>Chạy: <code>pip install PyQtWebEngine</code></p>")
        layout.addWidget(self.plotly_view)
        
        btn_export = QPushButton("📥 Xuất HTML")
        btn_export.clicked.connect(self.export_plotly_html)
        layout.addWidget(btn_export)
    
    def draw_3d_model(self):
        """Draw professional 3D model with enhanced styling"""
        self.ax_3d.clear()
        
        try:
            L = float(self.inp_length.text())
            W = float(self.inp_width.text())
            H = float(self.inp_height.text())
            col_x = float(self.inp_col_x.text())
            col_y = float(self.inp_col_y.text())
            sec_spacing = float(self.inp_sec_spacing.text())
            
            num_cols_x = int(L / col_x) + 1
            num_cols_y = int(W / col_y) + 1
            
            # === DRAW COLUMNS (GREEN or RED based on stress) ===
            if self.chk_show_columns.isChecked():
                design_checks = self.fem_results.get('design_checks', {}) if self.fem_results else {}
                
                for i in range(num_cols_x):
                    for j in range(num_cols_y):
                        x, y = i * col_x, j * col_y
                        
                        # Determine color based on stress check
                        col_name = f"Col_{i}_{j}"
                        if col_name in design_checks:
                            status = design_checks[col_name]['status']
                            unity = design_checks[col_name]['unity_check']
                            
                            if status == 'KHÔNG ĐẠT':
                                color = '#e74c3c'  # Red for failed
                                alpha = 1.0
                            elif unity > 0.8:
                                color = '#f39c12'  # Orange for warning (> 80%)
                                alpha = 0.9
                            else:
                                color = '#27ae60'  # Green for OK
                                alpha = 0.9
                        else:
                            color = '#27ae60'
                            alpha = 0.9
                        
                        # Column as thick line with end markers
                        self.ax_3d.plot([x, x], [y, y], [0, H],
                                       color=color, linewidth=10, alpha=alpha,
                                       solid_capstyle='round',
                                       label='🟢 Cột' if i==0 and j==0 else '')
                        # Column base
                        self.ax_3d.scatter([x], [y], [0], color=color, s=150, marker='s', alpha=0.8)
                        # Column top
                        self.ax_3d.scatter([x], [y], [H], color=color, s=100, marker='o', alpha=0.9)
            
            # === DRAW MAIN BEAMS (RED/ORANGE/GREEN based on stress) ===
            if self.chk_show_main_beams.isChecked():
                design_checks = self.fem_results.get('design_checks', {}) if self.fem_results else {}
                main_dir = self.cbo_main_dir.currentText()
                if main_dir == 'X':
                    for j in range(num_cols_y):
                        y = j * col_y
                        x_line = np.linspace(0, L, 50)
                        y_line = np.ones_like(x_line) * y
                        z_line = np.ones_like(x_line) * H
                        
                        # Check stress status
                        beam_name = f"MB_Y{j}"
                        if beam_name in design_checks:
                            status = design_checks[beam_name]['status']
                            unity = design_checks[beam_name]['unity_check']
                            if status == 'KHÔNG ĐẠT':
                                color = '#e74c3c'  # Red
                            elif unity > 0.8:
                                color = '#f39c12'  # Orange
                            else:
                                color = '#27ae60'  # Green
                        else:
                            color = '#e74c3c'  # Default red
                        
                        self.ax_3d.plot(x_line, y_line, z_line,
                                       color=color, linewidth=6, alpha=0.9,
                                       label='🔴 Dầm chính' if j==0 else '')
                else:
                    for i in range(num_cols_x):
                        x = i * col_x
                        y_line = np.linspace(0, W, 50)
                        x_line = np.ones_like(y_line) * x
                        z_line = np.ones_like(y_line) * H
                        
                        beam_name = f"MB_X{i}"
                        if beam_name in design_checks:
                            status = design_checks[beam_name]['status']
                            unity = design_checks[beam_name]['unity_check']
                            if status == 'KHÔNG ĐẠT':
                                color = '#e74c3c'
                            elif unity > 0.8:
                                color = '#f39c12'
                            else:
                                color = '#27ae60'
                        else:
                            color = '#e74c3c'
                        
                        self.ax_3d.plot(x_line, y_line, z_line,
                                       color=color, linewidth=6, alpha=0.9,
                                       label='🔴 Dầm chính' if i==0 else '')
            
            # === DRAW SECONDARY BEAMS (BLUE) ===
            if self.chk_show_sec_beams.isChecked():
                main_dir = self.cbo_main_dir.currentText()
                if main_dir == 'X':
                    num_sec = int(col_x / sec_spacing)
                    for i in range(num_cols_x - 1):
                        for k in range(1, num_sec + 1):
                            x = i * col_x + k * sec_spacing
                            y_line = np.linspace(0, W, 30)
                            x_line = np.ones_like(y_line) * x
                            z_line = np.ones_like(y_line) * H
                            self.ax_3d.plot(x_line, y_line, z_line,
                                           color='#3498db', linewidth=3, alpha=0.7,
                                           label='🔵 Dầm phụ' if i==0 and k==1 else '')
                else:
                    num_sec = int(col_y / sec_spacing)
                    for j in range(num_cols_y - 1):
                        for k in range(1, num_sec + 1):
                            y = j * col_y + k * sec_spacing
                            x_line = np.linspace(0, L, 30)
                            y_line = np.ones_like(x_line) * y
                            z_line = np.ones_like(x_line) * H
                            self.ax_3d.plot(x_line, y_line, z_line,
                                           color='#3498db', linewidth=3, alpha=0.7,
                                           label='🔵 Dầm phụ' if j==0 and k==1 else '')
            
            # === DRAW DECK SURFACE (GRAY TRANSPARENT) ===
            if self.chk_show_deck.isChecked():
                x_deck = np.linspace(0, L, 30)
                y_deck = np.linspace(0, W, 30)
                X, Y = np.meshgrid(x_deck, y_deck)
                Z = np.ones_like(X) * (H + 0.05)
                
                self.ax_3d.plot_surface(X, Y, Z, alpha=0.2, color='#95a5a6',
                                       edgecolor='#7f8c8d', linewidth=0.3)
            
            # === STYLING ===
            self.ax_3d.set_xlabel('Chiều dài X (m)', fontsize=11, fontweight='bold', color='#2c3e50')
            self.ax_3d.set_ylabel('Chiều rộng Y (m)', fontsize=11, fontweight='bold', color='#2c3e50')
            self.ax_3d.set_zlabel('Chiều cao Z (m)', fontsize=11, fontweight='bold', color='#2c3e50')
            self.ax_3d.set_title('🏗 MÔ HÌNH 3D KẾT CẤU CHUYÊN NGHIỆP', 
                                fontsize=14, fontweight='bold', pad=20, color='#2c3e50')
            
            # Set limits
            self.ax_3d.set_xlim(0, L)
            self.ax_3d.set_ylim(0, W)
            self.ax_3d.set_zlim(0, H + 1)
            
            # Grid styling
            self.ax_3d.grid(True, alpha=0.2, linestyle='--')
            self.ax_3d.xaxis.pane.fill = False
            self.ax_3d.yaxis.pane.fill = False
            self.ax_3d.zaxis.pane.fill = False
            
            # Background color
            self.ax_3d.set_facecolor('#f5f7fa')
            
            # Legend
            self.ax_3d.legend(loc='upper right', fontsize=10, framealpha=0.95)
            
            # View angle
            self.ax_3d.view_init(elev=25, azim=45)
            
        except Exception as e:
            print(f"3D Error: {e}")
            self.ax_3d.text(0.5, 0.5, 0.5, 'Nhập thông số để xem mô hình',
                          ha='center', va='center', fontsize=12, color='red')
        
        self.canvas_3d.draw()
    
    def run_fem_analysis(self):
        """Run FEM analysis"""
        if not HAS_ADVANCED_FEATURES:
            QMessageBox.warning(self, "Thiếu thư viện",
                              "Vui lòng cài đặt PyNite và Plotly:\n\n" +
                              "pip install PyNite plotly")
            return
        
        try:
            # Build layout object
            from types import SimpleNamespace
            
            layout = SimpleNamespace(
                length=float(self.inp_length.text()),
                width=float(self.inp_width.text()),
                floor_height=float(self.inp_height.text()),
                column_spacing_x=float(self.inp_col_x.text()),
                column_spacing_y=float(self.inp_col_y.text()),
                main_beam_direction=self.cbo_main_dir.currentText(),
                secondary_beam_spacing=float(self.inp_sec_spacing.text())
            )
            
            # Build specs
            layout.column_spec = SimpleNamespace(
                h=float(self.inp_col_h.text()),
                b=float(self.inp_col_b.text()),
                tf=float(self.inp_col_tf.text()),
                tw=float(self.inp_col_tw.text()),
                area=0, ix=0, wx=0
            )
            
            # Calculate properties
            h_cm, b_cm = layout.column_spec.h/10, layout.column_spec.b/10
            tf_cm, tw_cm = layout.column_spec.tf/10, layout.column_spec.tw/10
            layout.column_spec.area = 2*b_cm*tf_cm + (h_cm-2*tf_cm)*tw_cm
            layout.column_spec.ix = (b_cm*h_cm**3/12) - ((b_cm-tw_cm)*(h_cm-2*tf_cm)**3/12)
            
            # Main beam
            layout.main_beam_spec = SimpleNamespace(
                h=float(self.inp_main_h.text()),
                b=float(self.inp_main_b.text()),
                tf=float(self.inp_main_tf.text()),
                tw=float(self.inp_main_tw.text()),
                area=0, ix=0, wx=0
            )
            
            h_cm, b_cm = layout.main_beam_spec.h/10, layout.main_beam_spec.b/10
            tf_cm, tw_cm = layout.main_beam_spec.tf/10, layout.main_beam_spec.tw/10
            layout.main_beam_spec.area = 2*b_cm*tf_cm + (h_cm-2*tf_cm)*tw_cm
            layout.main_beam_spec.ix = (b_cm*h_cm**3/12) - ((b_cm-tw_cm)*(h_cm-2*tf_cm)**3/12)
            
            # Secondary beam
            layout.secondary_beam_spec = SimpleNamespace(
                h=float(self.inp_sec_h.text()),
                b=float(self.inp_sec_b.text()),
                tf=float(self.inp_sec_tf.text()),
                tw=float(self.inp_sec_tw.text()),
                area=0, ix=0, wx=0
            )
            
            h_cm, b_cm = layout.secondary_beam_spec.h/10, layout.secondary_beam_spec.b/10
            tf_cm, tw_cm = layout.secondary_beam_spec.tf/10, layout.secondary_beam_spec.tw/10
            layout.secondary_beam_spec.area = 2*b_cm*tf_cm + (h_cm-2*tf_cm)*tw_cm
            layout.secondary_beam_spec.ix = (b_cm*h_cm**3/12) - ((b_cm-tw_cm)*(h_cm-2*tf_cm)**3/12)
            
            loads = {
                'live_load': float(self.inp_live.text()),
                'dead_load_finish': float(self.inp_dead.text())
            }
            
            self.layout_data = layout
            
            # Run analysis in background thread
            self.fem_thread = FEMAnalysisThread(layout, loads)
            self.fem_thread.finished.connect(self.on_fem_complete)
            self.fem_thread.error.connect(self.on_fem_error)
            self.fem_thread.start()
            
            self.fem_browser.setHtml("<h3>⏳ Đang phân tích FEM...</h3>")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi: {str(e)}")
    
    def on_fem_complete(self, results):
        """Handle FEM analysis completion"""
        self.fem_results = results
        
        # Update FEM tab
        self.fem_browser.setHtml(results.get('html_report', '<h3>Hoàn thành</h3>'))
        
        # Update Plotly tab
        if HAS_ADVANCED_FEATURES:
            self.update_plotly_diagrams()
        
        # Refresh 3D model with stress-based coloring
        self.draw_3d_model()
        
        # Show success with critical member warning
        max_def = results.get('max_deflection', {})
        critical = results.get('critical_members', {})
        failed_count = len(critical.get('failed_members', []))
        
        msg = f"<h3 style='color:green;'>✓ PHÂN TÍCH THÀNH CÔNG</h3>"
        msg += f"<p>Độ võng tối đa: <b>{max_def.get('value', 0):.2f} mm</b></p>"
        msg += f"<p>Tại nút: {max_def.get('node', 'N/A')}</p>"
        
        if failed_count > 0:
            msg += f"<hr><p style='color:red; font-weight:bold;'>⚠️ CẢN H BÁO: {failed_count} members KHÔNG ĐẠT</p>"
            msg += "<p>Xem tab 'Kết quả FEM' để biết chi tiết</p>"
            msg += "<p><b>Mô hình 3D:</b> Members màu đỏ cần tăng kích thước</p>"
        
        QMessageBox.information(self, "Phân tích hoàn thành", msg)
    
    def on_fem_error(self, error_msg):
        """Handle FEM analysis error"""
        QMessageBox.critical(self, "Lỗi phân tích", f"Lỗi FEM:\n{error_msg}")
        self.fem_browser.setHtml(f"<h3 style='color:red;'>Lỗi: {error_msg}</h3>")
    
    def update_plotly_diagrams(self):
        """Update Plotly interactive diagrams with detailed member-by-member views"""
        if not self.fem_results or not HAS_ADVANCED_FEATURES:
            return
        
        try:
            creator = StructuralDiagramCreator()
            
            # Create comprehensive dashboard
            fig = creator.create_complete_analysis_dashboard(self.fem_results, self.layout_data)
            
            # Add member comparison diagrams
            member_forces = self.fem_results.get('member_forces', {})
            
            if member_forces:
                # Create detailed member-specific plots
                main_beams = {k: v for k, v in member_forces.items() if k.startswith('MB')}
                
                if main_beams:
                    # Add individual beam diagrams in dropdown
                    from plotly.subplots import make_subplots
                    import plotly.graph_objects as go
                    
                    # Create detailed multi-member view
                    fig_detailed = make_subplots(
                        rows=3, cols=1,
                        subplot_titles=('📉 Biểu đồ Moment (kN·m)', '📊 Biểu đồ Shear (kN)', '📈 Biểu đồ Axial (kN)'),
                        vertical_spacing=0.1
                    )
                    
                    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
                    
                    for idx, (member_name, data) in enumerate(list(main_beams.items())[:6]):
                        positions = data['positions']
                        color = colors[idx % len(colors)]
                        
                        # Moment
                        fig_detailed.add_trace(
                            go.Scatter(x=positions, y=data['moment'],
                                     mode='lines', name=member_name, line=dict(color=color, width=2),
                                     hovertemplate=f'<b>{member_name}</b><br>x=%{{x:.2f}}m<br>M=%{{y:.2f}}kN·m<extra></extra>'),
                            row=1, col=1
                        )
                        
                        # Shear
                        fig_detailed.add_trace(
                            go.Scatter(x=positions, y=data['shear'],
                                     mode='lines', name=member_name, line=dict(color=color, width=2),
                                     showlegend=False,
                                     hovertemplate=f'<b>{member_name}</b><br>x=%{{x:.2f}}m<br>V=%{{y:.2f}}kN<extra></extra>'),
                            row=2, col=1
                        )
                        
                        # Axial
                        fig_detailed.add_trace(
                            go.Scatter(x=positions, y=data['axial'],
                                     mode='lines', name=member_name, line=dict(color=color, width=2),
                                     showlegend=False,
                                     hovertemplate=f'<b>{member_name}</b><br>x=%{{x:.2f}}m<br>N=%{{y:.2f}}kN<extra></extra>'),
                            row=3, col=1
                        )
                    
                    fig_detailed.update_xaxes(title_text='Vị trí (m)', row=3, col=1)
                    fig_detailed.update_yaxes(title_text='Moment (kN·m)', row=1, col=1)
                    fig_detailed.update_yaxes(title_text='Lực cắt (kN)', row=2, col=1)
                    fig_detailed.update_yaxes(title_text='Lực dọc (kN)', row=3, col=1)
                    
                    fig_detailed.update_layout(
                        title='📋 NỘI LỰC CHI TIẾT TỪNG DẦM CHÍNH',
                        height=900,
                        hovermode='x unified',
                        template='plotly_white',
                        showlegend=True
                    )
                    
                    # Combine both figures
                    html = f"""
                    <html>
                    <head>
                    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                    <style>
                        body {{ font-family: 'Segoe UI'; margin: 0; padding: 20px; background: #f5f7fa; }}
                        h2 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                        .chart-container {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                    </style>
                    </head>
                    <body>
                    <h2>📊 TỔNG QUAN PHÂN TÍCH</h2>
                    <div class="chart-container">
                    {fig.to_html(include_plotlyjs=False, div_id='dashboard')}
                    </div>
                    <h2>🔍 CHI TIẾT NỘI LỰC TỪNG DẦM</h2>
                    <div class="chart-container">
                    {fig_detailed.to_html(include_plotlyjs=False, div_id='detailed')}
                    </div>
                    </body>
                    </html>
                    """
                else:
                    html = fig.to_html(include_plotlyjs='cdn')
            else:
                html = fig.to_html(include_plotlyjs='cdn')
            
            self.plotly_view.setHtml(html)
            
        except Exception as e:
            import traceback
            print(f"Plotly error: {e}")
            print(traceback.format_exc())
    
    def export_plotly_html(self):
        """Export Plotly diagrams to HTML"""
        if self.fem_results and HAS_ADVANCED_FEATURES:
            try:
                creator = StructuralDiagramCreator()
                fig = creator.create_complete_analysis_dashboard(self.fem_results, self.layout_data)
                
                filename = "fem_analysis_results.html"
                fig.write_html(filename)
                
                QMessageBox.information(self, "Xuất thành công",
                                      f"Đã xuất ra file: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi xuất: {str(e)}")
