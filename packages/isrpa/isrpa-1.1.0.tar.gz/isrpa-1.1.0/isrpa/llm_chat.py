from typing import Optional, Dict, Any, List, Union
from volcenginesdkarkruntime import Ark


def ai_query(
        query: str,
        context: Optional[List[Dict[str, str]]] = None,
        model: str = "deepseek-v3-250324",
        **kwargs
) -> Union[str, Dict[str, Any]]:
    """
    向AI发送查询，支持对话上下文和函数调用

    参数:
        query: 用户查询文本
        context: 之前的对话上下文(role/content格式)
        model: 使用的AI模型
        **kwargs: 其他API参数(temperature, max_tokens等)

    返回:
        普通回答: 返回字符串
    """
    try:
        # 初始化客户端
        client = Ark(api_key="f0f8b460-c4ea-42a4-a951-5e2e454022ee")

        # 构建消息列表
        messages = []

        # 添加上下文(如果有)
        if context:
            messages.extend(context)

        # 添加当前查询
        messages.append({"role": "user", "content": query})

        # 设置默认参数
        default_params = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.5)
        }

        # 调用聊天补全API
        completion = client.chat.completions.create(**default_params)

        # 获取响应内容
        response = completion.choices[0].message.content

        return response

    except Exception as e:
        return f"AI查询时出错: {str(e)}"
