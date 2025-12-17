"""
AI服务 - 处理任务智能分解
"""

from openai import OpenAI
import config

class AIService:
    def __init__(self):
        # 根据配置选择AI服务
        if config.CURRENT_AI == "openai":
            self.client = OpenAI(
                api_key=config.OPENAI_API_KEY,
                base_url=config.OPENAI_BASE_URL
            )
            self.model = "gpt-3.5-turbo"
            
        elif config.CURRENT_AI == "deepseek":
            self.client = OpenAI(
                api_key=config.DEEPSEEK_API_KEY,
                base_url=config.DEEPSEEK_BASE_URL
            )
            self.model = "deepseek-chat"
        
        # 系统提示词
        self.system_prompt = """你是一个任务分解专家，专门帮助用户克服拖延症。

用户会给你一个任务，你需要：
1. 将任务分解成5-8个具体的小步骤
2. 每个步骤要足够小，让人看到就想立刻开始做
3. 给每个步骤估算时间（单位：分钟）
4. 步骤要按照执行顺序排列

请严格按照以下JSON格式返回，不要有其他内容：
{
    "subtasks": [
        {"name": "步骤名称", "minutes": 预估分钟数},
        {"name": "步骤名称", "minutes": 预估分钟数}
    ]
}

注意：
- 每个步骤最好控制在5-30分钟内
- 第一个步骤要特别简单，降低启动门槛
- 步骤描述要具体、可执行，不要太笼统"""

    def break_down_task(self, task: str) -> dict:
        """
        调用AI分解任务
        
        参数:
            task: 用户输入的任务描述
        返回:
            包含子任务列表的字典
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"请帮我分解这个任务：{task}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # 解析返回的JSON
            import json
            content = response.choices[0].message.content
            
            # 清理可能的markdown代码块标记
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
            if content.endswith("```"):
                content = content.rsplit("```", 1)[0]
            content = content.strip()
            
            result = json.loads(content)
            return {"success": True, "data": result}
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# 测试代码
if __name__ == "__main__":
    ai = AIService()
    result = ai.break_down_task("学习Python爬虫")
    print(result)