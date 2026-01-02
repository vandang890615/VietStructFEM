# Contributing to VietStructFEM

Thank you for your interest in contributing to VietStructFEM! This document provides guidelines and instructions for contributing.

## 🌟 Ways to Contribute

### 1. Report Bugs
- Use GitHub Issues to report bugs
- Include detailed steps to reproduce
- Provide error messages and screenshots
- Mention your environment (Windows version, Python version)

### 2. Suggest Features
- Open a GitHub Issue with `[Feature Request]` prefix
- Describe the feature and its benefits
- Explain use cases for Vietnamese engineers

### 3. Improve Documentation
- Fix typos and errors
- Add examples and tutorials
- Translate documentation (English/Vietnamese)

### 4. Submit Code
- Fix bugs
- Implement new features
- Add TCVN standards support
- Optimize performance

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Basic understanding of PyQt5
- Knowledge of TCVN structural standards (helpful)

### Setting Up Development Environment

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/VietStructFEM.git
   cd VietStructFEM
   ```

3. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If exists
   ```

5. **Run the application**
   ```bash
   python -m steeldeckfem
   ```

6. **Run tests**
   ```bash
   python quick_test.py
   ```

---

## 📝 Code Contribution Process

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions

### 2. Make Changes
- Follow the existing code style
- Write clear, descriptive commit messages
- Add comments for complex logic
- Update documentation if needed

### 3. Test Your Changes
```bash
# Run import test
python quick_test.py

# Run the application
python -m steeldeckfem

# Test your specific module
# ... manual testing ...
```

### 4. Commit Your Changes
```bash
git add .
git commit -m "feat: Add [feature description]"
# or
git commit -m "fix: Resolve [bug description]"
```

**Commit message format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Code formatting
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### 5. Push to Your Fork
```bash
git push origin feature/your-feature-name
```

### 6. Create Pull Request
1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill in the PR template:
   - **Title**: Clear, concise description
   - **Description**: What changes were made and why
   - **Related Issues**: Link to any related issues
   - **Testing**: How you tested the changes

---

## 🎨 Code Style Guidelines

### Python Code
```python
# Use clear, descriptive names
class RCBeamDesigner:
    """RC Beam Designer per TCVN 5574:2018"""
    
    def calculate_flexure(self, M: float, b: float, h: float) -> dict:
        """
        Calculate flexural reinforcement
        
        Args:
            M: Bending moment (kNm)
            b: Width (mm)
            h: Height (mm)
        
        Returns:
            Dictionary with reinforcement details
        """
        # Implementation
        pass
```

**Guidelines:**
- Use 4 spaces for indentation
- Follow PEP 8 style guide
- Maximum line length: 100 characters
- Add docstrings for classes and methods
- Use type hints where applicable
- Include TCVN standard references in comments

### UI Code (PyQt5)
```python
# Clear naming for UI elements
self.inp_beam_width = QLineEdit()  # Not: self.le1
self.btn_calculate = QPushButton("Calculate")  # Not: self.pb
```

### Vietnamese Language
- UI labels: Vietnamese
- Code/variables: English
- Comments: English (with Vietnamese for TCVN terms)
- Documentation: Both languages

---

## 📚 Adding TCVN Standards Data

If you're adding new TCVN standards data:

1. **Update JSON file**
   ```json
   // In vn_construction_standards.json
   {
     "newStandard": {
       "version": "TCVN XXXX:2024",
       "data": { ... }
     }
   }
   ```

2. **Add loader method**
   ```python
   # In vn_standards_loader.py
   def get_new_standard_data(self, param: str) -> dict:
       """Get data from new TCVN standard"""
       return self._data['newStandard']['data'][param]
   ```

3. **Update documentation**
   - Add to README.md features list
   - Update TCVN_STANDARDS_COVERAGE.md
   - Add usage examples

---

## 🐛 Reporting Bugs

### Bug Report Template
```markdown
**Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. Enter '...'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Screenshots**
If applicable, add screenshots.

**Environment**
- OS: Windows 10/11
- Python Version: 3.11
- VietStructFEM Version: 1.0.0

**Error Messages**
```
Paste any error messages here
```
```

---

## 💡 Feature Requests

### Feature Request Template
```markdown
**Feature Description**
Clear description of the proposed feature.

**Use Case**
Why is this feature needed? Who will use it?

**TCVN Standard Reference**
If applicable, which TCVN standard supports this?

**Proposed Implementation**
(Optional) Ideas for how to implement this.

**Alternatives Considered**
(Optional) Other approaches you've thought about.
```

---

## ✅ Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows the style guidelines
- [ ] All tests pass (`python quick_test.py`)
- [ ] New code includes comments/docstrings
- [ ] TCVN references are cited where applicable
- [ ] UI text is in Vietnamese
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No unnecessary files are included (e.g., `.pyc`, `__pycache__`)

---

## 🔍 Code Review Process

1. **Automated Checks**
   - Import tests run automatically
   - Code style checks (if configured)

2. **Manual Review**
   - Maintainer reviews code quality
   - Tests proposed changes
   - Provides feedback

3. **Feedback Loop**
   - Address review comments
   - Update PR as needed
   - Re-request review

4. **Merge**
   - PR is merged to `main` branch
   - Changes appear in next release

---

## 📦 Project Structure

Understanding the codebase:

```
VietStructFEM/
├── steeldeckfem/
│   ├── core/               # Calculation engines
│   │   ├── vn_standards_loader.py
│   │   ├── rc_beam_designer.py
│   │   └── ...
│   ├── ui/                 # User interface
│   │   ├── modules/        # Feature modules
│   │   ├── widgets/        # Reusable widgets
│   │   └── main_window.py
│   └── __main__.py         # Entry point
├── vn_construction_standards.json  # TCVN data
├── tests/                  # Test files
├── docs/                   # Documentation
└── examples/               # Usage examples
```

---

## 🌐 Internationalization

### Adding Translations
1. UI strings should use Vietnamese by default
2. For English support, use string dictionaries:
   ```python
   LABELS = {
       'vi': 'Tính toán dầm',
       'en': 'Calculate Beam'
   }
   ```

---

## 📞 Getting Help

- **Questions**: Open a GitHub Discussion
- **Chat**: Contact via email (vandang890615@gmail.com)
- **Documentation**: Read the [README](README.md) and [Wiki](../../wiki)

---

## 🎯 Priority Areas

We especially welcome contributions in:

1. **TCVN Standards Data**
   - More steel sections
   - Additional load tables
   - Soil parameters for Vietnam regions

2. **Module Enhancements**
   - Warehouse module completion
   - Advanced reporting features
   - PEB/Zamil structural systems

3. **Testing**
   - Unit tests for core engines
   - Integration tests for modules
   - UI automation tests

4. **Documentation**
   - User guides in English
   - Video tutorials
   - TCVN standard references

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 🙏 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for helping make VietStructFEM better for Vietnamese engineers!

---

**Questions?** Open an issue or contact: vandang890615@gmail.com

**Happy Coding!** 🚀
