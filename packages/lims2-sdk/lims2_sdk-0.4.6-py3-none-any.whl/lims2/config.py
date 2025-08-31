"""配置管理模块"""

import os
from typing import Optional


class Config:
    """配置管理类"""

    def __init__(self, api_url: Optional[str] = None, token: Optional[str] = None):
        """初始化配置

        Args:
            api_url: API 地址，如果不提供则从环境变量读取
            token: API Token，如果不提供则从环境变量读取
        """
        self.api_url = (
            api_url
            if api_url is not None
            else os.environ.get("LIMS2_API_URL") or "https://api-v1.lims2.com"
        )
        self.token = token or os.environ.get("LIMS2_API_TOKEN")
        self.team_id = (
            os.environ.get("LIMS2_TEAM_ID") or "be4e0714c336d2b4bfe00718310d01d5"
        )

        # 网络配置
        self.timeout = int(os.environ.get("LIMS2_TIMEOUT", "600"))  # 默认10分钟
        self.max_retries = int(os.environ.get("LIMS2_MAX_RETRIES", "3"))  # 重试次数
        self.retry_delay = float(os.environ.get("LIMS2_RETRY_DELAY", "1.0"))  # 重试延迟
        self.connection_timeout = int(
            os.environ.get("LIMS2_CONNECTION_TIMEOUT", "30")
        )  # 连接超时
        self.read_timeout = int(os.environ.get("LIMS2_READ_TIMEOUT", "300"))  # 读取超时

        # OSS配置
        self.oss_endpoint = (
            os.environ.get("LIMS2_OSS_ENDPOINT")
            or "https://oss-cn-shanghai.aliyuncs.com"
        )
        self.oss_bucket_name = os.environ.get("LIMS2_OSS_BUCKET_NAME") or "protree"

        # 自定义 hosts 映射 (用于绕过 DNS 解析问题)
        # 格式: "host1:ip1,host2:ip2" 例如: "protree.oss-cn-shanghai.aliyuncs.com:47.96.86.30"
        self.custom_hosts = self._parse_custom_hosts(
            os.environ.get("LIMS2_CUSTOM_HOSTS", "")
        )

        # 优质DNS服务器列表，用于DNS回退策略
        self.fallback_dns_servers = self._parse_dns_servers(
            os.environ.get("LIMS2_FALLBACK_DNS", "223.6.6.6,223.5.5.5,8.8.8.8")
        )

        # IP健康检查配置
        self.ip_health_check_timeout = int(
            os.environ.get("LIMS2_IP_HEALTH_CHECK_TIMEOUT", "5")
        )  # 5秒

        # SSL验证配置 - 默认禁用以适应内网环境
        self.verify_ssl = os.environ.get("LIMS2_VERIFY_SSL", "false").lower() != "false"

        # 临时目录配置
        self.custom_temp_dir = os.environ.get("LIMS2_TEMP_DIR")  # 自定义临时目录

    def validate(self) -> None:
        """验证配置是否完整"""
        if not self.api_url:
            raise ValueError("API URL 未配置，请设置环境变量 LIMS2_API_URL")
        if not self.token:
            raise ValueError("API Token 未配置，请设置环境变量 LIMS2_API_TOKEN")

    def get_headers(self) -> dict[str, str]:
        """获取 API 请求头"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _parse_custom_hosts(self, hosts_str: str) -> dict[str, str]:
        """解析自定义 hosts 映射

        Args:
            hosts_str: hosts 字符串，格式如 "host1:ip1,host2:ip2"

        Returns:
            hosts 映射字典
        """
        if not hosts_str:
            return {}

        hosts_map = {}
        for pair in hosts_str.split(","):
            pair = pair.strip()
            if ":" in pair:
                host, ip = pair.split(":", 1)
                hosts_map[host.strip()] = ip.strip()

        return hosts_map

    def _parse_dns_servers(self, dns_str: str) -> list[str]:
        """解析优质DNS服务器列表

        Args:
            dns_str: DNS服务器字符串，格式如 "8.8.8.8,1.1.1.1"

        Returns:
            DNS服务器IP地址列表
        """
        if not dns_str:
            return []

        servers = []
        for server in dns_str.split(","):
            server = server.strip()
            if server:
                servers.append(server)

        return servers
