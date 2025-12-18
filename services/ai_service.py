"""
AI服务 - 处理任务智能分解
"""

from openai import OpenAI
from services.settings_service import SettingsService

class AIService:
    def __init__(self, settings_service: SettingsService):
        self.settings_service = settings_service
        self.client = None
        self.model = None
        self._init_client()
        
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

    def _init_client(self):
        """初始化API客户端"""
        if not self.settings_service.is_api_configured():
            self.client = None
            return
        
        config = self.settings_service.get_api_config()
        
        try:
            self.client = OpenAI(
                api_key=config["api_key"],
                base_url=config["base_url"]
            )
            self.model = config["model"]
        except Exception as e:
            print(f"初始化AI客户端失败: {e}")
            self.client = None
    
    def reload_config(self):
        """重新加载配置（设置更改后调用）"""
        self._init_client()
    
    def is_available(self) -> bool:
        """检查AI服务是否可用"""
        return self.client is not None
    
    def test_connection(self) -> dict:
        """测试API连接"""
        if not self.client:
            return {"success": False, "error": "API未配置"}
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "测试连接，请回复OK"}],
                max_tokens=10
            )
            return {"success": True, "message": "连接成功！"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def break_down_task(self, task: str) -> dict:
        """调用AI分解任务"""
        if not self.client:
            return {"success": False, "error": "请先在设置中配置API密钥"}
        
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
            
            import json
            content = response.choices[0].message.content
            
            # 清理markdown代码块
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