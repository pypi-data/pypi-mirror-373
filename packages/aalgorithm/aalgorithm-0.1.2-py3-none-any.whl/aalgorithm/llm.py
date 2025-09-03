import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Any

import diskcache as dc
import openai
from openai import AsyncOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from .utils import logger


class LLMProvider:
    """处理与LLM交互的类"""

    def __init__(self, api_key: str = None, base_url: str = None, cache_dir: str = None):
        api_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
        base_url = (
            base_url if base_url else os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        
        # 初始化 LangChain JSON 解析器
        self.json_parser = JsonOutputParser()
        
        # 从环境变量加载全局模型配置
        self.default_model = os.getenv("LLM_MODEL", "gpt-4.1-mini")
        logger.info(f"使用LLM模型: {self.default_model}")

        # 初始化缓存
        cache_dir = cache_dir or "./cache"
        cache_dir_obj = Path(cache_dir)
        if not cache_dir_obj.exists():
            cache_dir_obj.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建缓存目录: {cache_dir}")
        self.cache = dc.Cache(cache_dir)

    def _escape_for_logging(self, text: str) -> str:
        """
        Escape braces in text to prevent loguru format string conflicts.
        
        Args:
            text: Text that may contain braces that need escaping
            
        Returns:
            Text with braces properly escaped for loguru
        """
        return text.replace("{", "{{").replace("}", "}}")

    def _generate_cache_key(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        json_format: bool,
    ) -> str:
        """生成缓存键"""
        content = f"{system_prompt}|{user_prompt}|{model}|{temperature}|{max_tokens}|{json_format}"
        return hashlib.md5(content.encode()).hexdigest()

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = None,
        temperature: float = 0,
        max_tokens: int = 2000,
        json_format: bool = False,
        use_cache: bool = True,
        cache_expire: int = 3600 * 24 * 7,  # 默认缓存7天
    ) -> Dict[str, Any]:
        """生成非流式回复"""
        # 使用环境变量中的模型或传入的模型
        model = model or self.default_model
        # 生成缓存键
        cache_key = self._generate_cache_key(
            system_prompt, user_prompt, model, temperature, max_tokens, json_format
        )

        # 尝试从缓存获取
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"从缓存获取到结果，键: {cache_key[:8]}...")
                return cached_result

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_format:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = self.client.chat.completions.create(**kwargs)
            if json_format:
                try:
                    # 使用 LangChain 的 JsonOutputParser
                    result = self.json_parser.parse(response.choices[0].message.content)
                except OutputParserException as e:
                    logger.warning(f"LangChain JSON解析失败，尝试备用方法: {e}")
                    # 备用方法：使用 json_repair
                    try:
                        from json_repair import repair_json
                        # 尝试修复JSON格式错误
                        fixed_json = repair_json(response.choices[0].message.content)
                        result = json.loads(fixed_json)
                    except Exception as repair_e:
                        logger.error(f"JSON修复解析也失败: {repair_e}")
                        result = {}
            else:
                result = response.choices[0].message.content

            # 存入缓存
            if use_cache:
                self.cache.set(cache_key, result, expire=cache_expire)
                logger.debug(f"结果已缓存，键: {cache_key[:8]}...")

            return result

        except Exception as e:
            error_msg = self._escape_for_logging(str(e))
            logger.error(f"LLM生成出错: {error_msg}")
            return {} if json_format else {"text": ""}

    async def generate_completion_async(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = None,
        temperature: float = 0,
        max_tokens: int = 2000,
        json_format: bool = False,
        use_cache: bool = True,
        cache_expire: int = 3600 * 24 * 7,  # 默认缓存7天
    ) -> Dict[str, Any]:
        """异步生成非流式回复"""
        # 使用环境变量中的模型或传入的模型
        model = model or self.default_model
        # 生成缓存键
        cache_key = self._generate_cache_key(
            system_prompt, user_prompt, model, temperature, max_tokens, json_format
        )

        # 尝试从缓存获取
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"从缓存获取到结果，键: {cache_key[:8]}...")
                return cached_result

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_format:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = await self.async_client.chat.completions.create(**kwargs)
            if json_format:
                try:
                    # 使用 LangChain 的 JsonOutputParser
                    result = self.json_parser.parse(response.choices[0].message.content)
                except OutputParserException as e:
                    logger.warning(f"LangChain JSON解析失败，尝试备用方法: {e}")
                    # 备用方法：使用 json_repair
                    try:
                        from json_repair import repair_json
                        # 尝试修复JSON格式错误
                        fixed_json = repair_json(response.choices[0].message.content)
                        result = json.loads(fixed_json)
                        if isinstance(result,list) and len(result)==2 and result[0]=='':
                            logger.warning("修复后的JSON结果包含空字符串，尝试提取第二个元素")
                            result = result[1]
                    except Exception as repair_e:
                        logger.error(f"JSON修复解析也失败: {repair_e}")
                        result = {}
            else:
                result = response.choices[0].message.content

            # 存入缓存
            if use_cache:
                self.cache.set(cache_key, result, expire=cache_expire)
                logger.debug(f"结果已缓存，键: {cache_key[:8]}...")

            return result

        except Exception as e:
            error_msg = self._escape_for_logging(str(e))
            logger.error(f"LLM异步生成出错: {error_msg}")
            return {} if json_format else {"text": ""}

    def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = None,
        temperature: float = 0,
        max_tokens: int = 32768,
    ) -> Any:
        """生成流式回复 - 流式响应不使用缓存"""
        # 使用环境变量中的模型或传入的模型
        model = model or self.default_model
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            return self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
        except Exception as e:
            error_msg = self._escape_for_logging(str(e))
            logger.error(f"LLM流式生成出错: {error_msg}")
            return None

    def clear_cache(self):
        """清除所有缓存"""
        self.cache.clear()
        logger.info("缓存已清除")

    def cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            "size": len(self.cache),
            "directory": self.cache.directory,
            "disk_usage": self.cache.volume(),
        }
