# 炉火基于 Qwen3-MT 的翻译 MCP Server

基于阿里通义千问翻译模型 Qwen3-MT https://help.aliyun.com/zh/model-studio/machine-translation#144a0417aeg3d 的 MCP（Model Context Protocol）服务器，支持 92 种语言互译、流式翻译、术语干预和领域提示等高级功能。

## 项目简介

本项目是一个基于 FastMCP 框架开发的机器翻译服务器，集成了阿里通义千问翻译模型（Qwen3-MT）的强大翻译能力。通过 MCP 协议，可以轻松集成到各种 AI 应用和工具中，提供高质量的多语言翻译服务。

### 核心特性

- 🌍 **多语言支持**：支持 92 种语言互译，包括中、英、日、韩、法、西、德、泰、印尼、越、阿等主流语言
- 🚀 **双模型选择**：支持 qwen-mt-plus（高质量）和 qwen-mt-turbo（高速度）两种模型
- 📡 **流式翻译**：支持实时流式翻译，提供更好的用户体验
- 🎯 **术语干预**：支持自定义术语词典，确保专业术语翻译准确性
- 🏢 **领域提示**：支持领域特定翻译，如医学、法律、技术、商务等
- 🔍 **自动语言检测**：智能识别源语言，无需手动指定

### 支持的模型

| 模型名称      | 描述               | 适用场景                         | 上下文长度   |
| ------------- | ------------------ | -------------------------------- | ------------ |
| qwen-mt-plus  | 通义千问翻译增强版 | 对翻译质量要求较高的场景         | 4,096 tokens |
| qwen-mt-turbo | 通义千问翻译快速版 | 希望翻译速度更快或成本更低的场景 | 4,096 tokens |

## 项目结构

```
qwen-mt-mcp-server/
├── src/                     # 源代码目录
│   ├── __init__.py         # 包初始化文件
│   ├── config.py           # 配置模块
│   ├── clients.py          # 客户端模块
│   └── translation.py      # 翻译功能模块
├── luhuo_qwen3_mt_mcp_server.py   # 主服务器文件
├── pyproject.toml          # 项目配置文件
├── .env.example           # 环境变量示例文件
├── README.md              # 项目文档
└── LICENSE                # 许可证文件
```

## 部署指南

### 环境要求

- Python 3.10+
- 阿里云百炼 API 密钥

### 源码安装步骤

1. **克隆项目**

```bash
git clone https://github.com/RongjieChen/luhuo_qwen3_mt_mcp_server.git
cd luhuo_qwen3_mt_mcp_server
```

2. **安装依赖**

```bash
# 使用uv安装
uv sync
```

3. **配置环境变量**

创建 `.env` 文件或直接设置环境变量：

```bash
# API密钥（必需）
export DASHSCOPE_API_KEY="your-dashscope-api-key"

# 模型配置（可选）
# 默认使用的翻译模型，支持 qwen-mt-plus 或 qwen-mt-turbo
# 如果不设置，默认使用 qwen-mt-turbo
export QWEN_MT_MODEL="qwen-mt-turbo"
```

**获取 API 密钥：**

1. 访问 [阿里云百炼控制台](https://bailian.console.aliyun.com/?tab=globalset#/efm/api_key)
2. 创建并获取 API Key
3. 确保账户有足够的调用额度

4. **启动服务器**

```bash
# 直接运行
uv run python luhuo_qwen3_mt_mcp_server.py

```

### 快捷安装方式

**方式一：使用 pip 安装**

```bash
pip install luhuo_qwen3_mt_mcp_server
```

**方式二：使用 uvx 安装（推荐）**

```bash
uvx luhuo_qwen3_mt_mcp_server
```

### **客户端配置**

在 mcp json 文件中添加以下配置：

```json
{
  "mcpServers": {
    "luhuo_qwen3_mt_mcp_server": {
      "command": "uvx",
      "args": ["luhuo_qwen3_mt_mcp_server"],
      "env": {
        "DASHSCOPE_API_KEY": "your-dashscope-api-key-here"
      }
    }
  }
}
```

## 可用工具

### **1. translate_text_tool**

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

### **2. translate_text_streaming_tool**

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

## 使用示例

## 支持的语言

本服务器支持 92 种语言，包括但不限于：

**主要语言：**

- 中文 (Chinese)
- 英语 (English)
- 日语 (Japanese)
- 韩语 (Korean)
- 法语 (French)
- 西班牙语 (Spanish)
- 德语 (German)
- 俄语 (Russian)
- 阿拉伯语 (Arabic)
- 葡萄牙语 (Portuguese)
- 意大利语 (Italian)
- 荷兰语 (Dutch)

**亚洲语言：**

- 泰语 (Thai)
- 印尼语 (Indonesian)
- 越南语 (Vietnamese)
- 印地语 (Hindi)
- 乌尔都语 (Urdu)
- 孟加拉语 (Bengali)
- 泰米尔语 (Tamil)
- 缅甸语 (Burmese)
- 高棉语 (Khmer)
- 老挝语 (Lao)
- 蒙古语 (Mongolian)

更多语言请参考服务器的 `config://languages` 资源。

## 故障排除

### **常见问题**

1. **账户调用额度不足**: 确保账户有足够的调用额度
2. **网络连接问题**: 检查网络连接和防火墙设置
3. **模型不可用**: 确认使用的模型名称正确

## 许可证

本项目采用 Apache-2.0 license 许可证。

## 致谢

- 感谢阿里云提供的通义千问翻译模型服务
- 感谢 FastMCP 框架的开发者们
- 感谢所有贡献者和用户的支持

---

**注意：** 使用本服务需要有效的阿里云百炼 API 密钥，请确保遵守相关服务条款和使用限制。
