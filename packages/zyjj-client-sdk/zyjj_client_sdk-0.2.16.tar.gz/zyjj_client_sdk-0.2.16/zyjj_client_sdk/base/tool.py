import re
import asyncio
import logging
from typing import Any, Callable

import math
import json5
import regex


def format_ms(ms: int):
    """
    毫秒时间戳转换为字幕时间戳
    :param ms:
    :return:
    """
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    seconds = (ms % 60000) // 1000
    milliseconds = ms % 1000
    # 格式化字符串
    return "{:02d}:{:02d}:{:02d},{:03d}".format(int(hours), int(minutes), int(seconds), int(milliseconds))

def subtitles2srt(subtitles: list) -> bytes:
    """
    字幕转字节数据
    :param subtitles:
    :return:
    """
    srt = ""
    for i, subtitle in enumerate(subtitles):
        srt += f"{i + 1}\n"
        srt += f"{format_ms(subtitle['start'])} --> {format_ms(subtitle['end'])}\n"
        srt += f"{subtitle['text']}\n\n"
    return srt.encode()


async def task_warp(async_fun, err_default, sleep: int = 0, **kwargs):
    """
    异步任务包装
    :param async_fun: 异步函数
    :param err_default: 执行任务失败时返回的默认值
    :param sleep: 任务执行延迟
    :param kwargs: 异步函数的参数信息
    :return: 异步函数执行结果
    """
    try:
        # 延迟固定时间，避免并发太高
        await asyncio.sleep(sleep)
        # 触发我们的实际处理逻辑
        return await async_fun(**kwargs)
    except Exception as e:
        logging.error(f"task error {e}")
        if err_default is not None:
            return err_default
        raise e


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
    """
    num_segments = math.ceil(len(data_list) / split_size)
    logging.info(f"segments size {num_segments}")
    task_list = []
    res_list = []
    # 把任务全部添加到任务组里面去
    async with asyncio.TaskGroup() as tg:
        # 依次添加任务
        for i in range(num_segments):
            logging.info(f"start task {i}")
            start = i * split_size
            end = min((i + 1) * split_size, len(data_list))
            logging.info(f"args {args}")
            task_list.append(tg.create_task(task_warp(
                async_fun,
                err_default,
                sleep * i,
                data=data_list[start:end],
                **args
            )))
        # 等待所有任务完成
        for idx in range(num_segments):
            res_list.append(await task_list[idx])
            if on_progress is not None:
                on_progress(int((idx+1) / num_segments * 100))
    return res_list

def llm_json_parse(data: str) -> dict:
    """
    解析llm返回的字符串
    :param data: 原始字符串数据
    :return: 返回结果
    """
    # 我们使用json5来解析，避免大模型输出多余,
    try:
        return json5.loads(data)
    except Exception as e:
        logging.warning(f"parse json file err {e}")

    # 可以使用正则来匹配json里面的内容
    match = re.search(r'```json\s*([\s\S]*?)```', data)
    if match is not None:
        return llm_json_parse(match.group(1))

    # 最后直接匹配json格式
    pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')
    objects = pattern.findall(data)
    if len(objects) > 0:
        return llm_json_parse(objects[0])

    raise Exception('no json str found')


# 对象转换
def data_convert(data: Any) -> Any:
    # 基本类型直接转换
    if isinstance(data, (str, int, float, bool)):
        return data
    elif data is None:
        return None
    elif isinstance(data, dict):
        return {k: data_convert(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [data_convert(v) for v in data]
    else:
        return str(type(data))
