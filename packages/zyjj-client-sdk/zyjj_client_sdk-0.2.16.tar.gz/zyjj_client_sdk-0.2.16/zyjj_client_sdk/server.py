import asyncio
import json
import logging
import sys
import time
import traceback

from zyjj_client_sdk.base import Base, ApiService, MqttServer, MqttEventType
from zyjj_client_sdk.base.entity import TaskInfo, TaskStatus
from zyjj_client_sdk.base.exception import ServerError
from zyjj_client_sdk.flow import FlowBase, FlowService
from zyjj_client_sdk.lib import OSSService, Cache, NotifyService


class Service:
    # 初始化基本服务
    def __init__(self):
        self.__base = Base()
        # 对外暴露api服务
        self.api = ApiService(self.__base)
        self.__oss = OSSService(self.__base, self.api)
        self.__notify = NotifyService(self.__base)
        self.__handle = {}
        # mqtt服务
        self.__mqtt = MqttServer(self.__base, self.api)
        # 全局数据
        self.__global_data = Cache()
        # 初始化任务队列
        self.__task_queue = asyncio.Queue()
        # 当前正在执行的任务列表
        self.active_tasks = set()
        # 服务是否启动
        self.__running = False
        # 任务清理函数
        self.__clean_task = None
        # 控制我们同时最大执行的事件数
        self.__semaphore = asyncio.Semaphore(self.__base.process_size)

    def add_global(self, key: str, value: any) -> 'Service':
        """
        异步给服务添加全局变量
        :param key: 全局变量的key
        :param value: 全局值
        :return: 服务本身
        """
        self.__global_data.set_data(key, value)
        return self

    async def __start_consumer(self):
        """
        启动一个消费者不断去消费任务
        :return:
        """
        logging.info('[core] start consumer')
        # 不断循环消费任务
        while self.__running:
            try:
                # 使用 get 的超时机制，这样可以定期检查 running 状态
                try:
                    t = await asyncio.wait_for(self.__task_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                logging.info(f"[core] get new task {t}")
                # 创建任务并开始处理
                asyncio.create_task(self.execute_one_task())
                # 完成任务并开始下一轮消费
                self.__task_queue.task_done()
            except Exception as e:
                logging.error(f"[core] error processing task: {str(e)}")
                await asyncio.sleep(0.1)  # 发生错误时短暂暂停

    def start(self):
        """
        后台启动服务
        :return: 服务本身
        """
        # 服务只能启动一次
        if self.__running:
            return
        logging.info("[core] server start")
        self.__running = True
        # 启动mqtt
        asyncio.create_task(self.__mqtt.start())
        # 启动消费者
        asyncio.create_task(self.__start_consumer())

    async def stop(self):
        """
        停止服务
        :return:
        """
        logging.info("[core] stop service")
        if not self.__running:
            return
        self.__running = False
        # 关闭mqtt
        self.__mqtt.close()
        # 等待所有活动任务完成
        if self.active_tasks:
            logging.info("[core] wait task finish...")
            # return_exceptions 为true表示有一个失败也会继续执行
            await asyncio.gather(*self.active_tasks, return_exceptions=True)
        # 退出系统
        sys.exit(0)

    async def __success(self, uid: str, task_id: str, data: dict):
        """
        发送成功通知
        :param uid: 用户id
        :param task_id: 任务id
        :param data: 任务执行结果
        :return:
        """
        task1 = self.api.task_update_task(
            task_id,
            status=TaskStatus.Success,
            output=json.dumps(data, ensure_ascii=False),
            progress=100,
        )
        task2 = self.__mqtt.send_task_event(
            uid,
            task_id,
            MqttEventType.Success,
            data
        )
        await asyncio.gather(task1, task2)

    async def __fail(self, uid: str, task_id: str, code: int, msg: str):
        """
        发送失败通知
        :param uid: 用户id
        :param task_id: 任务id
        :param code: 错误码
        :param msg: 错误信息
        :return:
        """
        task1 = self.api.task_update_task(
            task_id,
            status=TaskStatus.Fail,
            code=code,
            msg=msg,
        )
        task2 = self.__mqtt.send_task_event(
            uid,
            task_id,
            MqttEventType.Fail,
            msg,
            code
        )
        await asyncio.gather(task1, task2)

    async def notify(self):
        """
        后台异步通知
        :return:
        """
        logging.info(f'notify new task')
        # 给任务队列添加一条新数据
        await self.__task_queue.put(time.time())

    async def execute_one_task(self, task_info: dict | None = None, sync: bool = True) -> dict | None:
        """
        执行单个任务,需要确保任务并发不能超过一定数量
        :param task_info: 任务信息
        :param sync: 是否同步执行成功失败通知
        :return: 任务返回
        """
        # __semaphore 只会限制execute_one_task 这个的并发，不会影响里面的任务
        async with self.__semaphore:
            task = asyncio.create_task(self.__execute_one_task(task_info, sync))
            self.active_tasks.add(task)
            data = await task
            self.active_tasks.discard(task)
            return data

    async def __execute_one_task(self, task_info: dict | None, sync: bool) -> dict | None:
        # 如果没有传任务信息，那么就手动拉一下任务
        if task_info is None:
            logging.info(f'[task] pull new task')
            task_info = await self.api.task_pull_task()
        if task_info is None:
            logging.info("[task] task not found")
            return None
        logging.info(f'[task] task is {task_info}')
        try:
            # 获取任务信息
            task_info = TaskInfo(
                task_id=task_info.get('id', ''),  # 任务id
                uid=task_info.get('uid', ''),
                task_type=task_info.get('task_type', 0),
                input=json.loads(task_info.get('input', '{}')),
                source=task_info.get('source', 'unknown')
            )
            # 初始化base服务
            _base = FlowBase(
                self.__base,
                self.api,
                self.__mqtt,
                self.__oss,
                self.__global_data,
                task_info
            )
            # 如果是代码节点，我们就可以直接去执行代码
            if task_info.task_type == 1:
                _input = task_info.input
                data = await _base.tiger_code(_input["entity_id"], _input["input"], _base)
                await self.__success(task_info.uid, task_info.task_id, data)
                return data
            # 否则我们正常去执行流程
            flow_info = await self.api.task_pull_flow(task_info.task_type)
            logging.info(f"flow info {flow_info}")
            # 初始化流程服务并触发流程
            data = await FlowService(_base, flow_info['flow_info']).tiger_flow()
            # 异步上报成功
            task = asyncio.create_task(self.__success(task_info.uid, task_info.task_id, data))
            if sync:
                await task
            return {"code": 0, "data": data, "msg": "success"}
        # 捕获服务错误
        except ServerError as e:
            traceback.print_exc()
            task = asyncio.create_task(self.__fail(task_info.uid, task_info.task_id, e.code, e.message))
            if sync:
                await task
            return {"code": e.code, "data": {}, "msg": str(e)}
        except Exception as e:
            traceback.print_exc()
            task = asyncio.create_task(self.__fail(task_info.uid, task_info.task_id, -1, str(e)))
            asyncio.create_task(self.__send_err_notify(task_info, e, traceback.format_exc()))
            if sync:
                await task
            return {"code": -1, "data": {}, "msg": str(e)}

    async def __send_err_notify(self, task: TaskInfo, err: Exception, stack: str):
        await self.__notify.send_notify("服务失败告警", '\n\n'.join([
            f"任务id: {task.task_id}",
            f"堆栈信息: \n```text\n{stack}\n```"
        ]), "server_err",  str(err))
