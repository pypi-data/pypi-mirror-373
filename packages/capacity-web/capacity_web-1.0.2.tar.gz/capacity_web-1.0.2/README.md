# Capacity Web Search

网络搜索功能包，提供简单易用的网络搜索接口。

## 🚀 快速开始

### 安装
```bash
pip install capacity-web
```

### 使用
```python
from capacity_web import search_web

# 基础搜索
result = search_web("人工智能最新发展")
if result["success"]:
    for item in result["data"]["results"]:
        print(f"{item['title']}: {item['url']}")

# 高级搜索
result = search_web(
    "Python教程",
    language="zh",
    max_results=10,
    categories=["general"],
    time_range="year"
)
```

## 📋 API 文档

### search_web(query, language="all", max_results=None, **kwargs)

进行网络搜索。

**参数:**
- `query` (str): 搜索关键词，必填
- `language` (str): 语言代码，默认 "all"
- `max_results` (int): 最大结果数量，1-100之间
- `**kwargs`: 高级选项

**返回:**
```python
{
    "success": bool,        # 是否成功
    "data": {               # 搜索结果数据
        "results": [...],   # 结果列表
        "query": "...",     # 查询词
        # ...其他数据
    },
    "message": str          # 状态信息
}
```

## ✨ 特性

- **统一返回格式**: 所有API都返回 `{"success": bool, "data": dict, "message": str}` 格式
- **自动重试**: 网络异常时自动重试，最多3次，指数退避
- **完整错误处理**: 捕获所有网络、HTTP、验证错误
- **AI友好**: 简洁的API设计，易于理解和使用
- **类型提示**: 完整的类型注解支持

## 🔧 高级选项

```python
result = search_web(
    "搜索词",
    language="zh",                    # 语言: "zh", "en", "all" 等
    max_results=20,                   # 最大结果数
    page_number=1,                    # 页码
    categories=["general", "news"],   # 搜索类别
    search_engines=["google", "bing"], # 搜索引擎
    time_range="month",               # 时间范围
    safe_search=1,                    # 安全搜索级别
    results_format="json"             # 结果格式
)
```

## 📊 规范兼容

本包遵循 [Simen Capacity  Package 脚本规范 v2.1](https://github.com/capacity/specification)：

- ✅ **功能导向设计**: API以业务功能为核心
- ✅ **统一返回格式**: 标准的成功/失败响应
- ✅ **完整错误处理**: 网络、HTTP、验证异常全覆盖
- ✅ **自动重试机制**: tenacity实现的指数退避重试
- ✅ **AI友好接口**: 清晰的函数签名和文档

## 📝 许可证

MIT License
