# User Guide - VietStruct FEM

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Using the GUI](#using-the-gui)
5. [Using the API](#using-the-api)
6. [Detailed Examples](#detailed-examples)

---

## Introduction

VietStruct FEM is an open-source structural analysis software designed for structural engineers in Vietnam. It supports:

- 🏭 **Industrial Buildings**: Purlin design, portal frames, wind loads
- 🏢 **Floor Systems**: Composite steel deck, beams, columns  
- 🔬 **FEM Analysis**: Uses PyNite for finite element analysis
- 📊 **Visualization**: 3D models and interactive charts

---

## Installation

### System Requirements
- Python 3.10 or higher
- Windows, Linux, or macOS

### Install from Source

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/VietStructFEM.git
cd VietStructFEM

# Install package and dependencies
pip install -e .

# Or install with developer tools
pip install -e .[dev]
```

### Verify Installation

```bash
python -c "from steeldeckfem.core import FloorSystemFEMAnalyzer; print('OK')"
```

---

## Quick Start

### Run GUI Application

```bash
python -m steeldeckfem
```

### Simple Python Example

```python
from steeldeckfem.core import FloorSystemFEMAnalyzer
from types import SimpleNamespace

# 1. Create floor system layout
layout = SimpleNamespace(
    length=20,  # meters
    width=15,
    floor_height=4.0,
    column_spacing_x=5.0,
    column_spacing_y=5.0,
    main_beam_direction='X',
    secondary_beam_spacing=2.5
)

# 2. Define sections (see examples/basic_floor_system.py for details)
layout.column_spec = SimpleNamespace(h=300, b=300, tf=10, tw=15, area=0, ix=0)
# ...

# 3. Run analysis
analyzer = FloorSystemFEMAnalyzer()
analyzer.build_fem_model(layout, {'live_load': 400, 'dead_load_finish': 30})
results = analyzer.run_analysis()

print(f"Max deflection: {results['max_deflection']['value']:.2f} mm")
```

---

## Using the GUI

### 1. Launch Application

```bash
python -m steeldeckfem
```

### 2. Input Parameters

**System Layout:**
- Select location → Automatically determines wind zone
- Enter length, width, height
- Enter column grid and secondary beam spacing

**Sections:**
- Columns: H, B, tf, tw
- Main beams: H, B, tf, tw  
- Secondary beams: H, B, tf, tw

**Loads:**
- Live load (kg/m²)
- Dead load - finishes (kg/m²)
- Wind (automatic from zone)

### 3. Analysis

Click **⚡ FEM ANALYSIS** button

### 4. View Results

- **Tab 🎨 3D Model**: Visualization with stress-based coloring
  - 🟢 Green: OK (unity < 0.8)
  - 🟠 Orange: Warning (0.8 ≤ unity < 1.0)
  - 🔴 Red: Failed (unity ≥ 1.0)

- **Tab 🔬 FEM Results**: Detailed report
  - Maximum deflection
  - Support reactions
  - Member forces

- **Tab 📊 Interactive Diagrams**: Plotly charts
  - Moment diagrams
  - Shear diagrams
  - Axial force diagrams

---

## Using the API

### Wind Zones

```python
from steeldeckfem.core import get_wind_pressure, get_all_locations

# Get all locations
locations = get_all_locations()

# Look up wind pressure
wind_data = get_wind_pressure("Hà Nội")
print(f"Zone: {wind_data['zone']}, Wo: {wind_data['Wo']} kg/m²")
```

### Steel Deck Design

```python
from steeldeckfem.core import SteelDeckCalculator

calc = SteelDeckCalculator()
result = calc.design_deck(
    profile_name="DECK_75",
    thickness=1.0,  # mm
    span=3.0,       # m
    concrete_thickness=120,  # mm
    construction_load=150,   # kg/m²
    live_load=400           # kg/m²
)

print(f"Status: {result.status}")
print(f"Max span: {result.max_span:.2f} m")
```

### Stability Checks

```python
from steeldeckfem.core import StabilityCalculator
from steeldeckfem.core.data_models import Section, Material

section = Section(name="H300x300x10x15", h=300, b=300, 
                  tf=10, tw=15, area=96, ix=24000)
material = Material()

calc = StabilityCalculator()
result = calc.check_column_stability(
    section=section,
    material=material,
    N_design=50000,  # kg
    L_x=4000,        # cm
    L_y=4000,        # cm
)

print(f"Status: {result.status}")
print(f"φ critical: {result.phi_critical:.3f}")
```

---

## Detailed Examples

See [`examples/basic_floor_system.py`](../examples/basic_floor_system.py)

```bash
python examples/basic_floor_system.py
```

---

## Standards Compliance

- **TCVN 2737:2023** - Wind loads
- **TCVN 5575:2012/2024** - Steel structure design
- **TCVN 9386:2024** - Seismic loads
- **ASTM A653** - Steel deck specifications

---

## FAQ

**Q: How can I view the calculation formulas?**  
A: Open source code files in `steeldeckfem/core/`, formulas are well-documented.

**Q: Which standards does the software support?**  
A: TCVN 2737:2023 (wind), TCVN 5575:2012/2024 (steel), TCVN 9386:2024 (seismic).

**Q: How to export reports?**  
A: In GUI, Plotly tab has "📥 Export HTML" button. Or use API: `analyzer.generate_fem_report()`.

**Q: Can I customize sections?**  
A: Yes! Enter any section with H, B, tf, tw parameters.

---

## Support

- 📧 Email: [Your Email]
- 💬 GitHub Issues: [Link]
- 📚 Documentation: [Link]

---

**Made with ❤️ for Vietnamese structural engineers**
