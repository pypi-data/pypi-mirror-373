# clients.py
from openai import OpenAI
from .config import get_api_key, get_base_url

def initialize_openai_client():
    """初始化OpenAI客户端"""
    api_key = get_api_key()
    base_url = get_base_url()
    
    return OpenAI(
        api_key=api_key,
        base_url=base_url
    )