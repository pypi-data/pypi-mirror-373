#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单搜索结果展示 - Capacity Web Package 示例
运行: uv run simple_search_display.py
"""

# /// script
# dependencies = ["capacity-web>=1.0.0"]
# ///

from capacity_web import search_web

# 搜索并格式化输出
result = search_web("人工智能最新发展", max_results=5)
if result["success"]:
    print(f"✅ {result['message']}")
    for i, item in enumerate(result["data"]["results"], 1):
        print(f"{i}. {item['title']}")
        print(f"   🔗 {item['url']}")
else:
    print(f"❌ 搜索失败: {result['message']}")
