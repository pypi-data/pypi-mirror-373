import asyncio
import logging
import time
from typing import Callable, Any, Awaitable
import threading

class Cache:
    """缓存管理"""
    def __init__(self):
        # 全局数据锁
        self.__global_async_lock: dict[str, asyncio.Lock] = {}
        self.__global_sync_lock: dict[str, threading.Lock] = {}
        # 全局数据
        self.__global_data = {}

    def __get_async_lock(self, key: str) -> asyncio.Lock:
        """获取一个全局锁"""
        if key not in self.__global_async_lock:
            self.__global_async_lock[key] = asyncio.Lock()
        return self.__global_async_lock[key]

    def __get_sync_lock(self, key: str) -> threading.Lock:
        """获取一个全局锁"""
        if key not in self.__global_sync_lock:
            self.__global_sync_lock[key] = threading.Lock()
        return self.__global_sync_lock[key]

    async def async_set_data(self, key: str, value: any):
        """添加全局数据"""
        async with self.__get_async_lock(key):
            self.__global_data[key] = value

    def set_data(self, key: str, value: any):
        """添加全局数据"""
        with self.__get_sync_lock(key):
            self.__global_data[key] = value

    async def async_get_data(
        self,
        key: str,
        init: Callable[[], Awaitable[Any]] = None
    ) -> Any:
        """
        获取全局数据
        :param key: 全局key
        :param init: 初始化函数（不存在时调用该方法初始化）
        :return: 缓存的数据
        """
        async with self.__get_async_lock(key):
            data = self.__global_data.get(key)
            if data is None:
                start = time.time()
                if init is not None:
                    data = await init()
                logging.info(f'get async {key} from init, cost {(time.time() - start):.4f}s')
                if data is not None:
                    self.__global_data[key] = data
            else:
                logging.info(f'get async {key} from cache')
        return data

    def get_data(
        self,
        key: str,
        init: Callable[[], Any] = None
    ) -> Any:
        """
        获取全局数据
        :param key: 全局key
        :param init: 初始化函数（不存在时调用该方法初始化）
        :return: 缓存的数据
        """
        with self.__get_sync_lock(key):
            data = self.__global_data.get(key)
            if data is None:
                start = time.time()
                if init is not None:
                    data = init()
                logging.info(f'get sync {key} from init, cost {(time.time() - start):.4f}s')
                if data is not None:
                    self.__global_data[key] = data
            else:
                logging.info(f'get sync {key} from cache')
        return data
