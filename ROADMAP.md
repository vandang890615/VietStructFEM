# VietStruct FEM - Development Roadmap

## 🎯 Vision
Trở thành phần mềm tính toán kết cấu mã nguồn mở hàng đầu cho kỹ sư Việt Nam, tích hợp đầy đủ TCVN và công nghệ hiển thị hiện đại.

---

## 🚀 Live Status (2026-01-03)

**Current Version**: `v0.6.0-beta`
**Progress**: ~60% of MVP Goals met.

### ✅ Completed Modules (Đã hoàn thành)
| Feature | Module | Details |
|---------|--------|---------|
| **GUI Framework** | Core | Modern Tabbed Interface, responsive layout |
| **Sàn Deck** | `SteelDeckModule` | 3D Visualization, Check Bending/Shear |
| **Cột BTCT** | `RCColumnModule` | Interaction Diagram (M-N), Bi-axial Check |
| **Khung 2D** | `FrameAnalysisModule` | FEM Engine (`anastruct`), M/V/Deflection Diagrams |
| **Nhà Công Nghiệp** | `WarehouseModule` | **NEW!** Wind Load (TCVN 2737:2023), Purlin Auto-Design |
| **Động Đất** | `OpenSeesModule` | Modal Analysis (Periods/Frequencies) using `OpenSeesPy` |
| **Báo Cáo** | All | Standardized HTML Reports ("Thuyết minh") for all modules |
| **Stability** | Core | Global Exception Handler, "Busy State" locking |

---

## 📅 Short-term Plans (Jan 2026)

### �️ v0.7.0 - Foundation & Connections (Móng & Liên kết)
**Priority**: High (User Request)
- [ ] **Móng Đơn/Cọc**: Implement logic from Excel references.
- [ ] **Liên kết Thép**: Check Base Plate (Chân cột) & Apex (Đỉnh kèo).

### � v0.8.0 - Advanced Industrial Building (Zamil)
**Priority**: High
- [ ] **Tapered Sections**: Support vát (Tapered) functionality in Frame Analysis.
- [ ] **Combo Generator**: Auto-generate load combinations (Dead + Live + Wind).

---

## 🔮 Medium-term Plans (Q1 2026)

### v1.0.0 - Production Release
- [ ] **Save/Open Project**: JSON/SQLite based file format.
- [ ] **DXF Export**: Expand DXF export to all modules (currently only Frame).
- [ ] **Settings**: User-defined material libraries & safety factors.

---

##  Long-term (Future)
- **BIM Integration**: Revit Plugin / IFC Export.
- **AI Assistant**: Natural language querying for code checks.
- **Web App**: Port key calculation modules to WebAssembly/React.

---

## 📊 Version History

| Version | Status | Key Features |
|---------|--------|--------------|
| v0.1.0 | ✅ Done | Initial CLI Tools |
| v0.2.0 | ✅ Done | Basic GUI & Frame Analysis |
| v0.5.0 | ✅ Done | Modular Architecture, Reporting, Stability |
| v0.6.0 | ✅ Done | Industrial Warehouse (Wind/Purlin), Auto-Design |
| v0.7.0 | � Next | Foundations & Connections |

---

**Maintainer**: [@vandang890615](https://github.com/vandang890615)
**Last Updated**: 2026-01-03
