# 📦 简单安装指南

使用 `pyproject.toml` 统一管理所有依赖，无需额外的 requirements 文件。

## 🚀 快速安装命令

### 1. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### 2. 升级 pip
```bash
pip install --upgrade pip
```

### 3. 安装依赖 (选择一个)

```bash
# 🎯 开发环境 (推荐) - 包含所有功能和开发工具
pip install -e ".[all,dev]"

# 🔧 完整功能版本 - 包含所有功能但不含开发工具  
pip install -e ".[all]"

# 📊 代码解释器版本 - 包含数据科学库
pip install -e ".[code-interpreter]"

# 🖥️ 桌面自动化版本
pip install -e ".[desktop]"

# ⚡ 基础版本 - 仅核心功能
pip install -e .
```

## 🧪 验证安装
```bash
python setup_check.py
```

## 📋 安装内容说明

### `.[all,dev]` - 开发环境 (推荐)
- ✅ 所有核心功能
- ✅ 代码解释器 (matplotlib, pandas, numpy 等)
- ✅ 桌面自动化 (pyautogui, opencv 等)  
- ✅ 开发工具 (pytest, black, mypy 等)
- ✅ 文档工具 (sphinx 等)

### `.[all]` - 完整功能
- ✅ 所有核心功能
- ✅ 代码解释器功能
- ✅ 桌面自动化功能
- ❌ 开发工具

### `.[code-interpreter]` - 数据科学
- ✅ 核心功能
- ✅ matplotlib, plotly, pandas, numpy, pillow
- ❌ 桌面自动化
- ❌ 开发工具

### `.[desktop]` - 桌面自动化
- ✅ 核心功能  
- ✅ pyautogui, pynput, opencv-python
- ❌ 代码解释器
- ❌ 开发工具

### `.` - 基础版本
- ✅ 核心功能 (httpx, attrs 等)
- ❌ 可选功能
- ❌ 开发工具

## 🔄 管理依赖

### 查看已安装的包
```bash
pip list
```

### 更新包
```bash
pip install --upgrade -e ".[all,dev]"
```

### 重新安装
```bash
pip uninstall ppio-sandbox -y
pip install -e ".[all,dev]"
```

---

就这么简单！所有依赖都在 `pyproject.toml` 中统一管理。
