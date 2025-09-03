from dotenv import load_dotenv, find_dotenv

from aalgorithm.agents.autodeploy.entry import deploy_from_git
from aalgorithm.llm import LLMProvider

load_dotenv(dotenv_path=find_dotenv())

# 创建 LLM 提供者
llm = LLMProvider()

# Git 仓库 URL
git_urls = {
    "ai2apps": "https://github.com/Avdpro/ai2apps.git",
    "FlashTTS": 'https://github.com/HuiResearch/FlashTTS.git',
    "Spark-TTS": "https://github.com/SparkAudio/Spark-TTS.git",
    "WebAgent":"https://github.com/Alibaba-NLP/WebAgent",
    "MeloTTS":"https://github.com/myshell-ai/MeloTTS",
    "sam2":"https://github.com/facebookresearch/sam2",
    "MinerU":"https://github.com/opendatalab/MinerU/",
    "PaddleOCR":"https://github.com/PaddlePaddle/PaddleOCR"

}

# 可选：定义交互处理器
def interaction_handler(message: str, options: list) -> str:
    """处理用户交互的回调函数"""
    print(f"\n{message}")
    print("选项:")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    while True:
        try:
            choice = input("请输入您的选择 (数字或选项名): ").strip().lower()

            # 尝试解析为数字
            if choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(options):
                    return options[choice_idx]

            # 尝试匹配选项名
            for option in options:
                if option.lower() == choice:
                    return option

            print(f"无效选择。请输入 1-{len(options)} 之间的数字或选项名。")

        except KeyboardInterrupt:
            print("\n部署被用户中止。")
            return "abort"
        except EOFError:
            print("\n部署被中止。")
            return "abort"


project_name = 'ai2apps'

success, report = deploy_from_git(
    git_url=git_urls[project_name],
    llm_provider=llm,
    project_name=project_name,
    working_dir="./deployment",
    enable_autoapi=True,  # 启用 AutoAPI
    autoapi_config={'api_port': 8081},  # 简单配置
    save_visualization=True,
    max_fix_depth=2,
    interaction_handler=interaction_handler,
)

# success, report = deploy_from_instructions(
#     instructions=open("./aa.md", "r").read(),
#     llm_provider=llm,
#     project_name="AI2Apps-Instructions",
#     working_dir="./deployment",
#     enable_autoapi=True,  # 启用 AutoAPI
#     autoapi_config={'api_port': 8081},  # 简单配置
#     save_visualization=True,
#     max_fix_depth=2,
#     interaction_handler=interaction_handler,
# )
