from urllib.parse import urlparse
from typing import List, Dict, Any
from .utils import logger


class ContentCleaner:
    """负责内容清洗的类"""
    
    def __init__(self):
        """初始化内容清洗器，添加一个URL缓存"""
        self.url_cache = {}  # 用于存储已处理过的URL的结果
        self.raw_content_cache = {}  # 用于存储已处理过的原始内容的结果
    
    def clean_with_trafilatura(self, url: str, raw_content: str, title: str,clean:bool=True) -> str:
        """使用Trafilatura清洗内容，带有缓存功能"""
        try:
            import trafilatura
            
            # 检查URL缓存
            if url and url in self.url_cache:
                logger.debug(f"命中URL缓存: {url[:50]}...")
                return self.url_cache[url]
            
            # 计算raw_content的缓存键（使用前100个字符作为键）
            raw_content_key = raw_content[:100] if raw_content else None
            if raw_content_key and raw_content_key in self.raw_content_cache:
                logger.debug(f"命中内容缓存: {title[:50]}...")
                return self.raw_content_cache[raw_content_key]

            cleaned_content = ""
            # 尝试从URL获取
            if url and urlparse(url).scheme:
                try:
                    downloaded = trafilatura.fetch_url(url)
                    if downloaded:
                        if clean:
                            extracted_text = trafilatura.extract(
                                downloaded,
                                include_comments=False,
                                include_tables=True,
                                include_links=True,
                                include_images=False,
                            )
                        else:
                            extracted_text = downloaded
                        if extracted_text:
                            cleaned_content = extracted_text
                            # 存入URL缓存
                            self.url_cache[url] = cleaned_content
                            logger.debug(f"成功从URL清洗内容并缓存: {url[:50]}...")
                            return cleaned_content
                except Exception as e:
                    logger.debug(f"从URL清洗失败 ({url[:30]}...): {str(e)}")

            # 尝试从原始HTML内容清洗
            if raw_content:
                try:
                    extracted_text = trafilatura.extract(
                        raw_content,
                        include_comments=False,
                        include_tables=True,
                        include_links=True,
                        include_images=False,
                    )
                    if extracted_text:
                        cleaned_content = extracted_text
                        # 存入内容缓存
                        if raw_content_key:
                            self.raw_content_cache[raw_content_key] = cleaned_content
                        logger.debug(f"成功从HTML清洗内容并缓存: {title[:50]}...")
                        return cleaned_content
                except Exception as e:
                    logger.debug(f"从HTML清洗失败 ({title[:30]}...): {str(e)}")

            # 如果都失败，返回空字符串
            return ""
        except ImportError:
            logger.warning("Trafilatura未安装，无法清洗内容")
            return ""

    def clean_url(self, url: str,clean:bool=True) -> str:
        """
        只接受URL参数并获取清洗后的内容

        Args:
            url: 需要清洗内容的URL

        Returns:
            str: 清洗后的内容，如果清洗失败则返回空字符串
        """
        return self.clean_with_trafilatura(url=url, raw_content="", title="",clean=clean)

    def clear_cache(self):
        """清除缓存"""
        self.url_cache.clear()
        self.raw_content_cache.clear()
        logger.debug("内容清洗缓存已清除")


class ResearchDocument:
    """表示研究文档的类"""

    def __init__(self, question: str):
        self.question = question
        self.content_sections = []
        self.combined_content = ""
        self.sources = {}  # Dictionary to track sources: {url: {title, content_summary, citation_id}}
        self.next_citation_id = 1  # For unique citation identifiers

    def add_content(self, content: str, url: str = None, title: str = None, 
                   published_date: str = None) -> None:
        """添加内容区块，可选添加来源信息"""
        self.content_sections.append(content)
        self.combined_content = "\n".join(self.content_sections)
        
        # Track source if URL provided
        if url and url not in self.sources:
            citation_id = self.next_citation_id
            self.next_citation_id += 1
            self.sources[url] = {
                "title": title or "Untitled",
                "published_date": published_date or "Unknown",
                "citation_id": citation_id
            }

    def get_content(self, max_chars: int = None) -> str:
        """获取截断的内容"""
        if max_chars:
            return self.combined_content[:max_chars]
        return self.combined_content
        
    def get_citation_list(self) -> list:
        """Generate formatted citation list"""
        if not self.sources:
            return []
            
        citations = []
        for url, info in sorted(self.sources.items(), key=lambda x: x[1]["citation_id"]):
            citation = {
                "citation_id": info["citation_id"],
                "title": info["title"],
                "url": url,
                "published_date": info["published_date"]
            }
            citations.append(citation)
            
        return citations
        
    def get_citation_for_url(self, url: str) -> str:
        """Return citation reference for a URL"""
        if url in self.sources:
            return f"[{self.sources[url]['citation_id']}]"
        return ""