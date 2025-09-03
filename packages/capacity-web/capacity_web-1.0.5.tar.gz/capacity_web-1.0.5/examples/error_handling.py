#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理示例 - Capacity Web Package 示例
运行: uv run error_handling.py
"""

# /// script
# dependencies = ["capacity-web>=1.0.2"]
# ///

from capacity_web import search_web

# 测试各种错误情况
test_cases = [
    ("正常搜索", "Python"),
    ("空查询", ""),
    ("无效参数", None),
    ("超大结果数", "test", {"max_results": 200})
]

for case_name, query, *args in test_cases:
    print(f"🧪 测试: {case_name}")
    
    kwargs = args[0] if args else {}
    result = search_web(query, **kwargs)
    
    if result["success"]:
        print(f"  ✅ 成功: {result['message']}")
    else:
        print(f"  ❌ 失败: {result['message']}")
    print()
