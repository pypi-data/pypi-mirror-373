from enum import Enum
from dataclasses import dataclass


# 任务状态
class TaskStatus(Enum):
    Create = 0
    Doing = 1
    Success = 2
    Fail = 3


# 任务信息
@dataclass
class TaskInfo:
    task_id: str = ''  # 任务id
    uid: str = ''  # 用户uid
    task_type: int = 0  # 任务类型
    input: dict = None  # 任务输入
    source: str = ''  # 任务来源
