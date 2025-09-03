import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, cast

from ..content import ContentCleaner, ResearchDocument
from ..llm import LLMProvider
from ..search import GoogleSearchProvider
from ..utils import logger, get_current_date


class DeepResearchAgent:
    """主要研究代理类"""

    def __init__(
        self,
            google_api_key=None,
            google_cx=None,
        openai_api_key=None,
        max_derivation_depth=None,
        max_derivation_width=None,
        llm_model=None,
        llm_temperature=None,
        search_max_results=None,
        search_depth=None,
        report_output_path=None,
    ):
        """初始化DeepResearchAgent，支持从环境变量加载配置

        Args:
            google_api_key: Google Custom Search API密钥，如未提供则从环境变量GOOGLE_API_KEY加载
            google_cx: Google Custom Search Engine ID，如未提供则从环境变量GOOGLE_CX加载，默认为"c22e0884b26a04213"
            openai_api_key: OpenAI API密钥，如未提供则从环境变量OPENAI_API_KEY加载
            max_derivation_depth: 衍生核心方面的最大深度，如未提供则从环境变量RESEARCH_MAX_DERIVATION_DEPTH加载，默认为1
            llm_model: 使用的LLM模型名称，如未提供则从环境变量RESEARCH_LLM_MODEL加载，默认为"gpt-4.1-mini"
            llm_temperature: LLM温度参数，如未提供则从环境变量RESEARCH_LLM_TEMPERATURE加载，默认为0
            search_max_results: 每次搜索返回的最大结果数，如未提供则从环境变量RESEARCH_SEARCH_MAX_RESULTS加载，默认为5
            search_depth: 搜索深度，如未提供则从环境变量RESEARCH_SEARCH_DEPTH加载，默认为"basic"
            report_output_path: 报告输出路径，如未提供则从环境变量RESEARCH_REPORT_PATH加载，默认为"/tmp/result.md"
        """
        # 初始化配置
        google_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        google_cx = google_cx or os.getenv("GOOGLE_CX", "c22e0884b26a04213")
        openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        # 初始化高级配置参数
        self.max_derivation_depth = max_derivation_depth or int(os.getenv("RESEARCH_DEPTH", "1"))
        self.max_derivation_width = max_derivation_width or int(os.getenv("RESEARCH_WIDTH", "10"))
        self.llm_model = llm_model or "gpt-4.1-mini"
        self.llm_temperature = float(llm_temperature or 0)
        self.search_max_results = int(search_max_results or 5)
        self.search_depth = search_depth or "basic"
        self.report_output_path = report_output_path or os.getenv(
            "RESEARCH_REPORT_PATH", "/tmp/result.md"
        )

        # 初始化各个组件
        self.search_provider = GoogleSearchProvider(google_key, google_cx)
        self.llm = LLMProvider(openai_key)
        self.cleaner = ContentCleaner()
        self.document = None

    def set_research_question(self, question: str) -> None:
        """设置研究问题并初始化文档"""
        self.document = ResearchDocument(question)

    def generate_search_strategy(self) -> Dict[str, Any]:
        """生成搜索策略"""
        logger.info("正在生成搜索策略...")

        system_prompt = f"""当前是{get_current_date()}。你是一位专业的研究策略专家。
        请根据我提供的研究问题，制定全面的搜索方案，以确保获取高质量、多角度的信息：

        1. 分析研究问题，识别不超过{self.max_derivation_width}个的核心方面。
        2. 为每个方面创建1-2个精确的搜索短语，确保：
           - 包含足够的上下文和关键词，避免模糊搜索
           - 针对性强，能直接获取该方面的专业信息
           - 适合网络搜索引擎使用
           - 每个短语之间有不同的角度或重点，以最大化信息覆盖范围
        3. 返回格式必须为有效的JSON对象，包含以下两个顶级键：
           - `event`: 字符串，简明概括研究问题的核心主题
           - `analysis`: 对象，键为各个研究方面的名称，值为包含多个搜索短语的数组

        优先关注最新信息、权威来源和多样化观点。仅返回JSON格式结果，不要添加任何额外说明。"""

        result = self.llm.generate_completion(
            system_prompt=system_prompt, user_prompt=self.document.question, json_format=True
        )

        logger.success("搜索策略生成完成")

        # 如果结果为空，则使用默认值
        if not result:
            return {
                "event": self.document.question,
                "analysis": {"default": [self.document.question]},
            }

        # 确保analysis中的值都是数组格式
        analysis = result.get("analysis", {})
        for key, value in analysis.items():
            if isinstance(value, str):
                analysis[key] = [value]

        result["analysis"] = analysis
        return result

    def search_and_extract(self, search_query: str, max_results: int = 5) -> str:
        """执行搜索并提取内容"""
        logger.info(f"🔍 正在分析: {search_query}")
        logger.info("  ├─ 搜索网络资源...")

        # 搜索获取结果
        results = self.search_provider.search(
            search_query, max_results=self.search_max_results, search_depth=self.search_depth
        )
        logger.success(f"  ├─ 搜索完成，获取到 {len(results)} 条结果")

        # 处理结果
        logger.info("  └─ 提取和清洗内容...")
        cleaned_results = []

        # 使用并发处理多个结果的清洗
        def clean_single_result(result):
            url = result.get("url", "")
            title = result.get("title", "无标题")
            content = result.get("content", "")
            raw_content = result.get("raw_content", "")

            # 使用ContentCleaner清洗内容
            cleaned_content = self.cleaner.clean_with_trafilatura(url, raw_content, title)

            # 如果清洗失败，使用原始内容
            if not cleaned_content:
                cleaned_content = raw_content or content

            # 对清洗后的内容进行格式标准化
            return (
                f"来源: {url}\n标题: {title}\n发布日期: {result.get('published_date', '未知')}\n"
                + f"相关度评分: {result.get('score', 0)}\n内容摘要:\n{cleaned_content[:1000]}...\n\n"
                + f"完整内容:\n{cleaned_content}\n\n---\n"
            )

        # 并发处理所有结果
        with ThreadPoolExecutor(max_workers=min(len(results), 10)) as executor:
            cleaned_results = list(executor.map(clean_single_result, results))

        combined_result = "".join(cleaned_results)
        logger.success("  └─ 内容提取完成")

        # 添加到研究文档
        self.document.add_content(combined_result)

        return combined_result

    def generate_report(self) -> str:
        """生成研究报告"""
        logger.info("\n📝 正在生成研究报告...")

        prompt = f"""作为专业研究分析师，请基于以下材料创建一份高质量研究报告。

### 研究问题
{self.document.question}

### 检索资料
{self.document.get_content()}

### 输出要求
1. **结构与格式**
   - 创建一个引人注目的一级标题（#），准确反映研究主题
   - 使用简明摘要作为引言，概述主要发现和结论
   - 运用二级标题（##）组织主要部分，每部分围绕一个核心主题
   - 采用三级标题（###）进一步细分复杂主题
   - 全文采用Markdown格式，充分利用标题层级、列表、粗体和引用

2. **内容要求**
   - 综合多个来源的信息，避免过度依赖单一来源
   - 对比不同观点，提供平衡的分析
   - 纳入相关统计数据、研究发现和专家观点，增强可信度
   - 明确指出信息缺口或有争议的领域
   - **非常重要**：在适当位置保留方括号中的引用标记（如 [1]、[2] 等）

3. **质量标准**
   - 报告篇幅内容丰富
   - 专业、客观的语气，避免过度修饰语
   - 清晰的逻辑流程，段落之间有自然过渡
   - 不要在报告末尾添加参考文献部分，这将由系统自动添加"""

        # 获取流式输出
        stream = self.llm.generate_stream(
            system_prompt="You are a professional research analyst. Always maintain academic citation standards by preserving citation markers in square brackets.",
            user_prompt=prompt,
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

        # 解析报告中使用的引用，并手动添加参考文献部分
        final_report = self._append_references_to_report(report)

        # 保存报告
        self._save_report(final_report)

        return final_report

    def _save_report(self, report: str, filepath: str = None) -> None:
        """保存报告到文件"""
        output_path = filepath or self.report_output_path
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        logger.success(f"报告已保存到 {output_path}")

    def _append_references_to_report(self, report: str) -> str:
        """解析报告并添加参考文献部分"""
        logger.info("正在解析报告并添加参考文献...")

        # 从报告中提取所有引用标记 [1], [2], 等
        import re

        citation_pattern = r"\[(\d+)\]"
        citations_used = set(re.findall(citation_pattern, report))

        if not citations_used:
            logger.warning("未在报告中发现任何引用标记")
            return report

        # 获取完整的引用列表
        all_citations = self.document.get_citation_list()

        # 筛选出报告中使用的引用
        used_references = []
        for citation_id in citations_used:
            try:
                citation_index = int(citation_id) - 1  # 转换为0-索引
                if 0 <= citation_index < len(all_citations):
                    used_references.append(all_citations[citation_index])
                else:
                    logger.warning(f"引用 [{citation_id}] 超出范围")
            except ValueError:
                logger.warning(f"无法解析引用ID: {citation_id}")

        # 构建参考文献部分
        if used_references:
            used_references.sort(key=lambda x: x.get("citation_id", 0))  # 按照引用ID排序
            references_section = "\n\n### 参考文献\n\n"
            for i, ref in enumerate(used_references):
                ref_id = ref.get("citation_id", i + 1)  # 使用引用ID或索引作为标识
                url = ref.get("url", "")
                title = ref.get("title", "无标题")

                # 格式化参考文献条目
                references_section += f"[{ref_id}] {title}. {url}\n\n"

            # 将参考文献部分添加到报告末尾
            final_report = report + references_section
            logger.success(f"成功添加了 {len(used_references)} 条参考文献")
            return final_report
        else:
            return report

    def synthesize_content(
        self, content: str = None, question_suffix: str = None
    ) -> Dict[str, Any]:
        """综合整理收集的内容

        Args:
            content: 可选，要处理的内容。如果未提供，则使用主文档内容。
            question_suffix: 问题后缀，用于生成更具体的提示
        """
        logger.info("正在综合整理收集的内容...")

        # 使用提供的内容或主文档内容
        document_content = content if content is not None else self.document.get_content()

        prompt = f"""作为信息分析专家，请对以下关于"{self.document.question}-{question_suffix or ""}"的收集资料进行综合整理与提炼。
        
### 原始资料
{document_content}

### 任务要求
1. 提取所有资料中的核心信息，识别关键事实、数据和观点
2. 合并重复信息，解决互相矛盾的说法（如有），标明信息来源的可信度
3. 按主题对信息进行结构化组织，确保逻辑连贯
4. 识别信息空白，指出哪些重要方面缺乏充分资料
5. 保留所有重要的原始链接和引用信息

### 输出格式
返回一个结构化的JSON对象，包含以下字段：
- `main_themes`: 数组，包含3-7个主要主题
- `key_facts`: 对象，每个主题对应的关键事实列表
- `controversies`: 数组，存在争议或矛盾的观点
- `missing_info`: 数组，需要进一步研究的信息空白
- `sources`: 数组，整理后的关键信息来源

确保输出可直接用于生成最终研究报告，内容全面、准确且结构清晰。"""

        result = self.llm.generate_completion(
            system_prompt="你是一位专业的信息分析师，擅长从大量资料中提取关键信息并进行结构化整理。",
            user_prompt=prompt,
            json_format=True,
            max_tokens=2000,
        )

        logger.success("内容综合整理完成")
        return result

    def run(self, question: str) -> str:
        """执行完整研究流程"""
        logger.info(f'\n🚀 开始研究: "{question}"')

        # 设置研究问题
        self.set_research_question(question)

        # 生成搜索策略
        search_strategy = self.generate_search_strategy()
        logger.info(f"📊 研究主题: {search_strategy.get('event', question)}")
        logger.info(f"📊 分析策略: {len(search_strategy.get('analysis', {}))} 个关键方面")

        # 1. 并发收集每个核心方面对应的搜索结果
        aspect_raw_data = self.collect_aspect_raw_data_concurrent(search_strategy, question)

        # 2. 并发处理每个核心方面的数据
        aspect_contents = self.process_aspect_data_concurrent(aspect_raw_data, question)

        # 3. 并发针对每个核心方面生成回答并处理衍生问题
        final_contents = self.process_aspects_with_derivation_concurrent(aspect_contents, question)

        # 4. 汇总所有内容到主文档
        for aspect, content in final_contents.items():
            self.document.add_content(f"## {aspect}\n\n{content}\n\n")

        logger.success("\n✅ 所有研究方面处理完成!")

        # 生成最终报告
        report = self.generate_report()

        return report

    def collect_aspect_raw_data_concurrent(
        self, search_strategy: Dict[str, Any], question: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """并发收集每个核心方面的原始搜索结果"""
        logger.info(f"\n📌 开始并发收集核心方面数据")
        aspect_raw_data = {}

        # 定义收集单个方面数据的函数
        def collect_aspect_data(aspect_item):
            aspect, queries = aspect_item
            logger.info(f"  🔍 开始收集核心方面数据: {aspect}")
            aspect_results = []

            # 确保查询是列表形式
            search_phrases = queries if isinstance(queries, list) else [queries]

            # 对每个搜索短语进行查询
            for query in search_phrases:
                logger.info(f"    搜索: {query}")
                # 搜索提供者已内置重试机制
                results = self.search_provider.search(query)

                if not results:
                    logger.warning(f"    ⚠️ 查询 '{query}' 未返回结果")
                    continue

                # 提取URL和content
                for result in results:
                    aspect_results.append(
                        {
                            "url": result.get("url", ""),
                            "title": result.get("title", "无标题"),
                            "content": result.get("content", ""),
                            "raw_content": result.get("raw_content", ""),
                            "published_date": result.get("published_date", "未知"),
                            "score": result.get("score", 0),
                        }
                    )

                logger.success(f"    获取到 {len(results)} 条结果")

            if not aspect_results:
                logger.warning(f"  ⚠️ 核心方面 '{aspect}' 未找到任何数据")

            logger.success(f"  ✅ 核心方面 '{aspect}' 数据收集完成，共 {len(aspect_results)} 条")
            return aspect, aspect_results

        # 并发执行所有方面的数据收集
        aspects = list(search_strategy.get("analysis", {}).items())

        with ThreadPoolExecutor(max_workers=min(len(aspects), 10)) as executor:
            results = list(executor.map(collect_aspect_data, aspects))

        # 整理结果
        for aspect, results in results:
            aspect_raw_data[aspect] = results

        logger.success(f"📊 所有核心方面数据收集完成，共 {len(aspect_raw_data)} 个方面")
        return aspect_raw_data

    def process_aspect_data_concurrent(
        self, aspect_raw_data: Dict[str, List[Dict[str, Any]]], question: str
    ) -> Dict[str, Dict[str, Any]]:
        """并发处理每个核心方面的数据"""
        logger.info(f"\n📊 开始并发处理核心方面数据")

        # 定义处理单个方面的函数
        def process_single_aspect(aspect_item):
            aspect, results = aspect_item
            logger.info(f"  处理核心方面: {aspect}")

            # 使用LLM过滤不相关的URL
            filtered_results = self.filter_relevant_results(aspect, results, question)
            logger.info(f"  '{aspect}' 过滤后剩余 {len(filtered_results)} 条相关结果")

            # 使用trafilatura获取并清洗内容
            cleaned_results = self.fetch_and_clean_content(filtered_results)
            logger.info(f"  '{aspect}' 清洗后获得 {len(cleaned_results)} 条有效内容")

            # 创建临时文档内容
            temp_document_content = "\n\n".join(cleaned_results)

            # 直接使用当前实例处理内容，传递临时内容
            synthesized = self.synthesize_content(temp_document_content,aspect)
            logger.success(f"  ✅ 核心方面 '{aspect}' 处理完成")

            return aspect, synthesized

        # 并发执行所有方面的处理
        aspect_items = list(aspect_raw_data.items())

        with ThreadPoolExecutor(max_workers=min(len(aspect_items), 10)) as executor:
            results = list(executor.map(process_single_aspect, aspect_items))

        # 整理结果
        aspect_contents = {}
        for aspect, synthesized in results:
            aspect_contents[aspect] = synthesized

        logger.success(f"📊 所有核心方面数据处理完成")
        return aspect_contents

    def process_aspects_with_derivation_concurrent(
        self, aspect_contents: Dict[str, Dict[str, Any]], question: str
    ) -> Dict[str, str]:
        """并发处理每个核心方面并处理衍生问题"""
        logger.info(f"\n🔄 开始并发处理核心方面及其衍生问题")

        # 定义处理单个方面的函数
        def process_single_aspect_with_derivation(aspect_item):
            aspect, synthesized = aspect_item
            logger.info(f"  处理核心方面及其衍生: {aspect}")

            # 检查是否需要处理衍生问题
            derivation_check = self.generate_aspect_answer_with_derivation_check(
                aspect, synthesized, question
            )

            # Create an empty citations list if we don't have actual citation data
            citations = []

            # If we have stored cleaned results for this aspect, extract citations
            if hasattr(self, "_cleaned_results_dict"):
                for results_id, results_dict in self._cleaned_results_dict.items():
                    for result in results_dict:
                        if "url" in result and "content" in result:
                            citations.append(
                                {
                                    "url": result.get("url", ""),
                                    "title": result.get("title", ""),
                                    "content": result.get("content", ""),
                                    "citation": result.get("citation", ""),
                                }
                            )

            # 生成针对该方面的基础回答
            base_answer = self.generate_aspect_base_answer(aspect, synthesized, question, citations)

            # 检查是否需要处理衍生问题
            if derivation_check.get("derivation_needed", False) and derivation_check.get(
                "derivation_topics"
            ):
                # 真正的递归处理衍生问题，从深度0开始
                derivation_results = self._recursive_process_derivation_concurrent(
                    aspect, derivation_check.get("derivation_topics", []), question, depth=0
                )
                # 合并当前方面和衍生问题的内容
                final_content = self.combine_aspect_with_derivations(
                    base_answer, derivation_results
                )
            else:
                final_content = base_answer

            logger.success(f"  ✅ 核心方面 '{aspect}' 及其衍生处理完成")
            return aspect, final_content

        # 并发执行所有方面的处理
        aspect_items = list(aspect_contents.items())

        with ThreadPoolExecutor(max_workers=min(len(aspect_items), 10)) as executor:
            results = list(executor.map(process_single_aspect_with_derivation, aspect_items))

        # 整理结果
        final_contents = {}
        for aspect, content in results:
            final_contents[aspect] = content

        logger.success(f"🔄 所有核心方面及其衍生处理完成")
        return final_contents

    def filter_relevant_results(
        self, aspect: str, results: List[Dict[str, Any]], question: str
    ) -> List[Dict[str, Any]]:
        """使用LLM过滤与主题相关的结果"""
        if not results:
            return []

        logger.info(f"  正在过滤 '{aspect}' 方面的相关结果...")

        # 构建批量评估请求
        evaluation_items = []
        for i, result in enumerate(results):
            content = result.get("content", "")
            if not content:
                continue

            evaluation_items.append(
                {
                    "id": i,
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content_preview": content[:500] + ("..." if len(content) > 500 else ""),
                }
            )

        system_prompt = """你是一位专业的研究助手，擅长判断内容与研究主题的相关性。
        你将收到一组搜索结果，每个结果包括标题、URL和内容预览。
        请评估每个结果与给定研究主题的相关程度，只保留真正相关的内容。"""

        user_prompt = f"""研究问题: {question}
        当前研究方面: {aspect}
        
        请评估以下搜索结果是否与研究主题相关。对每个结果返回一个布尔值(true/false)，表示是否应该保留该结果:
        
        {json.dumps(evaluation_items, ensure_ascii=False, indent=2)}
        
        请以JSON格式返回，键为ID，值为布尔值，例如: {{"0": true, "1": false}}"""

        try:
            response = self.llm.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                json_format=True,
                model=self.llm_model,
                temperature=self.llm_temperature,
            )

            filtered_results = []
            if response and isinstance(response, dict):
                for i, result in enumerate(results):
                    if str(i) in response and response[str(i)] is True:
                        filtered_results.append(result)
            else:
                # 如果LLM评估失败，保留所有结果
                logger.warning("  ⚠️ LLM过滤评估失败，保留所有结果")
                filtered_results = results

            return filtered_results

        except Exception as e:
            logger.error(f"  ⚠️ 过滤相关结果时出错: {e}")
            # 出错时保留所有结果
            return results

    def fetch_and_clean_content(self, results: List[Dict[str, Any]]) -> List[str]:
        """Using trafilatura to concurrently fetch and clean content with citation tracking"""
        if not results:
            return []

        logger.info(f"  正在并发清洗 {len(results)} 条内容...")

        cleaned_results_dict = []  # Will store the full result dictionaries

        def clean_result(result):
            url = result.get("url", "")
            title = result.get("title", "无标题")
            raw_content = result.get("raw_content", "")
            published_date = result.get("published_date", "未知")

            # Use ContentCleaner to clean content
            cleaned_content = self.cleaner.clean_with_trafilatura(url, raw_content, title)

            # Use original content if cleaning fails
            if not cleaned_content:
                cleaned_content = raw_content or result.get("content", "")

            # Track this source in the document (if you've implemented the document class)
            if hasattr(self, "document"):
                self.document.add_content("", url=url, title=title, published_date=published_date)
                citation = self.document.get_citation_for_url(url)
            else:
                citation = ""

            result_dict = {
                "url": url,
                "title": title,
                "published_date": published_date,
                "score": result.get("score", 0),
                "content": cleaned_content,
                "citation": citation,
                "formatted_content": (
                    f"来源: {url} {citation}\n标题: {title}\n发布日期: {published_date}\n"
                    + f"相关度评分: {result.get('score', 0)}\n内容摘要:\n{cleaned_content[:1000]}...\n\n"
                    + f"完整内容:\n{cleaned_content}\n\n---\n"
                ),
            }

            # Store the full dict for later use
            cleaned_results_dict.append(result_dict)

            # Return only the formatted content string
            return result_dict["formatted_content"]

        # Concurrently process
        with ThreadPoolExecutor(max_workers=min(len(results), 10)) as executor:
            cleaned_results = list(executor.map(clean_result, results))

        logger.success(f"  ✅ 并发清洗完成，处理了 {len(cleaned_results)} 条内容")

        # Store the dictionaries for later reference (if you need access to the structured data)
        if not hasattr(self, "_cleaned_results_dict"):
            self._cleaned_results_dict = {}
        self._cleaned_results_dict[id(results)] = cleaned_results_dict

        return cleaned_results

    def generate_aspect_answer(
        self, aspect: str, synthesized: Dict[str, Any], question: str
    ) -> str:
        """根据综合内容生成核心方面的回答"""
        logger.info(f"  生成 '{aspect}' 方面的回答...")

        # 构建用于回答的内容
        content = ""

        # 添加主题
        if "main_themes" in synthesized and synthesized["main_themes"]:
            content += "### 主要主题\n"
            for theme in synthesized["main_themes"]:
                content += f"* {theme}\n"
            content += "\n"

        # 添加关键事实
        if "key_facts" in synthesized and synthesized["key_facts"]:
            content += "### 关键事实\n"
            for theme, facts in synthesized["key_facts"].items():
                content += f"**{theme}**:\n"
                for fact in facts:
                    content += f"* {fact}\n"
                content += "\n"

        # 添加争议点
        if "controversies" in synthesized and synthesized["controversies"]:
            content += "### 存在争议的观点\n"
            for controversy in synthesized["controversies"]:
                content += f"* {controversy}\n"
            content += "\n"

        # 添加来源
        if "sources" in synthesized and synthesized["sources"]:
            content += "### 信息来源\n"
            for source in synthesized["sources"]:
                content += f"* {source}\n"
            content += "\n"

        system_prompt = """你是一位专业研究助手，擅长从整理好的资料中提炼出清晰、全面的答案。
        请基于提供的整理资料，就特定研究方面提供详细、准确的回答。"""

        user_prompt = f"""研究问题: {question}
        研究方面: {aspect}
        
        整理资料:
        {content}
        
        请基于以上资料，对"{aspect}"这一研究方面提供详尽、客观的分析。要求:
        1. 从多角度分析这一研究方面
        2. 必要时引用关键事实和数据
        3. 呈现不同观点（如有）
        4. 使用清晰、专业的语言
        5. 使用Markdown格式组织内容，合理使用标题、列表和强调
        """

        result = self.llm.generate_completion(
            system_prompt=system_prompt, user_prompt=user_prompt, json_format=False
        )

        result=cast(str,result)
        return result

    def generate_aspect_answer_with_derivation_check(
        self, aspect: str, synthesized: Dict[str, Any], question: str
    ) -> Dict[str, Any]:
        """根据综合内容检查是否需要处理衍生问题"""
        logger.info(f"  评估 '{aspect}' 方面是否需要衍生...")

        # 构建用于评估的内容
        content = ""

        # 添加主题
        if "main_themes" in synthesized and synthesized["main_themes"]:
            content += "### 主要主题\n"
            for theme in synthesized["main_themes"]:
                content += f"* {theme}\n"
            content += "\n"

        # 添加关键事实
        if "key_facts" in synthesized and synthesized["key_facts"]:
            content += "### 关键事实\n"
            for theme, facts in synthesized["key_facts"].items():
                content += f"**{theme}**:\n"
                for fact in facts:
                    content += f"* {fact}\n"
                content += "\n"

        # 添加争议点
        if "controversies" in synthesized and synthesized["controversies"]:
            content += "### 存在争议的观点\n"
            for controversy in synthesized["controversies"]:
                content += f"* {controversy}\n"
            content += "\n"

        # 添加来源
        if "sources" in synthesized and synthesized["sources"]:
            content += "### 信息来源\n"
            for source in synthesized["sources"]:
                content += f"* {source}\n"
            content += "\n"

        # 主要关注信息空白
        missing_info = synthesized.get("missing_info", [])
        if missing_info:
            content += "### 信息空白\n"
            for info in missing_info:
                content += f"* {info}\n"
            content += "\n"

        system_prompt = """你是一位专业研究质量评估专家，负责判断研究内容的完整性。
    请基于已有资料，判断是否针对已识别的信息空白点进行进一步研究。"""

        user_prompt = f"""研究问题: {question}
    研究方面: {aspect}
    
    整理资料:
    {content}
    
    请直接评估，对于"{aspect}"这一研究方面，现有材料是否足够全面，或者是否需要针对某些信息空白进行进一步研究。
    
    请仅返回有效的JSON对象，包含以下字段:
    - "derivation_needed": 布尔值，表示是否需要进一步研究
    - "derivation_topics": 数组，如果derivation_needed为true，包含需要进一步研究的信息空白点(最多3个，按优先级排序)
    - "reason": 字符串，简要解释为什么需要或不需要进一步研究
    """

        result = self.llm.generate_completion(
            system_prompt=system_prompt, user_prompt=user_prompt, json_format=True
        )

        # 确保返回的是字典类型
        if not result or not isinstance(result, dict):
            logger.warning(f"  ⚠️ 评估 '{aspect}' 方面是否需要衍生时失败，使用默认值")
            return {
                "derivation_needed": False,
                "derivation_topics": [],
                "reason": "评估失败，默认不需要衍生",
            }

        # 确保包含必要字段
        if "derivation_needed" not in result:
            result["derivation_needed"] = False
        if "derivation_topics" not in result:
            result["derivation_topics"] = []
        if "reason" not in result:
            result["reason"] = "未提供理由"

        return result

    def check_if_derivation_needed(
        self, aspect: str, answer: str, synthesized: Dict[str, Any]
    ) -> Dict[str, Any]:
        """检查是否需要处理衍生问题"""
        missing_info = synthesized.get("missing_info", [])
        if not missing_info:
            return {"needed": False}

        system_prompt = """你是一位专业研究质量评估专家，负责判断研究回答的完整性。
        请判断当前回答是否足够完整，或是否需要针对已识别出的信息空白点进行进一步研究。"""

        user_prompt = f"""研究方面: {aspect}
        
        当前回答:
        {answer}
        
        已识别的信息空白:
        {json.dumps(missing_info, ensure_ascii=False, indent=2)}
        
        请评估当前回答是否已经充分覆盖了主要内容，或者是否需要针对某些信息空白进行进一步研究。
        以JSON格式返回以下内容:
        1. "needed": 布尔值，表示是否需要进一步研究
        2. "priorities": 数组，如果needed为true，包含按优先级排序的需要进一步研究的信息空白点（最多3个）
        3. "reason": 字符串，解释为什么需要或不需要进一步研究
        """

        result = self.llm.generate_completion(
            system_prompt=system_prompt, user_prompt=user_prompt, json_format=True
        )

        # 如果评估失败，默认不需要衍生
        if not result or not isinstance(result, dict):
            return {"needed": False}

        return result

    def process_derivation_if_needed(
        self, aspect: str, context: str, synthesized: Dict[str, Any], question: str, depth: int = 0
    ) -> Dict[str, str]:
        """处理衍生问题（如果需要）"""
        # 检查是否已达到最大衍生深度
        if depth >= self.max_derivation_depth:
            logger.info(f"  ⚠️ '{aspect}' 已达到最大衍生深度 {self.max_derivation_depth}")
            return {}

        # 检查是否需要处理衍生问题
        evaluation = self.check_if_derivation_needed(aspect, context, synthesized)

        if not evaluation.get("needed", False):
            logger.info(f"  ✅ '{aspect}' 方面的回答已足够完善，无需处理衍生问题")
            return {}

        # 获取需要处理的衍生问题
        derivation_topics = evaluation.get("priorities", [])
        if not derivation_topics:
            return {}

        logger.info(
            f"  🔄 '{aspect}' 方面需要处理 {len(derivation_topics)} 个衍生问题 (深度: {depth})"
        )

        derivation_results = {}
        for topic in derivation_topics:
            derivation_aspect = f"{aspect} - {topic}"
            logger.info(f"    📎 处理衍生问题: {topic} (深度: {depth})")

            # 为衍生问题创建搜索短语
            search_queries = self.generate_derivation_queries(question, aspect, topic)

            # 收集衍生问题的数据
            results = []
            for query in search_queries:
                search_results = self.search_provider.search(query)
                results.extend(search_results)

            # 过滤相关结果
            filtered_results = self.filter_relevant_results(derivation_aspect, results, question)

            # 清洗内容
            cleaned_results = self.fetch_and_clean_content(filtered_results)

            # 为衍生问题创建临时文档
            temp_document = ResearchDocument(f"{question} - {derivation_aspect}")

            # 添加清洗后的内容
            for result in cleaned_results:
                temp_document.add_content(result)

            # 创建一个新的处理器实例来避免文档状态冲突
            temp_agent = DeepResearchAgent(
                google_api_key=self.search_provider.api_key, google_cx=self.search_provider.cx,
                openai_api_key=self.llm.client.api_key
            )
            temp_agent.document = temp_document
            temp_agent.max_derivation_depth = self.max_derivation_depth  # 确保继承衍生深度设置

            # 处理内容
            synthesized_derivation = temp_agent.synthesize_content()

            # 生成衍生问题的回答
            derivation_answer = temp_agent.generate_aspect_answer(
                derivation_aspect, synthesized_derivation, question
            )

            # 如果深度还没有达到最大值，递归处理下一级衍生问题
            if depth + 1 < self.max_derivation_depth:
                sub_derivations = temp_agent.process_derivation_if_needed(
                    derivation_aspect,
                    derivation_answer,
                    synthesized_derivation,
                    question,
                    depth=depth + 1,
                )

                # 如果有子衍生问题的结果，将其合并到当前衍生问题的回答中
                if sub_derivations:
                    derivation_results[topic] = temp_agent.combine_aspect_with_derivations(
                        derivation_answer, sub_derivations
                    )
            else:
                # 达到最大深度时，直接返回衍生问题的回答
                derivation_results[topic] = derivation_answer

        return derivation_results

    def generate_derivation_queries(self, question: str, aspect: str, topic: str) -> List[str]:
        """生成衍生问题的搜索短语"""
        system_prompt = """你是一位专业的搜索策略专家，擅长创建精确的搜索短语。
    请为给定的研究问题、核心方面和衍生主题创建3-5个有效的搜索短语。
    你必须以有效的JSON格式返回结果，即一个字符串数组。"""

        user_prompt = f"""研究问题: {question}
    核心方面: {aspect}
    衍生主题: {topic}
    
    请创建1-2个针对这个衍生主题的精确搜索短语，确保:
    1. 包含足够的上下文和关键词
    2. 针对性强，适合搜索引擎使用
    3. 每个短语有不同的角度或重点
    
    返回一个搜索短语数组，格式必须是有效的JSON数组，例如:
    ["搜索短语1", "搜索短语2"]
    
    不要包含任何额外解释，只返回JSON数组。
    """

        result = self.llm.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_format=True,
        )

        # 如果LLM返回格式不对，使用默认查询
        if not isinstance(result, list):
            return [
                f"{question} {aspect} {topic}",
                f"{topic} in {aspect}",
                f"{aspect} {topic} research",
            ]

        return result

    def combine_aspect_with_derivations(
        self, context: str, derivation_results: Dict[str, str], max_tokens: int = 2000
    ) -> str:
        """通过LLM智能合并方面内容与其衍生内容，并控制输出长度

        Args:
            context: 原始内容
            derivation_results: 衍生问题的结果字典，键为主题，值为内容
            max_tokens: 生成输出的最大token数

        Returns:
            合并后的内容
        """
        # 如果没有衍生结果，直接返回原文
        if not derivation_results:
            return context

        # 确保context是字符串类型
        if not isinstance(context, str):
            logger.warning("  ⚠️ 在合并衍生内容时收到非字符串类型的context，进行转换")
            context = str(context) if context is not None else ""

        # 准备所有材料，以便LLM整合
        materials = [f"## 主要内容\n\n{context}"]

        for topic, content in derivation_results.items():
            if content and isinstance(content, str) and content.strip():
                materials.append(f"## 延伸: {topic}\n\n{content}")
            elif content:  # 如果内容不是空的但不是字符串
                materials.append(f"## 延伸: {topic}\n\n{str(content)}")

        all_materials = "\n\n".join(materials)

        # 构建提示语
        system_prompt = """你是一位专业的研究内容整合专家，擅长将主要内容与延伸内容融合成一个连贯、全面但简洁的整体。
    请综合所有提供的材料，创建一个结构清晰的统一文档，保持重要信息的同时避免冗余。"""

        user_prompt = f"""请将以下研究内容整合成一个连贯、全面的文档：

{all_materials}

要求:
1. 优先保留主要内容中的核心观点和关键信息
2. 将延伸内容中的重要见解和补充信息融入适当位置
3. 消除重复内容，解决可能存在的矛盾观点
4. 使用清晰的标题层次和Markdown格式
5. 保持专业、客观的语气
6. 确保最终文档结构清晰、逻辑连贯

最终输出应为一个Markdown格式的综合文档，长度适中，内容全面。"""

        try:
            result = self.llm.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                json_format=False,
                max_tokens=max_tokens,
                temperature=0.1,  # 使用较低的temperature以确保内容忠实
            )

            combined_content = cast(str, result)
            # 如果LLM生成失败，回退到简单合并
            if not combined_content:
                logger.warning("  ⚠️ LLM合并内容失败，回退到简单合并")
                return self._simple_combine_aspects(context, derivation_results)

            return combined_content

        except Exception as e:
            logger.error(f"  ⚠️ LLM合并内容时出错: {e}")
            # 出错时回退到简单合并
            return self._simple_combine_aspects(context, derivation_results)

    def _simple_combine_aspects(self, context: str, derivation_results: Dict[str, str]) -> str:
        """简单合并主要内容和衍生内容（作为LLM合并的回退方案）"""
        combined = []
        if context.strip():
            combined.append(context)

        for topic, content in derivation_results.items():
            if isinstance(content, str) and content.strip():
                combined.append(f"### 延伸: {topic}\n\n{content}")
            elif content:
                combined.append(f"### 延伸: {topic}\n\n{str(content)}")

        return "\n\n".join(combined)

    def generate_aspect_base_answer(
        self,
        aspect: str,
        synthesized: Dict[str, Any],
        question: str,
        citations: List[Dict[str, Any]],
    ) -> str:
        """Generate base answer with citations for a research aspect"""
        logger.info(f"  生成 '{aspect}' 方面的基础回答...")

        # Build content with citations
        content = ""

        # Add themes
        if "main_themes" in synthesized and synthesized["main_themes"]:
            content += "### 主要主题\n"
            for theme in synthesized["main_themes"]:
                if theme:  # Check if theme is not empty
                    content += f"* {theme}\n"
            content += "\n"

        # Add key facts with citations
        if "key_facts" in synthesized and synthesized["key_facts"]:
            content += "### 关键事实\n"
            for theme, facts in synthesized["key_facts"].items():
                if theme:  # Check if theme is not empty
                    content += f"**{theme}**:\n"
                    for fact in facts:
                        if fact:  # Check if fact is not empty
                            # Try to find citation for this fact
                            citation_refs = self._find_citations_for_content(fact, citations)
                            citation_text = " " + " ".join(citation_refs) if citation_refs else ""
                            content += f"* {fact}{citation_text}\n"
                    content += "\n"

        # Add controversies with citations
        if "controversies" in synthesized and synthesized["controversies"]:
            content += "### 存在争议的观点\n"
            for controversy in synthesized["controversies"]:
                if controversy:  # Check if controversy is not empty
                    # Try to find citation
                    citation_refs = self._find_citations_for_content(controversy, citations)
                    citation_text = " " + " ".join(citation_refs) if citation_refs else ""
                    content += f"* {controversy}{citation_text}\n"
            content += "\n"

        # Add sources with citation IDs
        if "sources" in synthesized and synthesized["sources"]:
            content += "### 信息来源\n"
            for i, source in enumerate(synthesized["sources"]):
                if source:  # Check if source is not empty
                    url = self._extract_url_from_source(str(source))
                    citation = self.document.get_citation_for_url(url) if url else f"[S{i + 1}]"
                    content += f"* {source} {citation}\n"
            content += "\n"

        system_prompt = """你是一位专业的研究助手，擅长从整理好的资料中提炼出清晰、全面的答案。
    请基于提供的整理资料，对特定研究方面提供详尽、客观的分析。
    非常重要：当引用资料中的事实或观点时，请保留方括号中的引用标记（如[1]、[2]等）。"""

        user_prompt = f"""研究问题: {question}
    研究方面: {aspect}

    整理资料:
    {content}

    请基于以上资料，对"{aspect}"这一研究方面提供详尽、客观的分析。要求:
    - 从多角度分析这一研究方面
    - 必要时引用关键事实和数据，保留原始引用标记（如[1]、[2]）
    - 呈现不同观点（如有）
    - 使用清晰、专业的语言
    - 使用Markdown格式组织内容，合理使用标题、列表和强调"""

        result = self.llm.generate_completion(
            system_prompt=system_prompt, user_prompt=user_prompt, json_format=False, max_tokens=2000
        )
        result = cast(str, result)
        return result

    def _find_citations_for_content(
        self, content_text: str, citations: List[Dict[str, Any]]
    ) -> List[str]:
        """Find relevant citations for a piece of content"""
        relevant_citations = []

        # Make sure content_text is a string
        if not isinstance(content_text, str):
            # If it's a dictionary, try to extract text content from common keys
            if isinstance(content_text, dict):
                if "text" in content_text:
                    content_text = content_text["text"]
                elif "content" in content_text:
                    content_text = content_text["content"]
                else:
                    # Convert the entire dict to string as fallback
                    content_text = str(content_text)
            else:
                # Convert to string as fallback for other types
                content_text = str(content_text)

        # Now that content_text is definitely a string, proceed with search
        for citation in citations:
            if "content" not in citation or not citation["content"]:
                continue

            citation_content = citation["content"]
            # Make sure citation_content is a string
            if not isinstance(citation_content, str):
                citation_content = str(citation_content)

            # Check if content appears in citation
            if content_text.lower() in citation_content.lower():
                relevant_citations.append(citation["citation"])

        return relevant_citations

    def _extract_url_from_source(self, source_text: str) -> str:
        """Extract URL from source text if present"""
        # Simple extraction - look for http:// or https://
        if "http://" in source_text:
            start_idx = source_text.find("http://")
            end_idx = source_text.find(" ", start_idx)
            return source_text[start_idx:end_idx] if end_idx > 0 else source_text[start_idx:]
        elif "https://" in source_text:
            start_idx = source_text.find("https://")
            end_idx = source_text.find(" ", start_idx)
            return source_text[start_idx:end_idx] if end_idx > 0 else source_text[start_idx:]
        return ""

    def process_single_aspect(self, aspect_data):
        """Process a single research aspect"""
        aspect, result_list = aspect_data

        logger.info(f"  处理研究方面: '{aspect}'...")

        # 清理内容
        cleaned_results = self.fetch_and_clean_content(result_list)

        # Extract the content strings from the cleaned results dictionaries
        content_strings = [result.get("formatted_content", "") for result in cleaned_results]

        # Join the content strings
        temp_document_content = "\n\n".join(content_strings)

        # Synthesize content
        synthesized = self.synthesize_content_for_aspect(aspect, temp_document_content)

        # Generate a base answer for this aspect
        aspect_answer = self.generate_aspect_base_answer(
            aspect, synthesized, self.question, cleaned_results
        )

        logger.success(f"  ✅ 成功处理了研究方面 '{aspect}'")

        return {
            "aspect": aspect,
            "answer": aspect_answer,
            "synthesized": synthesized,
            "sources": [result.get("url") for result in cleaned_results],
            "citations": [
                {
                    "url": result.get("url"),
                    "title": result.get("title"),
                    "content": result.get("content", ""),
                    "citation": result.get("citation", ""),
                }
                for result in cleaned_results
            ],
        }

    def synthesize_content_for_aspect(self, aspect: str, content: str) -> Dict[str, Any]:
        """针对特定研究方面合成内容"""
        logger.info(f"  合成 '{aspect}' 方面的内容...")

        # 使用synthesize_content方法，传入特定研究方面的内容
        return self.synthesize_content(content)

    def _recursive_process_derivation_concurrent(
        self, parent_aspect: str, derivation_topics: List[str], question: str, depth: int = 0
    ) -> Dict[str, str]:
        """并发处理衍生主题"""
        if depth >= self.max_derivation_depth:
            logger.info(f"  已达到最大衍生深度 {self.max_derivation_depth}，停止进一步衍生")
            return {}

        logger.info(
            f"  处理 '{parent_aspect}' 的 {len(derivation_topics)} 个衍生主题 (深度: {depth})"
        )

        # 定义处理单个衍生主题的函数
        def process_single_derivation(topic):
            derivation_aspect = f"{parent_aspect} - {topic}"
            logger.info(f"    处理衍生主题: '{topic}'")

            # 生成衍生主题的搜索短语
            search_queries = self.generate_derivation_queries(question, parent_aspect, topic)
            logger.info(f"    为 '{topic}' 生成了 {len(search_queries)} 个搜索短语")

            # 收集衍生主题的搜索结果
            results = []
            for query in search_queries:
                search_results = self.search_provider.search(
                    query, max_results=max(3, self.search_max_results - 2)
                )
                results.extend(search_results)

            logger.info(f"    '{topic}' 收集到 {len(results)} 条搜索结果")

            # 过滤相关结果
            filtered_results = self.filter_relevant_results(derivation_aspect, results, question)
            logger.info(f"    '{topic}' 过滤后剩余 {len(filtered_results)} 条相关结果")

            # 清洗内容
            cleaned_results = self.fetch_and_clean_content(filtered_results)

            # 提取内容字符串
            content_strings = []
            for result in cleaned_results:
                if isinstance(result, str):
                    content_strings.append(result)
                elif isinstance(result, dict) and "formatted_content" in result:
                    content_strings.append(result["formatted_content"])

            temp_document_content = "\n\n".join(content_strings)

            # 综合内容
            synthesized = self.synthesize_content(temp_document_content)

            # 准备引用列表
            citations = []
            if hasattr(self, "_cleaned_results_dict"):
                for results_id, results_dict in self._cleaned_results_dict.items():
                    for result in results_dict:
                        if "url" in result and "content" in result:
                            citations.append(
                                {
                                    "url": result.get("url", ""),
                                    "title": result.get("title", ""),
                                    "content": result.get("content", ""),
                                    "citation": result.get("citation", ""),
                                }
                            )

            # 生成回答
            answer = self.generate_aspect_base_answer(
                derivation_aspect, synthesized, question, citations
            )

            # 检查是否需要进一步衍生
            if depth + 1 < self.max_derivation_depth:
                derivation_check = self.generate_aspect_answer_with_derivation_check(
                    derivation_aspect, synthesized, question
                )

                if derivation_check.get("derivation_needed", False) and derivation_check.get(
                    "derivation_topics"
                ):
                    sub_topics = derivation_check.get("derivation_topics", [])
                    logger.info(f"    '{topic}' 需要进一步衍生 {len(sub_topics)} 个子主题")

                    # 递归处理子衍生主题
                    sub_derivations = self._recursive_process_derivation_concurrent(
                        derivation_aspect, sub_topics, question, depth=depth + 1
                    )

                    # 合并当前回答与子衍生内容
                    if sub_derivations:
                        answer = self.combine_aspect_with_derivations(answer, sub_derivations)

            logger.success(f"    ✅ 衍生主题 '{topic}' 处理完成")
            return topic, answer

        # 并发处理所有衍生主题
        with ThreadPoolExecutor(max_workers=min(len(derivation_topics), 3)) as executor:
            results = list(executor.map(process_single_derivation, derivation_topics))

        # 整理结果
        derivation_results = {}
        for topic, content in results:
            derivation_results[topic] = content

        return derivation_results
