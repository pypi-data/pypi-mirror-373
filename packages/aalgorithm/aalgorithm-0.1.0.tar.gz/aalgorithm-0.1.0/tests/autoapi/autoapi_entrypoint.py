#!/usr/bin/env python3
"""
项目API化平台 - 服务器入口点
"""

import sys
from pathlib import Path

from aalgorithm import LLMProvider

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from aalgorithm.agents.autoapi import create_project_api_manager, create_project_api_server


def main():
    """启动API服务器"""
    import argparse

    parser = argparse.ArgumentParser(description='项目API化平台服务器')
    parser.add_argument('--host', default='127.0.0.1', help='主机地址')
    parser.add_argument('--port', type=int, default=8080, help='端口号')
    args = parser.parse_args()

    print(f"🚀 启动API服务器: http://{args.host}:{args.port}")

    # 创建管理器和服务器
    repository_root = str(Path("../../api_repository").resolve())  # 确保绝对路径
    manager = create_project_api_manager(llm_provider=LLMProvider(), repository_root=repository_root)
    server = create_project_api_server(manager, args.host, args.port)

    # 启动服务器
    server.run(debug=False)


if __name__ == "__main__":
    main()
