"""Lims2 SDK - 生信云平台 Python SDK

提供图表上传和文件存储功能
"""

import warnings
from pathlib import Path
from typing import Any, Optional, Union

from ._version import __version__
from .chart import ChartService
from .client import Lims2Client
from .exceptions import APIError, AuthError, ConfigError, Lims2Error, UploadError
from .storage import StorageService

__all__ = [
    # 版本信息
    "__version__",
    # 主要接口
    "Lims2Client",
    "ChartService",
    "StorageService",
    # 异常
    "Lims2Error",
    "ConfigError",
    "AuthError",
    "UploadError",
    "APIError",
    # 便捷函数
    "upload_chart_from_data",
    "upload_chart_from_file",
    "upload_result_file",
    "upload_result_dir",
]


def upload_chart_from_data(
    chart_name: str,
    project_id: str,
    chart_data: dict[str, Any],
    sample_id: Optional[str] = None,
    chart_type: Optional[str] = None,
    description: Optional[str] = None,
    contrast: Optional[str] = None,
    analysis_node: Optional[str] = None,
    precision: Optional[int] = 3,
) -> dict[str, Any]:
    """上传图表数据（向后兼容函数）

    .. deprecated:: 0.4.1
        请使用 Lims2Client 实例方法，避免重复创建连接：
        client = Lims2Client()
        client.chart.upload(...)

    Args:
        chart_name: 图表名称
        project_id: 项目 ID
        chart_data: 图表数据字典
        sample_id: 样本 ID（可选）
        chart_type: 图表类型（可选）
        description: 图表描述（可选）
        contrast: 对比策略（可选）
        analysis_node: 分析节点名称（可选）
        precision: 浮点数精度控制，保留小数位数（0-10，默认3）

    Returns:
        上传结果
    """
    warnings.warn(
        "upload_chart_from_data() 已弃用，建议使用 Lims2Client 实例方法复用连接池，"
        "避免批量上传时的连接问题。",
        DeprecationWarning,
        stacklevel=2,
    )
    client = Lims2Client()
    return client.chart.upload(
        chart_data,
        project_id,
        chart_name,
        sample_id=sample_id,
        chart_type=chart_type,
        description=description,
        contrast=contrast,
        analysis_node=analysis_node,
        precision=precision,
    )


def upload_chart_from_file(
    chart_name: str,
    project_id: str,
    file_path: Union[str, Path],
    sample_id: Optional[str] = None,
    chart_type: Optional[str] = None,
    description: Optional[str] = None,
    contrast: Optional[str] = None,
    analysis_node: Optional[str] = None,
    precision: Optional[int] = 3,
) -> dict[str, Any]:
    """上传图表文件（向后兼容函数）

    .. deprecated:: 0.4.1
        请使用 Lims2Client 实例方法，避免重复创建连接：
        client = Lims2Client()
        client.chart.upload(...)

    Args:
        chart_name: 图表名称
        project_id: 项目 ID
        file_path: 文件路径
        sample_id: 样本 ID（可选）
        chart_type: 图表类型（可选）
        description: 图表描述（可选）
        contrast: 对比策略（可选）
        analysis_node: 分析节点名称（可选）
        precision: 浮点数精度控制，保留小数位数（0-10，默认3）

    Returns:
        上传结果
    """
    warnings.warn(
        "upload_chart_from_file() 已弃用，建议使用 Lims2Client 实例方法复用连接池，"
        "避免批量上传时的连接问题。",
        DeprecationWarning,
        stacklevel=2,
    )
    client = Lims2Client()
    return client.chart.upload(
        file_path,
        project_id,
        chart_name,
        sample_id=sample_id,
        chart_type=chart_type,
        description=description,
        contrast=contrast,
        analysis_node=analysis_node,
        precision=precision,
    )


def upload_result_file(
    file_path: Union[str, Path],
    project_id: str,
    analysis_node: str,
    sample_id: Optional[str] = None,
    description: Optional[str] = None,
) -> dict[str, Any]:
    """上传结果文件（便捷函数）

    .. deprecated:: 0.4.1
        请使用 Lims2Client 实例方法，避免重复创建连接：
        client = Lims2Client()
        client.storage.upload_file(...)

    Args:
        file_path: 文件路径
        project_id: 项目 ID
        analysis_node: 分析节点名称
        sample_id: 样本 ID（可选）
        description: 文件描述（可选）

    Returns:
        上传结果
    """
    warnings.warn(
        "upload_result_file() 已弃用，建议使用 Lims2Client 实例方法复用连接池，"
        "避免批量上传时的连接问题。",
        DeprecationWarning,
        stacklevel=2,
    )
    client = Lims2Client()
    return client.storage.upload_file(
        file_path,
        project_id,
        analysis_node,
        "results",
        sample_id=sample_id,
        description=description,
    )


def upload_result_dir(
    dir_path: Union[str, Path],
    project_id: str,
    analysis_node: str,
    sample_id: Optional[str] = None,
    recursive: bool = True,
) -> list:
    """上传结果目录（便捷函数）

    .. deprecated:: 0.4.1
        请使用 Lims2Client 实例方法，避免重复创建连接：
        client = Lims2Client()
        client.storage.upload_directory(...)

    Args:
        dir_path: 目录路径
        project_id: 项目 ID
        analysis_node: 分析节点名称
        sample_id: 样本 ID（可选）
        recursive: 是否递归上传子目录（默认 True）

    Returns:
        上传结果列表
    """
    warnings.warn(
        "upload_result_dir() 已弃用，建议使用 Lims2Client 实例方法复用连接池，"
        "避免批量上传时的连接问题。",
        DeprecationWarning,
        stacklevel=2,
    )
    client = Lims2Client()
    return client.storage.upload_directory(
        dir_path,
        project_id,
        analysis_node,
        "results",
        sample_id=sample_id,
        recursive=recursive,
    )
