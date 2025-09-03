#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级搜索参数 - Capacity Web Package 示例
运行: uv run advanced_search.py
"""

# /// script
# dependencies = ["capacity-web>=1.0.2"]
# ///

from capacity_web import search_web

# 高级搜索配置
result = search_web(
    "机器学习算法",
    language="zh",
    max_results=3,
    categories=["general", "news"],
    time_range="month"
)

if result["success"]:
    print(f"🔍 搜索: 机器学习算法")
    print(f"📊 {result['message']}")
    for item in result["data"]["results"]:
        print(f"📰 {item['title']}")
        print(f"🔗 {item['url']}")
        print()
else:
    print(f"❌ {result['message']}")
