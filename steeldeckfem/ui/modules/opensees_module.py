# -*- coding: utf-8 -*-
"""
OpenSeesPy Module
Modal Analysis (Eigenvalue)
"""

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

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

try:
    import openseespy.opensees as ops
    HAS_OPENSEES = True
except (ImportError, RuntimeError) as e:
    HAS_OPENSEES = False
    print(f"OpenSees warning: {e}")

class OpenSeesWorker(QThread):
    """Background worker for OpenSees analysis"""
    finished = pyqtSignal(object) # Returns results dict
    error = pyqtSignal(str)
    
    def __init__(self, params):
        super().__init__()
        self.params = params
        
    def run(self):
        if not HAS_OPENSEES:
            self.error.emit("OpenSeesPy not installed")
            return

        try:
            # Clear existing model
            ops.wipe()
            
            # Model definition
            ops.model('basic', '-ndm', 2, '-ndf', 3)
            
            num_stories = self.params['stories']
            num_bays = self.params['bays']
            bay_width = self.params['bay_width'] # m
            story_height = self.params['story_height'] # m
            
            # Material properties
            E = self.params['E'] * 1e6 # MPa to Pa -> kN/m2 (input usually MPa, let's assume input is kN/m2 or MPa?)
            # Let's standardize input: 
            # E in GPa -> * 1e6 to kPa (kN/m2)? No.
            # Let's assume input units consistent. 
            # Recommended: kN, m. 
            # E = 200 GPa = 2e8 kN/m2.
            
            E = self.params['E'] # Input in kN/m2
            Ac = self.params['Ac']
            Ic = self.params['Ic']
            Ab = self.params['Ab']
            Ib = self.params['Ib']
            mass = self.params['mass'] # ton (Mg) -> Mass unit constraint.
            # In OpenSees, Force = Mass * Acc.
            # If Force in kN, L in m, Time in s.
            # Acc = m/s2. Mass = Force / Acc = kN / (m/s2) = ton.
            # So input mass in ton is correct if output is kN.
            
            # 1. Nodes
            # Grid: x = 0 to num_bays * W, y = 0 to num_stories * H
            node_map = {} # (i, j) -> node_id
            node_id_counter = 1
            
            for j in range(num_stories + 1): # y levels (0 to stories)
                for i in range(num_bays + 1): # x grid (0 to bays)
                    tag = node_id_counter
                    x = i * bay_width
                    y = j * story_height
                    ops.node(tag, x, y)
                    
                    # Fix base
                    if j == 0:
                        ops.fix(tag, 1, 1, 1)
                    else:
                        # Assign mass to story nodes
                        # Simple lumped mass: Total story mass / (num_bays + 1)
                        # Or just horizontal mass? Usually horizontal.
                        m_node = mass / (num_bays + 1)
                        ops.mass(tag, m_node, 1e-9, 1e-9) # x, y, rot (negligible)
                        
                    node_map[(i,j)] = tag
                    node_id_counter += 1
            
            # 2. Elements (ElasticBeamColumn)
            transf_tag = 1
            ops.geomTransf('Linear', transf_tag)
            
            ele_tag = 1
            # Columns
            for i in range(num_bays + 1):
                for j in range(num_stories):
                    n1 = node_map[(i, j)]
                    n2 = node_map[(i, j+1)]
                    ops.element('elasticBeamColumn', ele_tag, n1, n2, Ac, E, Ic, transf_tag)
                    ele_tag += 1
                    
            # Beams
            for j in range(1, num_stories + 1):
                for i in range(num_bays):
                    n1 = node_map[(i, j)]
                    n2 = node_map[(i+1, j)]
                    ops.element('elasticBeamColumn', ele_tag, n1, n2, Ab, E, Ib, transf_tag)
                    ele_tag += 1
                    
            # 3. Eigen Analysis
            num_modes = 3
            if num_modes > (num_stories * (num_bays+1)):
                num_modes = num_stories # Limit modes if small model
                
            eigen_vals = ops.eigen(num_modes)
            
            results = {
                'periods': [],
                'modes': [],
                'structure': {
                    'stories': num_stories,
                    'bays': num_bays,
                    'H': story_height,
                    'L': bay_width
                }
            }
            
            for lam in eigen_vals:
                w = lam ** 0.5
                T = 2 * 3.14159 / w
                results['periods'].append(T)
                
            # Record Mode Shapes
            for mode_idx in range(len(eigen_vals)):
                mode_data = {} # node_id -> [dx, dy]
                # OpenSees eigen command computes modes, but to get them we assume they are stored.
                # Actually need to reference documentation. 
                # 'nodeEigenvector' returns eigenvector at a node.
                
                mode_nodes = {}
                for j in range(num_stories + 1):
                    for i in range(num_bays + 1):
                        tag = node_map[(i, j)]
                        # Mode i (1-based for command?) No, lam index corresponds to mode.
                        # nodeEigenvector node modeDOF
                        # mode is 1-based index of the computed eigenvalues
                        dx = ops.nodeEigenvector(tag, mode_idx + 1, 1) # Mode shape X
                        dy = ops.nodeEigenvector(tag, mode_idx + 1, 2) # Mode shape Y
                        mode_nodes[(i, j)] = (dx, dy)
                
                results['modes'].append(mode_nodes)
                
            self.finished.emit(results)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))
        finally:
            ops.wipe()


class OpenSeesModule(QWidget):
    """
    Module: OpenSeesPy Modal Analysis
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.results = None
        
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
        
        title = QLabel("🌊 PHÂN TÍCH ĐỘNG ĐẤT (MODAL)")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #2c3e50; color: white; padding: 10px; border-radius: 5px;")
        layout.addWidget(title)
        
        # Geometry
        gb_geo = QGroupBox("1. HÌNH HỌC")
        form_geo = QFormLayout()
        
        self.inp_stories = QLineEdit("5")
        self.inp_bays = QLineEdit("3")
        self.inp_h = QLineEdit("3.5") # m
        self.inp_l = QLineEdit("6.0") # m
        
        form_geo.addRow("Số tầng:", self.inp_stories)
        form_geo.addRow("Số nhịp:", self.inp_bays)
        form_geo.addRow("Chiều cao tầng (m):", self.inp_h)
        form_geo.addRow("Chiều rộng nhịp (m):", self.inp_l)
        gb_geo.setLayout(form_geo)
        layout.addWidget(gb_geo)
        
        # Properties
        gb_prop = QGroupBox("2. ĐẶC TRƯNG & KHỐI LƯỢNG")
        form_prop = QFormLayout()
        
        self.inp_mass = QLineEdit("50") # ton/story
        self.inp_E = QLineEdit("20000000") # kN/m2 (20 GPa?) approx conc
        # 30 GPa = 30,000 MPa = 30,000,000 kPa (kN/m2)
        
        self.inp_Ic = QLineEdit("0.0054") # Column I (m4) 40x40 -> 0.4^4/12 = 0.0021
        self.inp_Ac = QLineEdit("0.16") # Column A (m2)
        self.inp_Ib = QLineEdit("0.0054") # Beam I (m4)
        self.inp_Ab = QLineEdit("0.16") # Beam A (m2)
        
        form_prop.addRow("Khối lượng tầng (tấn):", self.inp_mass)
        form_prop.addRow("Mô đun E (kN/m²):", self.inp_E)
        form_prop.addRow("Inertia Cột (m⁴):", self.inp_Ic)
        form_prop.addRow("Diện tích Cột (m²):", self.inp_Ac)
        form_prop.addRow("Inertia Dầm (m⁴):", self.inp_Ib)
        form_prop.addRow("Diện tích Dầm (m²):", self.inp_Ab)
        gb_prop.setLayout(form_prop)
        layout.addWidget(gb_prop)
        
        # Run
        btn_run = QPushButton("⚡ CHẠY PHÂN TÍCH MODE")
        btn_run.setStyleSheet("""
            QPushButton {
                background-color: #c0392b; color: white;
                font-size: 14px; font-weight: bold; padding: 15px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #e74c3c; }
        """)
        btn_run.clicked.connect(self.run_analysis)
        layout.addWidget(btn_run)
        
        if not HAS_OPENSEES:
            btn_run.setEnabled(False)
            btn_run.setText("⚠ OpenSees không khả dụng")
            btn_run.setToolTip("Cần cài đặt thư viện openseespy và Visual C++ Redistributable")
            btn_run.setStyleSheet("background-color: #95a5a6; color: white; padding: 15px; border-radius: 6px;")
        
        # Mode selector (hidden initially)
        self.cbo_mode = QComboBox()
        self.cbo_mode.currentTextChanged.connect(self.plot_mode)
        layout.addWidget(QLabel("Chọn Mode hiển thị:"))
        layout.addWidget(self.cbo_mode)
        
        layout.addStretch()
        return panel
        
    def create_output_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        self.tabs = QTabWidget()
        
        # Tab 1: Mode Shapes
        self.tab_modes = QWidget()
        layout_modes = QVBoxLayout(self.tab_modes)
        
        self.fig = Figure(figsize=(8, 6), facecolor='#ffffff')
        self.canvas = FigureCanvas(self.fig)
        layout_modes.addWidget(self.canvas)
        
        self.tabs.addTab(self.tab_modes, "🌊 Mode Vô hướng")
        
        # Tab 2: Report
        self.tab_report = QWidget()
        layout_report = QVBoxLayout(self.tab_report)
        
        if HAS_WEBENGINE:
            self.report_view = QWebEngineView()
        else:
            self.report_view = QTextBrowser()
            
        layout_report.addWidget(self.report_view)
        
        # Report Button
        btn_report = QPushButton("📝 Cập nhật Thuyết minh")
        btn_report.clicked.connect(self.generate_report)
        layout_report.addWidget(btn_report)
        
        self.tabs.addTab(self.tab_report, "📝 Thuyết minh Tính toán")
        
        layout.addWidget(self.tabs)
        return panel

    def generate_report(self):
        """Generate HTML report for Modal Analysis"""
        if not self.results:
            QMessageBox.warning(self, "Chưa có kết quả", "Vui lòng chạy phân tích trước.")
            return
            
        try:
            periods = self.results['periods']
            geo = self.results['structure']
            
            # Simple HTML generation
            rows = ""
            for i, T in enumerate(periods):
                f = 1/T
                w = 2*3.14159/T
                rows += f"<tr><td>{i+1}</td><td>{T:.4f}</td><td>{f:.4f}</td><td>{w:.4f}</td></tr>"
                
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI'; padding: 20px; }}
                    h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
                    th {{ background-color: #2980b9; color: white; }}
                    tr:nth-child(even) {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <h1>Kết quả Phân tích Dao động (Modal Analysis)</h1>
                <p><b>Dự án:</b> VietStructFEM - Advanced Analysis</p>
                <p><b>Mô hình:</b> Khung phẳng {geo['stories']} tầng, {geo['bays']} nhịp.</p>
                
                <h2>Bảng Tổng hợp Chu kỳ & Tần số</h2>
                <table>
                    <tr>
                        <th>Mode</th>
                        <th>Chu kỳ T (s)</th>
                        <th>Tần số f (Hz)</th>
                        <th>Tần số góc ω (rad/s)</th>
                    </tr>
                    {rows}
                </table>
                <p><i>(*) Phân tích trị riêng (Eigenvalue Analysis) sử dụng thư viện OpenSeesPy.</i></p>
            </body>
            </html>
            """
            
            import os
            output_path = os.path.abspath("reports/opensees_report.html")
            os.makedirs("reports", exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            abs_path = output_path.replace('\\', '/')
            if HAS_WEBENGINE:
                self.report_view.setUrl(QUrl(f"file:///{abs_path}"))
            else:
                self.report_view.setHtml(html_content)
                
            self.tabs.setCurrentWidget(self.tab_report)
            
        except Exception as e:
            QMessageBox.warning(self, "Lỗi Report", str(e))
        
    def run_analysis(self):
        if not HAS_OPENSEES:
            QMessageBox.warning(self, "Thiếu thư viện", "Chưa cài đặt openseespy")
            return
            
        try:
            params = {
                'stories': int(self.inp_stories.text()),
                'bays': int(self.inp_bays.text()),
                'story_height': float(self.inp_h.text()),
                'bay_width': float(self.inp_l.text()),
                'mass': float(self.inp_mass.text()),
                'E': float(self.inp_E.text()),
                'Ic': float(self.inp_Ic.text()),
                'Ac': float(self.inp_Ac.text()),
                'Ib': float(self.inp_Ib.text()),
                'Ab': float(self.inp_Ab.text())
            }
            
            self.fig.clear()
            ax = self.fig.add_subplot(111)
            ax.text(0.5, 0.5, "Đang chạy OpenSees...", ha='center')
            self.canvas.draw()
            
            self.worker = OpenSeesWorker(params)
            self.worker.finished.connect(self.on_complete)
            self.worker.error.connect(self.on_error)
            self.worker.start()
            
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Kiểm tra số liệu nhập")
            
    def on_complete(self, results):
        self.results = results
        self.cbo_mode.clear()
        
        periods = results['periods']
        items = [f"Mode {i+1} (T = {t:.3f}s)" for i, t in enumerate(periods)]
        self.cbo_mode.addItems(items)
        
        # Auto plot first mode
        self.plot_mode()
        
        # Auto generate report
        self.generate_report()
        
    def on_error(self, msg):
        QMessageBox.critical(self, "Lỗi", msg)
        
    def plot_mode(self):
        if not self.results:
            return
            
        current_idx = self.cbo_mode.currentIndex()
        if current_idx < 0: return
        
        mode_shape = self.results['modes'][current_idx]
        geo = self.results['structure']
        
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        scale = 5.0 # Scale factor for visualization
        
        # Plot Original (Grey dashed) and Deformed (Red solid)
        for j in range(geo['stories'] + 1):
            for i in range(geo['bays'] + 1):
                # Node Coords Original
                x0 = i * geo['L']
                y0 = j * geo['H']
                
                # Deformed
                dx, dy = mode_shape.get((i, j), (0, 0))
                x1 = x0 + dx * scale
                y1 = y0 + dy * scale
                
                # Beams (Connect to i+1)
                if i < geo['bays']:
                    x_next = (i+1) * geo['L']
                    y_next = y0
                    
                    dx_next, dy_next = mode_shape.get((i+1, j), (0, 0))
                    
                    # Original
                    ax.plot([x0, x_next], [y0, y_next], 'k--', alpha=0.3)
                    # Deformed
                    ax.plot([x1, x_next + dx_next*scale], [y1, y_next + dy_next*scale], 'b-', linewidth=2)
                    
                # Columns (Connect to j+1)
                if j < geo['stories']:
                    x_next = x0
                    y_next = (j+1) * geo['H']
                    
                    dx_next, dy_next = mode_shape.get((i, j+1), (0, 0))
                    
                    # Original
                    ax.plot([x0, x_next], [y0, y_next], 'k--', alpha=0.3)
                    # Deformed
                    ax.plot([x1, x_next + dx_next*scale], [y1, y_next + dy_next*scale], 'r-', linewidth=2)
                    
        ax.set_title(self.cbo_mode.currentText())
        ax.set_aspect('equal')
        ax.grid(True)
        self.canvas.draw()
