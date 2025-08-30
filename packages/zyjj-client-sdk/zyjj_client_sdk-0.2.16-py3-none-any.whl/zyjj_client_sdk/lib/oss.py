import logging
import shutil
from zyjj_client_sdk.base.api import ApiService
from zyjj_client_sdk.base import Base
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from io import BytesIO
from oss2 import ProviderAuth, Bucket
from oss2.credentials import StaticCredentialsProvider
from zyjj_client_sdk.base.const import CloudSourceType
from zyjj_client_sdk.base.exception import ParamInvalid


def _callback(i: float):
    logging.info(f"[storage] current progress {i}")

class OSSService:
    def __init__(self, base: Base, api: ApiService):
        self.__base = base
        self.__api = api
        self.__cos_client = None
        self.__cos_bucket = ""
        self.__cos_region = ""
        self.__oss_client = None

    async def __get_cos_client(self):
        if self.__cos_client is None:
            auth = await self.__api.could_get_tencent_cos()
            self.__cos_bucket = auth["bucket"]
            self.__cos_region = auth["region"]
            token = auth["token"]
            self.__cos_client = CosS3Client(CosConfig(
                Region=auth["region"],
                SecretId=token["TmpSecretId"],
                SecretKey=token["TmpSecretKey"],
                Token=token["Token"],
                Scheme="https",
            ))
        return self.__cos_client

    async def __get_oss_client(self):
        if self.__oss_client is None:
            auth = await self.__api.cloud_get_aliyun_oss()
            self.__oss_bucket = auth["bucket"]
            token = auth["token"]
            self.__oss_client = Bucket(
                ProviderAuth(StaticCredentialsProvider(token["TmpSecretId"], token["TmpSecretKey"], token["Token"])),
                auth["endpoint"],
                auth["bucket"],
                region=auth["region"]
            )
        return self.__oss_client

    # 下载文件到本地
    async def download_file(self, key: str, source: CloudSourceType) -> str:
        if key is None or key == "":
            return ""
        path = self.__base.generate_file_with_path(key)
        logging.info(f"download file {key}, local path {path}")
        if source == CloudSourceType.TencentCos:
            (await self.__get_cos_client()).download_file(Bucket=self.__cos_bucket, Key=key, DestFilePath=path)
        elif source == CloudSourceType.AliYunOss:
            (await self.__get_oss_client()).get_object_to_file(key, path)
        else:
            raise ParamInvalid("unknown cloud source")
        return path

    # 获取二进制数据
    async def get_bytes(self, key: str, source: CloudSourceType) -> bytes:
        if key is None or key == "":
            return b''
        buffer = BytesIO()
        if source == CloudSourceType.TencentCos:
            res = (await self.__get_cos_client()).get_object(self.__cos_bucket, key)
            shutil.copyfileobj(res['Body'], buffer)
        elif source == CloudSourceType.AliYunOss:
            stream = (await self.__get_oss_client()).get_object(key)
            shutil.copyfileobj(stream, buffer)
        buffer.seek(0)
        return buffer.read()

    # 文件上传
    async def upload_file(self, uid: str, path: str, source: CloudSourceType) -> str:
        # 拦截非法请求
        if path is None or path == "":
            return ""
        key = f"tmp/{uid}/{self.__base.generate_filename(path.split('.')[-1])}"
        if source == CloudSourceType.TencentCos:
            (await self.__get_cos_client()).upload_file(Bucket=self.__cos_bucket, Key=key, LocalFilePath=path,)
        elif source == CloudSourceType.AliYunOss:
            (await self.__get_oss_client()).put_object_from_file(key, path)
        else:
            raise ParamInvalid("unknown cloud source")
        return key

    # 二进制上传
    async def upload_bytes(self, uid: str, data: bytes, ext: str, source: CloudSourceType) -> str:
        if data is None or len(data) == 0:
            return ""
        key = f"tmp/{uid}/{self.__base.generate_filename(ext)}"
        if source == CloudSourceType.TencentCos:
            (await self.__get_cos_client()).upload_file_from_buffer(Bucket=self.__cos_bucket, Key=key, Body=BytesIO(data))
        elif source == CloudSourceType.AliYunOss:
            (await self.__get_oss_client()).put_object(key, data)
        else:
            raise ParamInvalid("unknown cloud source")
        return key

    # 默认链接有效期6个小时
    async def get_url(self, key: str, source: CloudSourceType, expired=3600*6):
        if key is None or key == "":
            return ""
        if source == CloudSourceType.TencentCos:
            url = (await self.__get_cos_client()).get_presigned_download_url(Bucket=self.__cos_bucket, Key=key, Expired=expired, SignHost=False,)
            return str(url).replace(f'{self.__cos_bucket}.cos.{self.__cos_region}.myqcloud.com', 'cos-origin.zyjj.cc')
        elif source == CloudSourceType.AliYunOss:
            return (await self.__get_oss_client()).sign_url("GET", key, expired)
        else:
            raise ParamInvalid("unknown cloud source")
