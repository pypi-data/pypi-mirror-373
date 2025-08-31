# translation.py
from typing import Any, Dict, List, Optional
from .config import validate_model, validate_language, get_default_model
from .clients import initialize_openai_client

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