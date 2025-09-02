#!/usr/bin/env python3
import argparse
import os
import time
from pathlib import Path
from .db import Database, TaskStatus
from .executor import TaskExecutor
from .src.task_display import show_task_info, list_tasks


def main():
    """Main entry point for the command line interface."""
    
    logo = r'''   

          _   _             ____  _       _        __
     /\  | | | |           |  _ \(_)     (_)      / _|
    /  \ | |_| | __ _ ___  | |_) |_  ___  _ _ __ | |_ ___
   / /\ \| __| |/ _` / __| |  _ <| |/ _ \| | '_ \|  _/ _ \
  / ____ \ |_| | (_| \__ \ | |_) | | (_) | | | | | || (_) |
 /_/    \_\__|_|\__,_|___/ |____/|_|\___/|_|_| |_|_| \___/

        `-:-.   ,-;"`-:-.   ,-;"`-:-.   ,-;"`-:-.   ,-;"
        `=`,'=/     `=`,'=/     `=`,'=/     `=`,'=/
            y==/        y==/        y==/        y==/
        ,=,-<=`.    ,=,-<=`.    ,=,-<=`.    ,=,-<=`.
        ,-'-'   `-=_,-'-'   `-=_,-'-'   `-=_,-'-'   `-=_
                    
    '''

    description_text = f'''{logo} 
AtlasRun is a lightweight local task queue and execution manager for batch command-line jobs. 
It allows you to add, monitor, and manage tasks from the command line.

        .'''

    parser = argparse.ArgumentParser(
        description=description_text,
        formatter_class=argparse.RawTextHelpFormatter,
        usage="arun [options] [command...]",
        add_help=False
    )
    

    parser.add_argument('-l', action='store_true', 
                       help='List all tasks')
    parser.add_argument('-i', '--info', type=int, metavar='TASK_ID',
                       help='Show detailed information about a specific task')
    parser.add_argument('-c', '--cleanup', type=int, metavar='DAYS',
                       help='Clean up completed tasks older than specified days')
    parser.add_argument('--clean', action='store_true',
                       help='Clean all data: delete all logs, scripts, and clear database')
    parser.add_argument('-u', '--update', action='store_true',
                       help='Update task statuses (check if PIDs are still running)')
    parser.add_argument('--mark-running', type=int, metavar='PID',
                       help='Mark a task with specific PID as running (internal use)')
    parser.add_argument('--mark-pending', type=int, metavar='PID',
                       help='Force mark a task with specific PID as pending')
    parser.add_argument('--mark-complete', type=int, metavar='PID',
                       help='Force mark a task with specific PID as completed')

    parser.add_argument('-h', '--help', action='store_true',
                       help='Show this help message and exit')
    
    # 解析已知参数，保留未知参数
    args, unknown = parser.parse_known_args()
    
    # 显示帮助信息
    if args.help:
        parser.print_help()
        print("\nExamples:")
        print("  arun sleep 3                    # Add command to queue")
        print("  arun -l                         # List all tasks")
        print("  arun -i 1                       # Show task details")
        print("  arun -c 7                       # Clean up tasks older than 7 days")
        print("  arun --clean                    # Clean all data")
        return
    
    db = Database()
    
    # 处理特殊命令
    if args.l:
        list_tasks(db)
        return
    
    if args.info:
        show_task_info(db, args.info)
        return
    
    if args.cleanup:
        cleanup_tasks(db, args.cleanup)
        return
    
    if args.clean:
        clean_all_data(db)
        return
    
    if args.update:
        update_task_statuses(db)
        return
    
    if args.mark_running:
        db.mark_task_running_by_pid(args.mark_running)
        return
    
    if args.mark_pending:
        db.mark_task_pending_by_pid(args.mark_pending)
        return
    
    if args.mark_complete:
        db.mark_task_complete_by_pid(args.mark_complete)
        return
    
    # 获取命令参数（所有没有-开头的参数）
    command_parts = []
    for arg in unknown:
        if not arg.startswith('-'):
            command_parts.append(arg)
        else:
            print(f"Warning: Ignoring unknown option {arg}")
    
    if not command_parts:
        print("Error: No command specified")
        print("Use 'arun -h' for help")
        return
    
    # 组合完整命令
    full_command = ' '.join(command_parts)
    
    # 使用当前工作目录
    working_dir = os.getcwd()
    
    # 初始化执行器并运行任务
    executor = TaskExecutor(db)
    
    try:
        # 运行任务
        task_id = executor.run_single_task(full_command, working_dir)
        print(f"Task {task_id} completed")
    except Exception as e:
        print(f"Error: {e}")


def cleanup_tasks(db, days):
    """清理任务"""
    count = db.cleanup_completed_tasks(days)
    print(f"Cleaned up {count} completed tasks older than {days} days")


def update_task_statuses(db):
    """更新任务状态"""
    executor = TaskExecutor(db)
    executor.update_task_statuses()


def clean_all_data(db):
    """清理所有数据：删除日志、脚本和清空数据库"""
    import shutil
    from pathlib import Path
    
    print("=== AtlasRun Complete Cleanup ===")
    print("This will delete ALL data, logs, and scripts!")
    
    # 获取统计信息
    stats = db.cleanup_all_data()
    
    print(f"\nDatabase cleanup completed:")
    print(f"  Total tasks removed: {stats['total_tasks']}")
    print(f"  - Pending: {stats['pending_tasks']}")
    print(f"  - Running: {stats['running_tasks']}")
    print(f"  - Completed: {stats['completed_tasks']}")
    print(f"  - Failed: {stats['failed_tasks']}")
    
    # 清理日志和脚本文件
    home_dir = Path.home()
    atlasrun_dir = home_dir / ".atlasrun"
    
    # 清理日志目录
    log_dir = atlasrun_dir / "logs"
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log")) + list(log_dir.glob("*.out")) + list(log_dir.glob("*.err"))
        if log_files:
            for log_file in log_files:
                log_file.unlink()
            print(f"  Log files removed: {len(log_files)}")
        else:
            print("  No log files found")
    
    # 清理临时脚本目录
    temp_scripts_dir = atlasrun_dir / "TEMP_script"
    if temp_scripts_dir.exists():
        script_files = list(temp_scripts_dir.glob("*.sh")) + list(temp_scripts_dir.glob("*.pid"))
        if script_files:
            for script_file in script_files:
                script_file.unlink()
            print(f"  Script files removed: {len(script_files)}")
        else:
            print("  No script files found")
    
    print("\nCleanup completed successfully!")
    print("All AtlasRun data has been cleared.")


if __name__ == '__main__':
    main()
