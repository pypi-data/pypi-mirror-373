#!/usr/bin/env python3
"""
项目API化平台 - 客户端程序
"""

import requests


def register_project(usage_md: str, project_path: str, project_name: str = None,
                     readme_md: str = None, server_url: str = "http://127.0.0.1:8080"):
    """向服务器注册项目API
    
    Args:
        usage_md: 项目使用说明文档
        project_path: 项目本地路径（必传）
        project_name: 项目名称（可选）
        readme_md: README内容（可选）
        server_url: 服务器URL
    """
    # 验证project_path有效性
    from pathlib import Path
    path = Path(project_path)
    if not path.exists():
        raise ValueError(f"项目路径不存在: {project_path}")
    if not path.is_dir():
        raise ValueError(f"项目路径必须是目录: {project_path}")
    
    data = {
        "usage_md": usage_md,
        "project_path": str(path.resolve())  # 使用绝对路径
    }
    if project_name:
        data["project_name"] = project_name
    if readme_md:
        data["readme_md"] = readme_md

    try:
        response = requests.post(f"{server_url}/projects", json=data, timeout=3000)
        return response.json() if response.status_code == 200 else {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """简单的使用示例"""

    result = register_project(
        usage_md=open("tests/autoapi/marker_usage.md", 'r').read(),
        project_path='/opt/marker',  # 现在是必传参数
        project_name="marker",
    )

    if result.get("success"):
        print("✅ 项目API注册成功!")
        print(f"📊 项目: {result.get('project_name', 'markitdown')}")
        print("🌐 API文档: http://127.0.0.1:8080/docs")
    else:
        print(f"❌ 注册失败: {result.get('error')}")


if __name__ == "__main__":
    main()
