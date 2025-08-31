import requests

def deepseek_chat(user_content: str, model: str = "deepseek-chat", api_key: str = None,
                  system_content: str = "You are a helpful assistant"):
    """
    调用DeepSeek AI API进行对话
    https://api-docs.deepseek.com/zh-cn/

    Args:
        user_content (str): 用户输入内容
        model (str): 模型名称，可选 "deepseek-chat" 或 "deepseek-reasoner"，默认为 "deepseek-chat"
        api_key (str): DeepSeek API密钥
        system_content (str): 系统提示词，默认为 "You are a helpful assistant"

    Returns:
        对于 deepseek-chat: 返回 str (AI回复内容) 或 None (失败时)
        对于 deepseek-reasoner: 返回 tuple (content, reasoning_content) 或 None (失败时)
    """
    
    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 构建消息列表
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content}
    ]

    data = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()  # 检查HTTP状态码
        response_data = response.json()

        # 提取AI回复内容
        if "choices" in response_data and len(response_data["choices"]) > 0:
            choice = response_data["choices"][0]
            message = choice["message"]

            if model == "deepseek-reasoner":
                # 推理模型返回推理过程和最终答案
                reasoning_content = message.get("reasoning_content", "")
                content = message.get("content", "")
                return content, reasoning_content
            else:
                # 普通对话模型只返回内容
                content = message.get("content", "")
                return content
        else:
            raise Exception("DeepSeek API响应格式异常，未找到choices字段")

    except Exception as e:
        raise Exception(f"DeepSeek API调用异常: {e}")