from enum import Enum

# 云端文件来源
class CloudSourceType(Enum):
    LocalPath = 0  # 本地(路径)
    TencentCos = 1  # 腾讯云cos
    ObjectUrl = 2  # ObjectUrl
    AliYunOss = 3  # 阿里云oss
