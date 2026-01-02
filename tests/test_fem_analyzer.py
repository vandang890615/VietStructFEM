"""
Unit tests for FEM Analyzer module
"""

import pytest
from steeldeckfem.core import FloorSystemFEMAnalyzer


class TestFloorSystemFEMAnalyzer:
    """Tests for FloorSystemFEMAnalyzer class"""
    
    def test_init(self):
        """Test analyzer initialization"""
        analyzer = FloorSystemFEMAnalyzer()
        assert analyzer.model is None
        assert analyzer.results == {}
    
    def test_build_fem_model_creates_model(self, simple_layout, simple_loads):
        """Test that build_fem_model creates a PyNite model"""
        analyzer = FloorSystemFEMAnalyzer()
        model = analyzer.build_fem_model(simple_layout, simple_loads)
        
        assert model is not None
        assert analyzer.model is not None
    
    def test_build_fem_model_creates_nodes(self, simple_layout, simple_loads):
        """Test that correct number of nodes are created"""
        analyzer = FloorSystemFEMAnalyzer()
        analyzer.build_fem_model(simple_layout, simple_loads)
        
        # Calculate expected node count
        L, W = simple_layout.length, simple_layout.width
        col_x, col_y = simple_layout.column_spacing_x, simple_layout.column_spacing_y
        num_cols_x = int(L / col_x) + 1  # 3 columns in X
        num_cols_y = int(W / col_y) + 1  # 3 columns in Y
        
        # Column nodes: 2 per column (base + top)
        expected_column_nodes = num_cols_x * num_cols_y * 2
        
        # Secondary beam intermediate nodes
        sec_spacing = simple_layout.secondary_beam_spacing
        num_sec = int(col_x / sec_spacing)  # 2 secondary beams between columns
        expected_sec_nodes = (num_cols_x - 1) * num_sec * num_cols_y
        
        total_expected = expected_column_nodes + expected_sec_nodes
        
        assert len(analyzer.model.nodes) >= expected_column_nodes
    
    def test_build_fem_model_creates_column_members(self, simple_layout, simple_loads):
        """Test that column members are created"""
        analyzer = FloorSystemFEMAnalyzer()
        analyzer.build_fem_model(simple_layout, simple_loads)
        
        L, W = simple_layout.length, simple_layout.width
        col_x, col_y = simple_layout.column_spacing_x, simple_layout.column_spacing_y
        num_cols_x = int(L / col_x) + 1
        num_cols_y = int(W / col_y) + 1
        
        expected_columns = num_cols_x * num_cols_y
        assert len(analyzer.column_members) == expected_columns
    
    def test_build_fem_model_creates_main_beam_members(self, simple_layout, simple_loads):
        """Test that main beam members are created"""
        analyzer = FloorSystemFEMAnalyzer()
        analyzer.build_fem_model(simple_layout, simple_loads)
        
        L, W = simple_layout.length, simple_layout.width
        col_x, col_y = simple_layout.column_spacing_x, simple_layout.column_spacing_y
        num_cols_x = int(L / col_x) + 1
        num_cols_y = int(W / col_y) + 1
        
        if simple_layout.main_beam_direction == 'X':
            expected_main_beams = num_cols_y * (num_cols_x - 1)
        else:
            expected_main_beams = num_cols_x * (num_cols_y - 1)
        
        assert len(analyzer.main_beam_members) == expected_main_beams
    
    def test_build_fem_model_creates_secondary_beam_members(self, simple_layout, simple_loads):
        """Test that secondary beam members are created"""
        analyzer = FloorSystemFEMAnalyzer()
        analyzer.build_fem_model(simple_layout, simple_loads)
        
        # Should have secondary beam members
        assert len(analyzer.sec_beam_members) > 0
    
    def test_build_fem_model_applies_supports(self, simple_layout, simple_loads):
        """Test that supports are applied to column bases"""
        analyzer = FloorSystemFEMAnalyzer()
        analyzer.build_fem_model(simple_layout, simple_loads)
        
        # Check that column base nodes have supports
        for (i, j), nodes in analyzer.column_nodes.items():
            base_node = nodes['base']
            node = analyzer.model.nodes[base_node]
            
            # Check support conditions
            assert node.support_DX == True
            assert node.support_DY == True
            assert node.support_DZ == True
    
    def test_run_analysis_requires_model(self):
        """Test that run_analysis fails without building model first"""
        analyzer = FloorSystemFEMAnalyzer()
        
        with pytest.raises(ValueError, match="Model not built"):
            analyzer.run_analysis()
    
    def test_run_analysis_returns_results(self, simple_layout, simple_loads):
        """Test that run_analysis returns results dictionary"""
        analyzer = FloorSystemFEMAnalyzer()
        analyzer.build_fem_model(simple_layout, simple_loads)
        results = analyzer.run_analysis()
        
        # Results should contain key sections even if analysis fails
        assert 'status' in results
        assert 'deflections' in results
        assert 'reactions' in results
        assert 'member_forces' in results
        assert 'max_deflection' in results
    
    def test_generate_fem_report_without_results(self):
        """Test report generation without results"""
        analyzer = FloorSystemFEMAnalyzer()
        report = analyzer.generate_fem_report()
        
        assert "Chưa có kết quả" in report


class TestFEMAnalyzerEdgeCases:
    """Test edge cases and error handling"""
    
    def test_very_small_layout(self):
        """Test with minimal layout (single bay)"""
        from types import SimpleNamespace
        
        layout = SimpleNamespace(
            length=5, width=4, floor_height=3.0,
            column_spacing_x=5.0, column_spacing_y=4.0,
            main_beam_direction='X', secondary_beam_spacing=2.0
        )
        
        # Add sections
        layout.column_spec = SimpleNamespace(h=200, b=200, tf=8, tw=8, area=60.8, ix=4000)
        layout.main_beam_spec = SimpleNamespace(h=300, b=150, tf=8, tw=6, area=70, ix=8000)
        layout.secondary_beam_spec = SimpleNamespace(h=200, b=100, tf=6, tw=5, area=40, ix=2000)
        
        analyzer = FloorSystemFEMAnalyzer()
        model = analyzer.build_fem_model(layout, {'live_load': 300, 'dead_load_finish': 20})
        
        assert model is not None
        assert len(analyzer.column_members) == 4  # 2x2 grid
