# AtlasRun

一个简单的命令行任务队列管理工具，可以按顺序执行命令。

## 特性

- 使用简单的命令行接口
- 命令按顺序排队执行
- 每个命令都有唯一编号
- 自动等待前一个命令完成后再执行下一个
- 使用SQLite存储命令队列
- 支持指定工作目录
- 自动创建临时bash脚本
- 进程监控和状态管理
- 任务历史记录和清理

## 安装

### 从源码安装

```bash
# 克隆仓库
git clone <repository-url>
cd atlasrun

# 安装依赖
pip install -r requirements.txt

# 安装开发模式
pip install -e .
```

### 依赖要求

- Python 3.7+
- click (命令行界面库)

## 使用方法

### 基本用法

添加命令到队列：
```bash
arun "your command here"
```

例如：
```bash
arun "sleep 10"
arun "echo hello world"
arun "python script.py"
```

第二个命令会等第一个命令完成后才开始执行。

### 指定工作目录

```bash
arun --dir /path/to/directory "your command"
# 或者
arun -d /path/to/directory "your command"
```

### 查看队列状态

```bash
arun --status
# 或者
arun -s
```

### 列出所有任务

```bash
arun --list
# 或者
arun -l
```

### 查看任务详情

```bash
arun --info <task_id>
# 或者
arun -i <task_id>
```

### 清理旧任务

```bash
arun --cleanup 7  # 清理7天前的已完成任务
# 或者
arun -c 7
```

## 工作原理

1. **任务添加**: 当您运行 `arun "command"` 时，命令会被添加到SQLite数据库中，状态为 `pending`

2. **队列检查**: 系统检查是否有其他任务正在运行

3. **任务执行**: 如果没有运行中的任务，系统会：
   - 创建临时bash脚本在 `~/.atlasrun/TEMP_script/` 目录
   - 切换到指定的工作目录
   - 使用 `nohup` 启动命令
   - 记录PID和开始时间

4. **等待机制**: 如果有其他任务在运行，新任务会等待，直到所有运行中的任务完成

5. **状态更新**: 任务完成后，状态会更新为 `completed` 或 `failed`

## 文件结构

```
~/.atlasrun/
├── tasks.db          # SQLite数据库文件
└── TEMP_script/     # 临时脚本目录
    └── task_*.sh    # 临时bash脚本
```

## 数据库结构

任务表包含以下字段：
- `id`: 任务唯一标识符
- `command`: 要执行的命令
- `working_dir`: 工作目录
- `status`: 任务状态 (pending/running/completed/failed)
- `pid`: 进程ID
- `created_at`: 创建时间
- `started_at`: 开始时间
- `completed_at`: 完成时间
- `exit_code`: 退出码

## 开发

1. 克隆仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 安装开发模式：`pip install -e .`
4. 运行测试：`python test_atlasrun.py`

## 许可证

Apache License 2.0

## 贡献

欢迎提交Issue和Pull Request！