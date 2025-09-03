# 📦 Simple Installation Guide

All dependencies are managed uniformly using `pyproject.toml`, no additional requirements files needed.

## 🚀 Quick Installation Commands

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### 2. Upgrade pip
```bash
pip install --upgrade pip
```

### 3. Install Dependencies (choose one)

```bash
# 🎯 Development Environment (Recommended) - Includes all features and development tools
pip install -e ".[all,dev]"

# 🔧 Complete Feature Version - Includes all features but no development tools  
pip install -e ".[all]"

# 📊 Code Interpreter Version - Includes data science libraries
pip install -e ".[code-interpreter]"

# 🖥️ Desktop Automation Version
pip install -e ".[desktop]"

# ⚡ Basic Version - Core functionality only
pip install -e .
```

## 🧪 Verify Installation
```bash
python setup_check.py
```

## 📋 Installation Content Description

### `.[all,dev]` - Development Environment (Recommended)
- ✅ All core functionality
- ✅ Code interpreter (matplotlib, pandas, numpy, etc.)
- ✅ Desktop automation (pyautogui, opencv, etc.)  
- ✅ Development tools (pytest, black, mypy, etc.)
- ✅ Documentation tools (sphinx, etc.)

### `.[all]` - Complete Features
- ✅ All core functionality
- ✅ Code interpreter functionality
- ✅ Desktop automation functionality
- ❌ Development tools

### `.[code-interpreter]` - Data Science
- ✅ Core functionality
- ✅ matplotlib, plotly, pandas, numpy, pillow
- ❌ Desktop automation
- ❌ Development tools

### `.[desktop]` - Desktop Automation
- ✅ Core functionality  
- ✅ pyautogui, pynput, opencv-python
- ❌ Code interpreter
- ❌ Development tools

### `.` - Basic Version
- ✅ Core functionality (httpx, attrs, etc.)
- ❌ Optional features
- ❌ Development tools

## 🔄 Dependency Management

### View Installed Packages
```bash
pip list
```

### Update Packages
```bash
pip install --upgrade -e ".[all,dev]"
```

### Reinstall
```bash
pip uninstall novita-sandbox -y
pip install -e ".[all,dev]"
```

---

That's it! All dependencies are managed uniformly in `pyproject.toml`.
