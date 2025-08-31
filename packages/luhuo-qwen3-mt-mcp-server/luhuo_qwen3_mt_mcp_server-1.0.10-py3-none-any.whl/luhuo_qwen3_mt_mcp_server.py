# luhuo_qwen3_mt_mcp_server.py
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from .config import SUPPORTED_LANGUAGES, SUPPORTED_MODELS, get_model_info, get_server_settings
from .translation import translate_text, translate_text_streaming

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