# luhuo_qwen3_mt_mcp_server.py
import os
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from openai import OpenAI

# ===== CONFIG MODULE =====
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

# ===== CLIENTS MODULE =====
def initialize_openai_client():
    """初始化OpenAI客户端"""
    api_key = get_api_key()
    base_url = get_base_url()
    
    return OpenAI(
        api_key=api_key,
        base_url=base_url
    )

# ===== TRANSLATION MODULE =====
def translate_text(
    text: str,
    target_lang: str,
    source_lang: str = "auto",
    model: Optional[str] = None,
    terminology: Optional[Dict[str, str]] = None,
    domain: Optional[str] = None
) -> Dict[str, Any]:
    """
    文本翻译功能 - 将文本从源语言翻译到目标语言
    
    Args:
        text: 需要翻译的文本
        target_lang: 目标语言，如"English", "Chinese"等
        source_lang: 源语言，默认为"auto"自动检测
        model: 使用的模型，默认使用环境变量配置的模型
    
    Returns:
        包含翻译结果或错误信息的字典
    """
    try:
        if model is None:
            model = get_default_model()
            
        if not validate_model(model):
            return {
                "success": False,
                "error": f"不支持的模型: {model}。请使用 qwen-mt-plus 或 qwen-mt-turbo"
            }
        
        if not validate_language(target_lang):
            return {
                "success": False,
                "error": f"不支持的目标语言: {target_lang}"
            }
        
        translation_options = {
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        
        # 添加术语支持
        if terminology:
            terms = [{"source": source_term, "target": target_term} for source_term, target_term in terminology.items()]
            translation_options["terms"] = terms
        
        # 添加领域支持
        if domain:
            translation_options["domains"] = [domain]
        
        # 使用OpenAI兼容API
        client = initialize_openai_client()
        messages = [{"role": "user", "content": text}]
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            extra_body={"translation_options": translation_options}
        )
        
        translated_text = response.choices[0].message.content
        
        return {
            "success": True,
            "translated_text": translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "model": model,
            "message": "翻译成功"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"翻译时出错: {str(e)}"
        }

async def translate_text_streaming(
    text: str,
    target_lang: str,
    source_lang: str = "auto",
    model: Optional[str] = None,
    terminology: Optional[Dict[str, str]] = None,
    domain: Optional[str] = None
) -> Dict[str, Any]:
    """
    流式翻译功能，支持术语干预和领域提示
    
    Args:
        text: 需要翻译的文本
        target_lang: 目标语言
        source_lang: 源语言，默认为"auto"
        model: 使用的模型
        terminology: 术语词典，格式为 {"原术语": "目标术语"}
        domain: 领域提示，如"医学"、"法律"、"技术"等
    
    Returns:
        包含流式翻译结果的字典
    """
    try:
        if model is None:
            model = get_default_model()
            
        if not validate_model(model):
            return {
                "success": False,
                "error": f"不支持的模型: {model}"
            }
        
        if not validate_language(target_lang):
            return {
                "success": False,
                "error": f"不支持的目标语言: {target_lang}"
            }
        
        translation_options = {
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        
        # 添加术语支持
        if terminology:
            terms = [{"source": source_term, "target": target_term} for source_term, target_term in terminology.items()]
            translation_options["terms"] = terms
        
        # 添加领域支持
        if domain:
            translation_options["domains"] = [domain]
        
        # 使用OpenAI兼容API的流式调用
        client = initialize_openai_client()
        messages = [{"role": "user", "content": text}]
        
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            extra_body={"translation_options": translation_options},
            stream=True
        )
        
        translated_chunks = []
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                translated_chunks.append(chunk.choices[0].delta.content)
        
        translated_text = ''.join(translated_chunks)
        
        return {
            "success": True,
            "translated_text": translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "model": model,
            "streaming": True,
            "message": "流式翻译完成"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"流式翻译时出错: {str(e)}"
        }

# 创建MCP服务器实例
mcp = FastMCP("Qwen Machine Translation Server")

@mcp.tool()
def translate_text_tool(
    text: str,
    target_lang: str,
    source_lang: str = "auto",
    model: Optional[str] = None,
    terminology: Optional[Dict[str, str]] = None,
    domain: Optional[str] = None
) -> Dict[str, Any]:
    """
    文本翻译功能 - 将文本从源语言翻译到目标语言，支持术语干预和领域提示
    
    Args:
        text: 需要翻译的文本
        target_lang: 目标语言，如"English", "Chinese"等
        source_lang: 源语言，默认为"auto"自动检测
        model: 使用的模型，默认使用环境变量配置的模型
        terminology: 术语词典，格式为 {"原术语": "目标术语"}
        domain: 领域提示，领域提示语句暂时只支持英文，如"The sentence is from Ali Cloud IT domain. It mainly involves computer-related software development and usage methods, including many terms related to computer software and hardware. Pay attention to professional troubleshooting terminologies and sentence patterns when translating. Translate into this IT domain style."等
    
    Returns:
        包含翻译结果或错误信息的字典
    """
    return translate_text(text, target_lang, source_lang, model, terminology, domain)



@mcp.tool()
async def translate_text_streaming_tool(
    text: str,
    target_lang: str,
    source_lang: str = "auto",
    model: Optional[str] = None,
    terminology: Optional[Dict[str, str]] = None,
    domain: Optional[str] = None
) -> Dict[str, Any]:
    """
    流式翻译功能 - 实时返回翻译结果，支持术语干预和领域提示
    
    Args:
        text: 需要翻译的文本
        target_lang: 目标语言
        source_lang: 源语言，默认为"auto"
        model: 使用的模型
        terminology: 术语词典，格式为 {"原术语": "目标术语"}
        domain: 领域提示，领域提示语句暂时只支持英文，如"The sentence is from Ali Cloud IT domain. It mainly involves computer-related software development and usage methods, including many terms related to computer software and hardware. Pay attention to professional troubleshooting terminologies and sentence patterns when translating. Translate into this IT domain style."等
    
    Returns:
        包含流式翻译结果的字典
    """
    return await translate_text_streaming(text, target_lang, source_lang, model, terminology, domain)



@mcp.resource("config://models")
def get_available_models() -> str:
    """获取可用的翻译模型列表"""
    models = get_model_info()
    return f"可用翻译模型: {models}"

@mcp.resource("config://languages")
def get_supported_languages() -> str:
    """获取支持的语言列表"""
    return f"支持的语言列表 ({len(SUPPORTED_LANGUAGES)}种): {', '.join(SUPPORTED_LANGUAGES)}"

@mcp.resource("config://settings")
def get_server_settings_resource() -> str:
    """获取服务器配置信息"""
    settings = get_server_settings()
    return f"服务器配置: {settings}"

def main():
    """主函数入口点"""
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()