#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON 格式输出 - Capacity Web Package 示例
运行: uv run json_output.py
"""

# /// script
# dependencies = ["capacity-web>=1.0.0"]
# ///

import json
from capacity_web import search_web

# 搜索并以 JSON 格式输出
result = search_web("云计算技术", max_results=3)

# 直接输出完整 JSON (适合程序处理)
print(json.dumps(result, ensure_ascii=False, indent=2))
