import sys
import unittest
from datetime import timedelta
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentic_kit_common.minio.minio_manager import MinioManager
from .config import load_config


class MyTestCase(unittest.TestCase):
    def test_minio_list_obj(self):
        config = load_config().get('minio', {})
        # 初始化客户端
        minio_client = MinioManager(
            endpoint=config.get('ENDPOINT'),
            access_key=config.get('ACCESS_KEY'),
            secret_key=config.get('SECRET_KEY'),
            secure=config.get('SECURE', False)
        )
        # 列出对象
        objects = minio_client.list_objects("my-bucket", prefix="path/")
        for obj in objects:
            print(obj)
            print(f"Object: {obj['name']}, Size: {obj['size']}")

    def test_minio(self):
        config = load_config().get('minio', {})

        # 初始化客户端
        minio_client = MinioManager(
            endpoint=config.get('ENDPOINT'),
            access_key=config.get('ACCESS_KEY'),
            secret_key=config.get('SECRET_KEY'),
            secure=config.get('SECURE', False)
        )

        if not minio_client.bucket_exists("my-bucket"):
            minio_client.create_bucket("my-bucket")

        # 上传文件
        minio_client.upload_file(
            bucket_name="my-bucket",
            object_name="/path/下载.png",
            file_path="/Users/manson/Downloads/下载.png"
        )

        # 下载文件
        minio_client.download_file(
            bucket_name="my-bucket",
            object_name="/path/下载.png",
            file_path="/Users/manson/Downloads/下载2.png"
        )

        # 列出对象
        objects = minio_client.list_objects("my-bucket", prefix="path")
        for obj in objects:
            print(f"Object: {obj['name']}, Size: {obj['size']}")

        # 生成预签名URL
        url = minio_client.get_presigned_url(
            bucket_name="my-bucket",
            object_name="/path/下载.png",
            expires=timedelta(hours=1)
        )
        print(f"Download URL: {url}")

        # 删除对象
        # minio_client.delete_object("my-bucket", "/path/下载.png")


if __name__ == '__main__':
    unittest.main()