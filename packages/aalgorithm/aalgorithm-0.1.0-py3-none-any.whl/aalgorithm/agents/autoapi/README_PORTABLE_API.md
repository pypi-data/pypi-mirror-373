# API Repository 使用指南

## 概述

API Repository 采用可迁移架构，通过分离通用配置和机器特定配置，支持在不同机器间灵活部署。本指南将介绍如何配置和使用 API Repository。

## 快速开始

### 1. 配置机器环境

编辑 `api_repository/machine_config.json`，填写实际路径：

```json
{
  "projects": {
    "paddleocr": {
      "project_path": "/your/actual/path/to/PaddleOCR",
      "environment_keys": ["paddleocr_env"]
    },
    "markitdown": {
      "project_path": "/your/actual/path/to/markitdown",
      "environment_keys": ["markitdown_env"]
    }
  },
  "environments": {
    "paddleocr_env": {
      "type": "conda",
      "name": "your_conda_env_name"
    },
    "markitdown_env": {
      "type": "conda",
      "name": "your_markitdown_env"
    }
  }
}
```

### 2. 验证配置

```python
# 运行Python代码验证配置
from src.aalgorithm.agents.autoapi.config_manager import create_config_manager

config_mgr = create_config_manager("api_repository")
validation = config_mgr.validate_config()

if validation["is_valid"]:
    print("✅ 配置有效")
else:
    print("❌ 配置错误:", validation["errors"])
```

## 编程接口使用

### 基本用法

```python
from src.aalgorithm.agents.autoapi.script_repository import create_script_repository

# 创建仓库实例
repo = create_script_repository("api_repository")

# 列出所有项目
projects = repo.list_projects()
print(f"可用项目: {projects}")

# 获取函数信息
func_info = repo.get_function_info("PaddleOCR", "ocr_inference_api")
print(f"项目路径: {func_info['project_path']}")
print(f"脚本路径: {func_info['script_path']}")
print(f"执行命令: {func_info['execution_template']}")
```

### 高级用法

```python
from src.aalgorithm.agents.autoapi.config_manager import create_config_manager
from src.aalgorithm.agents.autoapi.path_resolver import create_path_resolver

# 配置管理
config_mgr = create_config_manager("api_repository")
validation = config_mgr.validate_config()
if not validation["is_valid"]:
    print("配置错误:", validation["errors"])

# 路径解析
path_resolver = create_path_resolver(config_mgr)
exec_cmd = path_resolver.resolve_script_execution_command(
    "paddleocr", "ocr_inference_api.py", "paddleocr_env", "python script.py input.jpg"
)
print(f"完整执行命令: {exec_cmd}")
```

## 配置详解

### 项目配置
```json
{
  "projects": {
    "项目键": {
      "project_path": "项目在本机的绝对路径",
      "environment_keys": ["环境配置键列表"]
    }
  }
}
```

### 环境配置
```json
{
  "environments": {
    "环境键": {
      "type": "环境类型: conda/venv/poetry/system",
      "name": "环境名称或路径",
      "activation_command": "自定义激活命令（可选）"
    }
  }
}
```

### 支持的环境类型

1. **Conda环境**：
```json
{
  "type": "conda",
  "name": "your_env_name"
}
```
生成命令：`conda run -n your_env_name {command}`

2. **虚拟环境**：
```json
{
  "type": "venv",
  "path": "/path/to/venv"
}
```
生成命令：`source /path/to/venv/bin/activate && {command}`

3. **Poetry环境**：
```json
{
  "type": "poetry"
}
```
生成命令：`poetry run {command}`

4. **系统环境**：
```json
{
  "type": "system"
}
```
生成命令：`{command}`

## 常见问题

### Q: 如何检查配置是否正确？
```python
from src.aalgorithm.agents.autoapi.config_manager import create_config_manager

config_mgr = create_config_manager("api_repository")
result = config_mgr.validate_config()

if result["is_valid"]:
    print("✅ 配置有效")
else:
    print("❌ 配置错误:")
    for error in result["errors"]:
        print(f"  - {error}")
```

### Q: 如何添加新项目？
1. 在 `functions/` 目录添加项目功能定义文件
2. 在 `scripts/` 目录添加脚本文件
3. 在 `machine_config.json` 中添加项目和环境配置

### Q: 如何更新现有项目？
直接修改对应的功能定义文件和脚本文件，配置会自动生效。

### Q: 脚本执行失败怎么办？
1. 检查项目路径是否存在
2. 验证环境配置是否正确
3. 确认依赖包已在指定环境中安装
4. 检查脚本文件权限

## 最佳实践

### 1. 目录组织
```
your_project/
├── api_repository/             # API仓库
│   ├── functions/              # 功能定义文件
│   ├── scripts/                # 脚本文件
│   └── machine_config.json    # 机器配置
└── machine_config_backup.json  # 配置备份
```

### 2. 环境管理
- 为每个项目创建独立的conda环境
- 使用描述性的环境名称
- 定期验证环境依赖完整性

### 3. 配置管理
- 备份机器配置文件
- 使用版本控制管理功能定义
- 定期运行配置验证


## 故障排除

### 配置验证失败
```bash
# 检查配置文件格式
python -c "
import json
with open('api_repository/machine_config.json') as f:
    config = json.load(f)
print('配置文件格式正确')
"
```

### 路径解析错误
```python
from src.aalgorithm.agents.autoapi.path_resolver import create_path_resolver
from src.aalgorithm.agents.autoapi.config_manager import create_config_manager

config_mgr = create_config_manager("api_repository")
resolver = create_path_resolver(config_mgr)

# 测试路径解析
paths = resolver.resolve_project_paths("paddleocr", "ocr_inference_api.py")
if paths:
    print(f"项目路径: {paths.project_path}")
    print(f"脚本路径: {paths.script_path}")
else:
    print("路径解析失败，请检查配置")
```

### 环境激活问题
```python
from src.aalgorithm.agents.autoapi.path_resolver import create_path_resolver
from src.aalgorithm.agents.autoapi.config_manager import create_config_manager

config_mgr = create_config_manager("api_repository")
resolver = create_path_resolver(config_mgr)

# 测试环境解析
env = resolver.resolve_environment("paddleocr_env")
if env:
    print(f"环境类型: {env.env_type}")
    print(f"执行模板: {env.execution_command_template}")
else:
    print("环境解析失败，请检查环境配置")
```

## 更多帮助

如果遇到问题，可以：
1. 使用配置验证代码检查配置是否正确
2. 检查日志文件排查具体错误
3. 验证配置文件格式和路径正确性

---

🎉 现在你可以高效地使用 API Repository 了！