import os
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# API 配置
api_key = os.getenv('QWEN_API_KEY', '')
chat_url = os.getenv('QWEN_CHAT_URL',
                     'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions')
chat_model = os.getenv('QWEN_CHAT_MODEL', 'qwen-plus-2025-12-01')
max_tokens = int(os.getenv('MAX_TOKENS', 32768))


def log_message(message: str, log_file: str = "qwen_engine.log"):
    """
    统一日志记录函数
    
    Args:
        message: 要记录的消息
        log_file: 日志文件路径
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")


def chat_with_llm(query: str, enable_thinking: bool = True) -> str:
    """
    调用大模型生成响应
    
    Args:
        query: 用户查询
        enable_thinking: 是否启用推理模式
    
    Returns:
        模型响应文本
    
    Raises:
        ValueError: API 密钥未设置
        requests.exceptions.RequestException: API 调用失败
    """
    try:
        log_message(f"[DEBUG] chat_with_llm called with query: {repr(query)}")
        
        # 检查 API 密钥是否设置
        if not api_key:
            raise ValueError("QWEN_API_KEY 环境变量未设置")
        
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        # 确保查询文本是 UTF-8 编码
        if isinstance(query, str):
            query = query.encode('utf-8').decode('utf-8')
        
        payload = {
            'model': chat_model,
            'messages': [{'role': 'user', 'content': query}],
            'stream': False,
            'top_p': 0.2,
            'temperature': 0.05,
            'max_tokens': max_tokens,
            'seed': 1368,
            'enable_thinking': enable_thinking
        }
        
        response = requests.post(chat_url, headers=headers, json=payload, timeout=300)
        response.raise_for_status()
        
        response_data = response.json()
        message = response_data['choices'][0]['message']
        
        # 如果 content 为空，尝试使用 reasoning_content
        content = message.get('content', '')
        reasoning_content = message.get('reasoning_content', '')
        
        if not content and reasoning_content:
            log_message("[WARN] content is empty, using reasoning_content")
            content = reasoning_content
        
        log_message("[DEBUG] chat_with_llm success")
        return content
        
    except requests.exceptions.HTTPError as http_err:
        log_message(f'HTTP error: {http_err}')
        raise http_err
    except requests.exceptions.Timeout as timeout_err:
        log_message(f'Timeout error: {timeout_err}')
        raise timeout_err
    except Exception as error:
        log_message(f'Error: {error}')
        raise error