"""图表服务模块

基于原 biotree_chart 功能实现
"""

import gzip
from pathlib import Path
from typing import Any, Optional, Union

import orjson

from .network import network_retry
from .oss_base import OSSMixin
from .utils import (
    format_file_size,
    generate_unique_filename,
    get_file_size,
    get_json_size,
    handle_api_response,
    read_file_content,
    round_floats,
)

# 内联存储阈值 1Byte , 都存到OSS
INLINE_STORAGE_THRESHOLD = 1


class ChartService(OSSMixin):
    """图表服务"""

    def __init__(self, client):
        """初始化图表服务

        Args:
            client: Lims2Client 实例
        """
        self.client = client
        self.config = client.config
        self.session = client.session

        # 初始化OSS混入功能
        self.__init_oss__()

    def upload(
        self,
        data_source: Union[dict[str, Any], str, Path],
        project_id: str,
        chart_name: str,
        sample_id: Optional[str] = None,
        chart_type: Optional[str] = None,
        description: Optional[str] = None,
        contrast: Optional[str] = None,
        analysis_node: Optional[str] = None,
        precision: Optional[int] = None,
    ) -> dict[str, Any]:
        """上传图表

        Args:
            data_source: 图表数据源，可以是字典、文件路径或 Path 对象
            project_id: 项目 ID
            chart_name: 图表名称
            sample_id: 样本 ID（可选）
            chart_type: 图表类型（可选）
            description: 图表描述（可选）
            contrast: 对比策略（可选）
            analysis_node: 分析节点名称（可选）
            precision: 浮点数精度控制，保留小数位数（0-10，默认3）

        Returns:
            上传结果
        """
        # 参数验证
        if not chart_name:
            raise ValueError("图表名称不能为空")
        if not project_id:
            raise ValueError("项目 ID 不能为空")
        if not data_source:
            raise ValueError("数据源不能为空")
        if precision is not None and not 0 <= precision <= 10:
            raise ValueError("precision 必须在 0-10 之间")

        # 构建请求数据
        request_data = {
            "chart_name": chart_name,
            "project_id": project_id,
            "chart_type": chart_type,
            "description": description,
        }

        # 添加可选参数
        if sample_id:
            request_data["sample_id"] = sample_id
        if contrast:
            request_data["contrast"] = contrast
        if analysis_node:
            request_data["analysis_node"] = analysis_node

        # 根据数据源类型处理
        if isinstance(data_source, dict):
            return self._upload_from_dict(request_data, data_source, precision)
        elif isinstance(data_source, (str, Path)):
            return self._upload_from_file(request_data, data_source, precision)
        else:
            raise ValueError("数据源必须是字典、文件路径或 Path 对象")

    def _upload_from_dict(
        self,
        request_data: dict[str, Any],
        chart_data: dict[str, Any],
        precision: Optional[int] = None,
    ) -> dict[str, Any]:
        """从字典数据上传图表"""
        # 检测渲染器类型
        if "data" in chart_data and "layout" in chart_data:
            request_data["renderer_type"] = "plotly"
        elif "elements" in chart_data or (
            "nodes" in chart_data and "edges" in chart_data
        ):
            request_data["renderer_type"] = "cytoscape"
        else:
            raise ValueError("不支持的图表数据格式")

        # 应用精度控制（默认使用 3 位小数）
        if precision is None:
            precision = 3  # 默认精度为 3

        # 检测到 Plotly 图表时进行清理
        if request_data["renderer_type"] == "plotly":
            if "layout" in chart_data and "template" in chart_data["layout"]:
                del chart_data["layout"]["template"]

        # 记录原始大小
        original_size = get_json_size(chart_data)

        # 应用精度控制
        chart_data = round_floats(chart_data, precision)

        # 序列化数据
        json_str = orjson.dumps(chart_data).decode("utf-8")
        file_size = len(json_str.encode("utf-8"))

        # 显示大小减少信息
        if file_size < original_size:
            reduction_percent = (1 - file_size / original_size) * 100
            print(
                f"精度控制: {format_file_size(original_size)} -> "
                f"{format_file_size(file_size)} "
                f"(减少 {reduction_percent:.1f}%)"
            )

        if file_size > INLINE_STORAGE_THRESHOLD:
            # 大数据压缩后上传到 OSS
            compressed_data = gzip.compress(json_str.encode("utf-8"))

            # 生成文件名（使用.json后缀，虽然内容是gzip压缩的）
            filename = generate_unique_filename(request_data["chart_name"], "json")

            # 构建OSS键名并上传到OSS
            oss_key = self._build_chart_oss_key(
                request_data["project_id"], request_data.get("sample_id"), filename
            )
            bucket = self._get_oss_bucket(request_data["project_id"])
            bucket.put_object(
                oss_key,
                compressed_data,
                headers={
                    "Content-Type": "application/json",
                    "Content-Encoding": "gzip",
                },
            )

            request_data["file_format"] = "json"  # 记录格式为json，实际内容是gzip压缩的
            request_data["file_name"] = filename
            request_data["oss_key"] = oss_key
        else:
            # 小数据内联存储
            request_data["file_format"] = "json"
            request_data["chart_data"] = chart_data
            request_data["file_name"] = generate_unique_filename(
                request_data["chart_name"], "json"
            )

        # 创建图表记录
        return self._create_chart_record(request_data)

    def _upload_from_file(  # noqa: C901
        self,
        request_data: dict[str, Any],
        file_path: Union[str, Path],
        precision: Optional[int] = None,
    ) -> dict[str, Any]:
        """从文件上传图表"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        file_format = file_path.suffix.lower().strip(".")
        request_data["file_size"] = get_file_size(file_path)
        request_data["file_format"] = file_format

        # JSON 文件特殊处理
        if file_format == "json":
            try:
                chart_data = read_file_content(file_path)
                if isinstance(chart_data, dict):
                    return self._upload_from_dict(request_data, chart_data, precision)
            except FileNotFoundError:
                raise
            except orjson.JSONDecodeError as e:
                raise ValueError(f"JSON 文件格式错误: {e}")
            except Exception as e:
                raise ValueError(f"读取 JSON 文件失败: {e}")

        # 其他文件类型
        if file_format in ["png", "jpg", "jpeg", "svg", "pdf"]:
            request_data["renderer_type"] = "image"
        elif file_format == "html":
            request_data["renderer_type"] = "html"
        else:
            raise ValueError(f"不支持的文件格式: {file_format}")

        # 生成文件名
        filename = generate_unique_filename(request_data["chart_name"], file_format)
        request_data["file_name"] = filename

        # 构建OSS键名
        oss_key = self._build_chart_oss_key(
            request_data["project_id"], request_data.get("sample_id"), filename
        )

        # 读取文件内容
        file_content = read_file_content(file_path)
        if isinstance(file_content, dict):
            file_content = orjson.dumps(file_content)

        # 上传到 OSS
        content_type = self._get_content_type(file_format)
        bucket = self._get_oss_bucket(request_data["project_id"])
        bucket.put_object(oss_key, file_content, headers={"Content-Type": content_type})

        request_data["oss_key"] = oss_key

        # 创建图表记录
        return self._create_chart_record(request_data)

    def _build_chart_oss_key(
        self, project_id: str, sample_id: Optional[str], filename: str
    ) -> str:
        """构建图表的OSS键名

        Args:
            project_id: 项目ID
            sample_id: 样本ID（可选）
            filename: 文件名

        Returns:
            str: OSS键名，格式为biochart/{env}/project_id/[sample_id/]filename
            - 环境前缀：生产环境使用media，测试环境使用test
        """
        # 使用环境相关的路径前缀
        env_prefix = self._get_oss_path_prefix()
        parts = ["biochart", env_prefix, project_id]
        if sample_id:
            parts.append(sample_id)
        parts.append(filename)
        return "/".join(parts)

    @network_retry(max_retries=3, base_delay=1.0, max_delay=15.0)
    def _create_chart_record(self, request_data: dict[str, Any]) -> dict[str, Any]:
        """创建图表记录"""

        request_data["token"] = self.config.token
        request_data["team_id"] = self.config.team_id

        # 使用配置的超时时间和分离的连接/读取超时
        timeout = (self.config.connection_timeout, self.config.read_timeout)

        response = self.session.post(
            f"{self.config.api_url}/get_data/biochart/create_chart/",
            json=request_data,
            timeout=timeout,
        )
        return handle_api_response(response, "创建图表记录")

    def _get_content_type(self, file_format: str) -> str:
        """获取文件内容类型"""
        content_types = {
            "json": "application/json",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "svg": "image/svg+xml",
            "pdf": "application/pdf",
            "html": "text/html",
        }
        return content_types.get(file_format, "application/octet-stream")
