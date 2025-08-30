from enum import Enum
from typing import Optional

from zyjj_client_sdk.base.exception import PointNotEnough
from zyjj_client_sdk.flow.base import FlowBase


# 文件来源类型
class FileSourceType(Enum):
    UnKnow = 0  # 未知
    CloudFile = 1  # 云端文件
    CloudPath = 2  # 云端路径
    CloudLink = 3  # 云端链接
    LocalPath = 10  # 本地路径
    Bytes = 11  # 字节数据


# 获取默认参数
def get_val_or_default(key: str, data: dict, extra: Optional[dict], default=None):
    if data.get(key, None) is not None:
        return data[key]
    if extra is not None and extra.get(key, None) is not None:
        return extra[key]
    return default


# 检查积分
async def tool_check_point(base: FlowBase, point: int):
    current_point = await base.api.get_user_point(base.uid)
    base.add_log('current_point', current_point)
    if current_point < point:
        raise PointNotEnough(point, current_point)


# 扣除积分
async def tool_cost_point(base: FlowBase, name: str, desc: str, point: int):
    if not await base.api.use_user_point(base.task_id, base.uid, name, point, desc):
        raise PointNotEnough(point)
