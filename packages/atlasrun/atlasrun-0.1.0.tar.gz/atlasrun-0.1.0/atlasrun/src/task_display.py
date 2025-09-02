#!/usr/bin/env python3
"""
Task display utilities for AtlasRun
"""
import time
from datetime import datetime
from tabulate import tabulate
from ..db import TaskStatus


def format_duration(start_time, end_time=None):
    """格式化持续时间"""
    if not start_time:
        return "-"
    
    # 转换为秒级时间戳
    start_sec = start_time / 1000 if start_time > 1000000000000 else start_time
    
    if not end_time:
        end_sec = time.time()
    else:
        end_sec = end_time / 1000 if end_time > 1000000000000 else end_time
    
    duration = end_sec - start_sec
    if duration < 60:
        return f"{int(duration)}s"
    elif duration < 3600:
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        return f"{minutes}m {seconds}s"
    else:
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_time(timestamp, full=False):
    """格式化时间戳"""
    if not timestamp:
        return "-"
    # 转换为秒级时间戳
    timestamp_sec = timestamp / 1000 if timestamp > 1000000000000 else timestamp
    dt = datetime.fromtimestamp(timestamp_sec)
    
    if full:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        # 如果是今天，只显示时间；否则显示月日时间
        today = datetime.now().date()
        if dt.date() == today:
            return dt.strftime("%H:%M:%S")
        else:
            return dt.strftime("%m-%d %H:%M")


def get_status_icon(status):
    """获取状态图标"""
    status_icons = {
        TaskStatus.RUNNING: "▶",
        TaskStatus.PENDING: "⏳", 
        TaskStatus.COMPLETED: "✓",
        TaskStatus.FAILED: "✗"
    }
    return status_icons.get(status, "?")


def list_tasks(db):
    """显示任务列表"""
    # 获取所有任务
    all_tasks = db.get_all_tasks(limit=50)  # 限制显示最近50个任务
    
    if not all_tasks:
        print("No tasks found")
        return
    
    # 准备表格数据
    table_data = []
    headers = ["ID", "Status", "PID", "Submit Time", "Duration", "Command"]
    
    for task in all_tasks:
        # 计算运行时间
        if task.status == TaskStatus.RUNNING and task.start_time:
            duration = format_duration(task.start_time)
        elif task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and task.start_time and task.completed_at:
            duration = format_duration(task.start_time, task.completed_at)
        else:
            duration = "-"
        
        # 状态显示 - 确保对齐
        icon = get_status_icon(task.status)
        status_text = task.status.value
        status_display = f"{icon} {status_text:<9}"  # 左对齐，最小宽度9
        
        # 添加行数据
        row = [
            task.id,
            status_display,
            task.pid or "-",
            format_time(task.created_at),
            duration,
            task.command[:50] + "..." if len(task.command) > 50 else task.command
        ]
        table_data.append(row)
    
    # 按ID排序
    table_data.sort(key=lambda x: x[0])
    
    # 使用tabulate打印表格
    print("\n" + tabulate(
        table_data,
        headers=headers,
        tablefmt="fancy_grid",
        colalign=("right", "left", "right", "right", "right", "left")
    ) + "\n")


def show_status(db):
    """显示队列状态"""
    pending_tasks = db.get_pending_tasks()
    running_tasks = db.get_running_tasks()
    
    print("=== AtlasRun Queue Status ===")
    print(f"Pending tasks: {len(pending_tasks)}")
    print(f"Running tasks: {len(running_tasks)}")
    
    if running_tasks:
        print("\nRunning tasks:")
        for task in running_tasks:
            print(f"  {task.id}: {task.command} (PID: {task.pid})")
    
    if pending_tasks:
        print("\nPending tasks:")
        for task in pending_tasks:
            print(f"  {task.id}: {task.command}")


def show_task_info(db, task_id):
    """显示任务详细信息"""
    task = db.get_task_by_id(task_id)
    
    if not task:
        print(f"Task {task_id} not found")
        return
    
    print(f"=== Task {task_id} Information ===")
    print(f"Command: {task.command}")
    print(f"Working Directory: {task.working_dir}")
    print(f"Status: {task.status.value}")
    print(f"PID: {task.pid or 'N/A'}")
    print(f"Created: {format_time(task.created_at, full=True)}")
    
    if task.started_at:
        print(f"Started: {format_time(task.started_at, full=True)}")
    
    if task.completed_at:
        print(f"Completed: {format_time(task.completed_at, full=True)}")
        print(f"Exit Code: {task.exit_code}")
