"""
飞书群机器人通知模块
"""

import requests
from typing import Dict


def feishu_notification(content: str, webhook_url: str) -> Dict:
    """
    发送飞书群机器人文本通知，只支持纯文本无签名的情况
    https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot
    
    Args:
        content: 消息内容
        webhook_url: 飞书群机器人的webhook地址
        
    Returns:
        Dict: 接口返回结果
        
    Raises:
        requests.RequestException: 网络请求异常
        requests.HTTPError: HTTP状态码异常
        ValueError: API返回错误码非0
        requests.JSONDecodeError: JSON解析异常
        
    Examples:
        result = feishu_notification(
            content="测试消息",
            webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
        )
    """
    # 构造请求
    response = requests.post(
        webhook_url,
        json={
            "msg_type": "text",
            "content": {"text": content}
        },
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    
    # 检查HTTP状态码
    response.raise_for_status()
    
    # 解析响应
    result = response.json()
    
    # 检查API返回的错误码
    if result.get("code") != 0:
        raise ValueError(f"飞书API错误: {result.get('msg', '未知错误')}")
        
    return result
