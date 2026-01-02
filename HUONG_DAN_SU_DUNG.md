# Hướng Dẫn Sử Dụng VietStructFEM.exe

## Cho Kỹ Sư Không Biết Code

---

## 📦 DOWNLOAD & CÀI ĐẶT

### Cách 1: Tải File .exe Trực Tiếp (Đơn giản nhất)

1. **Tải về:**
   - Truy cập: https://github.com/vandang890615/VietStructFEM/releases
   - Tải file: `VietStructFEM_v1.0.0.zip` (khoảng 200-300MB)

2. **Giải nén:**
   - Click chuột phải vào file .zip
   - Chọn "Extract All" / "Giải nén tất cả"
   - Chọn thư mục đích (VD: `C:\VietStructFEM`)

3. **Chạy phần mềm:**
   - Vào thư mục đã giải nén
   - Tìm file: `VietStructFEM.exe`
   - **Click đúp** để chạy

**✅ XONG! Không cần cài Python hay bất kỳ thứ gì khác.**

---

## 🚀 CHẠY LẦN ĐẦU

### Bước 1: Mở phần mềm
- Click đúp vào `VietStructFEM.exe`
- Chờ 5-10 giây (lần đầu sẽ chậm hơn)

### Bước 2: Giao diện chính
- Sẽ hiện cửa sổ với các tab:
  - 🏢 Sàn Deck
  - 🏛 Cột BTCT
  - 🔲 Khung 2D
  - ... (11 modules)

### Bước 3: Chọn module cần dùng
- Click vào tab tương ứng
- Nhập số liệu
- Click nút "Tính toán" / "Thiết kế"

---

## 📋 HƯỚNG DẪN CÁC MODULE

### 1. Sàn Deck (Steel Deck)
**Dùng để:** Tính tôn deck

**Các bước:**
1. Nhập chiều dày tôn
2. Nhập nhịp dầm
3. Nhập tải trọng
4. Click "Tính toán"
5. Xem kết quả

---

### 2. Cột BTCT (RC Column)
**Dùng để:** Thiết kế cột bê tông cốt thép

**Các bước:**
1. Nhập kích thước cột (b x h)
2. Nhập mác bê tông (B20, B25...)
3. Nhập tải trọng (P, M)
4. Click "Thiết kế cột"
5. Xem biểu đồ P-M, cốt thép

---

### 3. Tổ hợp Tải trọng
**Dùng để:** Tạo tổ hợp tải trọng theo TCVN 2737:2023

**Các bước:**
1. Nhập các loại tải (Dead, Live, Wind...)
2. Chọn ULS hoặc SLS
3. Click "Tính toán"
4. Xem 12 tổ hợp

---

### 4. Dầm & Sàn BTCT
**Dùng để:** Thiết kế dầm và sàn BTCT

**Dầm:**
1. Nhập b x h x L
2. Nhập tải trọng
3. Click "Thiết kế dầm"
4. Xem cốt thép, biểu đồ

**Sàn:**
1. Chọn sàn 1 phương / 2 phương
2. Nhập kích thước
3. Click "Thiết kế sàn"
4. Xem cốt thép

---

### 5. Móng (Foundations)
**Dùng để:** Thiết kế móng đơn và móng cọc

**Móng đơn:**
1. Nhập tải trọng P
2. Chọn loại đất
3. Click "Thiết kế móng đơn"
4. Xem kích thước móng

---

### 6. Kết cấu Thép (Steel Members)
**Dùng để:** Kiểm tra dầm thép, cột thép

**Các bước:**
1. Chọn tiết diện (H200, BOX200...)
2. Nhập moment, lực cắt
3. Click "Kiểm tra"
4. Xem tỷ số ứng suất

---

### 7. Liên kết (Connections)
**Dùng để:** Thiết kế liên kết bu lông, hàn

**Các bước:**
1. Chọn loại liên kết (Bu lông / Hàn)
2. Nhập thông số
3. Click "Kiểm tra"

---

### 8. Kiểm tra Võng (Deflection)
**Dùng để:** Kiểm tra độ võng dầm

**Các bước:**
1. Chọn loại dầm
2. Nhập tải
3. Click "Kiểm tra võng"

---

## ⚠️ LƯU Ý QUAN TRỌNG

### Khi chạy lần đầu:
- **Antivirus có thể cảnh báo**: Đây là bình thường với file .exe mới
- **Giải pháp**: Cho phép (Allow) hoặc thêm vào danh sách ngoại lệ (Whitelist)
- **An toàn**: File .exe này 100% an toàn, mã nguồn mở trên GitHub

### Nếu gặp lỗi:
1. **Lỗi "VCRUNTIME140.dll missing":**
   - Tải Visual C++ Redistributable:
   - Link: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Cài đặt và chạy lại

2. **Phần mềm không mở:**
   - Click chuột phải vào VietStructFEM.exe
   - Chọn "Run as Administrator" / "Chạy với quyền quản trị"

3. **Module nào đó không hoạt động:**
   - Kiểm tra file `vn_construction_standards.json` có trong cùng thư mục không
   - Nếu thiếu, tải lại từ GitHub

---

## 💡 TIPS & TRICKS

### Để chạy nhanh hơn:
- Lần đầu chậm (10-15 giây)
- Từ lần 2 trở đi sẽ nhanh hơn (2-3 giây)

### Để lưu kết quả:
- Sử dụng nút "Xuất báo cáo" (nếu có)
- Hoặc chụp màn hình (Windows + Shift + S)

### Để cập nhật phiên bản mới:
1. Tải phiên bản mới từ GitHub Releases
2. Giải nén vào thư mục khác
3. Chạy file .exe mới

---

## 📞 HỖ TRỢ

**Nếu gặp vấn đề:**
- GitHub Issues: https://github.com/vandang890615/VietStructFEM/issues
- Email: vandang890615@gmail.com

**Báo lỗi:**
1. Chụp màn hình lỗi
2. Ghi rõ bước đang làm
3. Gửi vào GitHub Issues hoặc Email

---

## 📚 TÀI LIỆU THAM KHẢO

**TCVN áp dụng:**
- TCVN 2737:2023 - Tải trọng và tác động
- TCVN 5574:2018 - Kết cấu bê tông và bê tông cốt thép
- TCVN 5575:2024 - Kết cấu thép
- TCVN 9362:2012 - Móng cọc
- TCVN 10304:2014 - Móng nông

---

## ✅ CHECKLIST SỬ DỤNG

- [ ] Đã tải file .exe về
- [ ] Đã giải nén
- [ ] Đã thử click đúp vào .exe
- [ ] Phần mềm đã mở thành công
- [ ] Đã thử 1 module bất kỳ
- [ ] Kết quả tính toán hợp lý

**Nếu tất cả OK → Bạn đã sẵn sàng sử dụng! 🎉**

---

**Version**: 1.0.0  
**Ngày cập nhật**: 2026-01-03  
**Dành cho**: Kỹ sư kết cấu Việt Nam
