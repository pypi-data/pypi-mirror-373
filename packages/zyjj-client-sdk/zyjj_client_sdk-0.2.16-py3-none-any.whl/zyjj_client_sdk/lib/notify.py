from zyjj_client_sdk.base import Base
from httpx import AsyncClient

class NotifyService:
    def __init__(self, base: Base):
        self.__base = base
        self.__session = AsyncClient(timeout=60)

    async def send_notify(self, title: str, content: str, tags: list[str] | str = None, short: str = ''):
        """
        发送通知
        :param title: 通知标题
        :param content: 通知内容
        :param tags: 通知标签
        :param short: 推送消息的简短描述
        :return:
        """
        data = {"title": title, "desp": content}
        if tags:
            if isinstance(tags, str):
                tags = [tags]
            data["tags"] = '|'.join(tags)
        if short:
            data["short"] = short
        return (await self.__session.post(self.__base.notify_url, json=data)).json()
