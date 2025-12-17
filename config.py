"""
配置文件 - 存放API密钥和设置
"""

# AI API 配置（选择你要使用的）

# 选项1: OpenAI
OPENAI_API_KEY = "your-openai-api-key"
OPENAI_BASE_URL = "https://api.openai.com/v1"  # 可换成代理地址

# 选项2: Claude
CLAUDE_API_KEY = "your-claude-api-key"

# 选项3: 国内替代（通义千问/文心一言/DeepSeek等）
# DeepSeek 性价比高，推荐国内用户使用
DEEPSEEK_API_KEY = "your-deepseek-api-key"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

# 当前使用的AI服务
CURRENT_AI = "deepseek"  # 可选: "openai", "claude", "deepseek"

# 数据文件路径

DATA_FILE = "data/tasks.json"
