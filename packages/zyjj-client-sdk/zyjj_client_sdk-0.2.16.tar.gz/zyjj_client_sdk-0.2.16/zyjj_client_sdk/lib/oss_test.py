import hashlib

from zyjj_client_sdk.lib.oss import OSSService
from zyjj_client_sdk.base import Base, ApiService, CloudSourceType

base = Base("test", "test", "http://127.0.0.1:3000")
oss = OSSService(base, ApiService(base))

def test_upload():
    # key1 = oss.upload_file("test", "../../tmp/test.srt", CloudSourceType.TencentCos)
    # key2 = oss.upload_file("test", "../../tmp/test.srt", CloudSourceType.AliYunOss)
    # print(key1, key2)
    key1 = oss.upload_bytes("test", b"hello", "txt", CloudSourceType.TencentCos)
    key2 = oss.upload_bytes("test", b"hello", "txt", CloudSourceType.AliYunOss)
    print(key1, key2)


def calculate_md5(byte_data):
    # 创建一个 MD5 哈希对象
    md5_hash = hashlib.md5()

    # 更新哈希对象，传入字节数据
    md5_hash.update(byte_data)

    # 获取十六进制的哈希值
    return md5_hash.hexdigest()

def test_download():
    # path1 = oss.download_file("tmp/test/b85cf99d-085e-46d0-8ec3-9325faf050dc.txt", CloudSourceType.TencentCos)
    # path2 = oss.download_file("tmp/test/70512347-94ff-47bb-8150-04ee15848195.txt", CloudSourceType.AliYunOss)
    # print(path1, path2)
    # data1 = oss.get_bytes("tmp/65b1aa96d633cb4aefb7871e/0829b579-e45f-4ef0-b712-878280ed24dd.png", CloudSourceType.TencentCos)
    # data2 = oss.get_bytes("tmp/test/70512347-94ff-47bb-8150-04ee15848195.txt", CloudSourceType.AliYunOss)
    # print(data1, data2)
    data1 = oss.get_bytes("tmp/65b1aa96d633cb4aefb7871e/24958919-d4a3-457e-a991-204ece586812.jpg", CloudSourceType.TencentCos)
    print(calculate_md5(data1))

def test_link():
    url1 = oss.get_url("tmp/test/b85cf99d-085e-46d0-8ec3-9325faf050dc.txt", CloudSourceType.TencentCos)
    url2 = oss.get_url("tmp/test/70512347-94ff-47bb-8150-04ee15848195.txt", CloudSourceType.AliYunOss)
    print(url1, url2)

