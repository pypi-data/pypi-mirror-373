import asyncio
from zyjj_client_sdk.base.tool import data_convert
import logging
from enum import Enum

from zyjj_client_sdk.base.exception import ParamInvalid, RemoteError, ServerError, UnknownError
from zyjj_client_sdk.base.tool import subtitles2srt, async_batch_run, llm_json_parse
from zyjj_client_sdk.base.decorator import async_throttle

from zyjj_client_sdk.base import Base, ApiService, MqttServer, MqttEventType, CloudSourceType
from zyjj_client_sdk.base.entity import TaskInfo
from zyjj_client_sdk.lib import FFMpegService, OSSService, Cache
from dataclasses import dataclass
from typing import Callable, Optional, Any, Awaitable
import chardet
from httpx import AsyncClient


class NodeType(Enum):
    BasicStart = 'basic_start'
    BasicEnd = 'basic_end'
    BasicCode = 'basic_code'
    BasicObjectImport = 'basic_object_import'
    BasicObjectExport = 'basic_object_export'
    ToolGetConfig = 'tool_get_config'
    ToolCostPoint = 'tool_cost_point'
    ToolCheckPoint = 'tool_check_point'
    ToolUploadFile = 'tool_upload_file'
    ToolDownloadFile = 'tool_download_file'
    ToolFileParse = 'tool_file_parse'
    ToolFileExport = 'tool_file_export'
    ToolGetTencentToken = 'tool_get_tencent_token'
    ToolGenerateLocalPath = 'tool_generate_local_path'
    ToolFfmpegPoint = 'tool_ffmpeg_point'
    ToolFfmpeg = 'tool_ffmpeg'
    ToolLinkExtra = 'tool_link_extra'
    ToolOpenPlatform = 'tool_open_platform'


# 节点
@dataclass
class FlowNode:
    node_id: str
    node_type: NodeType
    data: str


@dataclass
class FlowRelation:
    from_id: str
    from_output: str
    to_id: str
    to_input: str


@dataclass
class NodeInfo:
    node_id: str = ''
    node_type: str = ''  # 节点类型
    data: str = ''  # 节点的额外参数
    cost: int = 0  # 执行耗时
    status: int = 0  # 执行状态
    msg: str = ''  # 错误信息


# 给flow节点提供的基本方法
class FlowBase:
    def __init__(
        self,
        base: Base,  # 基本信息
        api: ApiService,  # api服务
        mqtt: MqttServer,  # mqtt服务
        oss: OSSService,  # oss 服务
        global_data: Cache,  # 全局数据
        task_info: TaskInfo,  # 任务数据
    ):
        # 一些私有变量，不暴露
        self.__base = base
        # ffmpeg
        self.__ffmpeg = FFMpegService()
        # mqtt对象
        self.__mqtt = mqtt
        self.__global_data = global_data
        self.__task_info = task_info
        self.__node_current: FlowNode | None = None
        self.__node_pre: list[FlowRelation] = []
        self.__node_next: list[FlowRelation] = []
        # 节点的描述信息
        self.__node_desc = {}
        self.__node_log: dict[str, list] = {}
        # 可以被外部模块使用的变量
        # api接口
        self.api = api
        # oss对象，可以直接用于文件上传
        self.oss = oss
        # 用户uid
        self.uid = task_info.uid
        # 当前正在执行的任务id
        self.task_id = task_info.task_id
        # 当前任务来源
        self.source = task_info.source
        # 异步请求客户端
        self.client = AsyncClient(timeout=60)

    def add_desc(self, desc: str):
        """添加节点描述"""
        if self.__node_current is not None:
            self.__node_desc[self.__node_current.node_id] = desc

    def get_desc(self) -> dict:
        """获取节点描述"""
        return self.__node_desc

    def add_log(self, *args):
        """添加节点日志"""
        if self.__node_current is None:
            return
        log_str = " ".join([str(data_convert(arg)) for arg in args])
        node_id = self.__node_current.node_id
        logging.info(f"[base] node {node_id} {log_str}")
        if node_id not in self.__node_log:
            self.__node_log[node_id] = []
        self.__node_log[node_id].append(log_str)

    def get_log(self) -> dict:
        """获取节点日志"""
        return self.__node_log

    async def async_get_global(self, key: str, init: Callable[[], Awaitable[Any]] = None) -> Any:
        """
        获取全局数据
        :param key: 全局key
        :param init: 初始化函数
        :return: 缓存的数据
        """
        return await self.__global_data.async_get_data(key, init)

    def get_global(self, key: str, init: Callable[[], Any] = None) -> Any:
        """
        获取全局数据
        :param key: 全局key
        :param init: 初始化函数
        :return: 缓存的数据
        """
        return self.__global_data.get_data(key, init)

    async def set_global(self, key: str, value: Any):
        """
        设置全局数据
        :param key: key
        :param value: 对应值
        :return:
        """
        await self.__global_data.set_data(key, value)

    def set_flow_relation(self, node: FlowNode, prev: list[FlowRelation], after: list[FlowRelation]):
        """
        设置当前节点的关联关系
        :param node: 当前节点
        :param prev: 前一个节点
        :param after: 后一个节点
        :return:
        """
        self.__node_current = node
        self.__node_pre = prev
        self.__node_next = after

    # 获取输入
    def input_get(self) -> dict:
        """
        获取输入
        :return: 函数输入
        """
        return self.__task_info.input

    def node_output_need(self) -> list[str]:
        """
        获取当前节点需要哪些输出字段
        :return:
        """
        return [relation.from_output for relation in self.__node_next]

    async def oss_upload_file(self, path: str, source=1) -> str:
        """
        上传文件
        :param path: 本体路径
        :param source: 上传源
        :return: 云端路径
        """
        return await self.oss.upload_file(self.uid, path, CloudSourceType(source))

    async def oss_upload_bytes(self, data: bytes, ext: str, source=1) -> str:
        """
        上传字节数据
        :param data: 文件内容
        :param ext: 文件后缀
        :param source: 上传源
        :return: 云端路径
        """
        return await self.oss.upload_bytes(self.uid, data, ext, CloudSourceType(source))

    async def oss_upload_file_get_url(self, path: str, source=1) -> str:
        """
        上传文件并获取url
        :param path: 本地路径
        :param source: 云端资源
        :return: 资源链接
        """
        path = await self.oss.upload_file(self.uid, path, CloudSourceType(source))
        return await self.oss.get_url(path, CloudSourceType(source))

    async def oss_upload_bytes_get_url(self, data: bytes, ext: str, source=1) -> str:
        """
        上传文件并获取url
        :param data: 文件内容
        :param ext: 文件后缀
        :param source: 上传源
        :return: 资源链接
        """
        path = await self.oss.upload_bytes(self.uid, data, ext, CloudSourceType(source))
        return await self.oss.get_url(path, CloudSourceType(source))

    async def oss_get_url(self, path: str, source=1) -> str:
        """
        上传文件并获取url
        :param path: 云端路径
        :param source: 云端资源
        :return: 资源链接
        """
        return await self.oss.get_url(path, CloudSourceType(source))

    def tool_generate_local_path(self, ext: str) -> str:
        """
        生成一个本地路径
        :param ext: 文件后缀
        :return: 本体路径
        """
        return self.__base.generate_local_file(ext)

    async def tool_generate_local_file(self, ext: str, data: bytes) -> str:
        path = self.__base.generate_local_file(ext)
        with open(path, "wb") as f:
            f.write(data)
        return path

    @staticmethod
    def tool_get_bytes_encode(data: bytes) -> str:
        """
        获取二进制的编码信息
        :param data:
        :return: 编码信息 {'encoding': 'windows-1251', 'confidence': 0.99, 'language': 'Russian'}
        """
        return chardet.detect(data)['encoding']

    @staticmethod
    def subtitles2srt(subtitles: list) -> bytes:
        """
        字幕格式转srt
        :param subtitles:  字幕 [{"start": 1, "end": 2, "text": "hello"}]
        :return: srt字幕
        """
        return subtitles2srt(subtitles)

    @staticmethod
    async def async_batch_run(
        data_list: list,
        async_fun,
        split_size: int = 1,
        sleep: int = 1,
        args: dict = None,
        err_default: Any = None,
        on_progress: Callable[[int], None] = None,
    ) -> list:
        """
        异步函数批量执行
        :param data_list: 数据列表
        :param split_size: 分割大小
        :param async_fun: 处理数据的异步函数
        :param sleep: 每个任务启动间隔（s）
        :param args: 异步函数的额外参数信息
        :param err_default: 错误默认返回值
        :param on_progress: 进度回调
        :return: 所有处理好的结果
        :return:
        """
        return await async_batch_run(
            data_list,
            async_fun,
            split_size,
            sleep,
            args,
            err_default,
            on_progress
        )

    def ffmpeg_get_duration(self, path: str) -> float:
        """
         获取文件时长
        :param path: 本地路径
        :return: 文件时长
        """
        return self.__ffmpeg.get_duration(path)

    def ffmpeg_execute(self, cmd: str) -> str:
        """
        执行ffmpeg任务
        :param cmd: ffmpeg命令
        :return: 执行结果
        """
        return self.__ffmpeg.ffmpeg_run(cmd)

    def ffmpeg_compress_image(self, img_file: str, quality: int = 5, max_width: int = 1920) -> bytes:
        """
        ffmpeg压缩图片
        :param img_file: 图片路径
        :param quality: 图片质量
        :param max_width: 图片最大宽度
        :return:压缩后的图片内容
        """
        out = self.tool_generate_local_path('jpg')
        cmd = f"-i {img_file} -q {quality} -vf \"scale='if(gt(iw,{max_width}),{max_width},iw)':'if(gt(ih*{max_width}/iw,ih),ih,ih*{max_width}/iw)'\" {out}"
        self.add_log("cmd is", cmd)
        self.ffmpeg_execute(cmd)
        with open(out, "rb") as f:
            return f.read()

    async def tiger_code(self, func_id: str, _input: dict, base=None) -> dict:
        """
        触发代码节点
        :param func_id: 函数id
        :param _input: 函数输入
        :param base: base信息
        :return: 函数返回
        """
        # 获取代码信息
        info, code_info = await self.api.get_entity_info(func_id)
        self.add_desc(info.get('name', ''))
        _inputs = [_input[unique] if unique in _input else None for unique in code_info["inputs"]]
        tmp = {
            "base": base,
            "func_call": lambda _id, inputs: self.tiger_code(_id, inputs, base),
        }
        exec(code_info.get('code', ''), tmp)
        out = await tmp['handle'](*_inputs)
        if not isinstance(out, tuple):
            out = (out,)
        output = {}
        for idx, unique in enumerate(code_info["outputs"]):
            output[unique] = out[idx]
        return output

    @async_throttle(1)
    async def __mqtt_update_progress(self, progress: float):
        """
        更新任务进度，这里会等待任务完成
        :param progress:
        :return:
        """
        try:
            task1 = self.__mqtt.send_task_event(self.uid, self.task_id, MqttEventType.Progress, progress)
            task2 = self.api.task_update_task(self.task_id, progress=progress)
            await asyncio.gather(task1, task2)
        except Exception as e:
            logging.error(f"mqtt_update_progress error {e}")

    def progress_update(self, progress: float):
        """
        更新任务进度(放到后台执行)
        :param progress: 进度信息
        """
        logging.info(f"[base] update progress async {progress}")
        asyncio.create_task(self.__mqtt_update_progress(progress))

    async def progress_update_sync(self, progress: float):
        """
        更新任务进度(需要同步执行)
        :param progress: 进度信息
        """
        logging.info(f"[base] update progress sync {progress}")
        await self.__mqtt_update_progress(progress)

    async def mqtt_detail_append(self, data: dict):
        """
        mqtt详情新增(这里需要等待任务执行完成，否则会导致后面才开始调度)
        :param data: 详情信息
        :return:
        """
        task = self.__mqtt.send_task_event(self.uid, self.task_id, MqttEventType.DetailAppend, data)
        await asyncio.create_task(task)

    async def entity_get_prompt(self, entity_id: str) -> str:
        """
        获取prompt
        :param entity_id: 实体id
        :return: prompt内容
        """
        return (await self.api.get_entity_data(entity_id)).get("prompt", "")

    async def entity_get_name_and_prompt(self, entity_id: str) -> (str, str):
        """
        获取prompt
        :param entity_id: 实体id
        :return: prompt内容
        """
        info, data = await self.api.get_entity_info(entity_id)
        return info.get("name"), data.get("prompt")

    async def doc_query(self, query: str, tag: str = 'help', size: int = 1) -> list:
        """
        知识库查询
        :param query: 查询语句
        :param tag: 知识库标签
        :param size: 查询数量条数
        :return: 知识库列表
        """
        return await self.api.doc_query(query, tag, size)

    async def img_query(self, embedding: list[float], tag: str, size: int = 1) -> list:
        """
        图片信息检索
        :param embedding: 图片向量
        :param tag: 图片标签
        :param size: 数据条数
        :return: 查询结果
        """
        return await self.api.img_query(embedding, tag, size)

    @staticmethod
    def json_parse(data: str) -> dict:
        """
        大语言模型解析
        :param data: json字符串
        :return: json结果
        """
        return llm_json_parse(data)

    def exception_param_invalid(self, msg: str):
        """
        参数非法
        :param msg: 提示信息
        :return: 参数异常
        """
        raise ParamInvalid(msg)

    def exception_remote_error(self, code: int, msg: str):
        """
        远程服务错误
        :param code: 错误码
        :param msg: 错误信息
        """
        raise RemoteError(code, msg)

    def exception_unknown(self, msg: str):
        """
        未知错误
        :param msg: 错误信息
        """
        raise UnknownError(msg)

    def exception(self, msg: str = '', code: int = 1):
        """
        统一异常
        :param code: 错误码
        :param msg: 错误信息
        """
        raise ServerError(code, msg)


# 处理节点定义
node_define = Callable[[FlowBase, dict, Optional[dict]], Awaitable[dict]]
