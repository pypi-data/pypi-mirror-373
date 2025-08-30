import asyncio
import logging
import time

import pytest

from zyjj_client_sdk.base.decorator import async_debounce, async_throttle

@async_debounce(1)
async def echo1(msg: str | int):
    logging.info(f"echo {msg}")

@async_throttle(1)
async def echo2(msg: str | int):
    logging.info(f"echo {msg}")

@pytest.mark.asyncio
async def test_debounce():
    logging.info("hello")
    # 最后只会输出 9
    for i in range(10):
        asyncio.create_task(echo1(i))
        await asyncio.sleep(0.2)
    await asyncio.sleep(1)

@pytest.mark.asyncio
async def test_throttle():
    logging.info("hello")
    # 每隔1s输出一次
    for i in range(10):
        asyncio.create_task(echo2(i))
        await asyncio.sleep(0.5)
