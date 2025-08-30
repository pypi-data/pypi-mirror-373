import asyncio
import json
import logging
import time
import traceback

from graphviz import Digraph
from zyjj_client_sdk.base.tool import data_convert
from zyjj_client_sdk.flow.base import FlowBase, FlowNode, FlowRelation, node_define, NodeInfo, NodeType
import zyjj_client_sdk.flow.node as Node

node_type_name_map = {
    NodeType.BasicStart: '开始节点',
    NodeType.BasicEnd: '结束节点',
    NodeType.BasicCode: '代码节点',
    NodeType.BasicObjectImport: '对象导入',
    NodeType.BasicObjectExport: '对象导出',
    NodeType.ToolGetConfig: '获取配置',
    NodeType.ToolCheckPoint: '检查积分',
    NodeType.ToolCostPoint: '扣除积分',
    NodeType.ToolUploadFile: '上传文件',
    NodeType.ToolDownloadFile: '下载文件',
    NodeType.ToolFileParse: '文件解析',
    NodeType.ToolFileExport: '文件导出',
    NodeType.ToolGetTencentToken: '腾讯认证',
    NodeType.ToolGenerateLocalPath: '本地路径',
    NodeType.ToolFfmpegPoint: 'ffmpeg积分',
    NodeType.ToolFfmpeg: 'ffmpeg',
    NodeType.ToolLinkExtra: '链接提取',
    NodeType.ToolOpenPlatform: '开放平台',
}


class FlowService:
    def __init__(self, base: FlowBase, flow_data: dict):
        # 不同类型的节点处理函数
        self.__node_type_handle: dict[NodeType, node_define] = {
            NodeType.BasicStart: Node.node_input,
            NodeType.BasicEnd: Node.node_output,
            NodeType.BasicCode: Node.node_code,
            NodeType.BasicObjectImport: Node.object_import,
            NodeType.BasicObjectExport: Node.object_export,
            NodeType.ToolGetConfig: Node.node_get_config,
            NodeType.ToolCheckPoint: Node.node_check_point,
            NodeType.ToolCostPoint: Node.node_cost_point,
            NodeType.ToolUploadFile: Node.node_upload_file,
            NodeType.ToolDownloadFile: Node.node_download_file,
            NodeType.ToolFileParse: Node.node_file_parse,
            NodeType.ToolFileExport: Node.node_file_export,
            NodeType.ToolGetTencentToken: Node.node_get_tencent_token,
            NodeType.ToolGenerateLocalPath: Node.node_generate_local_path,
            NodeType.ToolFfmpegPoint: Node.node_ffmpeg_point,
            NodeType.ToolFfmpeg: Node.node_ffmpeg,
            NodeType.ToolLinkExtra: Node.node_link_extra,
            NodeType.ToolOpenPlatform: Node.node_openplatform,
        }
        # 基本服务
        self.__base = base
        # 通知服务

        # 所有节点对应的信息
        self.__node_id_info: dict[str, FlowNode] = {}
        # 开始节点
        self.__start_node_id = ""
        self.__end_node_id = ""
        # 当前节点对应的后继节点
        self.__node_next: dict[str, list[FlowRelation]] = {}
        # 当前节点对应的前驱节点
        self.__node_prev: dict[str, list[FlowRelation]] = {}
        # 每个节点的输出数据
        self.__node_output: dict[str, dict[str, str]] = {}
        # 已经完成的节点
        self.__node_finish = set()
        # 所有关系节点
        self.__flow_relations = []
        #  每个节点的相关日志
        self.__node_log: dict[str, NodeInfo] = {}
        # 先解析所有node对应的type
        for node in flow_data["nodes"]:
            node_data = node["data"] if "data" in node else "{}"
            flow_node = FlowNode(node["node_id"], NodeType(node["node_type"]), node_data)
            self.__node_id_info[flow_node.node_id] = flow_node
            if flow_node.node_type == NodeType.BasicStart:
                self.__start_node_id = flow_node.node_id
            elif flow_node.node_type == NodeType.BasicEnd:
                self.__end_node_id = flow_node.node_id
            self.__node_log[flow_node.node_id] = NodeInfo(
                node_id=flow_node.node_id,
                node_type=flow_node.node_type.name,
                data=flow_node.data
            )
            # 节点类型全部初始化
            self.__node_output[flow_node.node_id] = {}
            self.__node_prev[flow_node.node_id] = []
            self.__node_next[flow_node.node_id] = []

        # 解析出所有节点的依赖关系
        for relation in flow_data["relations"]:
            flow_relation = FlowRelation(
                relation["from"],
                relation["from_output"],
                relation["to"],
                relation["to_input"]
            )
            self.__flow_relations.append(flow_relation)
            self.__node_prev[flow_relation.to_id].append(flow_relation)
            self.__node_next[flow_relation.from_id].append(flow_relation)

    @staticmethod
    def __filter_dict_bytes(data: dict) -> dict:
        new_dict = {}
        for key, value in data.items():
            if isinstance(value, bytes):
                new_dict[key] = f'bytes({len(value)})'
            else:
                new_dict[key] = value
        return new_dict

    # 是否需要访问节点
    def __no_need_visited(self, node_id: str) -> bool:
        return node_id in self.__node_finish

    async def __execute_node(self, node_id: str):
        # 当前节点如果执行过就直接返回
        if self.__no_need_visited(node_id):
            return
        # 获取当前节点的信息
        info = self.__node_id_info[node_id]
        # 获取当前节点的处理函数
        handle = self.__node_type_handle[info.node_type]
        handle_intput = {}
        # 先判断一下当前节点前驱节点都处理完了，并获取到输出
        for before in self.__node_prev.get(node_id, []):
            await self.__execute_node(before.from_id)
            if before.from_id in self.__node_output:
                handle_intput[before.to_input] = self.__node_output[before.from_id].get(before.from_output)
        # 执行前再检查一下是否需要执行
        if self.__no_need_visited(node_id):
            return
        node_start = time.time()
        handle_extra = {}
        # data不为空不设置exta信息
        if info.data is not None and info.data != '':
            handle_extra = json.loads(info.data)
        # 设置当前节点的依赖信息，并传递给base，方便子模块调用
        self.__base.set_flow_relation(
            self.__node_id_info[node_id],
            self.__node_prev.get(node_id, []),
            self.__node_next.get(node_id, []),
        )
        try:
            # 执行当前节点
            self.__node_output[node_id] = await handle(self.__base, handle_intput, handle_extra)
            # 标记当前节点已完成
            self.__node_finish.add(node_id)
            logging.info(f"execute node {node_id} cost {(time.time() - node_start) * 1000}ms")
            self.__node_log[node_id].status = 1
        except Exception as e:
            logging.error(f"execute node {node_id} err {e}")
            self.__node_log[node_id].status = 2
            self.__node_log[node_id].msg = traceback.format_exc()
            raise e
        finally:
            self.__node_log[node_id].cost = int((time.time() - node_start) * 1000)
        # 执行当前节点的后继节点
        for after in self.__node_next.get(node_id, []):
            await self.__execute_node(after.to_id)

    # 触发流程
    async def tiger_flow(self) -> dict:
        flow_start = time.time()
        status = 0
        msg = ""
        try:
            await self.__execute_node(self.__start_node_id)
            status = 1
            # 直接返回结束节点的结果
            return data_convert(self.__node_output[self.__end_node_id])
        except Exception as e:
            status = 2
            msg = traceback.format_exc()
            logging.error(msg)
            raise e
        finally:
            # 后台上报日志
            asyncio.create_task(self.save_flow_log(
                int((time.time() - flow_start) * 1000),
                status,
                msg
            ))

    # 保存流程的日志
    async def save_flow_log(self, cost: int, flow_status: int, flow_msg: str):
        logging.info(f"save flow status log {flow_status} {flow_msg}")
        log = {}
        # 获取流程描述
        node_desc = self.__base.get_desc()
        # 先绘制一下流程图
        dot = Digraph(comment='执行流程', graph_attr={'rankdir': 'LR'})
        for node_id, info in self.__node_id_info.items():
            color = "#f2f3f5"
            status = self.__node_log[node_id].status
            if status == 1:
                color = "#ecfeec"
            elif status == 2:
                color = "#fcede9"
            desc = ""
            if node_id in node_desc:
                desc = f'[{node_desc[node_id]}]'
            dot.node(
                name=node_id,
                label=f"{node_type_name_map[info.node_type]}{desc}({node_id})", style="filled",
                fillcolor=color
            )
        # 绘制依赖关系
        for relation in self.__flow_relations:
            dot.edge(relation.from_id, relation.to_id, label=f"{relation.from_output}->{relation.to_input}")
        # 保存节点数据时不去存储字节类型的数据
        log["graph"] = dot.source
        log["node_data"] = data_convert(self.__node_output)
        log["node_log"] = self.__base.get_log()
        # 节点的信息
        log["node_info"] = {k: v.__dict__ for k, v in self.__node_log.items()}
        log["node_relation"] = [relation.__dict__ for relation in self.__flow_relations]
        await self.__base.api.upload_flow_log({
            "task_id": self.__base.task_id,
            "flow_log": json.dumps(log, ensure_ascii=False),
            "status": flow_status,
            "cost": cost,
            "msg": flow_msg,
            "create_time": int(time.time() * 1000),
        })
