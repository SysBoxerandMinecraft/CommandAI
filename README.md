# CommandAI

命令行 AI Agent — 支持多模型 API 调用、联网搜索与本地模型

## 功能特性

- **多模型 API 支持**：DeepSeek、Kimi、GLM、Qwen、OpenAI，一键切换
- **本地模型支持**：LLaMA (GGUF)、Ollama、Transformers (HuggingFace)
- **联网搜索**：Qwen/GLM/Kimi 原生搜索 + DuckDuckGo 本地搜索回退
- **运行时切换**：`/model` 命令动态切换模型，无需重启
- **灵活配置**：YAML 配置文件，支持环境变量读取 API Key
- **轻量跨平台**：Windows / Linux / macOS

## 快速开始

### 1. 安装依赖

```bash
pip install openai pyyaml colorama duckduckgo-search
```

### 2. 配置

复制配置模板并填入 API Key：

```bash
cp userconfig.example.yaml userconfig.yaml
```

编辑 `userconfig.yaml`：

```yaml
model:
  type: deepseek              # deepseek / kimi / glm / qwen / openai / llama
  api_key: "your-api-key"
  model: "deepseek-chat"

generation:
  max_tokens: 1024
  temperature: 0.7

context:
  system_prompt: "You are a helpful AI assistant."
```

### 3. 运行

```bash
python main.py
```

## 支持的模型提供商

| 提供商 | type 值 | 默认模型 | 环境变量 | 原生搜索 |
|--------|---------|----------|----------|----------|
| DeepSeek | `deepseek` | `deepseek-chat` | `DEEPSEEK_API_KEY` | - |
| Kimi | `kimi` | `kimi-k3` | `MOONSHOT_API_KEY` | ✅ |
| GLM | `glm` | `glm-4-flash` (免费) | `ZAI_API_KEY` | ✅ |
| Qwen | `qwen` | `qwen-plus` | `DASHSCOPE_API_KEY` | ✅ |
| OpenAI | `openai` | `gpt-3.5-turbo` | `OPENAI_API_KEY` | - |

所有提供商均兼容 OpenAI API 格式，`base_url` 自动配置。

### API Key 获取

| 提供商 | 注册地址 |
|--------|----------|
| DeepSeek | https://platform.deepseek.com/ |
| Kimi | https://platform.moonshot.cn/ |
| GLM | https://open.bigmodel.cn/ |
| Qwen | https://dashscope.aliyun.com/ |
| OpenAI | https://platform.openai.com/ |

## 命令列表

| 命令 | 说明 |
|------|------|
| `/model [类型]` | 切换或查看当前模型 |
| `/search <问题>` | 联网搜索并回答 |
| `/set key value` | 修改配置项 |
| `/reload` | 重新加载模型 |
| `/config` | 显示当前配置 |
| `/clear` | 清空对话历史 |
| `/help` | 显示帮助 |
| `/exit` | 退出 |

## 使用示例

```
>> 你好，请介绍一下自己

>> /model glm
模型已切换: glm-4-flash (glm)

>> /search 2026年诺贝尔奖获得者
正在使用 glm 原生联网搜索...

>> /set generation.temperature 0.5
已更新配置项

>> /model qwen
模型已切换: qwen-plus (qwen)
```

## 项目结构

```
CommandAI/
├── main.py                     # 入口
├── cli.py                      # 命令行界面
├── agent.py                    # Agent 核心逻辑
├── config.py                   # 配置管理
├── userconfig.yaml             # 用户配置 (gitignore)
├── userconfig.example.yaml     # 配置模板
├── requirements.txt
├── backends/
│   ├── __init__.py             # 后端工厂
│   ├── base.py                 # 后端基类
│   ├── openai_backend.py       # OpenAI 兼容后端 (含国内模型)
│   ├── llama_backend.py        # LLaMA 本地后端
│   ├── ollama_backend.py       # Ollama 后端
│   └── transformers_backend.py # Transformers 后端
└── utils/
    ├── logger.py               # 日志
    ├── file_utils.py           # 文件工具
    └── search.py               # 本地搜索
```

## License

MIT
