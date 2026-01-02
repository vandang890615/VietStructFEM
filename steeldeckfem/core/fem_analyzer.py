"""
PyNite FEM Analyzer for Steel Deck Floor Systems
Provides finite element analysis for columns, beams, and deck structures
"""

from Pynite import FEModel3D
import numpy as np
from typing import Dict, List, Tuple, Any


class FloorSystemFEMAnalyzer:
    """
    Finite Element Analysis for complete floor systems using PyNite
    """
    
    def __init__(self):
        self.model = None
        self.results = {}
        
    def build_fem_model(self, layout, loads: Dict) -> FEModel3D:
        """
        Build PyNite FEM model from floor system layout
        
        Args:
            layout: FloorSystemLayout object with system parameters
            loads: Dictionary with 'live_load' and 'dead_load_finish' in kg/m²
            
        Returns:
            FEModel3D: Configured PyNite model ready for analysis
        """
        # Create new model
        self.model = FEModel3D()
        
        # Define material properties (Steel)
        E = 200e6  # kN/m² (200 GPa)
        G = 77e6   # kN/m² (77 GPa)
        nu = 0.3   # Poisson's ratio
        rho = 7850 # kg/m³
        
        # Convert loads to kN/m²
        live_load_kn = loads.get('live_load', 400) / 100  # kg/m² to kN/m²
        dead_load_kn = loads.get('dead_load_finish', 30) / 100
        
        # 1. Define nodes
        self._define_nodes(layout)
        
        # 2. Define members
        self._define_members(layout, E, G, nu, rho)
        
        # 3. Apply supports
        self._apply_supports(layout)
        
        # 4. Apply loads
        self._apply_loads(layout, live_load_kn, dead_load_kn)
        
        return self.model
    
    def _define_nodes(self, layout):
        """Define all nodes in the system"""
        L = layout.length
        W = layout.width
        H = layout.floor_height
        col_x = layout.column_spacing_x
        col_y = layout.column_spacing_y
        
        num_cols_x = int(L / col_x) + 1
        num_cols_y = int(W / col_y) + 1
        
        # Column nodes (base and top)
        node_id = 1
        self.column_nodes = {}
        
        for i in range(num_cols_x):
            for j in range(num_cols_y):
                x = i * col_x
                y = j * col_y
                
                # Base node
                base_name = f'C{i}_{j}_B'
                self.model.add_node(base_name, x, y, 0)
                
                # Top node
                top_name = f'C{i}_{j}_T'
                self.model.add_node(top_name, x, y, H)
                
                self.column_nodes[(i, j)] = {'base': base_name, 'top': top_name}
        
        # Main beam nodes (already defined as column tops)
        # Secondary beam nodes (intermediate nodes along main beams)
        self._define_beam_intermediate_nodes(layout)
    
    def _define_beam_intermediate_nodes(self, layout):
        """Define intermediate nodes for secondary beams"""
        L = layout.length
        W = layout.width
        H = layout.floor_height
        col_x = layout.column_spacing_x
        col_y = layout.column_spacing_y
        sec_spacing = layout.secondary_beam_spacing
        
        num_cols_x = int(L / col_x) + 1
        num_cols_y = int(W / col_y) + 1
        
        self.sec_beam_nodes = []
        
        if layout.main_beam_direction == 'X':
            # Secondary beams run in Y direction
            num_sec = int(col_x / sec_spacing)
            for i in range(num_cols_x - 1):
                for k in range(1, num_sec + 1):
                    x = i * col_x + k * sec_spacing
                    for j in range(num_cols_y):
                        y = j * col_y
                        node_name = f'SB{i}_{k}_{j}'
                        self.model.add_node(node_name, x, y, H)
                        self.sec_beam_nodes.append(node_name)
        else:
            # Secondary beams run in X direction
            num_sec = int(col_y / sec_spacing)
            for j in range(num_cols_y - 1):
                for k in range(1, num_sec + 1):
                    y = j * col_y + k * sec_spacing
                    for i in range(num_cols_x):
                        x = i * col_x
                        node_name = f'SB{i}_{j}_{k}'
                        self.model.add_node(node_name, x, y, H)
                        self.sec_beam_nodes.append(node_name)
    
    def _define_members(self, layout, E, G, nu, rho):
        """Define all members (columns, beams)"""
        # First define materials and sections
        self._define_materials_and_sections(layout, E, G, nu, rho)
        
        # Then define members
        self._define_column_members(layout, E, G, nu, rho)
        self._define_main_beam_members(layout, E, G, nu, rho)
        self._define_secondary_beam_members(layout, E, G, nu, rho)
    
    def _define_materials_and_sections(self, layout, E, G, nu, rho):
        """Define materials and sections for Pynite 2.0"""
        # Add steel material
        self.model.add_material('Steel', E, G, nu, rho)
        
        # Column section
        col_spec = layout.column_spec
        A_col = col_spec.area / 10000  # cm² to m²
        Iy_col = col_spec.ix / 100000000  # cm⁴ to m⁴
        Iz_col = Iy_col
        J_col = Iy_col + Iz_col
        self.model.add_section('ColumnSection', A_col, Iy_col, Iz_col, J_col)
        
        # Main beam section
        beam_spec = layout.main_beam_spec
        A_beam = beam_spec.area / 10000
        Iy_beam = beam_spec.ix / 100000000
        Iz_beam = Iy_beam * 0.3
        J_beam = 0.1 * Iy_beam
        self.model.add_section('MainBeamSection', A_beam, Iy_beam, Iz_beam, J_beam)
        
        # Secondary beam section
        sec_spec = layout.secondary_beam_spec
        A_sec = sec_spec.area / 10000
        Iy_sec = sec_spec.ix / 100000000
        Iz_sec = Iy_sec * 0.3
        J_sec = 0.1 * Iy_sec
        self.model.add_section('SecBeamSection', A_sec, Iy_sec, Iz_sec, J_sec)
    
    def _define_column_members(self, layout, E, G, nu, rho):
        """Define column members"""
        self.column_members = []
        for (i, j), nodes in self.column_nodes.items():
            member_name = f'Col_{i}_{j}'
            self.model.add_member(
                member_name,
                nodes['base'],
                nodes['top'],
                'Steel',
                'ColumnSection'
            )
            self.column_members.append(member_name)
    
    def _define_main_beam_members(self, layout, E, G, nu, rho):
        """Define main beam members"""
        col_x = layout.column_spacing_x
        col_y = layout.column_spacing_y
        L = layout.length
        W = layout.width
        num_cols_x = int(L / col_x) + 1
        num_cols_y = int(W / col_y) + 1
        
        self.main_beam_members = []
        
        if layout.main_beam_direction == 'X':
            # Main beams run in X direction
            for j in range(num_cols_y):
                for i in range(num_cols_x - 1):
                    member_name = f'MB_Y{j}_S{i}'  # Y-row, Span i
                    node_i = self.column_nodes[(i, j)]['top']
                    node_j = self.column_nodes[(i+1, j)]['top']
                    self.model.add_member(member_name, node_i, node_j, 'Steel', 'MainBeamSection')
                    self.main_beam_members.append(member_name)
        else:
            # Main beams run in Y direction
            for i in range(num_cols_x):
                for j in range(num_cols_y - 1):
                    member_name = f'MB_X{i}_S{j}'  # X-row, Span j
                    node_i = self.column_nodes[(i, j)]['top']
                    node_j = self.column_nodes[(i, j+1)]['top']
                    self.model.add_member(member_name, node_i, node_j, 'Steel', 'MainBeamSection')
                    self.main_beam_members.append(member_name)
    
    def _define_secondary_beam_members(self, layout, E, G, nu, rho):
        """Define secondary beam members"""
        col_x = layout.column_spacing_x
        col_y = layout.column_spacing_y
        sec_spacing = layout.secondary_beam_spacing
        L = layout.length
        W = layout.width
        num_cols_x = int(L / col_x) + 1
        num_cols_y = int(W / col_y) + 1
        
        self.sec_beam_members = []
        
        if layout.main_beam_direction == 'X':
            # Main beams run in X direction, secondary beams run in Y direction
            # Secondary beams connect column tops in Y direction at intermediate X positions
            num_sec = int(col_x / sec_spacing)
            
            for i in range(num_cols_x - 1):  # Between each pair of column lines
                for k in range(1, num_sec + 1):  # Each secondary beam position
                    # Connect nodes from j=0 to j=num_cols_y-1
                    for j in range(num_cols_y - 1):
                        node_i = f'SB{i}_{k}_{j}'
                        node_j = f'SB{i}_{k}_{j+1}'
                        member_name = f'SecB_{i}_{k}_{j}'
                        
                        self.model.add_member(
                            member_name,
                            node_i,
                            node_j,
                            'Steel',
                            'SecBeamSection'
                        )
                        self.sec_beam_members.append(member_name)
        else:
            # Main beams run in Y direction, secondary beams run in X direction
            # Secondary beams connect column tops in X direction at intermediate Y positions
            num_sec = int(col_y / sec_spacing)
            
            for j in range(num_cols_y - 1):  # Between each pair of column lines
                for k in range(1, num_sec + 1):  # Each secondary beam position
                    # Connect nodes from i=0 to i=num_cols_x-1
                    for i in range(num_cols_x - 1):
                        node_i = f'SB{i}_{j}_{k}'
                        node_j = f'SB{i+1}_{j}_{k}'
                        member_name = f'SecB_{i}_{j}_{k}'
                        
                        self.model.add_member(
                            member_name,
                            node_i,
                            node_j,
                            'Steel',
                            'SecBeamSection'
                        )
                        self.sec_beam_members.append(member_name)
    
    def _apply_supports(self, layout):
        """Apply support conditions (fixed at column bases)"""
        for (i, j), nodes in self.column_nodes.items():
            base_node = nodes['base']
            # Fixed support (all DOF restrained)
            self.model.def_support(base_node, True, True, True, True, True, True)
    
    def _apply_loads(self, layout, live_load_kn, dead_load_kn):
        """Apply loads to the structure"""
        # Calculate deck self-weight
        deck_weight = 0.05  # kN/m² (approximate)
        
        # Total distributed load
        total_load = live_load_kn + dead_load_kn + deck_weight
        
        # Calculate tributary area for each beam
        sec_spacing = layout.secondary_beam_spacing
        col_spacing_x = layout.column_spacing_x
        col_spacing_y = layout.column_spacing_y
        
        # Apply distributed loads to main beams
        for member_name in self.main_beam_members:
            # Load per unit length (kN/m)
            w = total_load * sec_spacing
            self.model.add_member_dist_load(member_name, 'Fy', -w, -w, 0, 1)
        
        # Apply distributed loads to secondary beams
        if layout.main_beam_direction == 'X':
            # Secondary beams run in Y direction
            tributary_width = sec_spacing
        else:
            # Secondary beams run in X direction  
            tributary_width = sec_spacing
        
        for member_name in self.sec_beam_members:
            # Load per unit length for secondary beams (kN/m)
            w = total_load * tributary_width
            self.model.add_member_dist_load(member_name, 'Fy', -w, -w, 0, 1)
    
    def run_analysis(self) -> Dict[str, Any]:
        """
        Run FEM analysis and extract results
        
        Returns:
            Dictionary with analysis results
        """
        if self.model is None:
            raise ValueError("Model not built. Call build_fem_model() first.")
        
        try:
            # Analyze the model
            self.model.analyze(check_statics=True)
            
            # Extract results
            self.results = {
                'deflections': self._extract_deflections(),
                'reactions': self._extract_reactions(),
                'member_forces': self._extract_member_forces(),
                'max_deflection': self._find_max_deflection(),
                'status': 'Analysis Complete'
            }
        except Exception as e:
            # Analysis failed - return partial results with error info
            print(f"⚠️  FEM Analysis encountered issues: {e}")
            self.results = {
                'deflections': {},
                'reactions': {},
                'member_forces': {},
                'max_deflection': {'value': 0, 'node': 'N/A', 'limit': 'N/A'},
                'status': f'Analysis failed: {str(e)}',
                'error': str(e)
            }
        
        return self.results
    
    def _extract_deflections(self) -> Dict:
        """Extract nodal deflections"""
        deflections = {}
        for node_name in self.model.nodes:
            node = self.model.nodes[node_name]
            deflections[node_name] = {
                'dx': node.DX['Combo 1'],
                'dy': node.DY['Combo 1'],
                'dz': node.DZ['Combo 1']
            }
        return deflections
    
    def _extract_reactions(self) -> Dict:
        """Extract support reactions"""
        reactions = {}
        for (i, j), nodes in self.column_nodes.items():
            base_node = nodes['base']
            node = self.model.nodes[base_node]
            reactions[base_node] = {
                'Fx': node.RxnFX['Combo 1'],
                'Fy': node.RxnFY['Combo 1'],
                'Fz': node.RxnFZ['Combo 1']
            }
        return reactions
    
    def _extract_member_forces(self) -> Dict:
        """Extract member internal forces"""
        member_forces = {}
        
        # Main beams
        for member_name in self.main_beam_members:
            member = self.model.members[member_name]
            L = member.L()
            
            # Sample points along member
            positions = np.linspace(0, L, 21)
            
            member_forces[member_name] = {
                'positions': positions.tolist(),
                'shear': [member.shear('Fy', x) for x in positions],
                'moment': [member.moment('Mz', x) for x in positions],
                'axial': [member.axial(x) for x in positions],
                'length': L
            }
        
        return member_forces
    
    def _find_max_deflection(self) -> Dict:
        """Find maximum deflection in the structure"""
        max_def = 0
        max_node = None
        
        # Safety check
        if 'deflections' not in self.results or not self.results['deflections']:
            return {
                'value': 0,
                'node': 'N/A',
                'limit': 'N/A'
            }
        
        for node_name, defl in self.results['deflections'].items():
            total_def = abs(defl['dy'])  # Vertical deflection
            if total_def > max_def:
                max_def = total_def
                max_node = node_name
        
        return {
            'value': max_def * 1000,  # Convert to mm
            'node': max_node if max_node else 'N/A',
            'limit': 'L/360'  # Typical limit
        }
    
    def generate_fem_report(self) -> str:
        """
        Generate HTML report of FEM analysis results
        
        Returns:
            HTML string with formatted results
        """
        if not self.results:
            return "<h3>Chưa có kết quả phân tích. Vui lòng chạy phân tích trước.</h3>"
        
        max_def = self.results['max_deflection']
        
        html = f"""
        <html>
        <head>
        <style>
        body {{ font-family: 'Segoe UI', Arial; padding: 20px; line-height: 1.6; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; }}
        h2 {{ color: #2980b9; margin-top: 25px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        .ok {{ color: green; font-weight: bold; }}
        .warning {{ color: orange; font-weight: bold; }}
        .fail {{ color: red; font-weight: bold; }}
        .highlight {{ background-color: #e8f4f8; padding: 15px; border-left: 4px solid #3498db; margin: 15px 0; }}
        </style>
        </head>
        <body>
        
        <h1>📊 BÁO CÁO PHÂN TÍCH FEM (PyNite)</h1>
        
        <div class="highlight">
        <h2>I. KẾT QUẢ PHÂN TÍCH</h2>
        <table>
        <tr><th>Thông số</th><th>Giá trị</th></tr>
        <tr>
            <td>Độ võng tối đa</td>
            <td class="{'ok' if max_def['value'] < 10 else 'warning'}">{max_def['value']:.2f} mm</td>
        </tr>
        <tr>
            <td>Vị trí võng max</td>
            <td>{max_def['node']}</td>
        </tr>
        <tr>
            <td>Giới hạn cho phép</td>
            <td>{max_def['limit']}</td>
        </tr>
        <tr>
            <td>Số nút (nodes)</td>
            <td>{len(self.model.nodes)}</td>
        </tr>
        <tr>
            <td>Số thanh (members)</td>
            <td>{len(self.model.members)}</td>
        </tr>
        </table>
        </div>
        
        <h2>II. PHẢ­N LỰC GỐI</h2>
        <table>
        <tr><th>Cột</th><th>Fx (kN)</th><th>Fy (kN)</th><th>Fz (kN)</th></tr>
        """
        
        # Add reactions
        for node_name, reaction in list(self.results['reactions'].items())[:10]:  # Show first 10
            html += f"""
            <tr>
                <td>{node_name}</td>
                <td>{reaction['Fx']:.2f}</td>
                <td>{reaction['Fy']:.2f}</td>
                <td>{reaction['Fz']:.2f}</td>
            </tr>
            """
        
        html += """
        </table>
        
        <h2>III. NỘI LỰC DẦM CHÍNH</h2>
        <p>Xem biểu đồ Moment và Shear ở tab "📊 Biểu đồ Plotly"</p>
        
        </body>
        </html>
        """
        
        return html
