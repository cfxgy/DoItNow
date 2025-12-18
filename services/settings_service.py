"""
设置服务 - 管理用户配置（API密钥等）
支持加密存储敏感信息
"""

import json
import os
import base64
import hashlib
from datetime import datetime
from typing import Optional

class Encryptor:
    """简单的加密解密工具"""
    
    def __init__(self, secret_key: str = None):
        # 使用机器特征生成密钥（每台设备不同）
        if secret_key is None:
            secret_key = self._get_machine_key()
        
        # 生成32字节的密钥
        self.key = hashlib.sha256(secret_key.encode()).digest()
    
    def _get_machine_key(self) -> str:
        """获取机器特征作为密钥的一部分"""
        import platform
        
        # 组合多个系统信息
        info = [
            platform.node(),           # 计算机名
            platform.system(),         # 操作系统
            platform.machine(),        # 机器类型
            os.path.expanduser("~"),   # 用户目录
        ]
        return "TaskBreaker_" + "_".join(info)
    
    def encrypt(self, plain_text: str) -> str:
        """加密字符串"""
        if not plain_text:
            return ""
        
        try:
            # 将文本转为字节
            plain_bytes = plain_text.encode('utf-8')
            
            # XOR 加密
            encrypted_bytes = bytes([
                plain_bytes[i] ^ self.key[i % len(self.key)]
                for i in range(len(plain_bytes))
            ])
            
            # Base64 编码
            encrypted_b64 = base64.b64encode(encrypted_bytes).decode('utf-8')
            
            # 添加标记，表示这是加密过的数据
            return "ENC:" + encrypted_b64
            
        except Exception as e:
            print(f"加密失败: {e}")
            return plain_text
    
    def decrypt(self, encrypted_text: str) -> str:
        """解密字符串"""
        if not encrypted_text:
            return ""
        
        # 检查是否是加密过的数据
        if not encrypted_text.startswith("ENC:"):
            # 未加密的数据，直接返回（兼容旧数据）
            return encrypted_text
        
        try:
            # 移除标记
            encrypted_b64 = encrypted_text[4:]
            
            # Base64 解码
            encrypted_bytes = base64.b64decode(encrypted_b64.encode('utf-8'))
            
            # XOR 解密
            decrypted_bytes = bytes([
                encrypted_bytes[i] ^ self.key[i % len(self.key)]
                for i in range(len(encrypted_bytes))
            ])
            
            return decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            print(f"解密失败: {e}")
            return encrypted_text


class SettingsService:
    def __init__(self, settings_file: str = "data/settings.json"):
        self.settings_file = settings_file
        self.encryptor = Encryptor()
        self._ensure_dir()
        self.settings = self._load_settings()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
    
    def _get_default_settings(self) -> dict:
        """默认设置"""
        return {
            "ai_provider": "deepseek",
            "api_key": "",
            "api_base_url": "",
            "model": "",
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
                    
                    # 合并默认设置
                    default = self._get_default_settings()
                    default.update(saved)
                    
                    # 解密 API Key
                    if default.get("api_key"):
                        default["api_key"] = self.encryptor.decrypt(default["api_key"])
                    
                    return default
            except Exception as e:
                print(f"加载设置失败: {e}")
                return self._get_default_settings()
        return self._get_default_settings()
    
    def save(self):
        """保存设置（加密敏感信息）"""
        # 创建副本用于保存
        save_data = self.settings.copy()
        
        # 加密 API Key
        if save_data.get("api_key"):
            save_data["api_key"] = self.encryptor.encrypt(save_data["api_key"])
        
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    def get_api_config(self) -> dict:
        """获取当前API配置（返回解密后的数据）"""
        provider = self.settings["ai_provider"]
        provider_config = self.settings["providers"].get(provider, {})
        
        return {
            "api_key": self.settings["api_key"],  # 已经是解密状态
            "base_url": self.settings.get("api_base_url") or provider_config.get("base_url", ""),
            "model": self.settings.get("model") or provider_config.get("default_model", "")
        }
    
    def set_api_config(self, provider: str, api_key: str, 
                       base_url: str = "", model: str = ""):
        """设置API配置"""
        self.settings["ai_provider"] = provider
        self.settings["api_key"] = api_key  # 内存中保持明文
        self.settings["api_base_url"] = base_url
        self.settings["model"] = model
        self.save()  # 保存时会自动加密
    
    def is_api_configured(self) -> bool:
        """检查API是否已配置"""
        return bool(self.settings.get("api_key"))
    
    def get_providers(self) -> dict:
        """获取所有支持的服务商"""
        return self.settings["providers"]


# 测试代码
if __name__ == "__main__":
    # 测试加密解密
    enc = Encryptor()
    
    original = "sk-1234567890abcdef"
    print(f"原始: {original}")
    
    encrypted = enc.encrypt(original)
    print(f"加密: {encrypted}")
    
    decrypted = enc.decrypt(encrypted)
    print(f"解密: {decrypted}")
    
    print(f"匹配: {original == decrypted}")
    
    # 测试设置服务
    print("\n--- 测试设置服务 ---")
    ss = SettingsService()
    ss.set_api_config("deepseek", "sk-test-key-12345")
    
    # 查看文件内容
    with open("data/settings.json", "r") as f:
        print("文件内容:")
        print(f.read())
    
    # 重新加载验证
    ss2 = SettingsService()
    config = ss2.get_api_config()
    print(f"\n读取到的 API Key: {config['api_key']}")