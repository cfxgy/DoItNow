"""
任务分解器 - 主程序（颜色兼容版）
"""

import flet as ft
from services.data_service import DataService
from services.settings_service import SettingsService
from services.ai_service import AIService
from ui.settings_page import create_settings_view

# 兼容新旧版本的颜色
try:
    colors = ft.Colors
except AttributeError:
    colors = ft.colors

def main(page: ft.Page):
    # ============ 页面设置 ============
    page.title = "🎯 任务分解器"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 450
    page.window_height = 700
    
    # ============ 初始化服务 ============
    settings_service = SettingsService()
    data_service = DataService()
    ai_service = AIService(settings_service)
    
    current_task_id = None
    main_content = ft.Column(expand=True)
    
    # ============ UI 组件 ============
    
    task_input = ft.TextField(
        label="输入你的任务",
        hint_text="例如：完成毕业论文第三章",
        expand=True,
        on_submit=lambda e: add_task(e)
    )
    
    subtask_input = ft.TextField(label="子任务名称", expand=True)
    time_input = ft.TextField(
        label="分钟", 
        width=80, 
        value="25",
        keyboard_type=ft.KeyboardType.NUMBER
    )
    
    task_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=5)
    subtask_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=5)
    
    progress_bar = ft.ProgressBar(width=300, value=0)
    progress_text = ft.Text("选择一个任务开始", size=12)
    
    ai_status = ft.Text("", size=12, color=colors.BLUE)
    
    # ============ 功能函数 ============
    
    def show_message(message: str, color=colors.GREEN):
        page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        page.snack_bar.open = True
        page.update()
    
    def refresh_task_list():
        task_list.controls.clear()
        tasks = data_service.get_all_tasks()
        
        for task_id, task in tasks.items():
            total = len(task["subtasks"])
            done = sum(1 for s in task["subtasks"] if s["done"])
            progress = f"({done}/{total})" if total > 0 else ""
            
            is_selected = task_id == current_task_id
            is_completed = done == total and total > 0
            
            task_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE if is_completed 
                            else ft.Icons.RADIO_BUTTON_UNCHECKED,
                            color=colors.GREEN if is_completed else colors.GREY,
                            size=20
                        ),
                        ft.Text(
                            f"{task['name']} {progress}",
                            expand=True,
                            weight=ft.FontWeight.BOLD if is_selected else None,
                            size=14
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=colors.RED_400,
                            icon_size=18,
                            on_click=lambda e, tid=task_id: delete_task(tid)
                        )
                    ]),
                    padding=10,
                    border_radius=8,
                    bgcolor=colors.BLUE_100 if is_selected else colors.GREY_100,
                    on_click=lambda e, tid=task_id: select_task(tid)
                )
            )
        page.update()
    
    def refresh_subtask_list():
        subtask_list.controls.clear()
        
        if current_task_id:
            task = data_service.get_task(current_task_id)
            if task:
                for i, subtask in enumerate(task["subtasks"]):
                    subtask_list.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Checkbox(
                                    value=subtask["done"],
                                    on_change=lambda e, idx=i: toggle_subtask(idx)
                                ),
                                ft.Text(
                                    subtask["name"],
                                    expand=True,
                                    size=13,
                                    style=ft.TextStyle(
                                        decoration=ft.TextDecoration.LINE_THROUGH 
                                        if subtask["done"] else None,
                                        color=colors.GREY if subtask["done"] else None
                                    )
                                ),
                                ft.Text(f"{subtask['minutes']}min", 
                                       size=11, color=colors.GREY_600),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    icon_size=14,
                                    on_click=lambda e, idx=i: delete_subtask(idx)
                                )
                            ]),
                            padding=6,
                            border_radius=6,
                            bgcolor=colors.GREEN_50 if subtask["done"] else colors.WHITE
                        )
                    )
                update_progress(task)
        page.update()
    
    def update_progress(task: dict):
        total = len(task["subtasks"])
        done = sum(1 for s in task["subtasks"] if s["done"])
        
        progress_bar.value = done / total if total > 0 else 0
        progress_text.value = f"进度: {done}/{total}"
        
        if done == total and total > 0:
            progress_text.value += " 🎉"
    
    def add_task(e):
        nonlocal current_task_id
        if task_input.value.strip():
            task_id = data_service.add_task(task_input.value.strip())
            current_task_id = task_id
            task_input.value = ""
            refresh_task_list()
            refresh_subtask_list()
            show_message("✅ 任务已创建")
    
    def select_task(task_id: str):
        nonlocal current_task_id
        current_task_id = task_id
        refresh_task_list()
        refresh_subtask_list()
    
    def delete_task(task_id: str):
        nonlocal current_task_id
        data_service.delete_task(task_id)
        if current_task_id == task_id:
            current_task_id = None
        refresh_task_list()
        refresh_subtask_list()
    
    def add_subtask(e):
        if current_task_id and subtask_input.value.strip():
            minutes = int(time_input.value or 25)
            data_service.add_subtask(current_task_id, subtask_input.value.strip(), minutes)
            subtask_input.value = ""
            refresh_subtask_list()
            refresh_task_list()
    
    def toggle_subtask(index: int):
        data_service.toggle_subtask(current_task_id, index)
        refresh_subtask_list()
        refresh_task_list()
    
    def delete_subtask(index: int):
        data_service.delete_subtask(current_task_id, index)
        refresh_subtask_list()
        refresh_task_list()
    
    def ai_break_down(e):
        if not current_task_id:
            show_message("请先选择一个任务", colors.ORANGE)
            return
        
        if not ai_service.is_available():
            show_message("请先在设置中配置API", colors.ORANGE)
            show_settings(None)
            return
        
        task = data_service.get_task(current_task_id)
        if not task:
            return
        
        ai_status.value = "🤖 AI正在分析..."
        page.update()
        
        result = ai_service.break_down_task(task["name"])
        
        if result["success"]:
            subtasks = result["data"]["subtasks"]
            data_service.add_subtasks_batch(current_task_id, subtasks)
            ai_status.value = f"✅ 已生成 {len(subtasks)} 个步骤"
            refresh_subtask_list()
            refresh_task_list()
        else:
            ai_status.value = f"❌ {result['error'][:30]}..."
        
        page.update()
    
    # ============ 导入导出 ============
    
    def show_export_dialog(e):
        export_text = data_service.get_export_string()
        
        dialog = ft.AlertDialog(
            title=ft.Text("📤 导出数据"),
            content=ft.Column([
                ft.Text("复制下方内容到其他设备导入：", size=12),
                ft.TextField(value=export_text, multiline=True, 
                           min_lines=5, max_lines=8, read_only=True)
            ], tight=True, width=350),
            actions=[ft.TextButton("关闭", on_click=lambda e: close_dialog())]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def show_import_dialog(e):
        import_field = ft.TextField(
            hint_text="粘贴导出的数据",
            multiline=True, min_lines=5, max_lines=8
        )
        
        def do_import(e):
            result = data_service.import_from_string(import_field.value)
            if result["success"]:
                show_message(f"✅ 导入 {result['imported']} 个任务")
                refresh_task_list()
                close_dialog()
            else:
                show_message(f"❌ {result['error']}", colors.RED)
        
        dialog = ft.AlertDialog(
            title=ft.Text("📥 导入数据"),
            content=ft.Column([import_field], tight=True, width=350),
            actions=[
                ft.TextButton("取消", on_click=lambda e: close_dialog()),
                ft.ElevatedButton("导入", on_click=do_import)
            ]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def close_dialog():
        page.dialog.open = False
        page.update()
    
    # ============ 页面切换 ============
    
    def show_settings(e):
        main_content.controls.clear()
        main_content.controls.append(
            create_settings_view(page, settings_service, ai_service, show_main)
        )
        page.update()
    
    def show_main(e):
        main_content.controls.clear()
        main_content.controls.append(home_view)
        page.update()
    
    # ============ 主页面布局 ============
    
    api_tip = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=colors.ORANGE),
            ft.Text("未配置AI，点击右上角设置", size=12, color=colors.ORANGE),
        ]),
        visible=not settings_service.is_api_configured()
    )
    
    home_view = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("🎯 任务分解器", size=22, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.IconButton(icon=ft.Icons.UPLOAD, tooltip="导入", 
                                 on_click=show_import_dialog),
                    ft.IconButton(icon=ft.Icons.DOWNLOAD, tooltip="导出", 
                                 on_click=show_export_dialog),
                    ft.IconButton(icon=ft.Icons.SETTINGS, tooltip="设置",
                                 on_click=show_settings),
                ], spacing=0)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            api_tip,
            
            ft.Divider(height=15),
            
            ft.Row([
                task_input,
                ft.ElevatedButton("添加", icon=ft.Icons.ADD, on_click=add_task)
            ]),
            
            ft.Text("📋 我的任务", weight=ft.FontWeight.BOLD, size=14),
            ft.Container(
                content=task_list,
                height=130,
                border=ft.border.all(1, colors.GREY_300),
                border_radius=8,
                padding=8
            ),
            
            ft.Divider(height=15),
            
            ft.Row([
                ft.Text("📝 步骤", weight=ft.FontWeight.BOLD, size=14, expand=True),
                ft.ElevatedButton(
                    "🤖 AI分解",
                    on_click=ai_break_down,
                    bgcolor=colors.PURPLE_400,
                    color=colors.WHITE,
                    height=32
                )
            ]),
            ai_status,
            
            ft.Row([
                subtask_input,
                time_input,
                ft.IconButton(icon=ft.Icons.ADD, on_click=add_subtask)
            ]),
            
            ft.Row([progress_text, progress_bar]),
            
            ft.Container(
                content=subtask_list,
                expand=True,
                border=ft.border.all(1, colors.GREY_300),
                border_radius=8,
                padding=8
            )
        ], spacing=8),
        padding=15,
        expand=True
    )
    
    main_content.controls.append(home_view)
    page.add(main_content)
    refresh_task_list()
    
    if not settings_service.is_api_configured():
        page.snack_bar = ft.SnackBar(
            content=ft.Text("💡 点击右上角设置按钮配置AI API"),
            duration=5000
        )
        page.snack_bar.open = True


if __name__ == "__main__":
    ft.app(target=main)