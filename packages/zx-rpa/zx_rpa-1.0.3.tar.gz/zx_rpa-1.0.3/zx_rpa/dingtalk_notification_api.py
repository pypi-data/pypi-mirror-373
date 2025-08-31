"""
钉钉群机器人通知模块
"""

import requests
import time
import hmac
import hashlib
import base64
import urllib.parse
from typing import Dict


def dingtalk_notification(content: str, webhook_url: str, secret: str) -> Dict:
    """
    发送钉钉群机器人文本通知 简化只能发送纯文本类型
    
    Args:
        content: 消息内容
        webhook_url: 钉钉群机器人的webhook地址(不带签名参数)
        secret: 安全设置的签名密钥
        
    Returns:
        Dict: 接口返回结果
        
    Raises:
        requests.RequestException: 网络请求异常
        requests.HTTPError: HTTP状态码异常
        ValueError: API返回错误码非0
        requests.JSONDecodeError: JSON解析异常
        
    Examples:
        result = dingtalk_notification(
            content="测试消息",
            webhook_url="https://oapi.dingtalk.com/robot/send?access_token=xxx",
            secret="SEC123abc..."
        )
    """
    # 计算签名
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    
    # 添加签名参数到URL
    webhook_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
    
    # 构造请求
    response = requests.post(
        webhook_url,
        json={
            "msgtype": "text",
            "text": {
                "content": content
            }
        },
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    
    # 检查HTTP状态码
    response.raise_for_status()
    
    # 解析响应
    result = response.json()
    
    # 检查API返回的错误码
    if result.get("errcode") != 0:
        raise ValueError(f"钉钉API错误: {result.get('errmsg', '未知错误')}")
        
    return result
