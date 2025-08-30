import logging
import os
import uuid


class Base:
    def __init__(
        self,
        username=os.environ.get("zyjj_username"),
        password=os.environ.get("zyjj_password"),
        host=os.environ.get("zyjj_host"),
        mqtt_proxy=os.environ.get("zyjj_mqtt_proxy"),
        knowledge_host=os.environ.get("zyjj_knowledge"),
        process_size=os.environ.get("zyjj_process_size"),
        notify_url=os.environ.get("zyjj_notify_url")
    ):
        """
        初始化基础服务
        :param username: 用户名
        :param password: 密码
        :param host: 开放平台地址
        :param mqtt_proxy: mqtt代理地址
        :param knowledge_host: 知识库地址
        :param process_size: 同时处理的任务数量
        """
        self.username = username
        self.password = password
        self.host = host
        self.knowledge_host = knowledge_host
        self.mqtt_proxy = mqtt_proxy
        self.process_size = int(process_size if bool(process_size) else "1")
        self.tmp_dir = "/tmp"
        # server酱通知地址
        self.notify_url = notify_url
        logging.info(f"[core] process size {self.process_size}")

    # 生成一个文件名
    @staticmethod
    def generate_filename(extend: str) -> str:
        return f"{str(uuid.uuid4())}.{extend}"

    # 生成一个临时文件
    def generate_local_file(self, extend: str) -> str:
        return f"{self.tmp_dir}/{str(uuid.uuid4())}.{extend}"

    # 根据路径生成一个新的同名文件
    def generate_file_with_path(self, path: str) -> str:
        return self.generate_local_file(path.split(".")[-1])
