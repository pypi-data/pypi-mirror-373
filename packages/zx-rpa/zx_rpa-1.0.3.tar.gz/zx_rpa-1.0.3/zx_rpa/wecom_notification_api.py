"""
企业微信群机器人通知模块
"""

import requests
from typing import Dict


def wecom_notification(content: str, webhook_url: str) -> Dict:
    """
    发送企业微信群机器人文本通知
    简化只支持纯文本的内容发送
    
    Args:
        content: 消息内容
        webhook_url: 企业微信群机器人的完整webhook地址(包含key)
        
    Returns:
        Dict: 接口返回结果
        
    Raises:
        requests.RequestException: 网络请求异常
        requests.HTTPError: HTTP状态码异常
        ValueError: API返回错误码非0
        requests.JSONDecodeError: JSON解析异常
    """
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
        raise ValueError(f"企业微信API错误: {result.get('errmsg', '未知错误')}")
        
    return result
