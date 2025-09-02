#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
capacity-web 测试套件
保持规范v2.1的测试理念：经济原则 + 核心功能验证
"""

import pytest
from unittest.mock import Mock, patch
import httpx
from capacity_web import search_web


def test_search_web_success():
    """测试成功搜索 - P0核心功能"""
    # 模拟成功响应
    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [
            {"title": "Test Result 1", "url": "https://example1.com"},
            {"title": "Test Result 2", "url": "https://example2.com"}
        ],
        "query": "test query"
    }
    mock_response.raise_for_status.return_value = None
    
    with patch('capacity_web._make_request', return_value=mock_response):
        result = search_web("test query")
    
    # 验证返回格式符合规范
    assert result["success"] is True
    assert "data" in result
    assert "message" in result
    assert result["data"]["results"]
    assert len(result["data"]["results"]) == 2
    assert "找到 2 条结果" in result["message"]


def test_search_web_validation_error():
    """测试参数验证 - P1边界条件"""
    # 测试空查询
    result = search_web("")
    assert result["success"] is False
    assert "查询参数不能为空" in result["message"]
    
    # 测试None查询
    result = search_web(None)
    assert result["success"] is False
    assert "查询参数不能为空" in result["message"]
    
    # 测试非字符串查询
    result = search_web(123)
    assert result["success"] is False
    assert "查询参数必须是字符串" in result["message"]


def test_search_web_max_results_validation():
    """测试max_results参数验证"""
    # 测试无效的max_results
    result = search_web("test", max_results=0)
    assert result["success"] is False
    assert "max_results必须是1-100之间的整数" in result["message"]
    
    result = search_web("test", max_results=101)
    assert result["success"] is False
    assert "max_results必须是1-100之间的整数" in result["message"]


def test_search_web_network_error():
    """测试网络异常处理 - P2异常处理"""
    with patch('capacity_web._make_request', side_effect=httpx.ConnectError("Connection failed")):
        result = search_web("test query")
    
    assert result["success"] is False
    assert "网络连接失败" in result["message"]


def test_search_web_timeout_error():
    """测试超时异常处理"""
    with patch('capacity_web._make_request', side_effect=httpx.TimeoutException("Timeout")):
        result = search_web("test query")
    
    assert result["success"] is False
    assert "搜索请求超时" in result["message"]


def test_search_web_http_error():
    """测试HTTP状态码错误处理"""
    mock_response = Mock()
    mock_response.status_code = 404
    
    with patch('capacity_web._make_request', side_effect=httpx.HTTPStatusError("Not Found", request=Mock(), response=mock_response)):
        result = search_web("test query")
    
    assert result["success"] is False
    assert "搜索服务不可用" in result["message"]


def test_search_web_max_results_limiting():
    """测试结果数量限制功能"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [
            {"title": f"Result {i}", "url": f"https://example{i}.com"} 
            for i in range(10)  # 返回10个结果
        ]
    }
    mock_response.raise_for_status.return_value = None
    
    with patch('capacity_web._make_request', return_value=mock_response):
        result = search_web("test", max_results=5)
    
    assert result["success"] is True
    assert len(result["data"]["results"]) == 5  # 应该被限制为5个
    assert "找到 5 条结果" in result["message"]


if __name__ == "__main__":
    # 简单的测试运行器，遵循规范的测试输出要求
    print("=== Capacity Web Search 测试套件 ===\n")
    
    tests = [
        ("核心功能测试", test_search_web_success),
        ("参数验证测试", test_search_web_validation_error),
        ("max_results验证", test_search_web_max_results_validation),
        ("网络错误处理", test_search_web_network_error),
        ("超时错误处理", test_search_web_timeout_error),
        ("HTTP错误处理", test_search_web_http_error),
        ("结果数量限制", test_search_web_max_results_limiting),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print(f"⚠️  {total - passed} 个测试失败")
