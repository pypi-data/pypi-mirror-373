"""存储服务模块

通过 STS 临时凭证上传文件到阿里云 OSS，支持大文件断点续传
"""

import logging
from pathlib import Path
from typing import Any, Callable, Optional, Union

import oss2

from .exceptions import APIError
from .network import network_retry
from .oss_base import OSSMixin
from .utils import (
    format_file_size,
    generate_unique_filename,
    get_file_size,
    get_temp_dir,
    handle_api_response,
)

logger = logging.getLogger(__name__)


class StorageService(OSSMixin):
    """存储服务

    通过阿里云 OSS 提供文件存储功能，支持：
    - 大文件断点续传（>10MB）
    - STS 临时凭证安全上传
    - 文件元数据记录
    - 目录批量上传
    """

    def __init__(self, client):
        """初始化存储服务

        Args:
            client: Lims2Client 实例，提供配置和会话

        Raises:
            ValueError: 当必需的配置项缺失时
        """
        self.client = client
        self.config = client.config
        self.session = client.session

        # 初始化OSS混入功能
        self.__init_oss__()

        # 校验必需的配置项
        required = ["api_url", "team_id", "token"]
        missing = [attr for attr in required if not getattr(self.config, attr, None)]
        if missing:
            raise ValueError(f"配置项缺失: {', '.join(missing)}")

    def upload_file(
        self,
        file_path: Union[str, Path],
        project_id: str,
        analysis_node: Optional[str] = None,
        file_category: Optional[str] = None,
        key: Optional[str] = None,
        sample_id: Optional[str] = None,
        description: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
        base_path: Optional[str] = None,
    ) -> dict[str, Any]:
        """上传单个文件到 OSS

        Args:
            file_path: 本地文件路径
            project_id: 项目 ID
            analysis_node: 分析节点名称
            file_category: 文件分类（如 'results', 'plot_data'）
            key: 自定义 OSS 键名，不提供则自动生成
            sample_id: 样本 ID（可选）
            description: 文件描述（可选）
            progress_callback: 进度回调函数，签名为 callback(consumed_bytes, total_bytes)
            base_path: OSS 中的基础路径（可选）

        Returns:
            dict[str, Any]: 上传结果，包含文件信息和 OSS 键名

        Raises:
            FileNotFoundError: 文件不存在
            APIError: STS 凭证获取失败或 OSS 上传失败

        Example:
            >>> result = storage.upload_file(
            ...     "data.csv", "proj_001", "analysis1", "results",
            ...     progress_callback=lambda consumed, total: print(f"{consumed/total*100:.1f}%")
            ... )
            >>> print(result['oss_key'])
            biofile/test/proj_001/analysis1/data_123456.csv
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 构建 OSS 键名：biofile/{env}/project_id/[base_path/]filename
        if not key:
            # 如果没有指定 base_path，对单文件上传使用 analysis_node/sample_id 作为默认路径
            if base_path is None:
                path_parts = []
                if analysis_node:
                    path_parts.append(analysis_node)
                if sample_id:
                    path_parts.append(sample_id)
                base_path = "/".join(path_parts) if path_parts else None

            key = self._build_oss_key(project_id, file_path.name, base_path)

        # 获取 OSS bucket 并上传文件
        bucket = self._get_oss_bucket(project_id)
        self._upload_to_oss(bucket, file_path, key, progress_callback)

        # 在后端数据库记录文件信息
        return self._create_file_record(
            file_path,
            key,
            project_id,
            analysis_node or "files",
            file_category or "result",
            sample_id,
            description,
        )

    def upload_directory(
        self,
        dir_path: Union[str, Path],
        project_id: str,
        analysis_node: Optional[str] = None,
        file_category: Optional[str] = None,
        sample_id: Optional[str] = None,
        recursive: bool = True,
        base_path: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> list[dict[str, Any]]:
        """批量上传目录中的所有文件

        Args:
            dir_path: 目录路径
            project_id: 项目 ID
            analysis_node: 分析节点名称
            file_category: 文件分类
            sample_id: 样本 ID（可选）
            recursive: 是否递归上传子目录（默认 True）
            base_path: OSS 中的基础路径（可选）
            progress_callback: 进度回调函数，接收(current, total, filename)参数

        Returns:
            list[dict[str, Any]]: 每个文件的上传结果列表

        Raises:
            FileNotFoundError: 目录不存在
            ValueError: 路径不是目录

        Note:
            - 保持原目录结构上传到 OSS
            - 单个文件失败不影响其他文件
            - 返回结果包含成功和失败的文件信息

        Example:
            >>> results = storage.upload_directory(
            ...     "output/", "proj_001", "analysis1", "results"
            ... )
            >>> for result in results:
            ...     if 'error' in result:
            ...         print(f"失败: {result['file_path']} - {result['error']}")
            ...     else:
            ...         print(f"成功: {result['file_name']}")
        """
        dir_path = Path(dir_path)
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {dir_path}")
        if not dir_path.is_dir():
            raise ValueError(f"路径不是目录: {dir_path}")

        # 收集所有文件（递归或非递归）
        pattern = "**/*" if recursive else "*"
        files = [f for f in dir_path.glob(pattern) if f.is_file()]

        results = []
        total_files = len(files)
        for i, file_path in enumerate(files, 1):
            try:
                # 进度回调
                if progress_callback:
                    progress_callback(i, total_files, file_path.name)

                # 保持相对路径结构，包含原始目录名
                relative_path = file_path.relative_to(dir_path)
                # 添加原始目录名作为前缀
                dir_name = dir_path.name
                path_with_dir = f"{dir_name}/{relative_path}"
                key = self._build_oss_key(
                    project_id,
                    path_with_dir,
                    base_path,
                )

                # 上传单个文件（key已经包含完整路径，不需要再传base_path）
                result = self.upload_file(
                    file_path, project_id, analysis_node, file_category, key, sample_id
                )
                results.append(result)
            except Exception as e:
                # 记录失败的文件，继续处理其他文件
                results.append(
                    {"file_path": str(file_path), "error": str(e), "success": False}
                )

        return results

    def download_file(
        self,
        oss_key: str,
        local_path: Union[str, Path],
        project_id: str,
        progress_callback: Optional[Callable] = None,
    ) -> dict[str, Any]:
        """从 OSS 下载文件到本地

        Args:
            oss_key: OSS 文件键名
            local_path: 本地保存路径
            project_id: 项目 ID
            progress_callback: 进度回调函数，签名为 callback(consumed_bytes, total_bytes)

        Returns:
            dict[str, Any]: 下载结果信息

        Raises:
            FileNotFoundError: OSS 文件不存在
            APIError: OSS 访问失败
        """
        local_path = Path(local_path)

        # 确保本地目录存在
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # 获取 OSS bucket
        bucket = self._get_oss_bucket(project_id)

        try:
            # 检查文件是否存在并获取文件信息
            try:
                obj_info = bucket.get_object_meta(oss_key)
                file_size = obj_info.content_length
            except oss2.exceptions.NoSuchKey:
                raise FileNotFoundError(f"OSS 文件不存在: {oss_key}")

            # 直接下载文件
            bucket.get_object_to_file(
                oss_key, str(local_path), progress_callback=progress_callback
            )

            # 验证下载完成
            if not local_path.exists():
                raise APIError(f"下载失败: 文件未创建 {local_path}")

            downloaded_size = get_file_size(local_path)
            if downloaded_size != file_size:
                raise APIError(
                    f"下载不完整: 期望 {file_size} 字节，实际 {downloaded_size} 字节"
                )

            return {
                "oss_key": oss_key,
                "local_path": str(local_path),
                "file_name": local_path.name,
                "file_size": file_size,
                "file_size_readable": format_file_size(file_size),
                "success": True,
            }

        except oss2.exceptions.AccessDenied:
            raise APIError(f"OSS 访问权限不足: {oss_key}")
        except oss2.exceptions.RequestError as e:
            raise APIError(f"OSS 请求失败: {e}")

    def file_exists(self, oss_key: str, project_id: str) -> bool:
        """检查文件是否存在"""
        try:
            bucket = self._get_oss_bucket(project_id)
            return bucket.object_exists(oss_key)
        except Exception:
            return False

    def get_file_info(self, oss_key: str, project_id: str) -> dict[str, Any]:
        """获取文件详细信息"""
        bucket = self._get_oss_bucket(project_id)

        try:
            obj_info = bucket.get_object_meta(oss_key)
            if obj_info is None:
                raise APIError(f"无法获取文件元数据: {oss_key}")

            content_type = getattr(obj_info, "content_type", None)
            etag = getattr(obj_info, "etag", None)
            content_length = getattr(obj_info, "content_length", 0)

            return self._parse_file_info(
                oss_key,
                content_length,
                obj_info.last_modified,
                project_id,
                content_type,
                etag,
            )
        except oss2.exceptions.NoSuchKey:
            raise FileNotFoundError(f"文件不存在: {oss_key}")

    def _build_oss_key(
        self,
        project_id: str,
        filename: str,
        base_path: Optional[str] = None,
    ) -> str:
        """构建 OSS 文件键名

        生成规则：
        - 基础路径：biofile/{env}/project_id/[base_path/]
        - 环境前缀：生产环境使用media，测试环境使用test
        - 文件名：添加随机后缀避免冲突
        - 始终保持目录结构

        Args:
            project_id: 项目 ID
            filename: 文件名或相对路径
            base_path: OSS 中的基础路径（可选）

        Returns:
            str: OSS 键名

        Example:
            >>> self._build_oss_key("proj_001", "data.csv", base_path="results")
            "biofile/media/proj_001/results/data_123456.csv"  # 生产环境

            >>> self._build_oss_key("proj_001", "subdir/file.txt", "results")
            "biofile/test/proj_001/results/subdir/file_123456.txt"  # 测试环境
        """
        # 使用环境相关的路径前缀
        env_prefix = self._get_oss_path_prefix()
        parts = ["biofile", env_prefix, project_id]
        if base_path:
            parts.append(base_path)

        path_obj = Path(filename)
        if len(path_obj.parts) > 1:
            # 保持目录结构：包含子目录路径
            sub_dirs = "/".join(path_obj.parts[:-1])
            unique_filename = generate_unique_filename(path_obj.stem, path_obj.suffix)
            return "/".join(parts) + "/" + sub_dirs + "/" + unique_filename
        else:
            # 单文件：直接放在基础路径下
            unique_filename = generate_unique_filename(path_obj.stem, path_obj.suffix)
            return "/".join(parts) + "/" + unique_filename

    def _get_resumable_store_dir(self) -> str:
        """获取可用的断点续传临时目录"""
        custom_dir = getattr(self.config, "custom_temp_dir", None)
        return get_temp_dir(custom_dir, purpose="oss-upload")

    @network_retry(max_retries=3, base_delay=2.0, max_delay=30.0)
    def _upload_to_oss(
        self,
        bucket: oss2.Bucket,
        file_path: Path,
        key: str,
        progress_callback: Optional[Callable] = None,
    ):
        """使用断点续传方式上传文件到 OSS

        Args:
            bucket: OSS Bucket 对象
            file_path: 本地文件路径
            key: OSS 文件键名
            progress_callback: 进度回调函数（可选）

        Note:
            - 超过 10MB 的文件自动使用分片上传
            - 每个分片 5MB，使用 3 个线程并发上传
            - 支持断点续传，中断后可恢复
            - 临时文件存储在可写的临时目录中
            - 上传完成后自动清理临时文件
        """
        # 获取可用的临时目录
        temp_root = self._get_resumable_store_dir()

        # 创建断点续传存储对象
        temp_store = oss2.ResumableStore(root=temp_root)

        try:
            # 计算文件大小用于调整参数
            file_size_mb = get_file_size(file_path) / (1024 * 1024)

            # 根据网络质量调整并发数
            num_threads = min(
                3, max(1, int(file_size_mb / 50))
            )  # 大文件减少并发避免超时

            oss2.resumable_upload(
                bucket,
                key,
                str(file_path),
                store=temp_store,
                multipart_threshold=10 * 1024 * 1024,  # 10MB 阈值
                part_size=8 * 1024 * 1024,  # 增大分片减少请求次数
                num_threads=num_threads,  # 动态并发数
                progress_callback=progress_callback,
            )
        finally:
            # 清理断点续传的临时文件
            # 注意：新版本的 oss2.ResumableStore 可能没有 remove 方法
            # 临时文件会在上传成功后自动清理
            try:
                if hasattr(temp_store, "remove"):
                    temp_store.remove(key)
                elif hasattr(temp_store, "delete"):
                    temp_store.delete(key)
                # 如果都没有，让 oss2 自己管理临时文件
            except Exception:
                pass  # 忽略清理错误

    def _create_file_record(
        self,
        file_path: Path,
        key: str,
        project_id: str,
        analysis_node: str,
        file_category: str,
        sample_id: Optional[str],
        description: Optional[str],
    ) -> dict[str, Any]:
        """在后端数据库创建文件上传记录

        Args:
            file_path: 本地文件路径
            key: OSS 文件键名
            project_id: 项目 ID
            analysis_node: 分析节点名称
            file_category: 文件分类
            sample_id: 样本 ID（可选）
            description: 文件描述（可选）

        Returns:
            dict[str, Any]: 包含文件信息的结果，OSS 上传成功但记录失败时包含 error 字段

        Note:
            - 即使数据库记录失败，OSS 上传已完成，文件仍可访问
            - 返回结果总是包含基本文件信息
            - API 失败时在 error 字段中包含错误信息
        """
        file_size = get_file_size(file_path)

        # 构建基本返回信息
        result = {
            "project_id": project_id,
            "file_name": file_path.name,
            "oss_key": key,
            "file_size": file_size,
            "file_size_readable": format_file_size(file_size),
            "file_category": file_category,
            "analysis_node": analysis_node,
        }

        # 记录到数据库
        record_data = {
            "project_id": project_id,
            "sample_id": sample_id,
            "oss_key": key,
            "file_name": file_path.name,
            "analysis_node": analysis_node,
            "file_category": file_category,
            "description": description or "",
            "file_size": file_size,
            "team_id": self.config.team_id,
            "token": self.config.token,
        }

        response = self.session.post(
            f"{self.config.api_url}/get_data/biofile/record_file_upload/",
            json=record_data,
            timeout=self.config.timeout,
        )

        response_data = handle_api_response(response, "文件记录创建")

        # 兼容不同的响应格式
        if "data" in response_data:
            file_record = response_data["data"]
        elif "record" in response_data:
            file_record = response_data["record"]
        else:
            file_record = response_data

        # 提取文件信息并添加到结果
        if file_record.get("file_id"):
            result["file_id"] = file_record["file_id"]
        if file_record.get("file_url"):
            result["file_url"] = file_record["file_url"]

        result["record_created"] = True

        return result

    def _parse_file_info(
        self,
        oss_key: str,
        size: int,
        last_modified,
        project_id: str,
        content_type: str = None,
        etag: str = None,
    ) -> dict[str, Any]:
        """解析 OSS 文件元数据为标准格式

        Args:
            oss_key: OSS 文件键名
            size: 文件大小（字节）
            last_modified: 最后修改时间
            project_id: 项目 ID
            content_type: 内容类型（可选）
            etag: 文件 ETag（可选）

        Returns:
            dict[str, Any]: 标准化的文件信息

        Note:
            - 自动解析键名中的 analysis_node 和 sample_id
            - 处理不同格式的时间戳
            - 键名格式：biofile/{env}/project_id/analysis_node/[sample_id]/filename
        """
        key_parts = oss_key.split("/")

        # 处理last_modified的不同格式
        if last_modified:
            if hasattr(last_modified, "isoformat"):
                last_modified_str = last_modified.isoformat()
            else:
                last_modified_str = str(last_modified)
        else:
            last_modified_str = None

        file_info = {
            "oss_key": oss_key,
            "file_name": Path(oss_key).name,
            "file_size": size,
            "file_size_readable": format_file_size(size),
            "last_modified": last_modified_str,
            "project_id": project_id,
        }

        # 添加可选字段
        if content_type:
            file_info["content_type"] = content_type
        if etag:
            file_info["etag"] = etag

        # 解析路径结构: biofile/{env}/project_id/analysis_node/[sample_id]/filename
        if len(key_parts) >= 5:
            file_info["analysis_node"] = key_parts[3]
            if len(key_parts) >= 6:
                file_info["sample_id"] = key_parts[4]

        return file_info
