# ⚡ Capacity Web UV 极速部署指南

## 🚀 基于 UV 的现代化工作流

### 超快开发环境设置
```bash
# 克隆代码
git clone <repo>
cd capacity-web

# UV 一键初始化 (极速!)
make init
# 或者
uv sync

# 运行测试 (UV 环境)
make test
# 或者
uv run python tests/test_search.py
uv run pytest tests/ -v

# 开发模式测试
make dev
# 或者
uv run python -c "from capacity_web import search_with_nextchat; print('✅ 导入成功')"
```

### UV 极速构建
```bash
# UV 原生构建 (比 build 更快!)
make build
# 或者
uv build

# 构建完成后，会在 `dist/` 目录生成：
# - capacity_web-1.0.0-py3-none-any.whl (wheel格式)
# - capacity-web-1.0.0.tar.gz (源码包)
```

## 🌍 发布到 PyPI

### 1. 注册 PyPI 账户
- 主站：https://pypi.org/account/register/
- 测试站：https://test.pypi.org/account/register/

### 2. 获取 API Token
```bash
# 访问 https://pypi.org/manage/account/token/
# 创建API token，scope选择整个账户
```

### 3. 配置认证
```bash
# 方法1：环境变量
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-xxxxxxxxxx

# 方法2：配置文件 ~/.pypirc
[pypi]
username = __token__
password = pypi-xxxxxxxxxx

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-xxxxxxxxxx
```

### 4. UV 极速发布流程
```bash
# UV 配置认证 (一次性设置)
export UV_PUBLISH_USERNAME=__token__
export UV_PUBLISH_PASSWORD=pypi-xxxxxxxxxx

# 测试发布 (UV 原生, 超快!)
make test-publish
# 或者
uv publish --repository testpypi

# 测试安装 (UV 极速安装)
uv add --index https://test.pypi.org/simple/ capacity-web

# 正式发布 (UV 原生)
make publish
# 或者
uv publish
```

## 🏢 发布到私有 PyPI 镜像

### 1. 私有仓库选择

#### A. 使用 PyPI Server (简单)
```bash
# 安装
pip install pypiserver

# 运行私有仓库
pypi-server -p 8080 ./packages/

# 发布到私有仓库
python -m twine upload --repository-url http://localhost:8080/ dist/*
```

#### B. 使用 DevPI (推荐)
```bash
# 安装
pip install devpi-server devpi-client

# 启动服务器
devpi-server --start

# 配置客户端
devpi use http://localhost:3141
devpi login root --password=''
devpi index -c dev
devpi use root/dev

# 发布
devpi upload
```

#### C. 使用 Artifactory/Nexus (企业)
```bash
# 发布到 Artifactory
python -m twine upload \
  --repository-url https://your-company.jfrog.io/artifactory/api/pypi/pypi-local/ \
  --username your-username \
  --password your-password \
  dist/*
```

### 2. 私有仓库配置文件
```bash
# ~/.pypirc
[distutils]
index-servers =
    pypi
    testpypi
    private

[private]
repository = http://your-private-pypi.com/simple/
username = your-username
password = your-password
```

### 3. UV 发布到私有仓库
```bash
# UV 直接发布到私有仓库
uv publish --repository-url http://your-private-pypi.com/simple/

# 或者使用 Makefile
make publish-private
```

## 📥 UV 引用私有镜像 (极速配置)

### 1. UV 全局配置 (推荐)
```bash
# 设置默认索引 (一次配置，全局生效)
uv config set index-url http://your-private-pypi.com/simple/

# 添加备用索引 (私有优先，公共备用)
uv config set extra-index-url https://pypi.org/simple/

# 查看当前配置
uv config list
```

### 2. 项目级配置 (最佳实践)
```toml
# pyproject.toml - 团队共享配置
[tool.uv]
index-url = "http://your-private-pypi.com/simple/"
extra-index-url = ["https://pypi.org/simple/"]

# 或者更详细的配置
[[tool.uv.source]]
name = "private"
url = "http://your-private-pypi.com/simple/"
default = true

[[tool.uv.source]]
name = "pypi"
url = "https://pypi.org/simple/"
```

### 3. 环境变量配置 (CI/CD 友好)
```bash
# 一次设置，处处生效
export UV_INDEX_URL=http://your-private-pypi.com/simple/
export UV_EXTRA_INDEX_URL=https://pypi.org/simple/

# 安装包
uv add capacity-web

# 运行脚本
uv run script.py
```

### 4. 命令行快速指定
```bash
# 临时使用私有镜像 (无需配置)
uv add capacity-web --index-url http://your-private-pypi.com/simple/

# 同时使用多个索引 (私有优先)
uv add capacity-web \
  --index-url http://your-private-pypi.com/simple/ \
  --extra-index-url https://pypi.org/simple/

# 运行脚本时指定索引
uv run --index-url http://your-private-pypi.com/simple/ script.py
```

### 5. 私有源认证 (UV 原生支持)
```bash
# 方法1：URL 嵌入认证 (简单)
uv config set index-url http://username:password@private-pypi.com/simple/

# 方法2：环境变量认证 (安全)
export UV_INDEX_USERNAME=your-username
export UV_INDEX_PASSWORD=your-password
export UV_INDEX_URL=http://private-pypi.com/simple/

# 方法3：使用 UV 的认证管理
uv auth add private-pypi.com --username your-username --password-stdin
uv config set index-url http://private-pypi.com/simple/
```

### 6. 混合源策略 (企业推荐)
```toml
# pyproject.toml - 智能回退策略
[tool.uv]
# 优先级：内部私有 -> 公司镜像 -> 官方 PyPI
index-url = "http://internal-pypi.company.com/simple/"
extra-index-url = [
    "http://mirror.company.com/pypi/simple/",
    "https://pypi.org/simple/"
]

# 指定特定包的源
[tool.uv.sources]
capacity-web = { url = "http://internal-pypi.company.com/simple/" }
httpx = { url = "https://pypi.org/simple/" }
```

## 🔄 完整发布工作流

### 开发流程
```bash
# 1. 开发
vim capacity_web/__init__.py

# 2. 测试
make test

# 3. 更新版本号
vim pyproject.toml  # 修改 version = "1.0.1"

# 4. 构建
make clean
make build

# 5. 测试发布
make test-publish

# 6. 测试安装
pip install -i https://test.pypi.org/simple/ capacity-web==1.0.1

# 7. 正式发布
make publish
```

### 自动化发布 (GitHub Actions)
```bash
# 1. 推送 tag 触发自动发布
git tag v1.0.1
git push origin v1.0.1

# 2. GitHub Actions 自动:
#    - 多平台测试
#    - 构建包
#    - 发布到 PyPI
```

## 📋 最佳实践

### 版本管理
- 使用语义化版本：`1.0.0`, `1.0.1`, `1.1.0`, `2.0.0`
- 开发版本：`1.0.0.dev1`, `1.0.0a1`, `1.0.0b1`, `1.0.0rc1`

### 安全考虑
- ✅ 使用 API Token 而非密码
- ✅ 不在代码中硬编码认证信息
- ✅ 使用 `keyring` 管理密码
- ✅ 限制 token 权限范围

### 发布检查清单
- [ ] 更新版本号
- [ ] 运行所有测试
- [ ] 更新 CHANGELOG
- [ ] 先发布到 TestPyPI
- [ ] 验证安装和功能
- [ ] 正式发布到 PyPI
- [ ] 创建 Git tag
- [ ] 更新文档
