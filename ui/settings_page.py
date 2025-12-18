"""
设置页面 - API配置界面（颜色兼容版）
"""

import flet as ft
from services.settings_service import SettingsService
from services.ai_service import AIService

# 兼容新旧版本
try:
    colors = ft.Colors
    icons = ft.Icons
except AttributeError:
    colors = ft.colors
    icons = ft.icons

def create_settings_view(
    page: ft.Page, 
    settings_service: SettingsService,
    ai_service: AIService,
    on_close
):
    """创建设置页面"""
    
    providers = settings_service.get_providers()
    current_provider = settings_service.settings.get("ai_provider", "deepseek")
    current_config = settings_service.get_api_config()
    
    status_text = ft.Text("", size=12)
    
    api_key_input = ft.TextField(
        label="API Key",
        value=current_config["api_key"],
        password=True,
        can_reveal_password=True,
        hint_text="请输入你的API密钥",
        expand=True
    )
    
    base_url_input = ft.TextField(
        label="API Base URL（可选，留空使用默认）",
        value=settings_service.settings.get("api_base_url", ""),
        hint_text="例如: https://api.openai.com/v1",
        expand=True
    )
    
    model_input = ft.TextField(
        label="模型名称（可选，留空使用默认）",
        value=settings_service.settings.get("model", ""),
        hint_text="例如: gpt-3.5-turbo",
        expand=True
    )
    
    def on_provider_change(e):
        provider = provider_dropdown.value
        if provider in providers:
            config = providers[provider]
            base_url_input.hint_text = f"默认: {config['base_url']}"
            model_input.hint_text = f"默认: {config['default_model']}"
            page.update()
    
    provider_dropdown = ft.Dropdown(
        label="选择AI服务商",
        value=current_provider,
        options=[
            ft.dropdown.Option(key=k, text=v["name"]) 
            for k, v in providers.items()
        ],
        on_change=on_provider_change,
        expand=True
    )
    
    def save_settings(e):
        settings_service.set_api_config(
            provider=provider_dropdown.value,
            api_key=api_key_input.value.strip(),
            base_url=base_url_input.value.strip(),
            model=model_input.value.strip()
        )
        ai_service.reload_config()
        
        status_text.value = "✅ 设置已保存"
        status_text.color = colors.GREEN
        page.update()
    
    def test_api(e):
        save_settings(e)
        
        status_text.value = "🔄 正在测试连接..."
        status_text.color = colors.BLUE
        page.update()
        
        result = ai_service.test_connection()
        
        if result["success"]:
            status_text.value = "✅ 连接成功！API配置正确"
            status_text.color = colors.GREEN
        else:
            status_text.value = f"❌ 连接失败: {result['error']}"
            status_text.color = colors.RED
        
        page.update()
    
    help_text = ft.Column([
        ft.Text("📖 如何获取API Key？", weight=ft.FontWeight.BOLD, size=14),
        ft.Text("", size=8),
        ft.Text("DeepSeek (推荐):", weight=ft.FontWeight.BOLD, size=12),
        ft.Text("1. 访问 platform.deepseek.com", size=12),
        ft.Text("2. 注册账号并登录", size=12),
        ft.Text("3. 在API Keys页面创建密钥", size=12),
        ft.Text("4. 新用户有免费额度", size=12, color=colors.GREEN),
        ft.Text("", size=8),
        ft.Text("OpenAI:", weight=ft.FontWeight.BOLD, size=12),
        ft.Text("1. 访问 platform.openai.com", size=12),
        ft.Text("2. 注册并绑定支付方式", size=12),
        ft.Text("3. 创建API Key", size=12),
    ], spacing=2)
    
    settings_view = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.IconButton(
                    icon=icons.ARROW_BACK,
                    on_click=on_close
                ),
                ft.Text("⚙️ 设置", size=24, weight=ft.FontWeight.BOLD),
            ]),
            
            ft.Divider(),
            
            ft.Text("🤖 AI API 配置", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("配置AI服务后即可使用智能任务分解功能", 
                   size=12, color=colors.GREY),
            
            ft.Container(height=10),
            
            provider_dropdown,
            
            ft.Container(height=10),
            
            api_key_input,
            
            ft.ExpansionTile(
                title=ft.Text("高级选项", size=14),
                controls=[
                    base_url_input,
                    ft.Container(height=5),
                    model_input,
                ],
                initially_expanded=bool(base_url_input.value or model_input.value)
            ),
            
            ft.Container(height=10),
            
            ft.Row([
                ft.ElevatedButton(
                    "保存设置",
                    icon=icons.SAVE,
                    on_click=save_settings
                ),
                ft.OutlinedButton(
                    "测试连接",
                    icon=icons.WIFI_TETHERING,
                    on_click=test_api
                ),
            ]),
            
            status_text,
            
            ft.Divider(height=30),
            
            help_text,
            
        ], scroll=ft.ScrollMode.AUTO, spacing=5),
        padding=20,
        expand=True
    )
    
    return settings_view