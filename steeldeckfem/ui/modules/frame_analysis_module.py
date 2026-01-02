# -*- coding: utf-8 -*-
"""
Frame Analysis Module
Using anastruct for 2D Frame Analysis
"""

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
                             QLineEdit, QPushButton, QLabel, QSplitter, QMessageBox, QComboBox,
                             QTabWidget, QTextBrowser)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QFont

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False

from steeldeckfem.core.frame_dxf_exporter import FrameDXFExporter
from steeldeckfem.core.frame_report_generator import FrameReportGenerator
import os

try:
    from anastruct import SystemElements
    HAS_ANASTRUCT = True
except ImportError:
    HAS_ANASTRUCT = False

class FrameAnalysisWorker(QThread):
    """Background worker for frame analysis"""
    finished = pyqtSignal(object) # Returns the SystemElements object
    error = pyqtSignal(str)
    
    def __init__(self, params):
        super().__init__()
        self.params = params
        
    def run(self):
        try:
            ss = SystemElements()
            
            L = self.params['L']
            H = self.params['H']
            q = self.params['q']
            
            # Simple Portal Frame
            # Node 1 (0,0) -> Node 2 (0, H)
            ss.add_element(location=[[0, 0], [0, H]])
            # Node 2 (0, H) -> Node 3 (L, H)
            ss.add_element(location=[[0, H], [L, H]])
            # Node 3 (L, H) -> Node 4 (L, 0)
            ss.add_element(location=[[L, H], [L, 0]])
            
            # Supports
            if self.params['support'] == 'Fixed':
                ss.add_support_fixed(node_id=1)
                ss.add_support_fixed(node_id=4)
            else: # Pinned
                ss.add_support_hinged(node_id=1)
                ss.add_support_hinged(node_id=4)
                
            # Loads (on beam - element 2)
            ss.q_load(element_id=2, q=-q)
            
            # Solve
            ss.solve()
            
            self.finished.emit(ss)
            
        except Exception as e:
            self.error.emit(str(e))

class FrameAnalysisModule(QWidget):
    """
    Module: 2D Frame Analysis (Portal Frame MVP)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ss = None # SystemElements object
        self.init_ui()
        
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.create_input_panel())
        splitter.addWidget(self.create_output_panel())
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        
    def create_input_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        title = QLabel("🕸 PHÂN TÍCH NỘI LỰC (FEM)")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #8e44ad; color: white; padding: 10px; border-radius: 5px;")
        layout.addWidget(title)
        
        lbl_info = QLabel("<i>(*) Phân tích đàn hồi tuyến tính. Dùng cho cả BTCT và Kết cấu thép để tìm M, N, V, Chuyển vị.</i>")
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet("color: #555; font-size: 11px; margin-bottom: 5px;")
        layout.addWidget(lbl_info)
        
        gb_geom = QGroupBox("1. HÌNH HỌC & TẢI TRỌNG (Khung Portal)")
        form = QFormLayout()
        
        self.inp_L = QLineEdit("6.0")
        self.inp_H = QLineEdit("4.0")
        self.inp_q = QLineEdit("10.0") # kN/m
        self.cbo_support = QComboBox()
        self.cbo_support.addItems(["Fixed", "Pinned"])
        
        form.addRow("Nhịp L (m):", self.inp_L)
        form.addRow("Cao H (m):", self.inp_H)
        form.addRow("Tải phân bố đều q (kN/m):", self.inp_q)
        form.addRow("Liên kết chân cột:", self.cbo_support)
        gb_geom.setLayout(form)
        layout.addWidget(gb_geom)
        
        btn_calc = QPushButton("⚡ TÍNH TOÁN")
        btn_calc.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad; color: white;
                font-size: 14px; font-weight: bold; padding: 15px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #9b59b6; }
        """)
        btn_calc.clicked.connect(self.run_analysis)
        layout.addWidget(btn_calc)
        
        # Export DXF
        btn_dxf = QPushButton("📐 XUẤT CAD (DXF)")
        btn_dxf.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                font-size: 14px; font-weight: bold; padding: 10px; border-radius: 6px; margin-top: 5px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        btn_dxf.clicked.connect(self.export_dxf)
        layout.addWidget(btn_dxf)

        # Export Report
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
        
        self.fig = Figure(figsize=(8, 6), facecolor='#ffffff')
        self.canvas = FigureCanvas(self.fig)
        
        layout.addWidget(self.canvas)
        return panel
        
    def run_analysis(self):
        if not HAS_ANASTRUCT:
            QMessageBox.warning(self, "Thiếu thư viện", "Cần cài đặt: anastruct")
            return
            
        try:
            params = {
                'L': float(self.inp_L.text()),
                'H': float(self.inp_H.text()),
                'q': float(self.inp_q.text()),
                'support': self.cbo_support.currentText()
            }
            
            self.fig.clear()
            ax = self.fig.add_subplot(111)
            ax.text(0.5, 0.5, "Đang tính toán...", ha='center')
            self.canvas.draw()
            
            # Disable button
            self.sender().setEnabled(False)
            self.running_btn = self.sender()
            
            self.worker = FrameAnalysisWorker(params)
            self.worker.finished.connect(self.on_complete)
            self.worker.error.connect(self.on_error)
            self.worker.start()
            
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Kiểm tra số liệu nhập")
            
    def on_complete(self, ss):
        if hasattr(self, 'running_btn'): self.running_btn.setEnabled(True)
        self.ss = ss
        self.update_plot()
        
    def on_error(self, msg):
        if hasattr(self, 'running_btn'): self.running_btn.setEnabled(True)
        QMessageBox.critical(self, "Lỗi Analysis", msg)
        
    def update_plot(self):
        if not self.ss:
            return
            
        view_mode = self.cbo_view.currentText()
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        try:
            if view_mode == "Kết cấu":
                self.ss.show_structure(show=False, ax=ax)
            elif view_mode == "Biểu đồ Moment":
                self.ss.show_bending_moment(show=False, ax=ax)
            elif view_mode == "Biểu đồ Lực cắt":
                self.ss.show_shear_force(show=False, ax=ax)
            elif view_mode == "Biểu đồ Lực dọc":
                self.ss.show_axial_force(show=False, ax=ax)
            elif view_mode == "Chuyển vị":
                self.ss.show_displacement(show=False, ax=ax)
                
            ax.set_title(view_mode)
            ax.grid(True, linestyle='--', alpha=0.3)
            self.canvas.draw()
        except Exception as e:
            QMessageBox.warning(self, "Plot Error", f"Lỗi hiển thị biểu đồ:\n{str(e)}")
            self.fig.clear()
            ax = self.fig.add_subplot(111)
            ax.text(0.5, 0.5, "Lỗi hiển thị", ha='center', color='red')
            self.canvas.draw()
            
    def export_dxf(self):
        """Export current frame to DXF"""
        if not self.ss:
            QMessageBox.warning(self, "Chưa có dữ liệu", "Vui lòng chạy tính toán trước khi xuất.")
            return
            
        try:
            params = {
                'L': float(self.inp_L.text()),
                'H': float(self.inp_H.text())
            }
            
            os.makedirs("exports", exist_ok=True)
            filename = FrameDXFExporter.export(self.ss, params)
            
            QMessageBox.information(self, "Xuất thành công", f"Đã xuất file tại:\n{os.path.abspath(filename)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi Export", str(e))

    def export_report(self):
        """Export frame analysis report"""
        try:
            params = {
                'L': float(self.inp_L.text()),
                'H': float(self.inp_H.text()),
                'q': float(self.inp_q.text()),
                'support': self.cbo_support.currentText()
            }
            
            # Generate
            import webbrowser
            from steeldeckfem.core.frame_report_generator import FrameReportGenerator
            
            path = FrameReportGenerator.generate_report(params)
            
            # Load into viewer
            abs_path = os.path.abspath(path).replace('\\', '/')
            if HAS_WEBENGINE:
                self.report_view.setUrl(QUrl(f"file:///{abs_path}"))
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    self.report_view.setHtml(f.read())
                    
            # Switch to report tab
            self.tabs.setCurrentWidget(self.tab_report)
                
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Kiểm tra số liệu nhập")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi Report", str(e))

