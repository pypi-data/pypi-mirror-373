"""主客户端模块"""

from typing import Optional

import requests
import urllib3

from .chart import ChartService
from .config import Config
from .exceptions import ConfigError
from .network import HostsAdapter, set_dns_fallback_context
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

        # 创建带连接池优化的 HTTP 会话
        self.session = self._create_session()
        self.session.headers.update(self.config.get_headers())

        # 设置DNS回退上下文，让所有网络操作都支持DNS回退
        hosts_adapter = None
        for _protocol, adapter in self.session.adapters.items():
            if isinstance(adapter, HostsAdapter):
                hosts_adapter = adapter
                break

        if hosts_adapter:
            set_dns_fallback_context(self.config, hosts_adapter)

        # 直接初始化服务
        self.chart = ChartService(self)
        self.storage = StorageService(self)

    def _create_session(self) -> requests.Session:
        """创建配置了重试策略和连接池的会话

        针对网络不稳定问题：
        - 配置自动重试机制处理 DNS 解析失败
        - 指数退避避免频繁重试
        - 优化连接池复用连接
        - 设置合理的超时时间
        """
        session = requests.Session()

        # 不再使用urllib3的Retry，改用tenacity在应用层处理重试
        # 适配器专注于连接池管理，重试由@network_retry装饰器处理

        # 使用智能适配器，支持DNS回退策略
        # - 默认使用系统DNS
        # - 遇到DNS问题时自动回退到优质DNS解析IP直连
        # - 用户配置的custom_hosts优先级最高
        adapter = HostsAdapter(
            config=self.config,
            pool_connections=10,
            pool_maxsize=20,
            pool_block=False,
        )

        # 为 HTTP 和 HTTPS 设置适配器
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # 配置SSL验证
        session.verify = self.config.verify_ssl

        return session

    def close(self) -> None:
        """关闭客户端，清理资源"""
        # 清理DNS回退上下文
        from .network import clear_dns_fallback_context

        clear_dns_fallback_context()

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
