# ⚡ UV 极速上手指南

## 🚀 5分钟快速开始

### 前置条件
```bash
# 安装 uv (如果还没有)
curl -LsSf https://astral.sh/uv/install.sh | sh
# 或者
pip install uv
```

### 🎯 开发者工作流

#### 1. 初始化项目 (⚡ 超快)
```bash
cd capacity-web
make quickstart

# 或者手动
uv sync          # 安装所有依赖
uv run pytest   # 运行测试
```

#### 2. 日常开发 (⚡ 极速)
```bash
# 添加新依赖
uv add requests
uv add --dev black

# 运行代码
uv run python -c "from capacity_web import search_web; print('OK')"

# 运行测试
uv run pytest tests/

# 更新依赖
uv sync --upgrade
```

#### 3. 构建发布 (⚡ 原生)
```bash
# 构建包
uv build

# 发布到 TestPyPI
uv publish --repository testpypi

# 发布到 PyPI
uv publish
```

## 🔥 UV vs 传统方式速度对比

| 操作 | 传统方式 | UV 方式 | 速度提升 |
|------|----------|---------|----------|
| **环境创建** | `python -m venv` + `pip install` | `uv sync` | **10x+** |
| **安装依赖** | `pip install -r requirements.txt` | `uv sync` | **10-100x** |
| **添加依赖** | `pip install X` + 手动更新文件 | `uv add X` | **5x+** |
| **构建包** | `pip install build` + `python -m build` | `uv build` | **3x+** |
| **发布包** | `pip install twine` + `twine upload` | `uv publish` | **2x+** |

## 🎯 常用命令速查

### 项目管理
```bash
uv init                  # 初始化新项目
uv sync                  # 同步依赖 (相当于 pip install -r requirements.txt)
uv sync --upgrade        # 更新所有依赖
uv add package           # 添加依赖
uv add --dev pytest     # 添加开发依赖
uv remove package       # 删除依赖
uv tree                  # 显示依赖树
```

### 运行和构建
```bash
uv run script.py        # 运行脚本
uv run pytest          # 运行测试
uv run python -m module # 运行模块
uv build                # 构建包
uv publish              # 发布包
```

### 私有源配置
```bash
# 全局配置私有源
uv config set index-url http://private-pypi.com/simple/
uv config set extra-index-url https://pypi.org/simple/

# 查看配置
uv config list

# 临时使用私有源
uv add package --index-url http://private-pypi.com/simple/
```

## 📋 实际使用场景

### 场景1：新团队成员上手
```bash
# 传统方式 (5-10分钟)
git clone repo
cd repo
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m pytest

# UV 方式 (30秒)
git clone repo
cd repo
uv sync
uv run pytest
```

### 场景2：添加新依赖
```bash
# 传统方式
pip install requests
echo "requests>=2.28.0" >> requirements.txt
# 手动更新 requirements.txt...

# UV 方式 (一步完成)
uv add requests
# 自动更新 pyproject.toml 和 uv.lock
```

### 场景3：CI/CD 构建
```bash
# 传统 GitHub Actions (慢)
- name: Set up Python
  uses: actions/setup-python@v4
- name: Install dependencies
  run: |
    pip install -r requirements.txt
    pip install build twine
- name: Build
  run: python -m build
- name: Publish
  run: twine upload dist/*

# UV GitHub Actions (快)
- name: Install uv
  uses: astral-sh/setup-uv@v1
- name: Build and publish
  run: |
    uv sync
    uv build
    uv publish
```

### 场景4：跨平台开发
```bash
# Windows
uv sync && uv run pytest

# macOS  
uv sync && uv run pytest

# Linux
uv sync && uv run pytest

# 完全一致的行为，无需特殊配置
```

## 🏢 企业使用建议

### 1. 团队配置标准化
```toml
# pyproject.toml - 团队共享
[tool.uv]
index-url = "http://company-pypi.internal/simple/"
extra-index-url = ["https://pypi.org/simple/"]

[tool.uv.sources]
company-package = { url = "http://company-pypi.internal/simple/" }
```

### 2. CI/CD 优化
```yaml
# .github/workflows/ci.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: astral-sh/setup-uv@v1
    - uses: actions/checkout@v4
    - run: uv sync
    - run: uv run pytest
    - run: uv build
    # 比传统方式快 5-10x
```

### 3. 开发容器配置
```dockerfile
# Dockerfile
FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
# 比 pip 快 10x+
```

## 💡 最佳实践

1. **使用 `uv.lock`** - 锁定精确版本，确保团队一致性
2. **配置私有源** - 在 `pyproject.toml` 中统一配置
3. **环境变量认证** - CI/CD 中使用环境变量管理密钥
4. **定期更新** - `uv sync --upgrade` 保持依赖最新
5. **多阶段构建** - Docker 中分离 uv sync 和应用运行

## 🎉 总结

使用 UV 后，Capacity Package 开发变得：
- **更快** - 依赖安装提速 10-100x
- **更简单** - 一个工具完成所有操作  
- **更可靠** - 锁文件确保环境一致性
- **更现代** - 原生支持现代 Python 开发流程

UV 不仅解决了传统 Python 包管理的痛点，更重要的是让开发者专注于业务逻辑而非工具配置！
