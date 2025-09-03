import os
import json
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

from ..utils import logger, get_current_date
from ..content import ContentCleaner, ResearchDocument
from ..search import TavilySearchProvider
from ..llm import LLMProvider


class DeepSearchAgent:
    """简化版搜索代理"""

    def __init__(self, tavily_api_key=None, openai_api_key=None):
        # 初始化配置
        tavily_key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        # 初始化各个组件
        self.search_provider = TavilySearchProvider(tavily_key)
        self.llm = LLMProvider(openai_key)
        self.cleaner = ContentCleaner()
        self.questions = None
        self.document = None
        self.all_content = ""

    def set_research_question(self, question: str) -> None:
        """设置研究问题"""
        self.questions = question
        self.document = ResearchDocument(question)

    def generate_search_strategy(self) -> Dict[str, Any]:
        """生成搜索策略"""
        logger.info("正在生成搜索策略...")
        prompt = self.questions

        system_prompt = f"""当前是{get_current_date()}。你现在是一位搜索策略专家。当我描述一个事件或主题时，请你按照以下要求返回结果：
        1. 分析该事件或主题，识别出与之相关的重要方面，如背景、关键人物、关键事件、影响等（建议4-5个）。
        2. 针对每个方面，请提供1个详细的搜索短语。每个搜索短语应包含足够的描述信息，确保查询内容明确指向该事件或主题的具体情况，避免歧义。
        3. 返回结果必须是有效的 JSON 格式，并且只包含两个顶级键：`event` 和 `analysis`，其中：
            - `event` 的值为事件或主题的名称（字符串）。
            - "analysis" 的值为一个对象，每个键代表一个方面，对应的值为一个字符串，为详细的搜索短语。
        请严格遵守以上要求，并仅返回符合要求的 JSON 格式内容。"""

        result = self.llm.generate_completion(
            system_prompt=system_prompt, user_prompt=prompt, json_format=True
        )
        logger.success("搜索策略生成完成")

        # 如果结果为空，则使用默认值
        if not result:
            return {
                "event": self.questions,
                "analysis": {"default": self.questions},
            }

        return result

    def search_and_extract(self, search_query: str, max_results: int = 5) -> str:
        """执行搜索并提取内容"""
        logger.info(f"🔍 正在分析: {search_query}")
        logger.info("  ├─ 搜索网络资源...")

        # 搜索获取结果
        results = self.search_provider.search(search_query, max_results)
        logger.success(f"  ├─ 搜索完成，获取到 {len(results)} 条结果")

        # 处理结果
        logger.info("  └─ 提取和清洗内容...")
        cleaned_results = []

        for result in results:
            url = result.get("url", "")
            title = result.get("title", "无标题")
            raw_content = result.get("raw_content", "")

            # 使用ContentCleaner清洗内容
            cleaned_content = self.cleaner.clean_with_trafilatura(url, raw_content, title)

            # 如果清洗失败，使用原始内容
            if not cleaned_content:
                cleaned_content = raw_content or result.get("content", "")

            # 对清洗后的内容进行格式标准化
            record = (
                f"来源: {url}\n标题: {title}\n发布日期: {result.get('published_date', '未知')}\n"
                + f"相关度评分: {result.get('score', 0)}\n内容摘要:\n{cleaned_content[:1000]}...\n\n"
                + f"完整内容:\n{cleaned_content}\n\n---\n"
            )
            cleaned_results.append(record)

        combined_result = "".join(cleaned_results)
        logger.success("  └─ 内容提取完成")

        # 添加到研究文档和总内容
        self.document.add_content(combined_result)
        self.all_content += combined_result

        return combined_result

    def generate_report(self) -> str:
        """生成研究报告"""
        logger.info("\n📝 正在生成研究报告...")

        prompt = f"""你是一位领域研究员。请根据 **研究问题** 与 **检索资料**，撰写一份结构清晰、信息密集的 Markdown 报告。
---
### 研究问题
{self.questions}
### 检索资料
{self.document.get_content(127000)}
---
## 输出要求
1. **标题**  
   - 用一句话概括研究主题，作为一级标题 `#`。
2. **分条总结**  
   - 以 `##` 引出多个核心主题（按逻辑或重要性排序）。  
   - 主题示例：概念定义，现状概览、技术突破、案例分析、挑战与空白、未来趋势等。  
   - 在每个主题下，用无序列表 `*` 给出 5–8 条关键信息；可在必要处插入子列表或行内粗体/斜体强调。  
   - 每条信息 1–3 句，既提供事实数据，又给出简要分析或洞见。
3. **篇幅**  
   - **总字数 ≥ 2000 字**。  
4. **引用**    
   - 文末 `### 参考资料` 列出完整来源：作者（如果有）/ 标题 / 链接。
5. **语气与格式**  
   - 保持客观、精炼、逻辑清晰；避免与研究无关的闲谈。  
   - 使用 Markdown 标题、列表、行内标记等，确保易读。
"""

        # 获取流式输出
        stream = self.llm.generate_stream(
            system_prompt="You are a smart assistant.", user_prompt=prompt
        )

        if not stream:
            logger.error("无法创建流式输出")
            return ""

        report = ""
        logger.info("\n--- 研究报告开始 ---\n")

        try:
            for chunk in stream:
                # 安全地处理流块
                if (
                    hasattr(chunk, "choices")
                    and chunk.choices
                    and chunk.choices[0].delta
                    and hasattr(chunk.choices[0].delta, "content")
                    and chunk.choices[0].delta.content
                ):
                    content = chunk.choices[0].delta.content
                    report += content
                    print(content, end="", flush=True)
        except Exception as e:
            logger.error(f"处理流输出时出错: {e}")

        logger.info("\n\n--- 研究报告结束 ---")

        # 保存报告
        self._save_report(report)

        return report

    def _save_report(self, report: str, filepath: str = "/tmp/result.md") -> None:
        """保存报告到文件"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
        logger.success(f"报告已保存到 {filepath}")

    def run(self, question: str) -> str:
        """执行完整研究流程"""
        logger.info(f'\n🚀 开始研究: "{question}"')
        
        # 设置研究问题
        self.set_research_question(question)

        # 生成搜索策略
        search_strategy = self.generate_search_strategy()
        logger.info(f"📊 研究主题: {search_strategy.get('event', question)}")
        logger.info(f"📊 分析策略: {len(search_strategy.get('analysis', {}))} 个关键方面")

        # 获取所有搜索查询
        search_queries = list(search_strategy["analysis"].values())
        logger.info(f"🔍 搜索以下关键方面:")
        for i, query in enumerate(search_queries, 1):
            logger.info(f"  {i}. {query}")
        
        # 使用线程池并发执行搜索
        logger.info("\n🔄 开始并行处理搜索查询...")
        with ThreadPoolExecutor(max_workers=min(10, len(search_queries))) as executor:
            # 提交所有搜索任务
            future_to_query = {executor.submit(self.search_and_extract, query): query for query in search_queries}
            
            # 收集结果
            complete_count = 0
            total_count = len(future_to_query)
            for future in concurrent.futures.as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    # 获取结果 (但我们实际上不需要返回值，因为search_and_extract已经添加到self.document)
                    future.result()
                    complete_count += 1
                    logger.success(f"✅ 已完成 {complete_count}/{total_count} 个查询")
                except Exception as exc:
                    logger.error(f"❌ 查询 '{query}' 生成异常: {exc}")
        
        logger.success("\n✅ 所有搜索查询处理完成!")

        # 生成报告
        report = self.generate_report()

        return report

    def get_factual_background_and_entities(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        根据查询获取事实背景总结和关键实体/关键词
        
        Args:
            query: 搜索查询
            max_results: 获取的新闻搜索结果数量
            
        Returns:
            包含事实背景总结和关键实体/关键词的字典
        """
        logger.info(f"🔍 获取'{query}'的事实背景和关键实体...")
        
        # 1. 通过Tavily API搜索新闻
        logger.info("  ├─ 使用Tavily搜索新闻...")
        
        # 搜索获取结果
        search_results = self.search_provider.search(
            query, max_results=max_results, search_depth="advanced"
        )
        logger.success(f"  ├─ 已获取 {len(search_results)} 条新闻结果")
        
        # 2. 提取和清洗获取的内容
        logger.info("  ├─ 提取和整合内容...")
        
        # 整理所有内容
        all_content = ""
        sources = []
        
        for idx, result in enumerate(search_results, 1):
            if not (result.get("url") and result.get("raw_content", "")):
                continue
            
            url = result.get("url")
            title = result.get("title", "无标题")
            
            # 使用ContentCleaner清洗内容
            cleaned_content = self.cleaner.clean_with_trafilatura(url, result.get("raw_content", ""), title)
            
            # 如果清洗失败，使用原始内容
            if not cleaned_content:
                cleaned_content = result.get("raw_content", "")[:2000]  # 限制长度
                
            # 添加到汇总内容
            all_content += f"新闻 {idx}:\n"
            all_content += f"标题: {title}\n"
            all_content += f"内容: {cleaned_content}\n\n"
            
            # 保存来源信息用于引用
            sources.append({
                "title": title,
                "url": url
            })
        
        logger.success(f"  ├─ 已整合 {len(search_results)} 条内容，共 {len(all_content)} 字符")
        
        # 3. 使用LLM生成事实背景总结
        logger.info("  ├─ 生成事实背景总结...")
        
        system_prompt = "You are a helpful assistant skilled at providing structured factual information in JSON format."
        
        user_prompt = f"""
你是一名专业研究助手，请基于以下与"{query}"相关的新闻内容，完成两项任务:

1. 提供一份简洁但全面的事实背景总结 (500-800字)：
   - 确保逻辑严谨，按时间顺序或因果关系呈现关键事件
   - 只陈述客观事实，不包含个人观点或猜测
   - 明确标注信息存在争议、不确定或尚未证实的情况
   - 避免重复信息，确保总结内容全面且简洁

2. 从以上新闻中提取核心实体｜关键词，用于在百科上搜索信息：
   - 核心实体：直接相关、指代明确且有进一步研究价值的人物、组织、地点等
   - 重要关键词：与主题密切相关、有助于进一步研究的术语和概念

信息来源：
{all_content}

请按以下格式输出结果（使用JSON格式）:
{{
  "factual_background": "事实背景总结...",
  "entities": ["实体1", "实体2", ...],
  "keywords": ["关键词1", "关键词2", ...]
}}
"""
        
        summary_result = self.llm.generate_completion(
            system_prompt=system_prompt, user_prompt=user_prompt, json_format=True
        )
        
        # 处理结果
        if not summary_result:
            logger.error("  ❌ 生成事实背景总结失败")
            summary_result = {"factual_background": "", "entities": [], "keywords": []}
        
        # 添加来源信息
        summary_result["sources"] = sources
        logger.success("  └─ 事实背景总结生成完毕")
        return summary_result