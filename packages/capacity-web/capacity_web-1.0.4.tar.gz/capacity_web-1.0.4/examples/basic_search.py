#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础网络搜索 - Capacity Web Package 示例
运行: uv run basic_search.py
"""

# /// script
# dependencies = ["capacity-web>=1.0.2"]
# ///

from capacity_web import search_web

# 简洁实现 - 只调用能力并输出结果
result = search_web("武汉天气")
print(result)
