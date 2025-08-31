"""异常定义"""

from ._version import __version__


class Lims2Error(Exception):
    """Lims2 SDK 基础异常"""

    def __init__(self, message: str = ""):
        # 自动在错误信息末尾添加版本号
        if message and not message.endswith(f"(lims2-sdk v{__version__})"):
            message = f"{message} (lims2-sdk v{__version__})"
        super().__init__(message)


class ConfigError(Lims2Error):
    """配置错误"""

    pass


class AuthError(Lims2Error):
    """认证错误"""

    pass


class UploadError(Lims2Error):
    """上传错误"""

    pass


class APIError(Lims2Error):
    """API 调用错误"""

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code
