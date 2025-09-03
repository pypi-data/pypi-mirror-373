"""简化的网络模块

移除DNS回退策略，保留基本的网络重试功能
"""

import logging
from functools import wraps
from typing import Callable

import requests
from tenacity import (
    after_log,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_exponential_jitter,
)

logger = logging.getLogger(__name__)


def get_retryable_network_errors() -> tuple:
    """返回可重试的网络错误类型"""
    return (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.ReadTimeout,
        requests.exceptions.ConnectTimeout,
        requests.exceptions.SSLError,
        OSError,  # 包括网络相关的系统错误
    )


def network_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
) -> Callable:
    """网络重试装饰器

    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟时间（秒）
        max_delay: 最大延迟时间（秒）
        backoff_factor: 退避因子
        jitter: 是否添加抖动

    Returns:
        装饰器函数
    """
    # 配置等待策略
    if jitter:
        # 使用指数退避加抖动（Google推荐的策略）
        wait_strategy = wait_exponential_jitter(
            initial=base_delay, max=max_delay, jitter=base_delay
        )
    else:
        # 仅使用指数退避
        wait_strategy = wait_exponential(
            multiplier=base_delay, max=max_delay, exp_base=backoff_factor
        )

    def decorator(func):
        @wraps(func)
        @retry(
            retry=retry_if_exception_type(get_retryable_network_errors()),
            stop=stop_after_attempt(max_retries + 1),  # +1 包含首次尝试
            wait=wait_strategy,
            before_sleep=before_sleep_log(logger, logging.DEBUG),
            after=after_log(logger, logging.DEBUG),
            reraise=True,
        )
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
