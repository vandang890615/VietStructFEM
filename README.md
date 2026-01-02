# VietStruct FEM - Phần mềm tính toán kết cấu Việt Nam
**Open Source Structural Analysis Software for Vietnamese Engineers**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyNiteFEA](https://img.shields.io/badge/FEM-PyNiteFEA-green)](https://github.com/JWock82/PyNite)

## 🌟 Giới thiệu / Introduction

**Tiếng Việt:**
VietStruct FEM là phần mềm mã nguồn mở dành cho kỹ sư kết cấu tại Việt Nam, hỗ trợ phân tích và thiết kế:
- 🏗️ **Nhà xưởng** - Industrial buildings / Pre-engineered buildings
- 🔩 **Kết cấu thép** - Steel structures (beams, columns, trusses, steel deck)
- 🏢 **Kết cấu BTCT** - Reinforced concrete structures (beams, columns, slabs)
- 📐 **Phương pháp FEM** - Finite Element Method analysis

**English:**
VietStruct FEM is an open-source software for structural engineers in Vietnam, supporting analysis and design of industrial buildings, steel structures, and reinforced concrete structures using Finite Element Method.

## ✨ Tính năng / Features

### 🏗️ Nhà xưởng / Industrial Buildings
- Portal frame analysis
- Truss systems
- Wind and crane loads
- Base plate design

### 🔩 Kết cấu thép / Steel Structures
- 🔬 **Phân tích FEM** - PyNite-based finite element analysis
- 📊 **Biểu đồ tương tác** - Interactive Plotly diagrams (Moment, Shear, Axial)
- 🎨 **Visualization 3D** - Professional 3D model with stress-based coloring
- 🎯 **Unity Check** - Automatic stress ratio calculation (TCVN 5575:2024)
- 🟢🔴 **Color-coded results** - Visual indication of failed/warning/OK members

### 🏢 Kết cấu BTCT / Reinforced Concrete  
- Beam and column design
- Slab design (one-way, two-way)
- Reinforcement detailing
- Crack width checking

### 🌪️ Tải trọng Việt Nam / Vietnam Loads
- Wind load database (TCVN 2737:2023) 
- Seismic loads (TCVN 9386:2024)
- Live loads by building type

### 📝 Reporting
- Comprehensive HTML reports
- Critical member identification
- Design summary tables

## 📸 Screenshots

![3D Model](docs/images/screenshot_3d.png)
*Mô hình 3D với màu sắc theo tỷ lệ ứng suất*

![FEM Results](docs/images/screenshot_fem.png)
*Báo cáo kết quả FEM chi tiết*

![Plotly Diagrams](docs/images/screenshot_plotly.png)
*Biểu đồ Plotly tương tác*

## 🚀 Cài đặt / Installation

### Yêu cầu / Requirements
- Python 3.10 trở lên
- Windows/Linux/macOS

### Cài đặt từ source / Install from source

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/SteelDeckFEM.git
cd SteelDeckFEM

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc / or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m steeldeckfem
```

### Cài đặt qua pip (sắp có / coming soon)

```bash
pip install steeldeckfem
```

## 📖 Sử dụng / Usage

### Giao diện GUI / GUI Interface

```bash
python -m steeldeckfem
```

### Python API

```python
from steeldeckfem.core import FloorSystemFEMAnalyzer
from types import SimpleNamespace

# Define floor system layout
layout = SimpleNamespace(
    length=20,  # m
    width=15,   # m
    floor_height=4.0,
    column_spacing_x=5.0,
    column_spacing_y=5.0,
    main_beam_direction='X',
    secondary_beam_spacing=2.5
)

# Create analyzer
analyzer = FloorSystemFEMAnalyzer()

# Build and run FEM model
analyzer.build_fem_model(layout, loads={'live_load': 400, 'dead_load_finish': 30})
results = analyzer.run_analysis(layout)

# Get results
print(f"Max deflection: {results['max_deflection']['value']:.2f} mm")
```

Xem thêm ví dụ trong thư mục `examples/`

## 📚 Tài liệu / Documentation

- [Hướng dẫn sử dụng (Tiếng Việt)](docs/user_guide_vi.md)
- [User Guide (English)](docs/user_guide_en.md)
- [API Reference](docs/api_reference.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🤝 Đóng góp / Contributing

Chúng tôi rất hoan nghênh mọi đóng góp từ cộng đồng! / We welcome contributions from the community!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Xem chi tiết tại [CONTRIBUTING.md](CONTRIBUTING.md)

## 📋 Tiêu chuẩn / Standards

- TCVN 2737:2023 - Tải trọng gió
- TCVN 5575:2024 - Thiết kế kết cấu thép
- ASTM A653 - Steel deck specifications

## 🛠️ Công nghệ / Technology Stack

- **FEM Engine**: [PyNiteFEA](https://github.com/JWock82/PyNite) - Finite Element Analysis
- **Visualization**: [Plotly](https://plotly.com/) - Interactive charts
- **GUI**: [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - Desktop interface
- **Scientific Computing**: NumPy, SciPy, Matplotlib

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors & Contributors

- **Initial Author** - Project creator
- [List of contributors](https://github.com/YOUR_USERNAME/SteelDeckFEM/contributors)

## 🙏 Acknowledgments

- PyNiteFEA team for the excellent FEM library
- Vietnamese structural engineering community
- All contributors and users

## 📞 Liên hệ / Contact

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/SteelDeckFEM/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/SteelDeckFEM/discussions)

## ⭐ Support

If you find this project useful, please give it a star! ⭐

---

**Made with ❤️ for Vietnamese structural engineers / Được tạo ra với ❤️ cho các kỹ sư kết cấu Việt Nam**
