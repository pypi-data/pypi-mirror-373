#!/usr/bin/env python3

import time
from .models import TaskStatus
from .connection import get_connection

def add_task(db_path: str, command: str, working_dir: str) -> int:
    """添加新任务到队列"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (command, working_dir, status, created_at)
            VALUES (?, ?, ?, ?)
        """, (command, working_dir, TaskStatus.PENDING.value, time.time() * 1000))
        conn.commit()
        return cursor.lastrowid


def update_pid(db_path: str, task_id: int, pid: int):
    """只更新任务的PID，不改变状态"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET pid = ?
            WHERE id = ?
        """, (pid, task_id))
        conn.commit()


def fail_task(db_path: str, task_id: int, exit_code: int):
    """标记任务失败"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET status = ?, completed_at = ?, exit_code = ?
            WHERE id = ?
        """, (TaskStatus.FAILED.value, time.time() * 1000, exit_code, task_id))
        conn.commit()


def mark_task_pending_by_pid(db_path: str, pid: int):
    """通过PID强制标记任务为pending状态"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET status = ?, started_at = NULL, start_time = NULL, completed_at = NULL, exit_code = NULL
            WHERE pid = ?
        """, (TaskStatus.PENDING.value, pid))
        conn.commit()


def mark_task_complete_by_pid(db_path: str, pid: int, exit_code: int = 0):
    """通过PID强制标记任务为completed状态"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET status = ?, completed_at = ?, exit_code = ?
            WHERE pid = ?
        """, (TaskStatus.COMPLETED.value, time.time() * 1000, exit_code, pid))
        conn.commit()


def complete_task(db_path: str, task_id: int, exit_code: int = 0):
    """通过任务ID标记任务为completed状态"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET status = ?, completed_at = ?, exit_code = ?
            WHERE id = ?
        """, (TaskStatus.COMPLETED.value, time.time() * 1000, exit_code, task_id))
        conn.commit()


def mark_task_running_by_pid(db_path: str, pid: int):
    """通过PID强制标记任务为running状态"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET status = ?, started_at = ?, start_time = ?
            WHERE pid = ?
        """, (TaskStatus.RUNNING.value, time.time() * 1000, time.time() * 1000, pid))
        conn.commit()


def cleanup_completed_tasks(db_path: str, days: int = 7) -> int:
    """清理已完成的任务（保留指定天数）"""
    cutoff_time = time.time() * 1000 - (days * 24 * 3600 * 1000)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        # 先统计要删除的任务数
        cursor.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE status IN (?, ?) AND completed_at < ?
        """, (TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, cutoff_time))
        count = cursor.fetchone()[0]
        
        # 执行删除
        cursor.execute("""
            DELETE FROM tasks 
            WHERE status IN (?, ?) AND completed_at < ?
        """, (TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, cutoff_time))
        conn.commit()
        return count


def cleanup_all_data(db_path: str) -> dict:
    """清理所有数据：删除所有任务记录"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # 统计当前数据库中的任务数量
        cursor.execute("SELECT COUNT(*) FROM tasks")
        total_tasks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = ?", (TaskStatus.PENDING.value,))
        pending_tasks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = ?", (TaskStatus.RUNNING.value,))
        running_tasks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = ?", (TaskStatus.COMPLETED.value,))
        completed_tasks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = ?", (TaskStatus.FAILED.value,))
        failed_tasks = cursor.fetchone()[0]
        
        # 删除所有任务
        cursor.execute("DELETE FROM tasks")
        # 重置AUTO_INCREMENT，让下一个任务ID从1开始
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
        conn.commit()
        
        return {
            'total_tasks': total_tasks,
            'pending_tasks': pending_tasks,
            'running_tasks': running_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks
        }
