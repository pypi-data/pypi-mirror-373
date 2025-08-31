import os
import time
import base64
import requests
import re
from typing import Dict, Any
from urllib.parse import urlparse


class TjCaptcha:
    """图鉴验证码识别服务类"""

    API_URL = "http://api.ttshitu.com/predict"
    DEFAULT_USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36")
    NETWORK_SCHEMES = {'http', 'https'}

    def __init__(self, username: str, password: str) -> None:
        """
        初始化图鉴验证码识别服务

        Args:
            username: 图鉴平台注册用户名
            password: 图鉴平台注册密码
        """
        self._base_params = {'username': username, 'password': password}
        self._headers = {"User-Agent": self.DEFAULT_USER_AGENT}

    def main_captcha(self, image_source: str, type_id: int = 1) -> str:
        """
        识别验证码主入口方法

        Args:
            image_source: 图片来源，支持以下格式：
                        - base64编码字符串（自动识别）
                        - 本地文件路径
                        - 网络URL
            type_id: 验证码类型ID，详见：https://www.ttshitu.com/docs/index.html

        Returns:
            识别结果字符串

        Raises:
            Exception: 识别过程中的各种异常
        """
        try:
            # 自动判断图片格式并转换为base64
            image_base64 = self._auto_convert_to_base64(image_source)

            result = self._call_api(image_base64, type_id)

            if result.get('success'):
                return result["data"]["result"]
            else:
                raise Exception(f"API识别失败: {result.get('message', '未知错误')}")

        except (requests.RequestException, OSError, KeyError) as e:
            raise Exception(f"验证码识别失败: {e}")

    def check_balance(self) -> Dict[str, Any]:
        """
        查询账户信息余额

        Returns:
            账户信息字典
        """
        try:
            response = requests.post(
                "http://api.ttshitu.com/queryAccountInfo.json",
                json=self._base_params,
                headers=self._headers
            )
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"查询余额失败: {e}")


    def _auto_convert_to_base64(self, image_source: str) -> str:
        """
        自动判断图片格式并转换为base64编码

        Args:
            image_source: 图片来源（base64字符串、本地路径或网络URL）

        Returns:
            base64编码的图片数据
        """
        # 判断是否已经是base64格式
        if self._is_base64_string(image_source):
            return image_source

        # 判断是否是网络URL
        if self._is_network_url(image_source):
            return self._convert_url_to_base64(image_source)

        # 默认作为本地文件路径处理
        return self._convert_local_to_base64(image_source)

    def _is_base64_string(self, s: str) -> bool:
        """
        判断字符串是否为有效的base64编码

        Args:
            s: 待检测的字符串

        Returns:
            是否为base64编码
        """
        # 基本格式检查：长度应该是4的倍数，只包含base64字符
        if len(s) % 4 != 0:
            return False

        # 检查字符是否都是base64有效字符
        base64_pattern = re.compile(r'^[A-Za-z0-9+/]*={0,2}$')
        if not base64_pattern.match(s):
            return False

        # 尝试解码验证
        try:
            decoded = base64.b64decode(s, validate=True)
            # 检查解码后的数据是否像图片数据（至少有一定长度）
            return len(decoded) > 100  # 图片数据通常比较大
        except Exception:
            return False

    def _call_api(self, image_base64: str, type_id: int) -> Dict[str, Any]:
        """
        调用图鉴API进行验证码识别

        Args:
            image_base64: base64编码的图片数据
            type_id: 验证码类型ID

        Returns:
            API响应结果字典
        """
        params = {'typeid': type_id, 'image': image_base64}
        params.update(self._base_params)

        response = requests.post(self.API_URL, json=params, headers=self._headers)
        return response.json()

    def _convert_local_to_base64(self, image_path: str) -> str:
        """将本地图片转换为base64编码"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def _convert_url_to_base64(self, image_url: str) -> str:
        """将网络图片转换为base64编码"""
        response = requests.get(image_url, headers=self._headers)
        temp_filename = f"captcha_{time.time()}.png"

        try:
            with open(temp_filename, 'wb') as f:
                f.write(response.content)
            return self._convert_local_to_base64(temp_filename)
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    def _is_network_url(self, url: str) -> bool:
        """判断URL是否为网络资源"""
        parsed_url = urlparse(url)
        return parsed_url.scheme in self.NETWORK_SCHEMES