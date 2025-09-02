#!/usr/bin/env python3
"""
Data models for AtlasRun
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    id: int
    command: str
    working_dir: str
    status: TaskStatus
    pid: Optional[int]
    created_at: float
    started_at: Optional[float]
    start_time: Optional[float]
    completed_at: Optional[float]
    exit_code: Optional[int]
