class LoginFailed(Exception):
    """异常：登录失败"""

    def __init__(self, message="登录失败，请检查登录步骤"):
        self.message = message
        super().__init__(self.message)


class FileNotFound(Exception):
    """异常：文件不存在"""

    def __init__(self, message="文件不存在，请检查文件路径"):
        self.message = message
        super().__init__(self.message)


class Timeout(Exception):
    """异常：等待超时"""

    def __init__(self, message="等待超时"):
        self.message = message
        super().__init__(self.message)


class InvalidArgument(Exception):
    """异常：无效参数"""

    def __init__(self, message="输入参数无效"):
        self.message = message
        super().__init__(self.message)