# Đóng góp cho Steel Deck FEM / Contributing to Steel Deck FEM

## 🎯 Chúng tôi hoan nghênh / We Welcome

- 🐛 Báo cáo lỗi / Bug reports
- ✨ Tính năng mới / New features  
- 📝 Cải thiện tài liệu / Documentation improvements
- 🌍 Bản dịch / Translations
- ✅ Unit tests
- 💡 Ý tưởng / Ideas

## 🚀 Quy trình / Process

### 1. Fork & Clone

```bash
# Fork trên GitHub, sau đó clone
git clone https://github.com/vandang890615/SteelDeckFEM.git
cd SteelDeckFEM
```

### 2. Tạo branch / Create branch

```bash
git checkout -b feature/your-feature-name
# hoặc / or
git checkout -b bugfix/issue-number
```

### 3. Cài đặt development / Install for development

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

pip install -r requirements.txt
pip install -e .  # Install in editable mode
```

### 4. Thực hiện thay đổi / Make changes

- Viết code rõ ràng với docstrings
- Thêm unit tests nếu có thể
- Follow PEP 8 style guide
- Comment bằng tiếng Việt hoặc tiếng Anh đều OK

### 5. Test

```bash
# Run tests
python -m pytest tests/

# Run the app
python -m steeldeckfem
```

### 6. Commit

```bash
git add .
git commit -m "feat: Add new feature description"
# hoặc / or
git commit -m "fix: Fix bug description"
```

**Commit message format:**
- `feat:` - Tính năng mới / New feature
- `fix:` - Sửa lỗi / Bug fix
- `docs:` - Tài liệu / Documentation
- `test:` - Tests
- `refactor:` - Refactoring

### 7. Push & Pull Request

```bash
git push origin feature/your-feature-name
```

Sau đó mở Pull Request trên GitHub với mô tả chi tiết.

## 📝 Coding Standards

- **Python**: PEP 8
- **Docstrings**: Google style
- **Type hints**: Khuyến khích sử dụng
- **Comments**: Tiếng Việt hoặc English đều OK

## ✅ Pull Request Checklist

- [ ] Code chạy được không lỗi
- [ ] Tests pass (nếu có)
- [ ] Docstrings đã được thêm/cập nhật
- [ ] README được cập nhật (nếu cần)
- [ ] Không có hardcoded paths
- [ ] Code clean và readable

## 🐛 Báo cáo lỗi / Bug Reports

Khi báo lỗi, vui lòng cung cấp:
- **Mô tả lỗi** / Bug description
- **Các bước tái hiện** / Steps to reproduce
- **Expected behavior**
- **Screenshots** (nếu có)
- **Environment**: OS, Python version

## 💡 Đề xuất tính năng / Feature Requests

- Mô tả tính năng chi tiết
- Giải thích tại sao cần tính năng này
- Đưa ra ví dụ use case

## ❓ Questions?

- Mở GitHub Discussion
- Hoặc tạo Issue với label `question`

## 📜 Code of Conduct

- Tôn trọng mọi người / Be respectful
- Constructive feedback
- Help others
- Professional communication

---

**Cảm ơn bạn đã đóng góp! / Thank you for contributing!** 🙏
