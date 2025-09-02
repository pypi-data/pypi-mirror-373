#!/usr/bin/env python3
"""
Database connection management for AtlasRun
"""
import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    """获取数据库文件路径"""
    home_dir = Path.home()
    atlasrun_dir = home_dir / ".atlasrun"
    atlasrun_dir.mkdir(exist_ok=True)
    return atlasrun_dir / "tasks.db"


def init_database(db_path: Path) -> None:
    """初始化数据库表"""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                working_dir TEXT NOT NULL,
                status TEXT NOT NULL,
                pid INTEGER,
                created_at REAL NOT NULL,
                started_at REAL,
                start_time REAL,
                completed_at REAL,
                exit_code INTEGER
            )
        """)
        conn.commit()


def get_connection(db_path: Path) -> sqlite3.Connection:
    """获取数据库连接"""
    return sqlite3.connect(db_path)
