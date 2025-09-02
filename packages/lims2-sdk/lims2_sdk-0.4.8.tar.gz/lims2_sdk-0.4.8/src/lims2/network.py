"""网络重试和容错机制"""

import logging
import socket
import threading
from functools import wraps
from typing import Any, Callable, Optional
from urllib.parse import urlparse, urlunparse

import dns.exception
import dns.resolver
import oss2
import requests
from requests.adapters import HTTPAdapter
from tenacity import (
    after_log,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_combine,
    wait_exponential,
    wait_random,
)

logger = logging.getLogger(__name__)

# DNS回退上下文（线程本地存储）
_dns_context = threading.local()


# 可重试的网络异常
def get_retryable_network_errors():
    """获取可重试的网络异常类型"""
    return (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.ReadTimeout,
        requests.exceptions.ConnectTimeout,
        requests.exceptions.SSLError,
        OSError,  # DNS解析错误等
        oss2.exceptions.RequestError,
        oss2.exceptions.ServerError,
    )


class DNSFallbackContext:
    """DNS回退上下文数据容器"""

    def __init__(self, config, hosts_adapter):
        self.config = config
        self.hosts_adapter = hosts_adapter
        self.attempted_hosts = set()  # 避免重复尝试同一主机


def set_dns_fallback_context(config, hosts_adapter):
    """设置DNS回退上下文"""
    _dns_context.current = DNSFallbackContext(config, hosts_adapter)


def clear_dns_fallback_context():
    """清除DNS回退上下文"""
    if hasattr(_dns_context, "current"):
        delattr(_dns_context, "current")


def _is_dns_error(exception) -> bool:
    """检查是否为DNS相关错误"""
    dns_errors = (
        ConnectionError,
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        socket.gaierror,
        OSError,
    )
    return isinstance(exception, dns_errors)


def _try_dns_fallback_from_context(retry_state):
    """从上下文尝试DNS回退"""
    if not hasattr(_dns_context, "current"):
        return

    context = _dns_context.current
    exception = retry_state.outcome.exception()

    if not exception or not _is_dns_error(exception):
        return

    # 尝试从API URL提取主机名进行DNS回退
    if hasattr(context.config, "api_url"):
        parsed = urlparse(context.config.api_url)
        hostname = parsed.hostname

        if (
            hostname
            and hostname not in context.attempted_hosts
            and hasattr(context.config, "fallback_dns_servers")
        ):
            context.attempted_hosts.add(hostname)

            # 直接使用DNS回退函数，不通过HostsAdapter
            ip_address = resolve_with_fallback_dns(
                hostname, context.config.fallback_dns_servers
            )
            if ip_address:
                # 直接添加到HostsAdapter的动态映射中
                context.hosts_adapter.dynamic_hosts[hostname] = ip_address
                context.hosts_adapter._update_hosts_map()
                logger.info(
                    f"DNS回退成功，下次重试将使用解析的IP地址访问 {hostname} -> {ip_address}"
                )


def network_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
):
    """网络重试装饰器，使用tenacity实现，支持DNS回退

    使用线程本地存储简化DNS回退逻辑：
    - tenacity负责重试策略和异常处理
    - DNS回退通过before_sleep回调透明处理
    - 充分利用tenacity的功能，代码更简洁

    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟时间（秒）
        max_delay: 最大延迟时间（秒）
        backoff_factor: 退避倍数
        jitter: 是否添加随机抖动
    """
    # 配置等待策略
    wait_strategy = wait_exponential(
        multiplier=base_delay, max=max_delay, exp_base=backoff_factor
    )
    if jitter:
        wait_strategy = wait_combine(
            wait_strategy,
            wait_random(0, base_delay * 0.1),  # 10%的随机抖动
        )

    # 构建可重试的异常类型
    retryable_exceptions = get_retryable_network_errors()

    def decorator(func: Callable) -> Callable:
        @retry(
            stop=stop_after_attempt(max_retries + 1),
            wait=wait_strategy,
            retry=retry_if_exception_type(retryable_exceptions),
            before_sleep=lambda retry_state: (
                before_sleep_log(logger, logging.WARNING)(retry_state),
                _try_dns_fallback_from_context(retry_state),
            )[1],  # 先记录日志，然后尝试DNS回退
            after=after_log(logger, logging.DEBUG),
            reraise=True,
        )
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _resolve_with_system_dns(hostname: str) -> Optional[str]:
    """使用系统默认DNS解析域名"""
    try:
        system_resolver = dns.resolver.Resolver()
        system_resolver.timeout = 3.0
        system_resolver.lifetime = 5.0

        answers = system_resolver.resolve(hostname, "A")
        if answers:
            ip_address = str(answers[0])
            logger.info(f"使用系统默认DNS成功解析 {hostname} -> {ip_address}")
            return ip_address

    except Exception as e:
        logger.debug(f"系统默认DNS解析失败: {e}")

    return None


def _resolve_with_custom_dns(hostname: str, dns_server: str) -> Optional[str]:
    """使用指定DNS服务器解析域名"""
    try:
        # 创建自定义的DNS解析器
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [dns_server]
        resolver.timeout = 3.0  # 查询超时时间
        resolver.lifetime = 5.0  # 总超时时间

        try:
            # 执行A记录查询（IPv4地址）
            answers = resolver.resolve(hostname, "A")

            # 获取第一个IP地址
            if answers:
                ip_address = str(answers[0])
                logger.info(
                    f"使用DNS服务器 {dns_server} 成功解析 {hostname} -> {ip_address}"
                )
                return ip_address

        except dns.resolver.NXDOMAIN:
            logger.warning(f"域名 {hostname} 不存在（DNS服务器: {dns_server}）")
        except dns.resolver.NoAnswer:
            logger.warning(f"域名 {hostname} 没有A记录（DNS服务器: {dns_server}）")
        except dns.exception.Timeout:
            logger.warning(f"DNS服务器 {dns_server} 查询超时")
        except Exception as e:
            logger.warning(f"DNS服务器 {dns_server} 解析 {hostname} 失败: {e}")

    except Exception as e:
        logger.warning(f"创建DNS解析器失败（服务器: {dns_server}）: {e}")

    return None


def resolve_with_fallback_dns(hostname: str, dns_servers: list[str]) -> Optional[str]:
    """使用指定的DNS服务器解析域名

    使用dnspython库真正实现指定DNS服务器的解析，而不是依赖系统DNS。
    这确保了当系统DNS不可用时，仍然可以通过备用DNS服务器解析域名。

    Args:
        hostname: 要解析的域名
        dns_servers: DNS服务器列表（如 ['223.6.6.6', '223.5.5.5']）

    Returns:
        解析到的IP地址，失败返回None
    """
    # 如果没有指定DNS服务器，直接使用系统默认DNS
    if not dns_servers:
        result = _resolve_with_system_dns(hostname)
        if result:
            return result
        logger.error(f"系统默认DNS无法解析 {hostname}")
        return None

    # 尝试使用指定的DNS服务器
    for dns_server in dns_servers:
        result = _resolve_with_custom_dns(hostname, dns_server)
        if result:
            return result

    # 如果所有指定的DNS服务器都失败，尝试使用系统默认DNS
    result = _resolve_with_system_dns(hostname)
    if result:
        return result

    logger.error(f"所有DNS服务器都无法解析 {hostname}")
    return None


class OSSHostsSession:
    """智能OSS Session，支持IP直连并保持Host header

    功能：
    - 支持静态IP映射
    - 自动检测IP健康状态
    - IP失效时通过优质DNS重新解析
    - 用于解决DNS不可用时的OSS上传问题
    """

    def __init__(self, config=None, hosts_map: dict[str, str] = None):
        """初始化

        Args:
            config: 配置对象（推荐，包含DNS设置）
            hosts_map: 主机名到IP的映射字典（向后兼容）
        """
        # 创建一个requests session并配置自定义adapter
        self.session = requests.Session()

        # 使用智能或静态HostsAdapter
        if config:
            adapter = HostsAdapter(
                config=config,
                pool_connections=10,
                pool_maxsize=20,
            )
        elif hosts_map:
            # 向后兼容
            adapter = HostsAdapter(
                hosts_map=hosts_map,
                pool_connections=10,
                pool_maxsize=20,
            )
        else:
            # 没有配置，使用标准adapter
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=10,
                pool_maxsize=20,
            )

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # 配置SSL验证
        if config and hasattr(config, "verify_ssl"):
            self.session.verify = config.verify_ssl
            logger.debug(f"SSL验证设置: {config.verify_ssl}")

    def do_request(self, req, timeout):
        """实现OSS SDK要求的do_request接口

        Args:
            req: OSS SDK的Request对象
            timeout: 超时时间

        Returns:
            Response对象
        """
        # 准备requests库的参数
        kwargs = {
            "method": req.method,
            "url": req.url,
            "data": req.data,
            "headers": req.headers,
            "timeout": timeout,
        }

        # 使用配置了hosts映射的session发送请求
        resp = self.session.request(**kwargs)

        # 返回OSS SDK期望的Response对象
        return oss2.http.Response(resp)


class HostsAdapter(HTTPAdapter):
    """智能hosts映射的HTTP适配器

    功能：
    - 支持静态IP映射
    - 自动检测IP健康状态
    - IP失效时通过优质DNS重新解析
    - 缓存解析结果避免频繁查询
    """

    def __init__(self, config=None, hosts_map: dict[str, str] = None, *args, **kwargs):
        """初始化适配器

        Args:
            config: 配置对象（包含DNS设置）
            hosts_map: 主机名到IP的映射字典（向后兼容）
        """
        super().__init__(*args, **kwargs)
        self.config = config

        # 静态hosts映射（用户配置）
        if config and hasattr(config, "custom_hosts"):
            self.static_hosts = config.custom_hosts
            logger.info(f"启用静态hosts映射: {config.custom_hosts}")
        elif hosts_map:
            self.static_hosts = hosts_map
            logger.info(f"启用静态hosts映射: {hosts_map}")
        else:
            self.static_hosts = {}

        # 动态hosts映射（DNS回退时添加）
        self.dynamic_hosts = {}

        # 合并后的有效hosts映射
        self.hosts_map = {}
        self._update_hosts_map()

        self.hosts_manager = None

    def _update_hosts_map(self):
        """更新有效的hosts映射"""
        self.hosts_map = {}
        self.hosts_map.update(self.static_hosts)  # 静态映射
        self.hosts_map.update(self.dynamic_hosts)  # 动态映射优先级更高

    def add_dns_mapping(self, hostname: str, ip_address: str):
        """添加动态DNS映射（由DNS回退功能调用）

        Args:
            hostname: 域名
            ip_address: IP地址
        """
        self.dynamic_hosts[hostname] = ip_address
        self._update_hosts_map()
        logger.debug(f"动态DNS映射: {hostname} -> {ip_address}")

    def send(self, request, **kwargs):
        """重写send方法，实现智能IP直连同时保持Host header"""
        # 获取原始URL的主机名
        parsed = urlparse(request.url)
        original_host = parsed.hostname

        if not original_host:
            return super().send(request, **kwargs)

        # 获取IP地址（静态映射）
        custom_ip = None
        if hasattr(self, "hosts_map") and original_host in self.hosts_map:
            custom_ip = self.hosts_map[original_host]

        if custom_ip:
            # 精确替换netloc，避免子串误替换
            if parsed.port:
                original_netloc = f"{original_host}:{parsed.port}"
                new_netloc = f"{custom_ip}:{parsed.port}"
            else:
                original_netloc = original_host
                new_netloc = custom_ip

            # 只有完全匹配时才替换
            if parsed.netloc == original_netloc:
                new_parsed = parsed._replace(netloc=new_netloc)
                new_url = urlunparse(new_parsed)

                # 更新请求URL
                request.url = new_url

                # 关键：设置Host header为原始域名
                # 这样可以通过HTTPS证书验证
                request.headers["Host"] = original_host
                if parsed.port:
                    request.headers["Host"] = f"{original_host}:{parsed.port}"

                logger.debug(
                    f"IP直连: {original_host} -> {custom_ip}, Host: {request.headers['Host']}"
                )

        return super().send(request, **kwargs)
