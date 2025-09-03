from dotenv import load_dotenv, find_dotenv

from aalgorithm.agents import DeepResearchAgent
from aalgorithm.utils import logger

load_dotenv(dotenv_path=find_dotenv())

if __name__ == "__main__":
    # 创建实例
    agent = DeepResearchAgent()

    # 获取研究问题
    # question = input("🔍 请输入研究问题: ")
    question = (
        # "6 月 12 日一波音 787 客机在印度坠毁，242 人全部遇难，具体情况如何？事故原因可能是什么？"
        # "海贼王里索隆的左眼为什么是闭着的？"
        # "山东科技大学2025综合评价招生面试禁用红米手机考试，工作人员回应称「属实」，原因可能是什么？"
        # "伊朗首次白天对以色列发动袭击，以总理家庭住所也是目标之一，目前局势如何？将会怎样发展？"
        "金庸小说中，郭靖和张三丰是什么关系"
    )

    # 运行完整研究
    report = agent.run(question)
    logger.success("\n研究报告生成完成!")
    logger.info(f"报告已保存到 /tmp/result.md")
