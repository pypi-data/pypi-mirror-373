#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量搜索 - Capacity Web Package 示例
运行: uv run batch_search.py
"""

# /// script
# dependencies = ["capacity-web>=1.0.2"]
# ///

from capacity_web import search_web

# 批量搜索多个关键词
keywords = ["Python教程", "JavaScript框架", "数据库设计"]

for keyword in keywords:
    result = search_web(keyword, max_results=2)
    print(f"🔍 搜索: {keyword}")
    
    if result["success"]:
        for item in result["data"]["results"]:
            print(f"  📝 {item['title']}")
    else:
        print(f"  ❌ 搜索失败")
    print()
