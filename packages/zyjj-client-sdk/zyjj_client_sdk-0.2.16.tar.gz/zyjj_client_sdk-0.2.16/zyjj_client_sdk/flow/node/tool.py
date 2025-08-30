import asyncio
import json
import logging
import re

import math
import uuid
from typing import Optional
from tencentcloud.common import credential

from zyjj_client_sdk.lib.oss import OSSService
from zyjj_client_sdk.base.exception import RemoteError, ParamInvalid
from zyjj_client_sdk.flow.base import FlowBase
from zyjj_client_sdk.flow.node.common import get_val_or_default, tool_check_point, tool_cost_point, FileSourceType
from tenacity import retry, wait_fixed, stop_after_attempt
from zyjj_client_sdk.base.const import CloudSourceType


# 获取云端配置
async def node_get_config(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    name = get_val_or_default("name", data, extra)
    is_json = extra.get("is_json", False)
    val = await base.api.get_config(name)
    if is_json:
        val = json.loads(val)
    return {"val": val}


# 检查积分
async def node_check_point(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    point = get_val_or_default('point', data, extra, 0)
    await tool_check_point(base, point)
    return {"point": point, "pass": data.get("pass")}


# 扣除积分
@retry(wait=wait_fixed(1), stop=stop_after_attempt(3), reraise=True)
async def node_cost_point(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    name = get_val_or_default("name", data, extra, "")
    desc = get_val_or_default("desc", data, extra, "")
    point = get_val_or_default('point', data, extra, 0)
    await tool_cost_point(base, name, desc, point)
    return {"pass": data.get("pass")}


# 下载文件返回二进制数据
async def _download_file(base: FlowBase, url: str, referer: str) -> bytes:
    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'}
    if referer != "":
        header["referer"] = referer
    logging.info(f"start download {url}")
    res = await base.client.get(url, headers=header)
    if res.status_code != 200:
        logging.error(f"download error {res.content}")
        raise RemoteError(res.status_code, "文件下载失败")
    return res.content

async def _download_url_and_upload(
    base: FlowBase,
    oss: OSSService,
    url: str,
    referer: str,
    ext: str,
    cloud_source: CloudSourceType
) -> str:
    data = await _download_file(base, url, referer)
    return await oss.upload_bytes(base.uid, data, ext, cloud_source)

# 上传文件
@retry(wait=wait_fixed(1), stop=stop_after_attempt(3), reraise=True)
async def node_upload_file(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    # 输入和输出参数
    in_file_source = FileSourceType(get_val_or_default("in_file_source", data, extra, 0))
    out_file_source = FileSourceType(get_val_or_default("out_file_source", data, extra, 0))
    # 上传来源
    cloud_source = CloudSourceType(get_val_or_default("cloud_source", data, extra, 1))
    # 是否批量
    is_batch = get_val_or_default("is_batch", data, extra, False)
    oss = base.oss
    # 最后得出的云端路径
    cloud_path_list = []
    output = {}
    # 不同文件来源走不同的方式，最后统一拿到一个云端路径列表
    if in_file_source == FileSourceType.CloudPath:  # 云端路径 todo 需要考虑不同云端路径互转
        path = data.get("cloud_path", "")
        source = data.get("cloud_source")  # 先暂时不管
        cloud_path_list = path if is_batch else [path]
    elif in_file_source == FileSourceType.CloudFile:
        cloud_file = data.get("cloud_file", {})
        cloud_file_fields = extra.get("cloud_file_fields", [])
        cloud_file_list = cloud_file if is_batch else [cloud_file]
        output = _parse_file(cloud_file_list[0], cloud_file_fields)
        cloud_path_list = [_parse_file(file)["path"] for file in cloud_file_list]
    elif in_file_source == FileSourceType.CloudLink:  # 云端链接
        referer = get_val_or_default("referer", data, extra, "")
        ext = get_val_or_default("ext", data, extra, "")
        cloud_url = data.get("cloud_url")
        url_list = cloud_url if is_batch else [cloud_url]
        # 下载任务列表
        task_list = [
            _download_url_and_upload(base, oss, url, referer, ext, cloud_source)
            for url in url_list
        ]
        cloud_path_list = await asyncio.gather(*task_list)
    elif in_file_source == FileSourceType.LocalPath:  # 本地路径
        local_path = data.get("local_path")
        local_path_list = local_path if is_batch else [local_path]
        task_list = [
            oss.upload_file(base.uid, path, cloud_source)
            for path in local_path_list
        ]
        cloud_path_list = await asyncio.gather(*task_list)
    elif in_file_source == FileSourceType.Bytes:  # 字节数据
        bytes_data = data.get("bytes_data")
        ext = get_val_or_default("ext", data, extra, "")
        bytes_list = bytes_data if is_batch else [bytes_data]
        task_list = [
            oss.upload_bytes(base.uid, b, ext, cloud_source)
            for b in bytes_list
        ]
        cloud_path_list = await asyncio.gather(*task_list)
    # 根据输出类型执行不同的操作
    if out_file_source == FileSourceType.CloudPath:  # 云端路径
        output["cloud_path"] = cloud_path_list if is_batch else cloud_path_list[0]
        output["cloud_source"] = cloud_source.value
    elif out_file_source == FileSourceType.CloudLink:  # 云端链接
        task_list = [
            oss.get_url(path, cloud_source)
            for path in cloud_path_list
        ]
        url_list = await asyncio.gather(*task_list)
        output["cloud_url"] = url_list if is_batch else url_list[0]
    elif out_file_source == FileSourceType.CloudFile:  # 云端文件
        cloud_file_list = [_parse_file({"path": path, "source": cloud_source.value}) for path in cloud_path_list]
        output["cloud_file"] = cloud_file_list if is_batch else cloud_file_list[0]

    return output


# 下载文件
@retry(wait=wait_fixed(1), stop=stop_after_attempt(3), reraise=True)
async def node_download_file(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    in_file_source = FileSourceType(get_val_or_default("in_file_source", data, extra, 0))
    out_file_source = FileSourceType(get_val_or_default("out_file_source", data, extra, 0))
    is_batch = get_val_or_default("is_batch", data, extra, False)
    oss = base.oss
    output = {}
    if in_file_source == FileSourceType.CloudFile or in_file_source == FileSourceType.CloudPath:  # 云端路径或者云端文件
        cloud_source = CloudSourceType.TencentCos
        # 云端路径统一都是下载到本地（云端文件需要手动解析一下）
        if in_file_source == FileSourceType.CloudPath:
            cloud_path = data.get("cloud_path")
            cloud_source = CloudSourceType(data.get("cloud_source"))  # 先不管
            if cloud_path is None:
                return {}
            cloud_path_list = cloud_path if is_batch else [cloud_path]
        else:
            cloud_file = data.get("cloud_file")
            cloud_file_fields = extra.get("cloud_file_fields", [])
            if cloud_file is None:
                return {}
            cloud_file_list = cloud_file if is_batch else [cloud_file]
            output = _parse_file(cloud_file_list[0], cloud_file_fields)
            cloud_source = CloudSourceType(cloud_file_list[0]["source"])
            cloud_path_list = [_parse_file(file)['path'] for file in cloud_file_list]
        # 根据需求返回不同的数据
        if out_file_source == FileSourceType.LocalPath:  # 本地路径
            task_list = [
                oss.download_file(path, cloud_source)
                for path in cloud_path_list
            ]
            local_path_list = await asyncio.gather(*task_list)
            output["local_path"] = local_path_list if is_batch else local_path_list[0]
        elif out_file_source == FileSourceType.Bytes:  # 字节流
            task_list = [
                oss.get_bytes(path, cloud_source)
                for path in cloud_path_list
            ]
            bytes_list = await asyncio.gather(*task_list)
            output["bytes_data"] = bytes_list if is_batch else bytes_list[0]
    elif in_file_source == FileSourceType.CloudLink:  # 云端链接
        referer = get_val_or_default("referer", data, extra, "")
        ext = get_val_or_default("ext", data, extra, "")
        cloud_url = data.get("cloud_url")
        if cloud_url is None:
            return {}
        url_list = cloud_url if is_batch else [cloud_url]
        task_list = [
            _download_file(base, url, referer)
            for url in url_list
        ]
        bytes_list = await asyncio.gather(*task_list)
        if out_file_source == FileSourceType.LocalPath:  # 本地路径
            task_list = [
                base.tool_generate_local_file(ext, b)
                for b in bytes_list
            ]
            local_path_list = await asyncio.gather(*task_list)
            output["local_path"] = local_path_list if is_batch else local_path_list[0]
        elif out_file_source == FileSourceType.Bytes:  # 字节流
            output["bytes_data"] = bytes_list if is_batch else bytes_list[0]
    return output


def _parse_file(file: dict, fields=None) -> dict:
    path = file.get("path", "")
    file = {
        "path": path,
        "source": file.get("source", 0),
        "duration": file.get("duration", 0),
        "size": file.get("size", 0),
        "name": file.get("name", path.split("/")[-1]),
        "ext": file.get("ext", path.split(".")[-1]),
        "uid": file.get("uid", uuid.uuid4().hex)
    }
    return {field: file[field] for field in fields} if fields is not None else file


# 文件解析
async def node_file_parse(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    fields = get_val_or_default("fields", data, extra, [])
    return _parse_file(data.get("file"), fields)


# 文件组织
async def node_file_export(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    return _parse_file(data)


# 腾讯云token
async def node_get_tencent_token(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    token = await base.api.could_get_tencent_token()
    return {"token": credential.Credential(token["TmpSecretId"], token["TmpSecretKey"])}


# 生成本地路径
async def node_generate_local_path(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    ext = get_val_or_default('ext', data, extra)
    return {"path": base.tool_generate_local_path(ext)}


# ffmpeg 积分计算
async def node_ffmpeg_point(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    path = get_val_or_default("path", data, extra)
    point = get_val_or_default("point", data, extra, default=0)
    duration = get_val_or_default("duration", data, extra, default=0)
    check_point = get_val_or_default("check_point", data, extra, default=False)
    if path is not None:
        duration = base.ffmpeg_get_duration(path)
    final_point = math.ceil(float(point) * (duration / 60))
    base.add_log("duration", duration)
    output = {"point": final_point}
    if check_point:
        await tool_check_point(base, final_point)
        output["pass"] = get_val_or_default("pass", data, extra)
    return output


# ffmpeg 命令
async def node_ffmpeg(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    inputs = get_val_or_default("inputs", data, extra)
    in_ext = get_val_or_default("input_ext", data, extra)
    outputs = get_val_or_default("outputs", data, extra)
    out_ext = get_val_or_default("output_ext", data, extra)
    in_file_source = FileSourceType(get_val_or_default("in_file_source", data, extra, 10))
    out_file_source = FileSourceType(get_val_or_default("out_file_source", data, extra, 10))
    cmd = get_val_or_default("command", data, extra, '')
    if in_file_source == FileSourceType.Bytes:
        for _input in inputs:
            name = base.tool_generate_local_path(in_ext)
            open(name, "wb").write(data[_input])
            data[_input] = name
    for _output in outputs:
        data[_output] = base.tool_generate_local_path(out_ext)
    # 执行ffmpeg任务
    res = base.ffmpeg_execute(cmd.format(**data))
    logging.info("execute ffmpeg result", res)
    return {
        _output: data[_output] if out_file_source == FileSourceType.LocalPath else open(data[_output], "rb").read()
        for _output in outputs
    }


# 链接提取
@retry(wait=wait_fixed(1), stop=stop_after_attempt(3), reraise=True)
async def node_link_extra(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    url = get_val_or_default("url", data, extra, "").strip()
    regex = get_val_or_default("url_regex", data, extra, "")
    header = get_val_or_default("header", data, extra, {})
    # 首先我们使用正则表达式来提取字符串里面的url
    res = re.findall(r'(https?://\S+|www\.\S+)', url)
    if len(res) == 0:
        raise ParamInvalid("url非法")
    else:
        # 使用get请求获取一下重定向后的地址
        res = await base.client.get(res[0], headers=header)
        if res.status_code != 200:
            base.add_log(f"server code err {res.status_code}")
            raise RemoteError(res.status_code, f'服务错误，请稍后重试')
        url = str(res.url)
        # 使用正则进行匹配
        if regex != "":
            re_content = re.findall(regex, url)
            url = '' if len(re_content) == 0 else re_content[0]
        return {
            "url": url,
            "content": res.content
        }


# 开放平台操作
async def node_openplatform(base: FlowBase, data: dict, extra: Optional[dict]) -> dict:
    option = get_val_or_default("option", data, extra, 0)
    _input = get_val_or_default("input", data, extra, {})
    output = _input
    if base.source == "api":
        # 判断操作
        if option == 1:
            # 文件转url
            path, source = _input.get("path", ""), _input.get("source", 0)
            output = await base.oss_get_url(path, source)
        elif option == 2:
            # 开放平台使用输入2
            output = get_val_or_default("input2", data, extra, None)

    return {"output": output}
