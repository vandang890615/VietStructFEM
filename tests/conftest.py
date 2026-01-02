"""
Pytest configuration and fixtures for VietStruct FEM tests
"""

import pytest
from types import SimpleNamespace
from steeldeckfem.core.data_models import Section, Material, GeometryParams, WindParams


@pytest.fixture
def simple_layout():
    """Create a simple floor system layout for testing"""
    layout = SimpleNamespace(
        length=10,  # m
        width=8,   # m  
        floor_height=4.0,
        column_spacing_x=5.0,
        column_spacing_y=4.0,
        main_beam_direction='X',
        secondary_beam_spacing=2.0
    )
    
    # Column section
    layout.column_spec = SimpleNamespace(
        h=250, b=250, tf=10, tw=10,
        area=0, ix=0
    )
    
    # Calculate properties
    h_cm, b_cm = layout.column_spec.h/10, layout.column_spec.b/10
    tf_cm, tw_cm = layout.column_spec.tf/10, layout.column_spec.tw/10
    layout.column_spec.area = 2*b_cm*tf_cm + (h_cm-2*tf_cm)*tw_cm
    layout.column_spec.ix = (b_cm*h_cm**3/12) - ((b_cm-tw_cm)*(h_cm-2*tf_cm)**3/12)
    
    # Main beam section
    layout.main_beam_spec = SimpleNamespace(
        h=400, b=200, tf=10, tw=8,
        area=0, ix=0
    )
    h_cm, b_cm = layout.main_beam_spec.h/10, layout.main_beam_spec.b/10
    tf_cm, tw_cm = layout.main_beam_spec.tf/10, layout.main_beam_spec.tw/10
    layout.main_beam_spec.area = 2*b_cm*tf_cm + (h_cm-2*tf_cm)*tw_cm
    layout.main_beam_spec.ix = (b_cm*h_cm**3/12) - ((b_cm-tw_cm)*(h_cm-2*tf_cm)**3/12)
    
    # Secondary beam section
    layout.secondary_beam_spec = SimpleNamespace(
        h=250, b=150, tf=8, tw=6,
        area=0, ix=0
    )
    h_cm, b_cm = layout.secondary_beam_spec.h/10, layout.secondary_beam_spec.b/10
    tf_cm, tw_cm = layout.secondary_beam_spec.tf/10, layout.secondary_beam_spec.tw/10
    layout.secondary_beam_spec.area = 2*b_cm*tf_cm + (h_cm-2*tf_cm)*tw_cm
    layout.secondary_beam_spec.ix = (b_cm*h_cm**3/12) - ((b_cm-tw_cm)*(h_cm-2*tf_cm)**3/12)
    
    return layout


@pytest.fixture
def steel_material():
    """Create standard steel material"""
    return Material(
        name="Steel Grade 50",
        E=200000,  # MPa
        G=77000,
        fy=350,
        fu=490,
        density=7850
    )


@pytest.fixture
def test_section():
    """Create a test section"""
    return Section(
        name="Test-H400x200x10x8",
        h=400,
        b=200,
        tf=10,
        tw=8,
        area=96.0,
        ix=24000.0,
        iy=1600.0,
        wx=1200.0,
        wy=160.0
    )


@pytest.fixture
def simple_loads():
    """Create simple load dictionary"""
    return {
        'live_load': 400,  # kg/m²
        'dead_load_finish': 30  # kg/m²
    }


@pytest.fixture
def geometry_params():
    """Create geometry parameters for industrial buildings"""
    return GeometryParams(
        span=20.0,
        length=50.0,
        height_eave=6.0,
        roof_slope=10.0,
        purlin_spacing=1.5,
        frame_spacing=5.0
    )


@pytest.fixture
def wind_params():
    """Create wind parameters"""
    return WindParams(
        zone="II",
        Wo=110,
        terrain_category="B",
        height=10.0,
        k_factor=1.0,
        beta_factor=1.0
    )
