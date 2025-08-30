import json
import logging
from httpx import AsyncClient
from zyjj_client_sdk.base.base import Base
from zyjj_client_sdk.base.entity import TaskStatus
from zyjj_client_sdk.base.exception import RemoteError
import urllib.parse

class ApiService:
    def __init__(self, base: Base):
        self.__header = {
            "x-username": base.username,
            "x-password": base.password,
            "Content-Type": "application/json",
            "referer": "https://zyjj.cc"
        }
        self.__base = f"{base.host}/api/v1/client"
        self.__knowledge = f"{base.knowledge_host}/api/v1/client"
        self.__session = AsyncClient(timeout=60)

    async def __request(self, method: str, path: str, data: dict = None, host: str = None) -> dict | list | int:
        url = f"{self.__base}/{path}"
        if host is not None:
            url = f"{host}/{path}"
        logging.info(f"[api] request url {url}")
        res = None
        if method == "get":
            param = ""
            if data is not None:
                param = "?"+urllib.parse.urlencode(data, doseq=True)
                logging.info(f"[api] param is {param}")
            res = await self.__session.get(f"{url}{param}", headers=self.__header)
        elif method == "put":
            res = await self.__session.put(url, json=data, headers=self.__header)
        elif method == "post":
            res = await self.__session.post(url, json=data, headers=self.__header)
        elif method == "delete":
            res = await self.__session.delete(url, headers=self.__header)
        if res is None:
            logging.info("[request] request res is none")
        elif res.status_code != 200:
            logging.info(f"[request] request status code is {res.status_code}, res is {res.text}")
            raise RemoteError(res.status_code, "http请求错误")
        else:
            res = res.json()
            if "code" in res and res["code"] != 0:
                raise RemoteError(res["code"], res["msg"])
            else:
                return res["data"]
        return {}

    async def could_get_tencent_token(self) -> dict:
        """
        获取腾讯云token
        :return: token信息
        """
        return await self.__request("get", "cloud/tencent/token")

    async def could_get_tencent_cos(self) -> dict:
        """
        获取腾讯云cos秘钥信息
        :return: 秘钥值
        """
        return await self.__request("get", "cloud/tencent/cos")

    async def cloud_get_aliyun_oss(self) -> dict:
        """
        获取阿里云oss秘钥信息
        :return: 秘钥值
        """
        return await self.__request("get", "cloud/aliyun/oss")

    async def cloud_get_mqtt(self) -> dict:
        """
        获取MQTT链接
        :return: MQTT连接信息
        """
        return await self.__request("get", f"cloud/mqtt/task")

    async def task_pull_task(self) -> dict:
        """
        拉取一个新任务
        :return:
        """
        return await self.__request("get", "task/pull")

    async def task_pull_flow(self, task_type: int) -> dict:
        """
        获取任务流程信息
        :param task_type: 任务类型
        :return: 流程数据
        """
        return await self.__request("get", f"flow/{task_type}")

    async def task_update_task(
            self,
            task_id: str,
            status: TaskStatus = None,
            output: str = None,
            point_cost: int = None,
            code: int = None,
            msg: str = None,
            progress: float = None,
    ):
        """
        任务状态更新
        :param task_id: 任务id
        :param status: 任务状态
        :param point_cost: 消耗积分
        :param output: 任务输出
        :param code: 错误码
        :param msg: 错误信息
        :param progress: 执行进度
        :return:
        """
        data = {}
        if status is not None:
            data["status"] = status.value
        if output is not None:
            data["output"] = output
        if point_cost is not None:
            data["point_cost"] = point_cost
        if code is not None:
            data["code"] = code
        if msg is not None:
            data["msg"] = msg
        if progress is not None:
            data["progress"] = progress

        return await self.__request("put", f"task/{task_id}", data)

    async def get_user_point(self, uid: str) -> int:
        """
        获取用户剩余积分
        :param uid: 用户id
        :return:
        """
        return await self.__request("get", f"point/user/{uid}")

    async def use_user_point(self, task_id: str, uid: str, name: str, point: int, desc='') -> bool:
        """
        扣除用户积分
        :param task_id: 任务id
        :param uid: 用户id
        :param name: 任务名称
        :param point: 消耗积分
        :param desc: 任务描述
        :return:
        """
        if len(desc) > 20:
            desc = f'{desc[:20]}...'
        logging.info(f"[api] {uid} use point {point}")
        try:
            # 先尝试扣除积分
            await self.__request("post", "point/deducting", {
                "uid": uid,
                "name": name,
                "point": int(point),
                "desc": desc,
            })
            # 更新任务id消耗的积分
            await self.task_update_task(task_id, point_cost=point)
            return True
        except Exception as e:
            logging.error(f"[api] use_user_point error {e}")
            return False

    async def get_config(self, key: str) -> str:
        """
        获取配置信息
        :param key: 配置key
        :return:
        """
        config: dict = await self.__request("get", f"config/{key}")
        return config.get("value", "")

    async def get_config_json(self, key: str) -> dict:
        """
        获取配置信息
        :param key: 配置key
        :return: 配置值
        """
        return json.loads(await self.get_config(key))

    async def upload_flow_log(self, data: dict):
        """
        上传流程日志
        :param data: 流程信息
        :return: 日志返回
        """
        return await self.__request("post", "flow/log", data)

    async def get_entity_data(self, entity_id: str) -> dict:
        """
        获取实体数据
        :param entity_id: 实体id
        :return: 实体配置
        """
        res = await self.__request("get", f"entity/{entity_id}")
        return json.loads(res.get('data', '{}'))

    async def get_entity_info(self, entity_id: str) -> (dict, dict):
        """
        获取原始实体内容
        :param entity_id:
        :return: 原始实体内容，实体数据
        """
        data = await self.__request("get", f"entity/{entity_id}")
        return data, json.loads(data.get('data', '{}'))

    async def doc_query(self, query: str, tag: str, size: int) -> list:
        """
        文档检索
        :param query: 关键词
        :param tag: 标签
        :param size: 检索大小
        :return: 检索到的文档列表
        """

        return await self.__request("get", f"doc/query", {
            "query": query,
            "tag": tag,
            "size": size
        }, host=self.__knowledge)

    async def img_query(self, embedding: list[float], tag: str, size: int) -> list:
        """
        图片检索
        :param embedding: 特征值
        :param tag: 图片标签
        :param size: 检索大小
        :return: 图片列表
        """
        return await self.__request(
            'post',
            'img/query',
            {"embedding": embedding, "tag": tag, "size": size},
            host=self.__knowledge
        )
