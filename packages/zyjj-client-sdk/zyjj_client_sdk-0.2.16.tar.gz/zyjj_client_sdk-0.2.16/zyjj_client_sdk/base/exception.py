class ServerError(Exception):
    """服务器异常"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = str(message)

    def __str__(self):
        return f'错误码：{self.code}\n错误信息：{self.message}'

class BusinessError(ServerError):
    """业务错误，默认使用该错误"""
    def __init__(self, msg=''):
        super().__init__(1, msg)

class RemoteError(ServerError):
    """远程服务错误"""
    def __init__(self, code: int, msg=''):
        super().__init__(10, f'远程服务错误！错误码:{code} 错误信息:{msg}')

class PointNotEnough(ServerError):
    """积分不足"""
    def __init__(self, point: int, current: int = None):
        msg = f'积分不足！所需积分{point}'
        if current is not None:
            msg += f' 当前积分{current}'
        super().__init__(100, msg)

class ParamInvalid(ServerError):
    """参数非法"""
    def __init__(self, msg: str):
        super().__init__(400, msg)

class UnknownError(ServerError):
    """未知错误"""
    def __init__(self, msg: str):
        super().__init__(-1, msg)
