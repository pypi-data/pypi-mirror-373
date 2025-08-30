from typing import Any, Callable, Awaitable

class base:
    @staticmethod
    def add_log(*args):
        """
        添加节点日志
        :param args: 日志列表
        :return:
        """

    @staticmethod
    async def async_get_global(key: str, init: Callable[[], Awaitable[Any]] = None) -> Any:
        """
        异步获取全局数据
        :param key: 全局key
        :param init: 初始化函数
        :return: 缓存的数据
        """

    @staticmethod
    def get_global(key: str, init: Callable[[], Any] = None) -> Any:
        """
        获取全局数据
        :param key: 全局key
        :param init: 初始化函数
        :return: 缓存的数据
        """

    @staticmethod
    async def set_global(key: str, value: Any):
        """
        设置全局数据
        :param key: key
        :param value: 对应值
        :return:
        """

    @staticmethod
    async def oss_upload_file(path: str, source=1) -> str:
        """
        上传文件
        :param path: 本体路径
        :param source: 上传源
        :return: 云端路径
        """

    @staticmethod
    async def oss_upload_bytes(data: bytes, ext: str, source=1) -> str:
        """
        上传字节数据
        :param data: 文件内容
        :param ext: 文件后缀
        :param source: 上传源
        :return: 云端路径
        """

    @staticmethod
    async def oss_upload_file_get_url(path: str, source=1) -> str:
        """
        上传文件并获取url
        :param path: 本地路径
        :param source: 云端资源
        :return: 资源链接
        """

    @staticmethod
    async def oss_upload_bytes_get_url(data: bytes, ext: str, source=1) -> str:
        """
        上传文件并获取url
        :param data: 文件内容
        :param ext: 文件后缀
        :param source: 上传源
        :return: 资源链接
        """

    @staticmethod
    async def oss_get_url(path: str, source=1) -> str:
        """
        上传文件并获取url
        :param path: 云端路径
        :param source: 云端资源
        :return: 资源链接
        """

    @staticmethod
    def tool_generate_local_path(ext: str) -> str:
        """
        生成一个本地路径
        :param ext: 文件后缀
        :return: 本体路径信息
        """

    @staticmethod
    async def tool_generate_local_file(ext: str, data: bytes) -> str:
        """
        生成一个本地文件
        :param ext: 文件后缀
        :param data: 文件数据
        :return: 文件路径
        """


    @staticmethod
    def tool_get_bytes_encode(data: bytes) -> str:
        """
        获取二进制的编码信息
        :param data:
        :return: 编码信息 {'encoding': 'windows-1251', 'confidence': 0.99, 'language': 'Russian'}
        """

    @staticmethod
    def subtitles2srt(subtitles: list) -> bytes:
        """
        字幕格式转srt
        :param subtitles:  字幕 [{"start": 1, "end": 2, "text": "hello"}]
        :return: srt字幕
        """

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

    @staticmethod
    def ffmpeg_get_duration(path: str) -> float:
        """
         获取文件时长
        :param path: 本地路径
        :return: 文件时长
        """

    @staticmethod
    def ffmpeg_execute(cmd: str) -> str:
        """
        执行ffmpeg任务
        :param cmd: ffmpeg命令
        :return: 执行结果
        """

    @staticmethod
    def ffmpeg_compress_image(img_file: str, quality: int = 5, max_width: int = 1920) -> bytes:
        """
        ffmpeg压缩图片
        :param img_file: 图片路径
        :param quality: 图片质量
        :param max_width: 图片最大宽度
        :return:压缩后的图片内容
        """

    @staticmethod
    async def tiger_code(func_id: str, _input: dict, _base=None) -> dict:
        """
        触发代码节点
        :param func_id: 函数id
        :param _input: 函数输入
        :param _base: base信息
        :return: 函数返回
        """

    @staticmethod
    def progress_update(progress: float):
        """
        异步进度更新
        :param progress: 进度信息
        """

    @staticmethod
    async def progress_update_sync(progress: float):
        """
        同步更新任务进度
        :param progress: 进度信息
        """

    @staticmethod
    async def mqtt_detail_append(data: dict):
        """
        mqtt详情新增
        :param data: 详情信息
        :return:
        """

    @staticmethod
    async def entity_get_prompt(entity_id: str) -> str:
        """
        获取prompt
        :param entity_id: 实体id
        :return: prompt内容
        """

    @staticmethod
    async def entity_get_name_and_prompt(entity_id: str) -> (str, str):
        """
        获取prompt名称和prompt内容
        :param entity_id: 实体id
        :return: prompt名称，prompt内容
        """

    @staticmethod
    async def doc_query(query: str, tag: str = 'help', size: int = 1) -> list:
        """
        知识库查询
        :param query: 查询语句
        :param tag: 知识库标签
        :param size: 查询数量条数
        :return: 知识库列表
        """

    @staticmethod
    async def img_query(embedding: list[float], tag: str, size: int = 1) -> list:
        """
        图片信息检索
        :param embedding: 图片向量
        :param tag: 图片标签
        :param size: 数据条数
        :return: 查询结果
        """

    @staticmethod
    def json_parse(data: str) -> dict:
        """
        大语言模型解析
        :param data: json字符串
        :return: json结果
        """

    @staticmethod
    def exception_param_invalid(msg: str):
        """
        参数非法
        :param msg: 提示信息
        :return: 参数异常
        """

    @staticmethod
    def exception_remote_error(code: int, msg: str):
        """
        远程服务错误
        :param code: 错误码
        :param msg: 错误信息
        """

    @staticmethod
    def exception_unknown(msg: str):
        """
        未知错误
        :param msg: 错误信息
        """

    @staticmethod
    def exception(msg: str = '', code: int = 1):
        """
        统一异常
        :param code: 错误码
        :param msg: 错误信息
        """

