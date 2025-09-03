import time
import requests
from typing import List, Dict, Any
from .utils import logger


class GoogleSearchProvider:
    """处理Google Custom Search API的类"""

    def __init__(self, api_key: str, cx: str = None):
        self.api_key = api_key
        self.cx = cx or "c22e0884b26a04213"  # 默认使用用户提供的cx
        self.max_retries = 3  # 最大重试次数
        self.retry_delay = 2  # 重试间隔（秒）

    def search(
        self, query: str, max_results: int = 5, search_depth: str = "basic"
    ) -> List[Dict[str, Any]]:
        """执行搜索并返回结果，包含重试机制"""
        all_results = []
        
        # 计算需要多少次请求（Google每次最多返回10个结果）
        results_per_request = min(10, max_results)
        total_requests = (max_results + results_per_request - 1) // results_per_request
        
        for request_num in range(total_requests):
            start_index = request_num * results_per_request
            current_max_results = min(results_per_request, max_results - len(all_results))
            
            params = {
                "key": self.api_key,
                "q": query,
                "cx": self.cx,
                "start": start_index,
                "num": current_max_results
            }

            retries = 0
            while retries <= self.max_retries:
                try:
                    # 执行API请求
                    response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
                    response.raise_for_status()  # 如果响应状态码不是2xx，抛出异常

                    result = response.json()
                    items = result.get("items", [])
                    
                    # 转换为标准格式
                    for item in items:
                        formatted_result = {
                            "url": item.get("link", ""),
                            "title": item.get("title", ""),
                            "content": item.get("snippet", ""),
                            "raw_content": item.get("htmlSnippet", ""),
                            "published_date": "未知",  # Google Search API通常不提供发布日期
                            "score": 1.0  # Google不提供相关度评分，使用默认值
                        }
                        all_results.append(formatted_result)
                    
                    break  # 成功执行，跳出重试循环

                except Exception as err:
                    retries += 1
                    if retries > self.max_retries:
                        logger.error(f"搜索失败，已达到最大重试次数 ({self.max_retries}): {err}")
                        break  # 达到最大重试次数，跳出重试循环

                    logger.warning(f"搜索失败，正在重试 ({retries}/{self.max_retries}): {err}")
                    time.sleep(self.retry_delay * retries)  # 加入递增的重试延迟
            
            # 如果已经达到所需结果数量，提前退出
            if len(all_results) >= max_results:
                break

        return all_results[:max_results]  # 确保不超过请求的结果数量


class TavilySearchProvider:
    """处理Tavily搜索API的类"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.max_retries = 3  # 最大重试次数
        self.retry_delay = 2  # 重试间隔（秒）

    def search(
        self, query: str, max_results: int = 5, search_depth: str = "basic"
    ) -> List[Dict[str, Any]]:
        """执行搜索并返回结果，包含重试机制"""
        options = {
            "headers": {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            "json": {
                "query": query,
                "max_results": max_results,
                "topic": "general",
                "search_depth": search_depth,
                "include_answer": False,
                "include_raw_content": False,
            },
        }

        retries = 0
        while retries <= self.max_retries:
            try:
                # 执行API请求
                response = requests.post("https://api.tavily.com/search", **options)
                response.raise_for_status()  # 如果响应状态码不是2xx，抛出异常

                result = response.json()
                return result.get("results", [])

            except Exception as err:
                retries += 1
                if retries > self.max_retries:
                    logger.error(f"搜索失败，已达到最大重试次数 ({self.max_retries}): {err}")
                    return []  # 达到最大重试次数，返回空结果

                logger.warning(f"搜索失败，正在重试 ({retries}/{self.max_retries}): {err}")
                time.sleep(self.retry_delay * retries)  # 加入递增的重试延迟

        return []  # 默认返回空结果（实际上不会执行到这里）