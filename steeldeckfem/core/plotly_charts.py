"""
Plotly Interactive Charts for Structural Analysis
Creates interactive diagrams for moment, shear, axial force, and deflections
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Any


class StructuralDiagramCreator:
    """
    Creates interactive Plotly charts for structural analysis results
    """
    
    def __init__(self):
        self.fig = None
        
    def create_complete_analysis_dashboard(self, fem_results: Dict, layout) -> go.Figure:
        """
        Create comprehensive dashboard with all structural diagrams
        
        Args:
            fem_results: Results from FEM analysis
            layout: Floor system layout
            
        Returns:
            Plotly figure with multiple subplots
        """
        # Create subplots: 3 rows x 2 columns
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                '3D Structural Model',
                'Deflection Diagram',
                'Moment Diagram (Main Beams)',
                'Shear Force Diagram',
                'Axial Force Diagram',
                'Reactions at Supports'
            ),
            specs=[
                [{'type': 'scatter3d', 'rowspan': 2}, {'type': 'scatter'}],
                [None, {'type': 'scatter'}],
                [{'type': 'scatter'}, {'type': 'scatter'}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.12
        )
        
        # 1. 3D Structural Model
        self._add_3d_structure(fig, layout, fem_results, row=1, col=1)
        
        # 2. Deflection Diagram
        self._add_deflection_diagram(fig, fem_results, row=1, col=2)
        
        # 3. Moment Diagram
        self._add_moment_diagram(fig, fem_results, row=2, col=2)
        
        # 4. Shear Force Diagram
        self._add_shear_diagram(fig, fem_results, row=3, col=1)
        
        # 5. Axial Force Diagram
        self._add_axial_diagram(fig, fem_results, row=3, col=2)
        
        # Layout configuration
        fig.update_layout(
            title={
                'text': 'ðŸ“Š PHÃ‚N TÃCH Káº¾T Cáº¤U TÆ¯Æ NG TÃC (PyNite + Plotly)',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#2c3e50', 'family': 'Arial Black'}
            },
            height=1200,
            showlegend=True,
            hovermode='closest',
            template='plotly_white',
            font=dict(family='Segoe UI', size=11)
        )
        
        self.fig = fig
        return fig
    
    def _add_3d_structure(self, fig, layout, fem_results, row, col):
        """Add 3D structural model to subplot"""
        L = layout.length
        W = layout.width
        H = layout.floor_height
        col_x = layout.column_spacing_x
        col_y = layout.column_spacing_y
        
        num_cols_x = int(L / col_x) + 1
        num_cols_y = int(W / col_y) + 1
        
        # Draw columns
        for i in range(num_cols_x):
            for j in range(num_cols_y):
                x = i * col_x
                y = j * col_y
                
                fig.add_trace(
                    go.Scatter3d(
                        x=[x, x],
                        y=[y, y],
                        z=[0, H],
                        mode='lines+markers',
                        line=dict(color='#27ae60', width=8),
                        marker=dict(size=6, color='#27ae60'),
                        name='Cá»™t' if i==0 and j==0 else '',
                        showlegend=(i==0 and j==0),
                        hovertemplate=f'<b>Cá»™t C{i}_{j}</b><br>' +
                                    f'X: {x:.1f}m<br>Y: {y:.1f}m<br>H: %{{z:.1f}}m<extra></extra>'
                    ),
                    row=row, col=col
                )
        
        # Draw main beams
        if layout.main_beam_direction == 'X':
            for j in range(num_cols_y):
                y = j * col_y
                x_line = [i * col_x for i in range(num_cols_x)]
                y_line = [y] * num_cols_x
                z_line = [H] * num_cols_x
                
                fig.add_trace(
                    go.Scatter3d(
                        x=x_line,
                        y=y_line,
                        z=z_line,
                        mode='lines',
                        line=dict(color='#e74c3c', width=5),
                        name='Dáº§m chÃ­nh' if j==0 else '',
                        showlegend=(j==0),
                        hovertemplate='<b>Dáº§m chÃ­nh</b><br>Y=%{y:.1f}m<extra></extra>'
                    ),
                    row=row, col=col
                )
        
        # Update 3D scene
        fig.update_scenes(
            xaxis_title='X (m)',
            yaxis_title='Y (m)',
            zaxis_title='Z (m)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            ),
            row=row, col=col
        )
    
    def _add_deflection_diagram(self, fig, fem_results, row, col):
        """Add deflection diagram"""
        if 'max_deflection' not in fem_results:
            return
        
        # Simplified deflection profile for main beam
        x = np.linspace(0, 5, 50)
        # Parabolic deflection (simplified)
        deflection = -4 * fem_results['max_deflection']['value'] * x * (5 - x) / 25
        
        fig.add_trace(
            go.Scatter(
                x=x,
                y=deflection,
                mode='lines',
                line=dict(color='#9b59b6', width=3),
                fill='tozeroy',
                fillcolor='rgba(155, 89, 182, 0.2)',
                name='Äá»™ vÃµng',
                hovertemplate='<b>Äá»™ vÃµng</b><br>x=%{x:.2f}m<br>Î´=%{y:.2f}mm<extra></extra>'
            ),
            row=row, col=col
        )
        
        # Add limit line
        limit = fem_results['max_deflection']['value'] * 0.7  # Example limit
        fig.add_trace(
            go.Scatter(
                x=[0, 5],
                y=[-limit, -limit],
                mode='lines',
                line=dict(color='red', dash='dash', width=2),
                name='Giá»›i háº¡n',
                showlegend=True
            ),
            row=row, col=col
        )
        
        fig.update_xaxes(title_text='Vá»‹ trÃ­ (m)', row=row, col=col)
        fig.update_yaxes(title_text='Äá»™ vÃµng (mm)', row=row, col=col)
    
    def _add_moment_diagram(self, fig, fem_results, row, col):
        """Add moment diagram from FEM results"""
        if 'member_forces' not in fem_results:
            return
        
        # Get first main beam for demonstration
        member_forces = fem_results['member_forces']
        if not member_forces:
            return
        
        # Get first member
        member_name = list(member_forces.keys())[0]
        data = member_forces[member_name]
        
        positions = data['positions']
        moments = data['moment']
        
        fig.add_trace(
            go.Scatter(
                x=positions,
                y=moments,
                mode='lines',
                line=dict(color='#e74c3c', width=3),
                fill='tozeroy',
                fillcolor='rgba(231, 76, 60, 0.2)',
                name='Moment',
                hovertemplate='<b>Moment</b><br>x=%{x:.2f}m<br>M=%{y:.2f}kNÂ·m<extra></extra>'
            ),
            row=row, col=col
        )
        
        fig.update_xaxes(title_text='Vá»‹ trÃ­ (m)', row=row, col=col)
        fig.update_yaxes(title_text='Moment (kNÂ·m)', row=row, col=col)
    
    def _add_shear_diagram(self, fig, fem_results, row, col):
        """Add shear force diagram"""
        if 'member_forces' not in fem_results:
            return
        
        member_forces = fem_results['member_forces']
        if not member_forces:
            return
        
        member_name = list(member_forces.keys())[0]
        data = member_forces[member_name]
        
        positions = data['positions']
        shears = data['shear']
        
        fig.add_trace(
            go.Scatter(
                x=positions,
                y=shears,
                mode='lines',
                line=dict(color='#3498db', width=3),
                fill='tozeroy',
                fillcolor='rgba(52, 152, 219, 0.2)',
                name='Lá»±c cáº¯t',
                hovertemplate='<b>Lá»±c cáº¯t</b><br>x=%{x:.2f}m<br>V=%{y:.2f}kN<extra></extra>'
            ),
            row=row, col=col
        )
        
        fig.update_xaxes(title_text='Vá»‹ trÃ­ (m)', row=row, col=col)
        fig.update_yaxes(title_text='Lá»±c cáº¯t (kN)', row=row, col=col)
    
    def _add_axial_diagram(self, fig, fem_results, row, col):
        """Add axial force diagram"""
        if 'member_forces' not in fem_results:
            return
        
        member_forces = fem_results['member_forces']
        if not member_forces:
            return
        
        member_name = list(member_forces.keys())[0]
        data = member_forces[member_name]
        
        positions = data['positions']
        axials = data['axial']
        
        fig.add_trace(
            go.Scatter(
                x=positions,
                y=axials,
                mode='lines',
                line=dict(color='#f39c12', width=3),
                fill='tozeroy',
                fillcolor='rgba(243, 156, 18, 0.2)',
                name='Lá»±c dá»c',
                hovertemplate='<b>Lá»±c dá»c</b><br>x=%{x:.2f}m<br>N=%{y:.2f}kN<extra></extra>'
            ),
            row=row, col=col
        )
        
        fig.update_xaxes(title_text='Vá»‹ trÃ­ (m)', row=row, col=col)
        fig.update_yaxes(title_text='Lá»±c dá»c (kN)', row=row, col=col)
    
    def create_multi_member_comparison(self, fem_results: Dict, diagram_type: str = 'moment') -> go.Figure:
        """
        Create comparison chart for multiple members
        
        Args:
            fem_results: FEM analysis results
            diagram_type: 'moment', 'shear', or 'axial'
            
        Returns:
            Plotly figure with overlaid diagrams
        """
        fig = go.Figure()
        
        member_forces = fem_results.get('member_forces', {})
        
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        
        for idx, (member_name, data) in enumerate(member_forces.items()):
            if idx >= 5:  # Limit to 5 members
                break
            
            positions = data['positions']
            
            if diagram_type == 'moment':
                values = data['moment']
                y_title = 'Moment (kNÂ·m)'
            elif diagram_type == 'shear':
                values = data['shear']
                y_title = 'Lá»±c cáº¯t (kN)'
            else:  # axial
                values = data['axial']
                y_title = 'Lá»±c dá»c (kN)'
            
            fig.add_trace(
                go.Scatter(
                    x=positions,
                    y=values,
                    mode='lines',
                    line=dict(color=colors[idx], width=2),
                    name=member_name,
                    hovertemplate=f'<b>{member_name}</b><br>x=%{{x:.2f}}m<br>Value=%{{y:.2f}}<extra></extra>'
                )
            )
        
        fig.update_layout(
            title=f'SO SÃNH {diagram_type.upper()} - NHIá»€U Dáº¦M',
            xaxis_title='Vá»‹ trÃ­ (m)',
            yaxis_title=y_title,
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def export_to_html(self, filename: str):
        """Export current figure to HTML file"""
        if self.fig:
            self.fig.write_html(filename)
            return True
        return False
    
    def create_load_distribution_3d(self, layout, loads: Dict) -> go.Figure:
        """
        Create 3D visualization of load distribution
        
        Args:
            layout: Floor system layout
            loads: Dictionary with load values
            
        Returns:
            Plotly 3D surface plot showing load distribution
        """
        L = layout.length
        W = layout.width
        
        # Create mesh grid
        x = np.linspace(0, L, 30)
        y = np.linspace(0, W, 30)
        X, Y = np.meshgrid(x, y)
        
        # Uniform load (can be made non-uniform based on results)
        total_load = loads.get('live_load', 400) + loads.get('dead_load_finish', 30)
        Z = np.ones_like(X) * (total_load / 100)  # Convert to kN/mÂ²
        
        fig = go.Figure(data=[
            go.Surface(
                x=X,
                y=Y,
                z=Z,
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title='Táº£i (kN/mÂ²)'),
                hovertemplate='<b>Táº£i trá»ng</b><br>X=%{x:.1f}m<br>Y=%{y:.1f}m<br>Load=%{z:.2f}kN/mÂ²<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title='PHÃ‚N Bá» Táº¢I TRá»ŒNG 3D',
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Táº£i (kN/mÂ²)',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
            ),
            height=600
        )
        
        return fig

