# config.py
import os
from typing import Dict, List

# 全局配置
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 支持的语言列表
SUPPORTED_LANGUAGES = [
    "Chinese", "English", "Japanese", "Korean", "French", "Spanish", "German", 
    "Thai", "Indonesian", "Vietnamese", "Arabic", "Russian", "Portuguese", 
    "Italian", "Dutch", "Polish", "Turkish", "Swedish", "Norwegian", "Danish",
    "Finnish", "Greek", "Hebrew", "Hindi", "Urdu", "Bengali", "Tamil", "Telugu",
    "Marathi", "Gujarati", "Kannada", "Malayalam", "Punjabi", "Nepali", "Sinhala",
    "Burmese", "Khmer", "Lao", "Mongolian", "Kazakh", "Kyrgyz", "Tajik", "Uzbek",
    "Turkmen", "Azerbaijani", "Georgian", "Armenian", "Albanian", "Serbian",
    "Croatian", "Bosnian", "Macedonian", "Bulgarian", "Romanian", "Hungarian",
    "Czech", "Slovak", "Slovenian", "Estonian", "Latvian", "Lithuanian",
    "Ukrainian", "Belarusian", "Icelandic", "Irish", "Welsh", "Scots Gaelic",
    "Maltese", "Luxembourgish", "Faroese", "Basque", "Catalan", "Galician",
    "Corsican", "Sardinian", "Sicilian", "Neapolitan", "Venetian", "Lombard",
    "Piedmontese", "Ligurian", "Emilian", "Romagnol", "Friulian", "Ladin",
    "Romansh", "Occitan", "Franco-Provençal", "Walloon", "Breton", "Norman",
    "Picard", "Champenois", "Lorrain", "Burgundian", "Frisian", "Low German",
    "Alemannic", "Bavarian", "Austrian German", "Swiss German", "Yiddish"
]

# 支持的模型列表
SUPPORTED_MODELS = ["qwen-mt-plus", "qwen-mt-turbo"]

def get_api_key() -> str:
    """获取API密钥"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Please set DASHSCOPE_API_KEY environment variable.")
    return api_key

def get_default_model() -> str:
    """获取默认模型"""
    return os.getenv("QWEN_MT_MODEL", "qwen-mt-turbo")

def get_base_url() -> str:
    """获取API基础URL"""
    return BASE_URL

def validate_model(model: str) -> bool:
    """验证模型是否支持"""
    return model in SUPPORTED_MODELS

def validate_language(language: str) -> bool:
    """验证语言是否支持"""
    return language in SUPPORTED_LANGUAGES or language == "auto"

def get_model_info() -> Dict[str, Dict]:
    """获取模型信息"""
    return {
        "qwen-mt-plus": {
            "description": "通义千问翻译增强版，翻译质量更高，适合对翻译质量要求较高的场景",
            "context_length": 4096,
            "max_input": 2048,
            "max_output": 2048,
            "supported_languages": len(SUPPORTED_LANGUAGES)
        },
        "qwen-mt-turbo": {
            "description": "通义千问翻译快速版，翻译速度更快，成本更低",
            "context_length": 4096,
            "max_input": 2048,
            "max_output": 2048,
            "supported_languages": len(SUPPORTED_LANGUAGES)
        }
    }

def get_server_settings() -> Dict:
    """获取服务器配置信息"""
    return {
        "base_url": BASE_URL,
        "default_model": get_default_model(),
        "supported_models": SUPPORTED_MODELS,
        "supported_languages_count": len(SUPPORTED_LANGUAGES),
        "features": [
            "基础翻译",
            "流式翻译",
            "术语干预翻译",
            "领域提示翻译",
            "批量翻译",
            "自动语言检测"
        ],
        "api_compatibility": ["OpenAI Compatible API", "DashScope SDK"]
    }