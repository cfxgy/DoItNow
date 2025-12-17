"""
任务分解器 - 主程序
告别拖延症，从分解任务开始！
"""

import flet as ft
from services.data_service import DataService
from services.ai_service import AIService

def main(page: ft.Page):
    # ============ 页面设置 ============
    page.title = "🎯 任务分解器 - 告别拖延症"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.window_width = 500
    page.window_height = 700
    
    # ============ 初始化服务 ============
    data_service = DataService()
    ai_service = AIService()
    
    # 当前选中的任务
    current_task_id = None
    
    # ============ UI 组件 ============
    
    # 任务输入
    task_input = ft.TextField(
        label="输入你的任务",
        hint_text="例如：完成毕业论文第三章",
        expand=True,
        on_submit=lambda e: add_task(e)
    )
    
    # 子任务输入
    subtask_input = ft.TextField(label="子任务名称", expand=True)
    time_input = ft.TextField(
        label="分钟", 
        width=80, 
        value="25",
        keyboard_type=ft.KeyboardType.NUMBER
    )
    
    # 任务列表和子任务列表
    task_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=5)
    subtask_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=5)
    
    # 进度显示
    progress_bar = ft.ProgressBar(width=400, value=0)
    progress_text = ft.Text("选择一个任务开始")
    
    # AI状态显示
    ai_status = ft.Text("", color=ft.colors.BLUE)
    
    # ============ 功能函数 ============
    
    def show_message(message: str, color=ft.colors.GREEN):
        """显示提示消息"""
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color
        )
        page.snack_bar.open = True
        page.update()
    
    def refresh_task_list():
        """刷新主任务列表"""
        task_list.controls.clear()
        tasks = data_service.get_all_tasks()
        
        for task_id, task in tasks.items():
            # 计算完成进度
            total = len(task["subtasks"])
            done = sum(1 for s in task["subtasks"] if s["done"])
            progress = f"({done}/{total})" if total > 0 else ""
            
            is_selected = task_id == current_task_id
            
            task_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            ft.icons.CHECK_CIRCLE if done == total and total > 0 
                            else ft.icons.RADIO_BUTTON_UNCHECKED,
                            color=ft.colors.GREEN if done == total and total > 0 
                            else ft.colors.GREY
                        ),
                        ft.Text(
                            f"{task['name']} {progress}",
                            expand=True,
                            weight=ft.FontWeight.BOLD if is_selected else None
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE_OUTLINE,
                            icon_color=ft.colors.RED_400,
                            icon_size=20,
                            on_click=lambda e, tid=task_id: delete_task(tid)
                        )
                    ]),
                    padding=10,
                    border_radius=8,
                    bgcolor=ft.colors.BLUE_100 if is_selected else ft.colors.GREY_100,
                    on_click=lambda e, tid=task_id: select_task(tid)
                )
            )
        page.update()
    
    def refresh_subtask_list():
        """刷新子任务列表"""
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
                                    style=ft.TextStyle(
                                        decoration=ft.TextDecoration.LINE_THROUGH 
                                        if subtask["done"] else None,
                                        color=ft.colors.GREY if subtask["done"] 
                                        else None
                                    )
                                ),
                                ft.Text(
                                    f"{subtask['minutes']}分钟",
                                    color=ft.colors.GREY_600
                                ),
                                ft.IconButton(
                                    icon=ft.icons.CLOSE,
                                    icon_size=16,
                                    on_click=lambda e, idx=i: delete_subtask(idx)
                                )
                            ]),
                            padding=8,
                            border_radius=6,
                            bgcolor=ft.colors.GREEN_50 if subtask["done"] 
                            else ft.colors.WHITE
                        )
                    )
                
                # 更新进度
                update_progress(task)
        
        page.update()
    
    def update_progress(task: dict):
        """更新进度条"""
        total = len(task["subtasks"])
        done = sum(1 for s in task["subtasks"] if s["done"])
        
        progress_bar.value = done / total if total > 0 else 0
        progress_text.value = f"进度: {done}/{total}"
        
        if done == total and total > 0:
            progress_text.value += " 🎉 完成！"
    
    def add_task(e):
        """添加主任务"""
        nonlocal current_task_id
        if task_input.value.strip():
            task_id = data_service.add_task(task_input.value.strip())
            current_task_id = task_id
            task_input.value = ""
            
            refresh_task_list()
            refresh_subtask_list()
            show_message("✅ 任务已创建，点击AI分解或手动添加子任务")
    
    def select_task(task_id: str):
        """选择任务"""
        nonlocal current_task_id
        current_task_id = task_id
        refresh_task_list()
        refresh_subtask_list()
    
    def delete_task(task_id: str):
        """删除任务"""
        nonlocal current_task_id
        data_service.delete_task(task_id)
        if current_task_id == task_id:
            current_task_id = None
        refresh_task_list()
        refresh_subtask_list()
        show_message("已删除任务")
    
    def add_subtask(e):
        """手动添加子任务"""
        if current_task_id and subtask_input.value.strip():
            minutes = int(time_input.value or 25)
            data_service.add_subtask(
                current_task_id, 
                subtask_input.value.strip(), 
                minutes
            )
            subtask_input.value = ""
            refresh_subtask_list()
            refresh_task_list()
    
    def toggle_subtask(index: int):
        """切换子任务状态"""
        data_service.toggle_subtask(current_task_id, index)
        refresh_subtask_list()
        refresh_task_list()
    
    def delete_subtask(index: int):
        """删除子任务"""
        data_service.delete_subtask(current_task_id, index)
        refresh_subtask_list()
        refresh_task_list()
    
    def ai_break_down(e):
        """AI智能分解任务"""
        if not current_task_id:
            show_message("请先选择一个任务", ft.colors.ORANGE)
            return
        
        task = data_service.get_task(current_task_id)
        if not task:
            return
        
        # 显示加载状态
        ai_status.value = "🤖 AI正在分析任务..."
        page.update()
        
        # 调用AI
        result = ai_service.break_down_task(task["name"])
        
        if result["success"]:
            subtasks = result["data"]["subtasks"]
            data_service.add_subtasks_batch(current_task_id, subtasks)
            ai_status.value = f"✅ AI已生成 {len(subtasks)} 个子任务"
            refresh_subtask_list()
            refresh_task_list()
        else:
            ai_status.value = f"❌ 分解失败: {result['error']}"
        
        page.update()
    
    # ============ 导入导出对话框 ============
    
    def show_export_dialog(e):
        """显示导出对话框"""
        export_text = data_service.get_export_string()
        
        dialog = ft.AlertDialog(
            title=ft.Text("📤 导出数据"),
            content=ft.Column([
                ft.Text("复制以下内容，在其他设备粘贴导入：", size=12),
                ft.TextField(
                    value=export_text,
                    multiline=True,
                    min_lines=5,
                    max_lines=10,
                    read_only=True
                )
            ], tight=True, width=400),
            actions=[
                ft.TextButton("关闭", on_click=lambda e: close_dialog())
            ]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def show_import_dialog(e):
        """显示导入对话框"""
        import_field = ft.TextField(
            hint_text="粘贴从其他设备导出的数据",
            multiline=True,
            min_lines=5,
            max_lines=10
        )
        
        def do_import(e):
            result = data_service.import_from_string(import_field.value)
            if result["success"]:
                show_message(f"✅ 成功导入 {result['imported']} 个任务")
                refresh_task_list()
                close_dialog()
            else:
                show_message(f"❌ 导入失败: {result['error']}", ft.colors.RED)
        
        dialog = ft.AlertDialog(
            title=ft.Text("📥 导入数据"),
            content=ft.Column([
                ft.Text("粘贴从其他设备导出的数据：", size=12),
                import_field
            ], tight=True, width=400),
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
    
    # ============ 页面布局 ============
    
    page.add(
        # 标题栏
        ft.Row([
            ft.Text("🎯 任务分解器", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.IconButton(
                    icon=ft.icons.UPLOAD,
                    tooltip="导入数据",
                    on_click=show_import_dialog
                ),
                ft.IconButton(
                    icon=ft.icons.DOWNLOAD,
                    tooltip="导出数据",
                    on_click=show_export_dialog
                )
            ])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        ft.Text("把大任务拆成小步骤，战胜拖延症！", color=ft.colors.GREY_600, size=12),
        
        ft.Divider(height=20),
        
        # 任务输入区
        ft.Row([
            task_input,
            ft.ElevatedButton(
                "添加任务",
                icon=ft.icons.ADD,
                on_click=add_task
            )
        ]),
        
        # 任务列表
        ft.Text("📋 我的任务", weight=ft.FontWeight.BOLD),
        ft.Container(
            content=task_list,
            height=150,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=8,
            padding=10
        ),
        
        ft.Divider(height=20),
        
        # 子任务区域
        ft.Row([
            ft.Text("📝 任务步骤", weight=ft.FontWeight.BOLD, expand=True),
            ft.ElevatedButton(
                "🤖 AI分解",
                on_click=ai_break_down,
                bgcolor=ft.colors.PURPLE_400,
                color=ft.colors.WHITE
            )
        ]),
        ai_status,
        
        # 手动添加子任务
        ft.Row([
            subtask_input,
            time_input,
            ft.IconButton(icon=ft.icons.ADD, on_click=add_subtask)
        ]),
        
        # 进度条
        ft.Row([progress_text, progress_bar]),
        
        # 子任务列表
        ft.Container(
            content=subtask_list,
            height=200,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=8,
            padding=10,
            expand=True
        )
    )
    
    # 初始化加载数据
    refresh_task_list()


# 启动应用
if __name__ == "__main__":
    ft.app(target=main)