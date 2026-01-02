# -*- coding: utf-8 -*-
"""
RC Column Module
Interaction Diagrams using concreteproperties
"""

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
                             QLineEdit, QPushButton, QLabel, QSplitter, QMessageBox, QScrollArea,
                             QTabWidget, QTextBrowser)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QFont

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False

# Library imports
try:
    from concreteproperties.material import Concrete, SteelBar
    from concreteproperties.stress_strain_profile import ConcreteLinear, RectangularStressBlock, SteelElasticPlastic
    from concreteproperties.concrete_section import ConcreteSection
    from sectionproperties.pre.library.concrete_sections import concrete_rectangular_section
    HAS_CP = True
except ImportError:
    HAS_CP = False

# Import Report Generator
from steeldeckfem.core.rc_report_generator import RCReportGenerator
import webbrowser
import os


class RCAnalysisThread(QThread):
    """Background thread for Interaction Diagram calculation"""
    finished = pyqtSignal(object) # Returns the interaction result object
    error = pyqtSignal(str)
    
    def __init__(self, params):
        super().__init__()
        self.params = params
        
    def run(self):
        try:
            # 1. Materials
            conc_E = 4700 * (self.params['fc'] ** 0.5) # ACI approx
            conc_profile = ConcreteLinear(elastic_modulus=conc_E)
            conc_ultimate = RectangularStressBlock(
                compressive_strength=self.params['fc'], 
                alpha=0.85, 
                gamma=0.85, 
                ultimate_strain=0.003
            )
            
            steel_profile = SteelElasticPlastic(
                yield_strength=self.params['fy'], 
                elastic_modulus=200000, 
                fracture_strain=0.05
            )
            
            concrete = Concrete(
                name=f"C{self.params['fc']}",
                density=2.4e-6,
                stress_strain_profile=conc_profile,
                ultimate_stress_strain_profile=conc_ultimate,
                flexural_tensile_strength=0.6 * (self.params['fc']**0.5),
                colour='lightgrey'
            )
            
            steel = SteelBar(
                name=f"Grade {self.params['fy']}",
                density=7.85e-6,
                stress_strain_profile=steel_profile,
                colour='grey'
            )
            
            # 2. Geometry
            # concrete_rectangular_section signature:
            # (b, d, dia_top, n_top, dia_bot, n_bot, dia_side, n_side, c_top, c_bot, c_side, ...)
            
            geom = concrete_rectangular_section(
                b=self.params['b'], 
                d=self.params['h'],
                dia_top=self.params['d_bar'], 
                n_top=self.params['n_top'],
                dia_bot=self.params['d_bar'], 
                n_bot=self.params['n_bot'],
                dia_side=self.params['d_bar'], 
                n_side=self.params['n_side'],
                c_top=self.params['cover'], 
                c_bot=self.params['cover'], 
                c_side=self.params['cover'],
                area_top=self.params['bar_area'], 
                area_bot=self.params['bar_area'], 
                area_side=self.params['bar_area'],
                conc_mat=concrete, 
                steel_mat=steel
            )
            
            # 3. Create Mesh & Section
            # Optimize: Set max_area to avoid excessively fine mesh (Slow performance fix)
            # For a 300x400 col, area = 120,000. 100 elements -> 1200 mm2.
            # Let's target ~200 concrete elements for speed.
            target_elements = 150
            total_area = self.params['b'] * self.params['h']
            mesh_area = total_area / target_elements
            
            geom.create_mesh(mesh_area=mesh_area)
            sec = ConcreteSection(geom)
            
            # 4. Analysis
            mi_res = sec.moment_interaction_diagram()
            self.finished.emit(mi_res)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))


class RCColumnModule(QWidget):
    """
    Module: Reinforced Concrete Column Design
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Inputs
        left_panel = self.create_input_panel()
        splitter.addWidget(left_panel)
        
        # Right: Output (Diagram)
        right_panel = self.create_output_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        
    def create_input_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("🏛 THIẾT KẾ CỘT BTCT")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #7f8c8d; color: white; padding: 10px; border-radius: 5px;")
        layout.addWidget(title)
        
        # 1. Properties
        gb_mat = QGroupBox("1. VẬT LIỆU & TIẾT DIỆN")
        form_mat = QFormLayout()
        
        self.inp_fc = QLineEdit("30") # MPa
        self.inp_fy = QLineEdit("400") # MPa
        self.inp_b = QLineEdit("300") # mm
        self.inp_h = QLineEdit("400") # mm
        self.inp_cover = QLineEdit("30") # mm
        
        form_mat.addRow("Bê tông f'c (MPa):", self.inp_fc)
        form_mat.addRow("Thép fy (MPa):", self.inp_fy)
        form_mat.addRow("Rộng B (mm):", self.inp_b)
        form_mat.addRow("Cao H (mm):", self.inp_h)
        form_mat.addRow("Lớp bảo vệ (mm):", self.inp_cover)
        gb_mat.setLayout(form_mat)
        layout.addWidget(gb_mat)
        
        # 2. Reinforcement
        gb_rebar = QGroupBox("2. CỐT THÉP")
        form_rebar = QFormLayout()
        
        self.inp_d_bar = QLineEdit("20") # mm
        self.inp_n_top = QLineEdit("3")
        self.inp_n_bot = QLineEdit("3")
        self.inp_n_side = QLineEdit("0") # per side
        
        form_rebar.addRow("Đường kính (mm):", self.inp_d_bar)
        form_rebar.addRow("Số thanh lớp trên:", self.inp_n_top)
        form_rebar.addRow("Số thanh lớp dưới:", self.inp_n_bot)
        form_rebar.addRow("Số thanh lớp bên (mỗi bên):", self.inp_n_side)
        gb_rebar.setLayout(form_rebar)
        layout.addWidget(gb_rebar)
        
        # Button
        btn_calc = QPushButton("⚡ VẼ BIỂU ĐỒ TƯƠNG TÁC")
        btn_calc.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50; color: white;
                font-size: 14px; font-weight: bold; padding: 15px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #34495e; }
        """)
        btn_calc.clicked.connect(self.run_analysis)
        layout.addWidget(btn_calc)
        
        # Export Button
        btn_report = QPushButton("📝 XUẤT THUYẾT MINH (HTML)")
        btn_report.setStyleSheet("""
            QPushButton {
                background-color: #e67e22; color: white;
                font-size: 14px; font-weight: bold; padding: 10px; border-radius: 6px; margin-top: 5px;
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        btn_report.clicked.connect(self.export_report)
        layout.addWidget(btn_report)
        
        layout.addStretch()
        return panel
        
    def create_output_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        self.tabs = QTabWidget()
        
        # Tab 1: Diagram
        self.tab_diagram = QWidget()
        layout_diag = QVBoxLayout(self.tab_diagram)
        self.fig = Figure(figsize=(8, 6), facecolor='#ffffff')
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        layout_diag.addWidget(self.canvas)
        self.tabs.addTab(self.tab_diagram, "📊 Biểu đồ Tương tác")
        
        # Tab 2: Report
        self.tab_report = QWidget()
        layout_report = QVBoxLayout(self.tab_report)
        
        if HAS_WEBENGINE:
            self.report_view = QWebEngineView()
        else:
            self.report_view = QTextBrowser()
            
        layout_report.addWidget(self.report_view)
        self.tabs.addTab(self.tab_report, "📝 Thuyết minh Tính toán")
        
        layout.addWidget(self.tabs)
        return panel
        
    def run_analysis(self):
        if not HAS_CP:
            QMessageBox.warning(self, "Thiếu thư viện", "Cần cài đặt: concreteproperties")
            return
            
        try:
            # Parse inputs
            d = float(self.inp_d_bar.text())
            area = 3.14159 * (d/2)**2
            
            params = {
                'fc': float(self.inp_fc.text()),
                'fy': float(self.inp_fy.text()),
                'b': float(self.inp_b.text()),
                'h': float(self.inp_h.text()),
                'cover': float(self.inp_cover.text()),
                'd_bar': d,
                'bar_area': area,
                'n_top': int(self.inp_n_top.text()),
                'n_bot': int(self.inp_n_bot.text()),
                'n_side': int(self.inp_n_side.text())
            }
            
            # Validation
            if params['b'] <= 0 or params['h'] <= 0 or params['fc'] <= 0 or params['fy'] <= 0:
                QMessageBox.warning(self, "Lỗi nhập liệu", "Kích thước và vật liệu phải lớn hơn 0.")
                return
            
            # Disable button to prevent double-click crash
            self.sender().setEnabled(False) 
            self.running_btn = self.sender() # Store reference
            
            self.ax.clear()
            self.ax.text(0.5, 0.5, "Đang tính toán...", ha='center', va='center')
            self.canvas.draw()
            
            self.thread = RCAnalysisThread(params)
            self.thread.finished.connect(self.on_complete)
            self.thread.error.connect(self.on_error)
            self.thread.start()
            
        except ValueError:
            QMessageBox.critical(self, "Lỗi", "Vui lòng kiểm tra số liệu nhập vào")
            
    def on_complete(self, mi_res):
        if hasattr(self, 'running_btn'): self.running_btn.setEnabled(True)
        self.ax.clear()
        
        # ... (rest of code)

    def on_error(self, msg):
        if hasattr(self, 'running_btn'): self.running_btn.setEnabled(True)
        QMessageBox.critical(self, "Lỗi Analysis", msg)
        self.ax.clear()
        self.canvas.draw()

    def export_report(self):
        """Generate and show calculation report"""
        try:
            # Gather params (same as run_analysis)
            d = float(self.inp_d_bar.text())
            area = 3.14159 * (d/2)**2
            
            params = {
                'fc': float(self.inp_fc.text()),
                'fy': float(self.inp_fy.text()),
                'b': float(self.inp_b.text()),
                'h': float(self.inp_h.text()),
                'cover': float(self.inp_cover.text()),
                'd_bar': d,
                'bar_area': area,
                'n_top': int(self.inp_n_top.text()),
                'n_bot': int(self.inp_n_bot.text()),
                'n_side': int(self.inp_n_side.text())
            }
            
            # Generate
            path = RCReportGenerator.generate_report(params)
            
            # Load into viewer
            abs_path = os.path.abspath(path).replace('\\', '/')
            if HAS_WEBENGINE:
                self.report_view.setUrl(QUrl(f"file:///{abs_path}"))
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    self.report_view.setHtml(f.read())
            
            # Switch to report tab
            self.tabs.setCurrentWidget(self.tab_report)
            
            # Optional: Don't force open browser if viewed internally, but give option
            # reply = QMessageBox.question(self, "Xuất thành công", 
            #                            f"Đã tạo report. Bạn có muốn mở file gốc không?",
            #                            QMessageBox.Yes | QMessageBox.No)
            #                            
            # if reply == QMessageBox.Yes:
            #     webbrowser.open(f"file:///{path.replace(os.sep, '/')}")
                
        except ValueError:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Vui lòng kiểm tra các thông số đầu vào trước khi xuất báo cáo.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tạo báo cáo: {str(e)}")
