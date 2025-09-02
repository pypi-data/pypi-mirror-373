#!/usr/bin/env python3
"""
Task query operations for AtlasRun
"""
import sqlite3
from typing import List, Optional
from .models import Task, TaskStatus
from .connection import get_connection


def get_pending_tasks(db_path: str) -> List[Task]:
    """获取所有待处理的任务"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, command, working_dir, status, pid, created_at, 
                   started_at, start_time, completed_at, exit_code
            FROM tasks 
            WHERE status = ? 
            ORDER BY created_at ASC
        """, (TaskStatus.PENDING.value,))
        
        tasks = []
        for row in cursor.fetchall():
            task = Task(
                id=row[0],
                command=row[1],
                working_dir=row[2],
                status=TaskStatus(row[3]),
                pid=row[4],
                created_at=row[5],
                started_at=row[6],
                start_time=row[7],
                completed_at=row[8],
                exit_code=row[9]
            )
            tasks.append(task)
        return tasks


def get_running_tasks(db_path: str) -> List[Task]:
    """获取所有正在运行的任务"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, command, working_dir, status, pid, created_at, 
                   started_at, start_time, completed_at, exit_code
            FROM tasks 
            WHERE status = ?
        """, (TaskStatus.RUNNING.value,))
        
        tasks = []
        for row in cursor.fetchall():
            task = Task(
                id=row[0],
                command=row[1],
                working_dir=row[2],
                status=TaskStatus(row[3]),
                pid=row[4],
                created_at=row[5],
                started_at=row[6],
                start_time=row[7],
                completed_at=row[8],
                exit_code=row[9]
            )
            tasks.append(task)
        return tasks


def get_all_running_tasks(db_path: str) -> List[Task]:
    """获取所有状态为running的任务"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, command, working_dir, status, pid, created_at, 
                   started_at, start_time, completed_at, exit_code
            FROM tasks 
            WHERE status = ?
            ORDER BY started_at ASC
        """, (TaskStatus.RUNNING.value,))
        
        tasks = []
        for row in cursor.fetchall():
            task = Task(
                id=row[0],
                command=row[1],
                working_dir=row[2],
                status=TaskStatus(row[3]),
                pid=row[4],
                created_at=row[5],
                started_at=row[6],
                start_time=row[7],
                completed_at=row[8],
                exit_code=row[9]
            )
            tasks.append(task)
        return tasks


def get_completed_tasks(db_path: str) -> List[Task]:
    """获取所有已完成的任务"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, command, working_dir, status, pid, created_at, 
                   started_at, start_time, completed_at, exit_code
            FROM tasks 
            WHERE status IN (?, ?)
            ORDER BY created_at DESC
        """, (TaskStatus.COMPLETED.value, TaskStatus.FAILED.value))
        
        tasks = []
        for row in cursor.fetchall():
            task = Task(
                id=row[0],
                command=row[1],
                working_dir=row[2],
                status=TaskStatus(row[3]),
                pid=row[4],
                created_at=row[5],
                started_at=row[6],
                start_time=row[7],
                completed_at=row[8],
                exit_code=row[9]
            )
            tasks.append(task)
        return tasks


def get_all_tasks(db_path: str, limit: int = 100) -> List[Task]:
    """获取所有任务（限制数量）"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, command, working_dir, status, pid, created_at, 
                   started_at, start_time, completed_at, exit_code
            FROM tasks 
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        tasks = []
        for row in cursor.fetchall():
            task = Task(
                id=row[0],
                command=row[1],
                working_dir=row[2],
                status=TaskStatus(row[3]),
                pid=row[4],
                created_at=row[5],
                started_at=row[6],
                start_time=row[7],
                completed_at=row[8],
                exit_code=row[9]
            )
            tasks.append(task)
        return tasks


def get_task_by_id(db_path: str, task_id: int) -> Optional[Task]:
    """根据ID获取任务"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, command, working_dir, status, pid, created_at, 
                   started_at, start_time, completed_at, exit_code
            FROM tasks 
            WHERE id = ?
        """, (task_id,))
        
        row = cursor.fetchone()
        if row:
            return Task(
                id=row[0],
                command=row[1],
                working_dir=row[2],
                status=TaskStatus(row[3]),
                pid=row[4],
                created_at=row[5],
                started_at=row[6],
                start_time=row[7],
                completed_at=row[8],
                exit_code=row[9]
            )
        return None


def get_task_by_pid(db_path: str, pid: int) -> Optional[Task]:
    """根据PID获取任务"""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, command, working_dir, status, pid, created_at, 
                   started_at, start_time, completed_at, exit_code
            FROM tasks 
            WHERE pid = ?
        """, (pid,))
        
        row = cursor.fetchone()
        if row:
            return Task(
                id=row[0],
                command=row[1],
                working_dir=row[2],
                status=TaskStatus(row[3]),
                pid=row[4],
                created_at=row[5],
                started_at=row[6],
                start_time=row[7],
                completed_at=row[8],
                exit_code=row[9]
            )
        return None
