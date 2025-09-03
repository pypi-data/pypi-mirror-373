#!/usr/bin/env python3
"""
AAlgorithm CLI - 命令行工具入口
"""

import argparse
import sys
from pathlib import Path

from .llm import LLMProvider


def start_autoapi_server():
    """启动 AutoAPI 服务器的 CLI 入口点"""
    parser = argparse.ArgumentParser(
        description='AAlgorithm AutoAPI 服务器 - 将项目功能转换为 API 服务',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  aalgorithm-autoapi                          # 使用默认配置启动
  aalgorithm-autoapi --host 0.0.0.0 --port 8080   # 指定主机和端口
  aalgorithm-autoapi --repository-root /path/to/repo  # 指定仓库根目录
        """
    )

    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='服务器主机地址 (默认: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='服务器端口 (默认: 8080)'
    )
    parser.add_argument(
        '--repository-root',
        type=str,
        default=None,
        help='API 仓库根目录路径 (默认: 当前目录下的 api_repository)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )

    args = parser.parse_args()

    try:
        # 动态导入 autoapi 模块
        from .agents.autoapi import create_project_api_manager, create_project_api_server

        # 确定仓库根目录
        if args.repository_root:
            repository_root = str(Path(args.repository_root).resolve())
        else:
            # 默认使用当前工作目录下的 api_repository
            repository_root = str(Path.cwd() / "api_repository")

        # 确保仓库目录存在
        Path(repository_root).mkdir(parents=True, exist_ok=True)

        print(f"🚀 启动 AAlgorithm AutoAPI 服务器")
        print(f"📍 服务地址: http://{args.host}:{args.port}")
        print(f"📚 API 文档: http://{args.host}:{args.port}/docs")
        print(f"📖 ReDoc 文档: http://{args.host}:{args.port}/redoc")
        print(f"🗃️  仓库目录: {repository_root}")

        if args.debug:
            print("🔍 调试模式已启用")

        # 创建 LLM Provider
        llm_provider = LLMProvider()

        # 创建管理器和服务器
        manager = create_project_api_manager(
            llm_provider=llm_provider,
            repository_root=repository_root
        )
        server = create_project_api_server(manager, args.host, args.port)

        # 启动服务器
        server.run(debug=args.debug)

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("确保已安装必要的依赖包。可以运行: pip install -e .")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main():
    """主入口点（向后兼容）"""
    start_autoapi_server()


if __name__ == "__main__":
    main()
