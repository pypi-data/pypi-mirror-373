"""工具函数"""

import math
import os
import re
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any, Union
from urllib.parse import urlparse

import orjson
import requests

from .exceptions import APIError


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """清理文件名，保留中文等 Unicode 字符

    Args:
        filename: 原始文件名
        max_length: 最大长度

    Returns:
        清理后的文件名
    """
    # 保留字母、数字、中文、日文、韩文等常见字符，以及 .-_
    filename = re.sub(
        r"[^\w\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af\.-]", "_", filename
    )

    # 移除开头和结尾的特殊字符
    filename = filename.strip("._")

    # 限制长度
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        if ext:
            name = name[: max_length - len(ext)]
            filename = name + ext
        else:
            filename = filename[:max_length]

    return filename or "unnamed"


def generate_unique_filename(base_name: str, extension: str = "") -> str:
    """生成唯一文件名，精确到毫秒

    Args:
        base_name: 基础文件名
        extension: 文件扩展名

    Returns:
        带毫秒时间戳的唯一文件名
    """
    from datetime import datetime

    # 确保扩展名格式正确
    if extension and not extension.startswith("."):
        extension = "." + extension

    # 毫秒时间戳：HHMMSS_fff（精确到毫秒）
    timestamp = datetime.now().strftime("%H%M%S_%f")[:-3]

    # 清理并截断文件名，留出时间戳空间
    clean_base = sanitize_filename(base_name)[:80]  # 最多80字符

    return f"{clean_base}_{timestamp}{extension}"


def read_file_content(file_path: Union[str, Path]) -> Union[dict[str, Any], bytes]:
    """读取文件内容

    Args:
        file_path: 文件路径

    Returns:
        JSON 文件返回字典，其他文件返回字节
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    if file_path.suffix.lower() == ".json":
        with open(file_path, encoding="utf-8") as f:
            return orjson.loads(f.read())
    else:
        with open(file_path, "rb") as f:
            return f.read()


def get_file_size(file_path: Union[str, Path]) -> int:
    """获取文件大小（字节）

    Args:
        file_path: 文件路径

    Returns:
        文件大小（字节）
    """
    return Path(file_path).stat().st_size


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小为人类可读格式

    Args:
        size_bytes: 文件大小（字节）

    Returns:
        格式化后的字符串
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def is_json_content(content: Union[str, bytes, dict]) -> bool:
    """判断内容是否为 JSON 格式

    Args:
        content: 要检查的内容

    Returns:
        是否为 JSON 格式
    """
    if isinstance(content, dict):
        return True

    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="ignore")

    if isinstance(content, str):
        try:
            orjson.loads(content)
            return True
        except (orjson.JSONDecodeError, ValueError):
            return False

    return False


def handle_api_response(
    response: requests.Response, operation: str = "API调用"
) -> dict[str, Any]:
    """统一处理 API 响应

    Args:
        response: requests 响应对象
        operation: 操作描述，用于错误信息

    Returns:
        解析后的响应数据

    Raises:
        APIError: 当 HTTP 状态码非 200 或业务错误码非 200 时
    """
    if response.status_code == 200:
        response_data = orjson.loads(response.content)

        # 检查业务错误码
        if "code" in response_data and response_data.get("code") != 200:
            error_msg = f"{operation}失败: {response_data.get('message', '未知错误')}"
            raise APIError(error_msg, response_data.get("code"))

        return response_data
    else:
        error_msg = f"{operation}失败: HTTP {response.status_code}"
        try:
            error_detail = orjson.loads(response.content)
            if "detail" in error_detail:
                error_msg += f" - {error_detail['detail']}"
            elif "error" in error_detail:
                error_msg += f" - {error_detail['error']}"
        except (orjson.JSONDecodeError, ValueError, KeyError):
            error_msg += f" - {response.text}"
        except Exception as e:
            error_msg += f" - 响应解析失败: {e}"

        raise APIError(error_msg, response.status_code)


def round_floats(o: Any, precision: int = 3) -> Any:
    """递归处理数据结构中的浮点数，使用 decimal 实现精确四舍五入

    对于 NaN 和 Infinity 等特殊值，转换为 None 以确保 JSON 兼容性。

    Args:
        o: 要处理的对象
        precision: 保留的小数位数（0-10），默认为 3

    Returns:
        处理后的对象，NaN/Infinity 转换为 None
    """
    if isinstance(o, float):
        if math.isnan(o) or math.isinf(o):
            return None

        # 使用 decimal 进行精确四舍五入
        try:
            decimal_value = Decimal(str(o))
            quantizer = Decimal("0.1") ** precision
            rounded = decimal_value.quantize(quantizer, rounding=ROUND_HALF_UP)
            return float(rounded)
        except (ValueError, ArithmeticError):
            # 如果 decimal 转换失败，回退到普通 round
            return round(o, precision)
    elif isinstance(o, dict):
        return {k: round_floats(v, precision) for k, v in o.items()}
    elif isinstance(o, (list, tuple)):
        return type(o)(round_floats(x, precision) for x in o)
    return o


def get_json_size(data: Any) -> int:
    """获取数据序列化为 JSON 后的字节大小

    Args:
        data: 要序列化的数据

    Returns:
        JSON 字节大小
    """
    json_str = orjson.dumps(data).decode("utf-8")
    return len(json_str.encode("utf-8"))


def get_hostname_from_url(url: str) -> str:
    """从URL中提取主机名

    Args:
        url: URL地址

    Returns:
        主机名字符串
    """
    parsed = urlparse(url)
    return parsed.hostname or ""


def get_temp_dir(custom_dir: str = None, purpose: str = "oss-upload") -> str:
    """获取可用的临时目录

    Args:
        custom_dir: 自定义临时目录，优先使用
        purpose: 目录用途，用于创建子目录

    Returns:
        可用的临时目录路径
    """
    import tempfile

    # 候选目录列表，按优先级排序
    candidates = []
    if custom_dir and isinstance(custom_dir, str):
        candidates.append(os.path.expanduser(custom_dir))

    candidates.extend(
        [
            os.path.join(tempfile.gettempdir(), f"lims2-{purpose}"),
            os.path.expanduser(f"~/.cache/lims2-sdk/{purpose}"),
            f".lims2-{purpose}",
        ]
    )

    # 测试每个目录
    for temp_dir in candidates:
        try:
            Path(temp_dir).mkdir(parents=True, exist_ok=True)
            test_file = Path(temp_dir) / ".test"
            test_file.write_text("test")
            test_file.unlink()
            return temp_dir
        except (PermissionError, OSError):
            continue

    # 兜底方案
    fallback = os.path.join(tempfile.gettempdir(), f"lims2-{os.getpid()}")
    Path(fallback).mkdir(parents=True, exist_ok=True)
    return fallback
