from typing import Optional

from zyjj_client_sdk.flow.base import FlowBase
from zyjj_client_sdk.flow.node.common import get_val_or_default, tool_check_point, tool_cost_point


# 输入节点
async def node_input(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    user_input = base.input_get()
    check_point = get_val_or_default("check_point", data, extra, False)
    point = get_val_or_default("point", data, extra, 0)
    if check_point:
        await tool_check_point(base, point)
    output = {"point": point}
    for field in extra["fields"]:
        output[field] = user_input.get(field, None)
    return output


# 输出节点
async def node_output(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    cost_point = get_val_or_default("cost_point", data, extra, False)
    name = get_val_or_default("name", data, extra, "")
    desc = get_val_or_default("desc", data, extra, "")
    point = get_val_or_default("point", data, extra, 0)
    if cost_point:
        await tool_cost_point(base, name, desc, point)
    return {
        field: data.get(field, None) for field in extra["fields"]
    }


# 代码节点
async def node_code(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    return await base.tiger_code(extra["entity_id"], data, base)


# 对象导入
async def object_import(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    return {
        "object": {
            field: data.get(field, None) for field in extra["fields"]
        }
    }


# 对象导出
async def object_export(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    fields = extra["fields"]
    obj = data.get("object", {})
    return {
        field: obj.get(field, None) for field in fields
    }
