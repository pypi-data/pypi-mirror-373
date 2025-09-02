#!/usr/bin/env python3
"""
Script templates for AtlasRun
"""
import time
from pathlib import Path


def create_task_script(task_id: int, command: str, working_dir: str, 
                      temp_scripts_dir: Path, log_dir: Path, 
                      wait_for_pid: int = None) -> str:
    """创建任务脚本内容"""
    
    # 构建等待逻辑
    wait_logic = ""
    if wait_for_pid:
        wait_logic = f"""# 等待前一个任务完成
echo "Waiting for previous task (PID: {wait_for_pid}) to complete..." >&2
arun --mark-pending $current_pid
while kill -0 {wait_for_pid} 2>/dev/null; do
    sleep 1
done
echo "Previous task completed, starting this task..." >&2
"""
    
    stdout_log = log_dir / f"task_{task_id}.out"
    stderr_log = log_dir / f"task_{task_id}.err"
    
    script_content = f"""#!/bin/bash

# AtlasRun temporary script for task {task_id}
# Created at: {time.strftime('%Y-%m-%d %H:%M:%S')}
current_pid=$$
set -e

{wait_logic}

arun --mark-running $current_pid

cd "{working_dir}"

{command} > {stdout_log} 2> {stderr_log}

exit_code=$?
echo "Task $current_pid completed at $(date) with exit code $exit_code" >&2

arun --mark-complete $current_pid

exit $exit_code
"""
    
    return script_content

