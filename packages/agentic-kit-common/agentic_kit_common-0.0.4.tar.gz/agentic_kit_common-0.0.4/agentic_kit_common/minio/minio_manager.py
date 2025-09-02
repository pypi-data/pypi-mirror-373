import os
from typing import Optional, BinaryIO, Union, List, Dict
from datetime import timedelta
from minio import Minio
from minio.error import S3Error
from io import BytesIO
import logging
from urllib3.exceptions import HTTPError

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MinioManager:
    """
    MinIO 客户端封装类

    提供对 MinIO 的常用操作封装，包括:
    - 文件上传/下载
    - 文件管理(列表/删除/检查存在)
    - 生成预签名URL
    - 桶管理
    """

    def __init__(
            self,
            endpoint: str,
            access_key: str,
            secret_key: str,
            secure: bool = False,
            region: Optional[str] = None,
            http_client=None
    ):
        """
        初始化 MinIO 客户端

        :param endpoint: MinIO 服务器地址 (e.g. 'play.min.io:9000')
        :param access_key: 访问密钥
        :param secret_key: 秘密密钥
        :param secure: 是否使用 HTTPS (默认 False)
        :param region: 区域名称 (可选)
        :param http_client: 自定义 HTTP 客户端 (可选)
        """
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.region = region
        self.http_client = http_client

        # 初始化 MinIO 客户端
        self._client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
            region=region,
            http_client=http_client
        )

    def upload_file(
            self,
            bucket_name: str,
            object_name: str,
            file_path: str,
            content_type: str = "application/octet-stream",
            metadata: Optional[Dict] = None,
            part_size: int = 10 * 1024 * 1024  # 10MB
    ) -> bool:
        """
        上传文件到 MinIO

        :param bucket_name: 桶名称
        :param object_name: 对象名称 (包含路径)
        :param file_path: 本地文件路径
        :param content_type: 文件内容类型
        :param metadata: 元数据字典 (可选)
        :param part_size: 分片大小 (字节)
        :return: 是否成功
        """
        try:
            if not os.path.isfile(file_path):
                logger.error(f"File not found: {file_path}")
                return False

            # 确保桶存在
            self._ensure_bucket_exists(bucket_name)

            # 获取文件大小
            file_size = os.path.getsize(file_path)

            # 上传文件
            self._client.fput_object(
                bucket_name=bucket_name,
                object_name=object_name,
                file_path=file_path,
                content_type=content_type,
                metadata=metadata,
                part_size=part_size
            )

            logger.info(
                f"Successfully uploaded {file_path} as {object_name} to bucket {bucket_name}. "
                f"File size: {file_size} bytes"
            )
            return True
        except (S3Error, HTTPError) as e:
            logger.error(f"Error uploading file {file_path} to MinIO: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {str(e)}")
            return False

    def upload_data(
            self,
            bucket_name: str,
            object_name: str,
            data: Union[bytes, BinaryIO],
            length: int,
            content_type: str = "application/octet-stream",
            metadata: Optional[Dict] = None,
            part_size: int = 10 * 1024 * 1024  # 10MB
    ) -> bool:
        """
        上传二进制数据到 MinIO

        :param bucket_name: 桶名称
        :param object_name: 对象名称 (包含路径)
        :param data: 二进制数据或文件流
        :param length: 数据长度
        :param content_type: 内容类型
        :param metadata: 元数据字典 (可选)
        :param part_size: 分片大小 (字节)
        :return: 是否成功
        """
        try:
            # 确保桶存在
            self._ensure_bucket_exists(bucket_name)

            if isinstance(data, bytes):
                data = BytesIO(data)

            self._client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=data,
                length=length,
                content_type=content_type,
                metadata=metadata,
                part_size=part_size
            )

            logger.info(
                f"Successfully uploaded data as {object_name} to bucket {bucket_name}. "
                f"Data length: {length} bytes"
            )
            return True
        except (S3Error, HTTPError) as e:
            logger.error(f"Error uploading data to MinIO: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error uploading data: {str(e)}")
            return False

    def download_file(
            self,
            bucket_name: str,
            object_name: str,
            file_path: str
    ) -> bool:
        """
        从 MinIO 下载文件到本地

        :param bucket_name: 桶名称
        :param object_name: 对象名称 (包含路径)
        :param file_path: 本地保存路径
        :return: 是否成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            self._client.fget_object(
                bucket_name=bucket_name,
                object_name=object_name,
                file_path=file_path
            )

            logger.info(
                f"Successfully downloaded {object_name} from bucket {bucket_name} to {file_path}"
            )
            return True
        except (S3Error, HTTPError) as e:
            logger.error(f"Error downloading file {object_name} from MinIO: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading file: {str(e)}")
            return False

    def download_data(
            self,
            bucket_name: str,
            object_name: str
    ) -> Optional[bytes]:
        """
        从 MinIO 下载对象为二进制数据

        :param bucket_name: 桶名称
        :param object_name: 对象名称 (包含路径)
        :return: 二进制数据或 None (如果失败)
        """
        try:
            response = self._client.get_object(
                bucket_name=bucket_name,
                object_name=object_name
            )

            data = response.read()
            response.close()
            response.release_conn()

            logger.info(
                f"Successfully downloaded {object_name} from bucket {bucket_name}. "
                f"Data length: {len(data)} bytes"
            )
            return data
        except (S3Error, HTTPError) as e:
            logger.error(f"Error downloading data {object_name} from MinIO: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading data: {str(e)}")
            return None

    def list_objects(
            self,
            bucket_name: str,
            prefix: str = "",
            recursive: bool = False
    ) -> List[Dict]:
        """
        列出桶中的对象

        :param bucket_name: 桶名称
        :param prefix: 对象前缀 (可选)
        :param recursive: 是否递归列出 (默认 False)
        :return: 对象信息列表
        """
        try:
            objects = self._client.list_objects(
                bucket_name=bucket_name,
                prefix=prefix,
                recursive=recursive
            )

            result = []
            for obj in objects:
                result.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "etag": obj.etag,
                    "is_dir": obj.is_dir
                })

            logger.info(
                f"Listed {len(result)} objects from bucket {bucket_name} with prefix '{prefix}'"
            )
            return result
        except (S3Error, HTTPError) as e:
            logger.error(f"Error listing objects in bucket {bucket_name}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing objects: {str(e)}")
            return []

    def delete_object(
            self,
            bucket_name: str,
            object_name: str
    ) -> bool:
        """
        删除 MinIO 中的对象

        :param bucket_name: 桶名称
        :param object_name: 对象名称 (包含路径)
        :return: 是否成功
        """
        try:
            self._client.remove_object(
                bucket_name=bucket_name,
                object_name=object_name
            )

            logger.info(f"Successfully deleted {object_name} from bucket {bucket_name}")
            return True
        except (S3Error, HTTPError) as e:
            logger.error(f"Error deleting object {object_name} from MinIO: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting object: {str(e)}")
            return False

    def delete_objects(
            self,
            bucket_name: str,
            object_names: List[str]
    ) -> bool:
        """
        批量删除 MinIO 中的对象

        :param bucket_name: 桶名称
        :param object_names: 对象名称列表
        :return: 是否成功
        """
        try:
            errors = self._client.remove_objects(
                bucket_name=bucket_name,
                object_names=object_names
            )

            # 检查是否有删除错误
            has_errors = False
            for error in errors:
                logger.error(f"Error deleting object {error.object_name}: {error.message}")
                has_errors = True

            if has_errors:
                return False

            logger.info(f"Successfully deleted {len(object_names)} objects from bucket {bucket_name}")
            return True
        except (S3Error, HTTPError) as e:
            logger.error(f"Error deleting objects from MinIO: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting objects: {str(e)}")
            return False

    def object_exists(
            self,
            bucket_name: str,
            object_name: str
    ) -> bool:
        """
        检查对象是否存在

        :param bucket_name: 桶名称
        :param object_name: 对象名称 (包含路径)
        :return: 是否存在
        """
        try:
            self._client.stat_object(
                bucket_name=bucket_name,
                object_name=object_name
            )
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            logger.error(f"Error checking object existence: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking object existence: {str(e)}")
            return False

    def get_presigned_url(
            self,
            bucket_name: str,
            object_name: str,
            expires: timedelta = timedelta(days=7),
            method: str = "GET"
    ) -> Optional[str]:
        """
        生成预签名 URL

        :param bucket_name: 桶名称
        :param object_name: 对象名称 (包含路径)
        :param expires: URL 过期时间 (默认 7 天)
        :param method: HTTP 方法 ("GET" 或 "PUT")
        :return: 预签名 URL 或 None (如果失败)
        """
        try:
            url = self._client.get_presigned_url(
                method=method,
                bucket_name=bucket_name,
                object_name=object_name,
                expires=expires
            )

            logger.info(f"Generated presigned URL for {object_name} in bucket {bucket_name}")
            return url
        except (S3Error, HTTPError) as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL: {str(e)}")
            return None

    def create_bucket(
            self,
            bucket_name: str,
            location: Optional[str] = None,
            object_lock: bool = False
    ) -> bool:
        """
        创建桶

        :param bucket_name: 桶名称
        :param location: 区域位置 (可选)
        :param object_lock: 是否启用对象锁定
        :return: 是否成功
        """
        try:
            self._client.make_bucket(
                bucket_name=bucket_name,
                location=location,
                object_lock=object_lock
            )

            logger.info(f"Successfully created bucket {bucket_name}")
            return True
        except (S3Error, HTTPError) as e:
            logger.error(f"Error creating bucket {bucket_name}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating bucket: {str(e)}")
            return False

    def delete_bucket(
            self,
            bucket_name: str,
            force: bool = False
    ) -> bool:
        """
        删除桶

        :param bucket_name: 桶名称
        :param force: 是否强制删除非空桶 (默认 False)
        :return: 是否成功
        """
        try:
            if force:
                # 先删除桶中的所有对象
                objects = self.list_objects(bucket_name, recursive=True)
                object_names = [obj["name"] for obj in objects]
                if object_names:
                    self.delete_objects(bucket_name, object_names)

            self._client.remove_bucket(bucket_name)

            logger.info(f"Successfully deleted bucket {bucket_name}")
            return True
        except (S3Error, HTTPError) as e:
            logger.error(f"Error deleting bucket {bucket_name}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting bucket: {str(e)}")
            return False

    def bucket_exists(
            self,
            bucket_name: str
    ) -> bool:
        """
        检查桶是否存在

        :param bucket_name: 桶名称
        :return: 是否存在
        """
        try:
            return self._client.bucket_exists(bucket_name)
        except (S3Error, HTTPError) as e:
            logger.error(f"Error checking bucket existence: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking bucket existence: {str(e)}")
            return False

    def _ensure_bucket_exists(
            self,
            bucket_name: str,
            location: Optional[str] = None
    ) -> bool:
        """
        确保桶存在，如果不存在则创建

        :param bucket_name: 桶名称
        :param location: 区域位置 (可选)
        :return: 是否成功
        """
        if self.bucket_exists(bucket_name):
            return True

        return self.create_bucket(bucket_name, location)

    def get_object_metadata(
            self,
            bucket_name: str,
            object_name: str
    ) -> Optional[Dict]:
        """
        获取对象元数据

        :param bucket_name: 桶名称
        :param object_name: 对象名称 (包含路径)
        :return: 元数据字典或 None (如果失败)
        """
        try:
            stat = self._client.stat_object(
                bucket_name=bucket_name,
                object_name=object_name
            )

            metadata = {
                "size": stat.size,
                "last_modified": stat.last_modified,
                "content_type": stat.content_type,
                "metadata": stat.metadata,
                "version_id": stat.version_id,
                "etag": stat.etag
            }

            logger.info(f"Retrieved metadata for {object_name} in bucket {bucket_name}")
            return metadata
        except (S3Error, HTTPError) as e:
            logger.error(f"Error getting object metadata: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting object metadata: {str(e)}")
            return None

    def copy_object(
            self,
            source_bucket: str,
            source_object: str,
            dest_bucket: str,
            dest_object: str,
            metadata: Optional[Dict] = None
    ) -> bool:
        """
        复制对象

        :param source_bucket: 源桶名称
        :param source_object: 源对象名称
        :param dest_bucket: 目标桶名称
        :param dest_object: 目标对象名称
        :param metadata: 新元数据 (可选)
        :return: 是否成功
        """
        try:
            self._ensure_bucket_exists(dest_bucket)

            self._client.copy_object(
                bucket_name=dest_bucket,
                object_name=dest_object,
                source=f"/{source_bucket}/{source_object}",
                metadata=metadata
            )

            logger.info(
                f"Successfully copied {source_bucket}/{source_object} "
                f"to {dest_bucket}/{dest_object}"
            )
            return True
        except (S3Error, HTTPError) as e:
            logger.error(f"Error copying object: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error copying object: {str(e)}")
            return False

    def list_buckets(self) -> List[Dict]:
        """
        列出所有桶

        :return: 桶信息列表
        """
        try:
            buckets = self._client.list_buckets()

            result = []
            for bucket in buckets:
                result.append({
                    "name": bucket.name,
                    "creation_date": bucket.creation_date
                })

            logger.info(f"Listed {len(result)} buckets")
            return result
        except (S3Error, HTTPError) as e:
            logger.error(f"Error listing buckets: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing buckets: {str(e)}")
            return []

    def set_bucket_policy(
            self,
            bucket_name: str,
            policy: Union[str, Dict]
    ) -> bool:
        """
        设置桶策略

        :param bucket_name: 桶名称
        :param policy: 策略 JSON 字符串或字典
        :return: 是否成功
        """
        try:
            if isinstance(policy, dict):
                import json
                policy = json.dumps(policy)

            self._client.set_bucket_policy(
                bucket_name=bucket_name,
                policy=policy
            )

            logger.info(f"Successfully set policy for bucket {bucket_name}")
            return True
        except (S3Error, HTTPError) as e:
            logger.error(f"Error setting bucket policy: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting bucket policy: {str(e)}")
            return False

    def get_bucket_policy(
            self,
            bucket_name: str
    ) -> Optional[Dict]:
        """
        获取桶策略

        :param bucket_name: 桶名称
        :return: 策略字典或 None (如果失败)
        """
        try:
            policy = self._client.get_bucket_policy(bucket_name)
            import json
            return json.loads(policy)
        except (S3Error, HTTPError) as e:
            logger.error(f"Error getting bucket policy: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting bucket policy: {str(e)}")
            return None

    def set_object_metadata(
            self,
            bucket_name: str,
            object_name: str,
            metadata: Dict
    ) -> bool:
        """
        设置对象元数据

        :param bucket_name: 桶名称
        :param object_name: 对象名称
        :param metadata: 元数据字典
        :return: 是否成功
        """
        try:
            # 获取当前对象元数据
            stat = self._client.stat_object(bucket_name, object_name)

            # 复制对象以更新元数据
            self._client.copy_object(
                bucket_name=bucket_name,
                object_name=object_name,
                source=f"/{bucket_name}/{object_name}",
                metadata=metadata,
                metadata_directive="REPLACE"
            )

            logger.info(f"Successfully updated metadata for {object_name} in bucket {bucket_name}")
            return True
        except (S3Error, HTTPError) as e:
            logger.error(f"Error setting object metadata: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting object metadata: {str(e)}")
            return False