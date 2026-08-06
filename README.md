# CommandAI

> 命令行 AI Agent — 支持多家国内大模型 API 与本地模型，一行命令切换。

## 简介

CommandAI 是一个轻量级命令行 AI 助手，支持通过 API Key 调用国内主流大模型（DeepSeek、Kimi、GLM、Qwen）以及 OpenAI，同时保留本地模型（LLaMA、Ollama、Transformers）能力。内置联网搜索、多模型热切换、灵活配置等功能。

## 支持的模型

| 提供商 | type 值 | 默认模型 | 环境变量 | 原生搜索 |
|--------|---------|----------|----------|:--------:|
| **DeepSeek** | `deepseek` | `deepseek-chat` | `DEEPSEEK_API_KEY` | - |
| **Kimi** | `kimi` | `kimi-k3` | `MOONSHOT_API_KEY` | ✅ |
| **GLM (智谱)** | `glm` | `glm-4-flash` (免费) | `ZAI_API_KEY` | ✅ |
| **Qwen (通义)** | `qwen` | `qwen-plus` | `DASHSCOPE_API_KEY` | ✅ |
| **OpenAI** | `openai` | `gpt-3.5-turbo` | `OPENAI_API_KEY` | - |
| **LLaMA (本地)** | `llama` | - | - | - |
| **Ollama (本地)** | `ollama` | - | - | - |
| **Transformers** | `transformers` | - | - | - |

## 快速开始

### 1. 安装

```bash
git clone https://github.com/SysBoxerandMinecraft/CommandAI.git
cd CommandAI
pip install -r requirements.txt
```

### 2. 配置

复制配置模板并填入 API Key：

```bash
cp userconfig.example.yaml userconfig.yaml   # Windows: copy userconfig.example.yaml userconfig.yaml
```

编辑 `userconfig.yaml`：

```yaml
model:
  type: deepseek                          # 选择提供商
  api_key: "your-api-key-here"            # 填入 API Key
  model: "deepseek-chat"                  # 可选: deepseek-chat, deepseek-reasoner
```

### 3. 运行

```bash
python main.py
```

## API Key 获取

| 提供商 | 获取地址 |
|--------|----------|
| DeepSeek | https://platform.deepseek.com/ |
| Kimi | https://platform.moonshot.cn/ |
| GLM | https://open.bigmodel.cn/ |
| Qwen | https://dashscope.aliyun.com/ |
| OpenAI | https://platform.openai.com/ |

> 也可以不填 `api_key`，改为设置环境变量（如 `DEEPSEEK_API_KEY`），程序会自动读取。

## 使用方法

### 普通对话

```
>> 你好，请介绍一下自己
你好！我是 CommandAI，一个运行在命令行的 AI 助手……
```

### 内置命令

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助 |
| `/model` | 查看当前模型 |
| `/model <类型>` | 切换模型（如 `/model kimi`） |
| `/search <问题>` | 联网搜索并回答 |
| `/set <key> <value>` | 修改配置（如 `/set generation.temperature 0.5`） |
| `/reload` | 重新加载模型 |
| `/config` | 显示当前配置 |
| `/clear` | 清空对话历史 |
| `/exit` | 退出 |

### 模型切换

运行时随时切换提供商，无需重启：

```
>> /model glm
模型类型已从 deepseek 切换到 glm
模型已成功加载: glm-4-flash (提供商: glm)

>> /model kimi
模型类型已从 glm 切换到 kimi
模型已成功加载: kimi-k3 (提供商: kimi)
```

### 联网搜索

使用 `/search` 命令，支持模型原生搜索（Qwen/GLM/Kimi）或本地 DuckDuckGo 搜索：

```
>> /search 2026年诺贝尔物理学奖获得者
正在使用 qwen 原生联网搜索: 2026年诺贝尔物理学奖获得者 ...
[AI 基于最新搜索结果回答]
```

## 配置示例

### DeepSeek

```yaml
model:
  type: deepseek
  api_key: "your-key"
  model: "deepseek-chat"
```

### GLM（有免费模型）

```yaml
model:
  type: glm
  api_key: "your-key"
  model: "glm-4-flash"
```

### Qwen（支持深度推理）

```yaml
model:
  type: qwen
  api_key: "your-key"
  model: "qwen-plus"

generation:
  enable_thinking: true
  thinking_budget: 4096
  enable_search: true
```

### 本地模型

```yaml
model:
  type: llama
  path: "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
```

## 项目结构

```
CommandAI/
├── main.py                     # 入口
├── cli.py                      # 命令行界面
├── agent.py                    # Agent 核心逻辑
├── config.py                   # 配置管理
├── userconfig.example.yaml     # 配置模板
├── requirements.txt            # 依赖
├── backends/                   # 模型后端
│   ├── __init__.py             # 后端工厂
│   ├── base.py                # 抽象基类
│   ├── openai_backend.py       # OpenAI 兼容后端 (含国内模型)
│   ├── llama_backend.py        # LLaMA 本地后端
│   ├── ollama_backend.py       # Ollama 后端
│   └── transformers_backend.py # Transformers 后端
└── utils/
    ├── logger.py               # 日志
    ├── file_utils.py           # 文件工具
    └── search.py               # 联网搜索
```

## 常见问题

**Q: 切换模型后提示 API Key 错误？**

设置对应提供商的 Key：`/set model.api_key your-key`，然后 `/reload`。

**Q: llama.dll 加载失败？**

安装 [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)，或直接使用 API 提供商（如 GLM 免费模型）。

**Q: 搜索失败？**

使用 Qwen/GLM/Kimi 可获得原生联网搜索能力。其他提供商使用本地 DuckDuckGo 搜索，需网络连通。

## 许可证

MIT License
