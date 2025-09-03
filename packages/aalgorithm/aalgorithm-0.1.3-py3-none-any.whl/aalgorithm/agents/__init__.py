"""
智能代理包
===========

该包提供了各种智能代理，用于不同类型的任务。

当前包含的代理:
- DeepSearchAgent: 用于深度研究和信息收集  
- SimpleSearchAgent: 简化版搜索代理
- AutoDeployAgent: 自动部署代理 (autodeploy 包)
- AutoAPIAgent: 自动API封装代理 (autoapi 包)

注意：
- autodeploy 和 autoapi 是独立的子包，可单独导入使用
- autoapi_integration 提供了 autodeploy 与 autoapi 的集成功能
"""

from .deepresearch import DeepResearchAgent
from .deepsearch import DeepSearchAgent

# autodeploy 和 autoapi 作为独立包，不在此处导入
# 用户可以根据需要导入：
# from aalgorithm.agents.autodeploy import ...
# from aalgorithm.agents.autoapi import ...

__all__ = ["DeepResearchAgent", "DeepSearchAgent"]