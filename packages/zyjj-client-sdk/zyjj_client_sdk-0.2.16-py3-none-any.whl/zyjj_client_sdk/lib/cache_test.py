import asyncio
import logging
from threading import Thread
import time

from zyjj_client_sdk.lib.cache import Cache
import pytest

cache = Cache()

async def async_get_data():
    logging.info('get data')
    await asyncio.sleep(1)
    return 1

def get_data():
    logging.info('get data')
    time.sleep(1)
    return 1

@pytest.mark.asyncio
async def test_async_get_lock():
    task1 = cache.async_get_data('a', async_get_data)
    task2 = cache.async_get_data('a', async_get_data)
    await asyncio.gather(task1, task2)

def _get_data():
    data = cache.get_data('a', get_data)
    print(data)

def test_get_lock():
    Thread(target=_get_data).start()
    Thread(target=_get_data).start()
    time.sleep(2)
