"""
七牛云存储API模块

安装依赖：
    pip install zx_rpa[qiniu]
    # 或者
    pip install qiniu
"""

import time
from pathlib import Path
from typing import Union, Dict

from qiniu import Auth, put_file


class QiniuManager:
    """
    七牛云存储管理器

    功能：
    - 文件上传到七牛云存储
    - 自动生成和缓存上传凭证
    - 返回文件访问URL
    """

    def __init__(self, access_key: str, secret_key: str, bucket_name: str, domain: str = None):
        """
        初始化七牛云存储管理器

        Args:
            access_key: 七牛云AccessKey
            secret_key: 七牛云SecretKey
            bucket_name: 七牛云存储空间名称
            domain: 七牛云存储空间的域名（可选）

        Raises:
            ImportError: 七牛云依赖库未安装
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.domain = domain

        # 初始化七牛云认证
        self.auth = Auth(access_key, secret_key)

        # 上传凭证缓存
        self._token_cache = {}
        self._token_expires = 3600  # 1小时
        self._buffer_time = 300     # 5分钟缓冲时间

    def upload_file(self, local_file_path: Union[str, Path], remote_key: str) -> Dict:
        """
        上传文件到七牛云存储

        Args:
            local_file_path: 本地文件路径
            remote_key: 远程文件名（含路径），如: products/123456/main/1.jpg

        Returns:
            Dict: 上传结果
                - key: 文件在七牛云的键名
                - hash: 文件哈希值
                - url: 文件访问URL

        Raises:
            FileNotFoundError: 本地文件不存在
            ValueError: 上传失败（HTTP状态码非200）
            Exception: 其他七牛云SDK异常
        """
        # 检查本地文件是否存在
        local_path = Path(local_file_path)
        if not local_path.exists():
            raise FileNotFoundError(f"本地文件不存在: {local_file_path}")

        # 获取上传凭证
        upload_token = self._get_upload_token(remote_key)

        # 执行上传
        result, response_info = put_file(
            up_token=upload_token,
            key=remote_key,
            file_path=str(local_path)
        )

        # 检查上传结果
        if response_info.status_code != 200:
            raise ValueError(f"七牛云上传失败: HTTP {response_info.status_code}, {response_info.text_body}")

        # 返回上传结果
        return {
            'key': result['key'],
            'hash': result['hash'],
            'url': self._build_file_url(result['key'])
        }

    def _get_upload_token(self, key: str) -> str:
        """
        获取上传凭证（带缓存机制）

        Args:
            key: 文件键名

        Returns:
            str: 上传凭证
        """
        current_time = time.time()

        # 检查缓存中是否有有效的凭证
        if key in self._token_cache:
            cached_data = self._token_cache[key]
            # 如果距离过期时间还有缓冲时间，则使用缓存的凭证
            if cached_data['expires_at'] - current_time > self._buffer_time:
                return cached_data['token']

        # 生成新的上传凭证
        token = self.auth.upload_token(
            bucket=self.bucket_name,
            key=key,
            expires=self._token_expires
        )

        # 缓存凭证
        self._token_cache[key] = {
            'token': token,
            'expires_at': current_time + self._token_expires
        }

        return token

    def _build_file_url(self, key: str) -> str:
        """
        构建文件访问URL

        Args:
            key: 文件键名

        Returns:
            str: 文件访问URL
        """
        if self.domain:
            return f"https://{self.domain}/{key}"
        else:
            return key  # 如果没有域名，返回键名