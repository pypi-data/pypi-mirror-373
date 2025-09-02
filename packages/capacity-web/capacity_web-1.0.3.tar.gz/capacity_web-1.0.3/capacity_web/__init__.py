# Capacity Web Search Package
# 保持规范v2.1的核心设计理念：功能导向 > 技术导向

"""
Capacity Web Search - 网络搜索功能包

【快速使用】
from capacity_web import search_web

result = search_web("人工智能最新发展")
if result["success"]:
    for item in result["data"]["results"]:
        print(f"{item['title']}: {item['url']}")
"""

__version__ = "1.0.0"

# === 直接在这里放入所有功能代码，保持最简结构 ===

import httpx
from typing import Dict, Any, Optional
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# 全局常量
DEFAULT_API_URL = "https://nextchat-search.zeabur.app/search"
DEFAULT_TIMEOUT = 15
DEFAULT_LANGUAGE = "all"
DEFAULT_SAFE_SEARCH = 0

# 统一异常处理装饰器（保持规范2的要求）
def _handle_api_errors(func_name: str, context_info: str = ""):
    """统一错误处理装饰器工厂"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except httpx.TimeoutException:
                return {"success": False, "data": None, "message": f"搜索请求超时（超过{DEFAULT_TIMEOUT}秒），请稍后重试"}
            except httpx.ConnectError:
                return {"success": False, "data": None, "message": "网络连接失败，请检查网络状态"}
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    return {"success": False, "data": None, "message": "API访问被拒绝，请检查服务状态"}
                elif e.response.status_code == 404:
                    return {"success": False, "data": None, "message": "搜索服务不可用"}
                elif e.response.status_code == 429:
                    return {"success": False, "data": None, "message": "请求频率过高，请稍后重试"}
                elif e.response.status_code >= 500:
                    return {"success": False, "data": None, "message": "搜索服务器内部错误"}
                else:
                    return {"success": False, "data": None, "message": f"HTTP错误: {e.response.status_code}"}
            except ValueError as e:
                return {"success": False, "data": None, "message": str(e)}
            except Exception as e:
                return {"success": False, "data": None, "message": f"{func_name}失败: {str(e)}"}
        return wrapper
    return decorator

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))
)
def _make_request(url: str, params: dict) -> httpx.Response:
    """执行HTTP请求，带标准重试机制"""
    return httpx.get(url, params=params, timeout=DEFAULT_TIMEOUT)

def _validate_query(query) -> str:
    """验证和预处理查询参数"""
    if query is None:
        raise ValueError("查询参数不能为空")
    if not isinstance(query, str):
        raise ValueError("查询参数必须是字符串")
    if not query.strip():
        raise ValueError("查询参数不能为空")
    return query.strip()

@_handle_api_errors("网络搜索")
def search_web(
    query: str,
    language: str = DEFAULT_LANGUAGE,
    max_results: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """进行网络搜索
    
    【快速使用】
    result = search_web("人工智能最新发展")
    if result["success"]:
        for item in result["data"]["results"]:
            print(f"{item['title']}: {item['url']}")
    
    【参数说明】
    query: 搜索关键词，支持中英文和搜索语法
    language: 语言代码，如 "zh", "en", "all"，默认 "all"
    max_results: 最大结果数量，1-100之间，默认使用API默认值
    **kwargs: 高级选项，包括categories, search_engines, page_number, time_range等
    
    【返回值】
    Dict[str, Any]: 标准响应格式
    - success: bool - 操作是否成功
    - data: Dict - 搜索结果数据，包含results列表等
    - message: str - 状态信息
    
    【异常处理】
    网络异常、超时、HTTP错误都会被捕获并返回失败状态
    """
    # 验证输入参数
    validated_query = _validate_query(query)
    
    # 构建基础请求参数
    params = {
        "q": validated_query,
        "language": language,
        "format": kwargs.get("results_format", "json"),
        "pageno": kwargs.get("page_number", 1),
        "safesearch": kwargs.get("safe_search", DEFAULT_SAFE_SEARCH),
        "image_proxy": kwargs.get("image_proxy", True)
    }
    
    # 添加可选参数
    if max_results is not None:
        if not isinstance(max_results, int) or max_results < 1 or max_results > 100:
            return {
                "success": False,
                "data": None,
                "message": "max_results必须是1-100之间的整数"
            }
        params["results_per_page"] = max_results
        
    categories = kwargs.get("categories")
    if categories and isinstance(categories, list):
        params["categories"] = ",".join(categories)
        
    search_engines = kwargs.get("search_engines")
    if search_engines and isinstance(search_engines, list):
        params["engines"] = ",".join(search_engines)
        
    time_range = kwargs.get("time_range")
    if time_range:
        params["time_range"] = time_range
    
    # 执行搜索请求
    response = _make_request(DEFAULT_API_URL, params)
    response.raise_for_status()
    
    # 处理响应数据
    data = response.json()
    results = data.get("results", [])
    
    # 如果指定了max_results，确保结果数量不超过限制
    if max_results is not None and len(results) > max_results:
        results = results[:max_results]
        data = dict(data)  # 创建副本以避免修改原始数据
        data["results"] = results
    
    results_count = len(results)
    
    return {
        "success": True, 
        "data": data, 
        "message": f"搜索成功，找到 {results_count} 条结果"
    }

# 导出的公共API
__all__ = ["search_web"]
