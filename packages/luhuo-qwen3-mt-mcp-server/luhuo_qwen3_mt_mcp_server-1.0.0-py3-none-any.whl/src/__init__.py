# __init__.py

__version__ = "1.0.0"
__author__ = "炉火"
__description__ = "基于Qwen3-MT的翻译MCP Server"

from .config import (
    BASE_URL,
    SUPPORTED_LANGUAGES,
    SUPPORTED_MODELS,
    get_api_key,
    get_default_model,
    validate_model,
    validate_language,
    get_model_info,
    get_server_settings
)

from .clients import (
    initialize_openai_client
)

from .translation import (
    translate_text,
    translate_text_streaming
)

__all__ = [
    "BASE_URL",
    "SUPPORTED_LANGUAGES",
    "SUPPORTED_MODELS",
    "get_api_key",
    "get_default_model",
    "validate_model",
    "validate_language",
    "get_model_info",
    "get_server_settings",
    "initialize_openai_client",
    "translate_text",
    "translate_text_streaming"
]