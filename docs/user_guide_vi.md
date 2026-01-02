# Hướng Dẫn Sử Dụng - VietStruct FEM

## 📖 Mục lục

1. [Giới thiệu](#giới-thiệu)
2. [Cài đặt](#cài-đặt)
3. [Bắt đầu nhanh](#bắt-đầu-nhanh)
4. [Sử dụng GUI](#sử-dụng-gui)
5. [Sử dụng API](#sử-dụng-api)
6. [Ví dụ chi tiết](#ví-dụ-chi-tiết)

---

## Giới thiệu

VietStruct FEM là phần mềm phân tích kết cấu mã nguồn mở dành cho kỹ sư kết cấu tại Việt Nam. Phần mềm hỗ trợ:

- 🏭 **Nhà xưởng**: Tính toán xà gồ, khung portal, tải trọng gió
- 🏢 **Hệ thống sàn**: Sàn deck composite, dầm, cột  
- 🔬 **Phân tích FEM**: Sử dụng PyNite cho phân tích phần tử hữu hạn
- 📊 **Visualization**: Biểu đồ 3D và interactive charts

---

## Cài đặt

### Yêu cầu hệ thống
- Python 3.10 trở lên
- Windows, Linux, hoặc macOS

### Cài đặt từ source

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/VietStructFEM.git
cd VietStructFEM

# Cài đặt package và dependencies
pip install -e .

# Hoặc cài đặt với công cụ developer
pip install -e .[dev]
```

### Kiểm tra cài đặt

```bash
python -c "from steeldeckfem.core import FloorSystemFEMAnalyzer; print('OK')"
```

---

## Bắt đầu nhanh

### Chạy ứng dụng GUI

```bash
python -m steeldeckfem
```

### Ví dụ Python đơn giản

```python
from steeldeckfem.core import FloorSystemFEMAnalyzer, get_wind_pressure
from types import SimpleNamespace

# 1. Tạo layout hệ thống sàn
layout = SimpleNamespace(
    length=20,  # m
    width=15,   # m
    floor_height=4.0,
    column_spacing_x=5.0,
    column_spacing_y=5.0,
    main_beam_direction='X',
    secondary_beam_spacing=2.5
)

# 2. Định nghĩa tiết diện
layout.column_spec = SimpleNamespace(h=300, b=300, tf=10, tw=15, area=0, ix=0)
# ... (xem examples/basic_floor_system.py để biết chi tiết)

# 3. Chạy phân tích
analyzer = FloorSystemFEMAnalyzer()
analyzer.build_fem_model(layout, {'live_load': 400, 'dead_load_finish': 30})
results = analyzer.run_analysis()

print(f"Độ võng max: {results['max_deflection']['value']:.2f} mm")
```

---

## Sử dụng GUI

### 1. Khởi động ứng dụng

```bash
python -m steeldeckfem
```

### 2. Nhập thông số

**Bố trí hệ thống:**
- Chọn địa điểm → Tự động tính vùng gió
- Nhập chiều dài, rộng, cao
- Nhập lưới cột và khoảng cách dầm phụ

**Tiết diện:**
- Cột: H, B, tf, tw
- Dầm chính: H, B, tf, tw  
- Dầm phụ: H, B, tf, tw

**Tải trọng:**
- Hoạt tải (kg/m²)
- Tĩnh tải hoàn thiện (kg/m²)
- Gió (tự động từ vùng)

### 3. Phân tích

Nhấn nút **⚡ PHÂN TÍCH FEM**

### 4. Xem kết quả

- **Tab 🎨 Mô hình 3D**: Visualization với màu theo ứng suất
  - 🟢 Xanh: OK (unity < 0.8)
  - 🟠 Cam: Cảnh báo (0.8 ≤ unity < 1.0)
  - 🔴 Đỏ: Không đạt (unity ≥ 1.0)

- **Tab 🔬 Kết quả FEM**: Báo cáo chi tiết
  - Độ võng max
  - Phản lực gối
  - Nội lực thanh

- **Tab 📊 Biểu đồ Interactive**: Plotly charts
  - Moment diagrams
  - Shear diagrams
  - Axial force diagrams

---

## Sử dụng API

### Wind Zones

```python
from steeldeckfem.core import get_wind_pressure, get_all_locations

# Lấy danh sách địa điểm
locations = get_all_locations()

# Tra cứu áp lực gió
wind_data = get_wind_pressure("Hà Nội")
print(f"Vùng: {wind_data['zone']}, Wo: {wind_data['Wo']} kg/m²")
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

### Purlin Calculator (Industrial Buildings)

```python
from steeldeckfem.core import PurlinCalculator
from steeldeckfem.core.data_models import CalculationInput, PurlinParams

# Tạo input
input_data = CalculationInput()
input_data.purlin = PurlinParams(
    profile_name="Z17515",
    span=6.0,          # m
    spacing=1.5,       # m
    roof_slope=10.0,   # degrees
    dead_load=25,      # kg/m²
    live_load=30       # kg/m²
)

calc = PurlinCalculator()
result = calc.check_purlin(input_data)
```

---

## Ví dụ chi tiết

### Ví dụ 1: Hệ thống sàn đơn giản

Xem file [`examples/basic_floor_system.py`](../examples/basic_floor_system.py)

```bash
python examples/basic_floor_system.py
```

### Ví dụ 2: Tính toán với nhiều tầng

```python
from steeldeckfem.core import FloorLoadDistributor

loads = FloorLoadDistributor.calculate_column_loads(
    num_floors=5,
    floor_load=600,  # kg/m²
    tributary_area=25.0,  # m²
    roof_load=300  # kg/m²
)

print(f"Tải trọng tổng lên cột: {loads['total_axial_force']:.0f} kg")
```

### Ví dụ 3: Kiểm tra ổn định cột

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
    k_x=1.0,
    k_y=1.0
)

print(f"Status: {result.status}")
print(f"φ critical: {result.phi_critical:.3f}")
```

---

## Câu hỏi thường gặp (FAQ)

**Q: Làm sao để xem công thức tính toán?**  
A: Mở file source code trong `steeldeckfem/core/`, các công thức được document rõ ràng.

**Q: Phần mềm hỗ trợ tiêu chuẩn nào?**  
A: TCVN 2737:2023 (gió), TCVN 5575:2012/2024 (thép), TCVN 9386:2024 (động đất).

**Q: Làm sao xuất báo cáo?**  
A: Trong GUI, tab Plotly có nút "📥 Xuất HTML". Hoặc dùng API: `analyzer.generate_fem_report()`.

**Q: Có thể tùy biến tiết diện không?**  
A: Có! Nhập bất kỳ tiết diện nào với H, B, tf, tw.

---

## Hỗ trợ

- 📧 Email: [Your Email]
- 💬 GitHub Issues: [Link]
- 📚 Documentation: [Link]

---

**Made with ❤️ for Vietnamese structural engineers**
