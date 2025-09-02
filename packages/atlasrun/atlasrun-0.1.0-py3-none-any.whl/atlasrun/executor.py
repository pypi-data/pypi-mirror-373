import os
import subprocess
import time
import signal
from pathlib import Path
from typing import Optional
from .db import Database, Task, TaskStatus
from .src.script_templates import create_task_script
import sqlite3


class TaskExecutor:
    def __init__(self, db: Database):
        self.db = db
        self.home_dir = Path.home()
        self.atlasrun_dir = self.home_dir / ".atlasrun"
        self.temp_scripts_dir = self.atlasrun_dir / "TEMP_script"
        self.temp_scripts_dir.mkdir(exist_ok=True)
    
    def create_temp_script(self, command: str, task_id: int, working_dir: str, wait_for_pid: int = None) -> Path:
        """创建临时bash脚本"""
        # 创建日志目录
        log_dir = self.atlasrun_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        script_content = create_task_script(
            task_id=task_id,
            command=command,
            working_dir=working_dir,
            temp_scripts_dir=self.temp_scripts_dir,
            log_dir=log_dir,
            wait_for_pid=wait_for_pid
        )
        
        script_path = self.temp_scripts_dir / f"task_{task_id}.sh"
        script_path.write_text(script_content)
        script_path.chmod(0o755)
        return script_path
    
    def wait_for_pid(self, pid: int, timeout: int = 300) -> bool:
        """等待指定PID的进程结束"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # 检查进程是否还在运行
                os.kill(pid, 0)
                time.sleep(1)
            except OSError:
                # 进程已经结束
                return True
        return False
    
    def is_pid_running(self, pid: int) -> bool:
        """检查PID是否还在运行"""
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    
    def wait_for_running_tasks(self) -> None:
        """等待所有正在运行的任务完成"""
        while True:
            running_tasks = self.db.get_running_tasks()
            if not running_tasks:
                break
            
            # 检查每个运行中的任务
            for task in running_tasks:
                if task.pid and not self.is_pid_running(task.pid):
                    # 进程已经结束，更新状态
                    self.db.complete_task(task.id, 0)  # 假设正常退出
                    print(f"Task {task.id} completed")
            
            # 等待一秒后再次检查
            time.sleep(1)
    
    def update_task_statuses(self) -> None:
        """更新所有运行中任务的状态，检查PID是否还在运行"""
        running_tasks = self.db.get_all_running_tasks()
        updated_count = 0
        
        if not running_tasks:
            print("No running tasks found")
            return
        
        print(f"Checking {len(running_tasks)} running tasks...")
        
        for task in running_tasks:
            if task.pid and not self.is_pid_running(task.pid):
                # 进程已经结束，更新状态为completed
                # 尝试从日志获取退出码
                exit_code = 0  # 默认假设成功
                try:
                    log_dir = self.atlasrun_dir / "logs"
                    stderr_log = log_dir / f"task_{task.id}.err"
                    if stderr_log.exists():
                        # 从日志中提取退出码
                        content = stderr_log.read_text()
                        if "exit code" in content:
                            # 简单解析退出码
                            lines = content.split('\n')
                            for line in lines:
                                if "exit code" in line:
                                    try:
                                        exit_code = int(line.split()[-1])
                                        break
                                    except:
                                        pass
                except:
                    pass
                
                self.db.complete_task(task.id, exit_code)
                print(f"Task {task.id} completed with exit code {exit_code}")
                updated_count += 1
            else:
                print(f"Task {task.id} (PID: {task.pid}) is still running")
        
        # 检查是否有pending任务可以开始运行
        pending_tasks = self.db.get_pending_tasks()
        if pending_tasks and not running_tasks:
            # 没有运行中的任务，可以启动第一个pending任务
            next_task = pending_tasks[0]
            print(f"Starting next pending task: {next_task.id}")
            # 这里可以启动任务，但为了避免循环调用，我们只是标记状态
            # 实际的任务启动会在脚本执行时通过arun -u触发
        
        if updated_count > 0:
            print(f"Updated {updated_count} task(s)")
        else:
            print("No tasks to update")
    
    def execute_task(self, task: Task, wait_for_pid: int = None) -> bool:
        """执行指定任务"""
        try:
            # 创建临时脚本
            script_path = self.create_temp_script(task.command, task.id, task.working_dir, wait_for_pid)
            
            # 使用nohup在后台启动进程
            pid_file = self.temp_scripts_dir / f"task_{task.id}.pid"
            os.system(f"nohup bash {script_path} > /dev/null 2>&1 & echo $! > {pid_file}")
            
            # 读取PID
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                # 删除PID文件
                pid_file.unlink()
            except:
                # 如果无法获取PID，使用一个虚拟PID
                pid = os.getpid() + task.id  # 简单的虚拟PID生成
            
            # 记录PID，但状态保持为pending，等待脚本自己更新
            # 这里我们只更新PID，不改变状态
            self.db.update_pid(task.id, pid)
            
            print(f"Task {task.id} started with PID {pid} (status: pending)")
            
            return True
            
        except Exception as e:
            print(f"Error executing task {task.id}: {e}")
            self.db.fail_task(task.id, -1)
            return False
    
    def process_queue(self) -> None:
        """处理任务队列"""
        while True:
            # 等待所有运行中的任务完成
            self.wait_for_running_tasks()
            
            # 获取下一个待处理任务
            pending_tasks = self.db.get_pending_tasks()
            if not pending_tasks:
                print("No pending tasks")
                break
            
            # 执行下一个任务
            next_task = pending_tasks[0]
            print(f"Executing task {next_task.id}: {next_task.command}")
            
            if not self.execute_task(next_task):
                print(f"Failed to execute task {next_task.id}")
                break
            
            # 短暂休息，避免过于频繁的检查
            time.sleep(1)
    
    def run_single_task(self, command: str, working_dir: str = None) -> int:
        """运行单个任务（用于命令行接口）"""
        if working_dir is None:
            working_dir = os.getcwd()
        
        # 先检查并显示当前运行中的任务
        running_tasks = self.db.get_running_tasks()
        if running_tasks:
            print(f"Currently running tasks:")
            for task in running_tasks:
                print(f"  Task {task.id}: {task.command} (PID: {task.pid})")
            print()
        
        # 添加任务到队列
        task_id = self.db.add_task(command, working_dir)
        print(f"Task {task_id} added to queue: {command}")
        
        # 获取队列中所有任务，按ID排序（创建时间顺序）
        all_tasks = self.db.get_all_tasks(limit=1000)  # 获取足够多的任务
        # 按ID升序排序，确保按创建时间顺序
        all_tasks.sort(key=lambda x: x.id)
        
        # 找到当前任务之前最近的任务
        current_task = None
        previous_task = None
        
        for i, task in enumerate(all_tasks):
            if task.id == task_id:
                current_task = task
                # 前一个任务就是列表中的前一个（如果存在）
                if i > 0:
                    previous_task = all_tasks[i-1]
                break
        
        # 确定需要等待的PID和任务状态
        wait_for_pid = None
        should_start_immediately = previous_task is None
        
        if previous_task:
            # 等待前一个任务完成（不管它是什么状态）
            wait_for_pid = previous_task.pid
            print(f"Task {task_id} will wait for task {previous_task.id} (PID: {wait_for_pid}, status: {previous_task.status.value}) to complete")
        else:
            print(f"No previous tasks, starting task {task_id} immediately")
        
        print(f"DEBUG: wait_for_pid = {wait_for_pid}")
        
        # 启动任务
        print(f"Starting task {task_id}...")
        self.execute_task(Task(
            id=task_id,
            command=command,
            working_dir=working_dir, 
            status=TaskStatus.PENDING,
            pid=None,
            created_at=time.time() * 1000,
            started_at=None,
            start_time=None,
            completed_at=None,
            exit_code=None
        ), wait_for_pid)
        
        if should_start_immediately:
            print(f"Task {task_id} started in background")
        else:
            print(f"Task {task_id} queued, waiting for previous task to complete")
        
        return task_id
