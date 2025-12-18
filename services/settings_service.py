"""
设置服务 - 管理用户配置（API密钥等）
"""

import json
import os

class SettingsService:
    def __init__(self, settings_file: str = "data/settings.json"):
        self.settings_file = settings_file
        self._ensure_dir()
        self.settings = self._load_settings()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
    
    def _get_default_settings(self) -> dict:
        """默认设置"""
        return {
            "ai_provider": "deepseek",  # openai / deepseek / zhipu / custom
            "api_key": "",
            "api_base_url": "",
            "model": "",
            # 预设的服务商配置
            "providers": {
                "openai": {
                    "name": "OpenAI",
                    "base_url": "https://api.openai.com/v1",
                    "default_model": "gpt-3.5-turbo"
                },
                "deepseek": {
                    "name": "DeepSeek (推荐国内用户)",
                    "base_url": "https://api.deepseek.com/v1",
                    "default_model": "deepseek-chat"
                },
                "zhipu": {
                    "name": "智谱AI (国内)",
                    "base_url": "https://open.bigmodel.cn/api/paas/v4",
                    "default_model": "glm-4-flash"
                },
                "moonshot": {
                    "name": "Moonshot (Kimi)",
                    "base_url": "https://api.moonshot.cn/v1",
                    "default_model": "moonshot-v1-8k"
                },
                "custom": {
                    "name": "自定义",
                    "base_url": "",
                    "default_model": ""
                }
            }
        }
    
    def _load_settings(self) -> dict:
        """加载设置"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    # 合并默认设置（防止新版本添加的配置项丢失）
                    default = self._get_default_settings()
                    default.update(saved)
                    return default
            except:
                return self._get_default_settings()
        return self._get_default_settings()
    
    def save(self):
        """保存设置"""
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
    
    def get_api_config(self) -> dict:
        """获取当前API配置"""
        provider = self.settings["ai_provider"]
        provider_config = self.settings["providers"].get(provider, {})
        
        return {
            "api_key": self.settings["api_key"],
            "base_url": self.settings.get("api_base_url") or provider_config.get("base_url", ""),
            "model": self.settings.get("model") or provider_config.get("default_model", "")
        }
    
    def set_api_config(self, provider: str, api_key: str, 
                       base_url: str = "", model: str = ""):
        """设置API配置"""
        self.settings["ai_provider"] = provider
        self.settings["api_key"] = api_key
        self.settings["api_base_url"] = base_url
        self.settings["model"] = model
        self.save()
    
    def is_api_configured(self) -> bool:
        """检查API是否已配置"""
        return bool(self.settings.get("api_key"))
    
    def get_providers(self) -> dict:
        """获取所有支持的服务商"""
        return self.settings["providers"]