"""OSS操作基类

提取图表服务和存储服务的共同OSS操作逻辑
"""

import logging
import time
from typing import Any

import oss2

from .network import OSSHostsSession, network_retry
from .utils import get_hostname_from_url, handle_api_response


class OSSMixin:
    """OSS操作混入类

    提供STS临时凭证获取和OSS Bucket创建的通用功能
    """

    def __init_oss__(self):
        """初始化OSS混入功能"""
        # STS 凭证缓存，避免频繁请求
        self._sts_cache = {}
        self._max_cache_size = 50  # 最大缓存条目数，防止内存泄漏

    def _get_oss_path_prefix(self) -> str:
        """根据API URL判断环境并返回相应的OSS路径前缀

        Returns:
            str: 环境相关的路径前缀
                - 生产环境 (api-v2): "media"
                - 测试环境 (其他): "test"
        """
        # 检查API URL是否包含"api-v2"
        is_production = "api-v2" in self.config.api_url
        return "media" if is_production else "test"

    @network_retry(max_retries=3, base_delay=1.0, max_delay=10.0)
    def _get_sts_token(self, project_id: str) -> dict[str, Any]:
        """获取阿里云 STS 临时访问凭证

        Args:
            project_id: 项目 ID

        Returns:
            dict[str, Any]: STS 凭证信息，包含：
                - access_key_id: 临时访问密钥 ID
                - access_key_secret: 临时访问密钥
                - security_token: 安全令牌
                - endpoint: OSS 服务端点
                - bucket_name: OSS 存储桶名称

        Raises:
            APIError: 获取 STS 凭证失败

        Note:
            - 使用带时间戳的内存缓存避免频繁请求
            - 缓存键格式：project_id:team_id
            - STS 凭证有时效性，默认15分钟，缓存10分钟后自动刷新
            - 批量上传时能显著减少API请求次数
        """
        cache_key = f"{project_id}:{self.config.team_id}"

        # 检查缓存是否有效（包含时间检查）
        if cache_key in self._sts_cache:
            cached_data = self._sts_cache[cache_key]
            # STS凭证默认有效期15分钟，提前5分钟刷新
            if time.time() - cached_data["cache_time"] < 10 * 60:  # 10分钟内有效
                return {k: v for k, v in cached_data.items() if k != "cache_time"}

        # 从 API 获取新的 STS 凭证
        params = {"team_id": self.config.team_id} if self.config.team_id else {}
        response = self.session.get(
            f"{self.config.api_url}/get_data/aliyun_sts/",
            params=params,
            timeout=self.config.timeout,
        )

        result = handle_api_response(response, "获取STS凭证")
        raw_data = result.get("record", result)

        # 构建标准化的凭证信息
        token_data = {
            "access_key_id": raw_data.get("AccessKeyId"),
            "access_key_secret": raw_data.get("AccessKeySecret"),
            "security_token": raw_data.get("SecurityToken"),
            "endpoint": self.config.oss_endpoint,
            "bucket_name": self.config.oss_bucket_name,
            "cache_time": time.time(),  # 添加缓存时间戳
        }

        # 缓存凭证并返回（返回时去除时间戳）
        self._sts_cache[cache_key] = token_data

        # 检查缓存大小，清理过期项目以防止内存泄漏
        self._cleanup_cache()

        return {k: v for k, v in token_data.items() if k != "cache_time"}

    def _cleanup_cache(self) -> None:
        """清理过期的STS缓存条目，防止内存泄漏"""
        current_time = time.time()
        expired_keys = []

        # 找出所有过期的缓存键（超过10分钟）
        for key, data in self._sts_cache.items():
            if current_time - data.get("cache_time", 0) > 10 * 60:
                expired_keys.append(key)

        # 删除过期缓存
        for key in expired_keys:
            self._sts_cache.pop(key, None)

        # 如果缓存仍然过大，删除最旧的条目
        if len(self._sts_cache) > self._max_cache_size:
            # 按缓存时间排序，删除最旧的条目
            sorted_items = sorted(
                self._sts_cache.items(), key=lambda x: x[1].get("cache_time", 0)
            )

            num_to_remove = len(self._sts_cache) - self._max_cache_size
            for key, _ in sorted_items[:num_to_remove]:
                self._sts_cache.pop(key, None)

    def _get_oss_bucket(self, project_id: str) -> oss2.Bucket:
        """获取配置了 STS 认证的 OSS Bucket 对象

        Args:
            project_id: 项目 ID，用于获取对应的 STS 凭证

        Returns:
            oss2.Bucket: 配置了临时凭证的 Bucket 实例

        Raises:
            APIError: STS 凭证获取失败
        """
        sts_info = self._get_sts_token(project_id)
        auth = oss2.StsAuth(
            sts_info["access_key_id"],
            sts_info["access_key_secret"],
            sts_info["security_token"],
        )

        endpoint = sts_info["endpoint"]
        bucket_name = sts_info["bucket_name"]

        # 检查是否需要使用自定义IP
        if self.config.custom_hosts:
            # 获取主机名
            hostname = get_hostname_from_url(endpoint)

            # 如果有自定义映射
            if hostname in self.config.custom_hosts:
                custom_ip = self.config.custom_hosts[hostname]

                logging.getLogger(__name__).info(
                    f"OSS使用自定义IP: {hostname} -> {custom_ip}"
                )

                # 创建智能session，实现IP直连且保持Host header
                session = OSSHostsSession(config=self.config)

                # 使用原始endpoint（包含域名），让session处理IP替换
                return oss2.Bucket(auth, endpoint, bucket_name, session=session)

        # 没有自定义hosts映射，使用默认方式
        return oss2.Bucket(auth, endpoint, bucket_name)
