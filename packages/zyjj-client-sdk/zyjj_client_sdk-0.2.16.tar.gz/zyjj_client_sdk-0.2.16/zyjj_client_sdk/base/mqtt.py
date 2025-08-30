import json
import logging
import time
from enum import Enum

import httpx

from zyjj_client_sdk.base.base import Base
from zyjj_client_sdk.base.api import ApiService
import paho.mqtt.client as mqtt


class MqttEventType(Enum):
    Start = 1  # 开始任务
    Progress = 2  # 进度事件
    Success = 3  # 成功
    Fail = 4  # 失败
    DetailAppend = 5  # 详情追加
    DetailSet = 6  # 详情覆盖


class MqttServer:
    def __init__(self, base: Base, api: ApiService):
        self.__subscribe = {}
        self.__proxy = None
        self.__base = base
        self.__api = api
        # 客户端信息
        self.__client_id = ''
        self.__username = ''
        self.__password = ''
        # 消息队列
        self.__client: mqtt.Client | None = None

    async def start(self):
        """启动mqtt服务"""
        # 获取客户端信息
        info = await self.__api.cloud_get_mqtt()
        host = info['host']
        self.__client_id, self.__username, self.__password = (info['client_id'], info['username'], info['password'])
        logging.info(
            f"[mqtt] info host {host} client_id {self.__client_id} "
            f"username {self.__username} password {self.__password}"
        )
        # 如果不是代理我们才建立mqtt连接
        logging.info(f"[mqtt] mqtt proxy is {self.__base.mqtt_proxy}")
        if bool(self.__base.mqtt_proxy):
            self.__proxy = httpx.AsyncClient(base_url=self.__base.mqtt_proxy)
            return
        self.__client = mqtt.Client(client_id=self.__client_id, protocol=mqtt.MQTTv311)
        self.__client.username_pw_set(self.__username, self.__password)
        self.__client.on_connect = lambda client, userdata, flags, rc: self.__on_connect(rc)
        self.__client.on_disconnect = lambda client, userdata, rc: self.__on_disconnect(rc)
        # self.__client.on_message = lambda client, userdata, msg: self.__on_message(msg)
        self.__client.connect(host, 1883, 30)
        self.__client.loop_start()

    def __on_disconnect(self, code: int):
        """重连函数"""
        logging.info(f"[mqtt] disconnect {code}")
        if code != 0:
            logging.info(f"[mqtt] reconnect in 3 second ~")
            time.sleep(3)
            self.__client.reconnect()

    def close(self):
        """关闭mqtt连接"""
        self.__client.loop_stop()
        self.__client.disconnect()

    @staticmethod
    def __on_connect(rc: int):
        if rc == 0:
            logging.info(f"[mqtt] connect success")

    # 发送event事件
    async def send_task_event(self, uid: str, task_id: str, event_type: MqttEventType, data=None, code=-1):
        topic = f"task_event/{uid}"
        data = json.dumps({
            'task_id': task_id,
            'event_type': event_type.value,
            'code': code,
            'data': data
        }, ensure_ascii=False).encode()
        if bool(self.__proxy):
            logging.info(f"[mqtt] proxy {topic} send message {event_type} data {data}")
            res = await self.__proxy.post(
                topic,
                content=data,
                headers={
                    "x-cid": self.__client_id,
                    "x-username": self.__username,
                    "x-password": self.__password
                }
            )
            res.raise_for_status()
        else:
            logging.info(f'[mqtt] mqtt publish data {data}')
            self.__client.publish(topic, data, qos=1, retain=True)
