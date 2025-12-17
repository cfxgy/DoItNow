"""
数据服务 - 处理数据的保存、导入、导出
"""

import json
import os
from datetime import datetime
from typing import Optional

class DataService:
    def __init__(self, data_file: str = "data/tasks.json"):
        self.data_file = data_file
        self._ensure_data_dir()
        self.data = self._load_data()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def _load_data(self) -> dict:
        """从文件加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"tasks": {}, "settings": {}}
        return {"tasks": {}, "settings": {}}
    
    def save(self):
        """保存数据到文件"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    # ============ 任务操作 ============
    
    def add_task(self, task_name: str) -> str:
        """添加主任务，返回任务ID"""
        task_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.data["tasks"][task_id] = {
            "name": task_name,
            "created_at": datetime.now().isoformat(),
            "subtasks": [],
            "completed": False
        }
        self.save()
        return task_id
    
    def add_subtask(self, task_id: str, name: str, minutes: int):
        """添加子任务"""
        if task_id in self.data["tasks"]:
            self.data["tasks"][task_id]["subtasks"].append({
                "name": name,
                "minutes": minutes,
                "done": False,
                "created_at": datetime.now().isoformat()
            })
            self.save()
    
    def add_subtasks_batch(self, task_id: str, subtasks: list):
        """批量添加子任务（用于AI生成的结果）"""
        if task_id in self.data["tasks"]:
            for st in subtasks:
                self.data["tasks"][task_id]["subtasks"].append({
                    "name": st["name"],
                    "minutes": st["minutes"],
                    "done": False,
                    "created_at": datetime.now().isoformat()
                })
            self.save()
    
    def toggle_subtask(self, task_id: str, subtask_index: int):
        """切换子任务完成状态"""
        subtask = self.data["tasks"][task_id]["subtasks"][subtask_index]
        subtask["done"] = not subtask["done"]
        self.save()
    
    def delete_task(self, task_id: str):
        """删除主任务"""
        if task_id in self.data["tasks"]:
            del self.data["tasks"][task_id]
            self.save()
    
    def delete_subtask(self, task_id: str, subtask_index: int):
        """删除子任务"""
        del self.data["tasks"][task_id]["subtasks"][subtask_index]
        self.save()
    
    def get_all_tasks(self) -> dict:
        """获取所有任务"""
        return self.data["tasks"]
    
    def get_task(self, task_id: str) -> Optional[dict]:
        """获取单个任务"""
        return self.data["tasks"].get(task_id)
    
    # ============ 导入导出 ============
    
    def export_to_json(self, export_path: str) -> bool:
        """导出数据到JSON文件"""
        try:
            export_data = {
                "app": "TaskBreaker",
                "version": "1.0",
                "exported_at": datetime.now().isoformat(),
                "data": self.data
            }
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False
    
    def import_from_json(self, import_path: str) -> dict:
        """从JSON文件导入数据"""
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)
            
            # 验证数据格式
            if "data" in import_data and "tasks" in import_data["data"]:
                # 合并数据（不覆盖现有任务）
                imported_count = 0
                for task_id, task in import_data["data"]["tasks"].items():
                    if task_id not in self.data["tasks"]:
                        self.data["tasks"][task_id] = task
                        imported_count += 1
                
                self.save()
                return {"success": True, "imported": imported_count}
            else:
                return {"success": False, "error": "无效的数据格式"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_export_string(self) -> str:
        """获取导出数据的字符串（用于复制分享）"""
        export_data = {
            "app": "TaskBreaker",
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "data": self.data
        }
        return json.dumps(export_data, ensure_ascii=False)
    
    def import_from_string(self, data_string: str) -> dict:
        """从字符串导入数据（用于粘贴同步）"""
        try:
            import_data = json.loads(data_string)
            if "data" in import_data and "tasks" in import_data["data"]:
                imported_count = 0
                for task_id, task in import_data["data"]["tasks"].items():
                    if task_id not in self.data["tasks"]:
                        self.data["tasks"][task_id] = task
                        imported_count += 1
                self.save()
                return {"success": True, "imported": imported_count}
            return {"success": False, "error": "无效的数据格式"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# 测试代码
if __name__ == "__main__":
    ds = DataService()
    
    # 测试添加任务
    task_id = ds.add_task("测试任务")
    ds.add_subtask(task_id, "第一步", 10)
    ds.add_subtask(task_id, "第二步", 20)
    
    print("所有任务:", ds.get_all_tasks())
    
    # 测试导出
    export_str = ds.get_export_string()
    print("导出数据:", export_str)