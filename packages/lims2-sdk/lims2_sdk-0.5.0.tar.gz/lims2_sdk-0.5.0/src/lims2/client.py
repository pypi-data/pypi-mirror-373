"""主客户端模块"""

from typing import Optional

import requests
import urllib3

from .chart import ChartService
from .config import Config
from .exceptions import ConfigError
from .storage import StorageService

# 禁用 urllib3 的 SSL 警告，因为我们在内网环境中使用，用户可以根据需要启用 SSL 验证
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Lims2Client:
    """Lims2 SDK 主客户端

    提供图表和文件存储等服务的统一入口。典型用法：

    Example:
        >>> from lims2 import Lims2Client
        >>> client = Lims2Client()
        >>>
        >>> # 上传图表
        >>> client.chart.upload("plot.json", project_id="proj_001")
        >>>
        >>> # 上传文件
        >>> client.storage.upload_file("results.csv", project_id="proj_001")
    """

    def __init__(self, api_url: Optional[str] = None, token: Optional[str] = None):
        """初始化客户端

        Args:
            api_url: API 地址（可选，默认从环境变量读取）
            token: API Token（可选，默认从环境变量读取）
        """
        # 初始化配置
        self.config = Config(api_url, token)

        # 验证配置
        try:
            self.config.validate()
        except ValueError as e:
            raise ConfigError(str(e))

        # 创建标准的 HTTP 会话
        self.session = requests.Session()
        self.session.headers.update(self.config.get_headers())

        # 配置SSL验证
        self.session.verify = self.config.verify_ssl

        # 直接初始化服务
        self.chart = ChartService(self)
        self.storage = StorageService(self)

    def close(self) -> None:
        """关闭客户端，清理资源"""
        if hasattr(self, "session"):
            self.session.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

    def __repr__(self) -> str:
        return f"Lims2Client(api_url={self.config.api_url!r})"
