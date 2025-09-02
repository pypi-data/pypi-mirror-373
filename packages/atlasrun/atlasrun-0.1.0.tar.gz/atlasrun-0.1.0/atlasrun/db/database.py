#!/usr/bin/env python3
"""
Main Database class for AtlasRun
"""
from pathlib import Path
from .connection import get_db_path, init_database
from .queries import (
    get_pending_tasks, get_running_tasks, get_all_running_tasks,
    get_completed_tasks, get_all_tasks, get_task_by_id, get_task_by_pid
)
from .updates import (
    add_task, update_pid, fail_task, mark_task_pending_by_pid, 
    mark_task_complete_by_pid, mark_task_running_by_pid, cleanup_completed_tasks,
    cleanup_all_data, complete_task
)


class Database:
    """AtlasRun数据库管理类"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = str(get_db_path())
        else:
            self.db_path = db_path
        
        init_database(Path(self.db_path))
    
    # 查询方法
    def get_pending_tasks(self):
        return get_pending_tasks(self.db_path)
    
    def get_running_tasks(self):
        return get_running_tasks(self.db_path)
    
    def get_all_running_tasks(self):
        return get_all_running_tasks(self.db_path)
    
    def get_completed_tasks(self):
        return get_completed_tasks(self.db_path)
    
    def get_all_tasks(self, limit: int = 100):
        return get_all_tasks(self.db_path, limit)
    
    def get_task_by_id(self, task_id: int):
        return get_task_by_id(self.db_path, task_id)
    
    def get_task_by_pid(self, pid: int):
        return get_task_by_pid(self.db_path, pid)
    
    # 更新方法
    def add_task(self, command: str, working_dir: str) -> int:
        return add_task(self.db_path, command, working_dir)
    
    def update_pid(self, task_id: int, pid: int):
        update_pid(self.db_path, task_id, pid)
    
    def fail_task(self, task_id: int, exit_code: int):
        fail_task(self.db_path, task_id, exit_code)
    
    def mark_task_pending_by_pid(self, pid: int):
        mark_task_pending_by_pid(self.db_path, pid)
    
    def mark_task_complete_by_pid(self, pid: int, exit_code: int = 0):
        mark_task_complete_by_pid(self.db_path, pid, exit_code)
    
    def mark_task_running_by_pid(self, pid: int):
        mark_task_running_by_pid(self.db_path, pid)
    
    def cleanup_completed_tasks(self, days: int = 7) -> int:
        return cleanup_completed_tasks(self.db_path, days)
    
    def complete_task(self, task_id: int, exit_code: int = 0):
        complete_task(self.db_path, task_id, exit_code)
    
    def cleanup_all_data(self) -> dict:
        return cleanup_all_data(self.db_path)
