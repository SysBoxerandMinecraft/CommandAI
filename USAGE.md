# CommandAI 使用指南

## 快速开始

### 1. 安装依赖

```bash
pip install openai pyyaml colorama duckduckgo-search
```

### 2. 配置模型

编辑 `userconfig.yaml`，选择模型提供商并填入 API Key。

### 3. 运行

```bash
python main.py
```

## 支持的模型提供商

| 提供商 | type 值 | base_url | 默认模型 | 环境变量 |
|--------|---------|----------|----------|----------|
| **DeepSeek** | `deepseek` | `https://api.deepseek.com` | `deepseek-chat` | `DEEPSEEK_API_KEY` |
| **Kimi** | `kimi` | `https://api.moonshot.cn/v1` | `kimi-k3` | `MOONSHOT_API_KEY` |
| **GLM** | `glm` | `https://open.bigmodel.cn/api/paas/v4/` | `glm-4-flash` (免费) | `ZAI_API_KEY` |
| **Qwen** | `qwen` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` | `DASHSCOPE_API_KEY` |
| **OpenAI** | `openai` | `https://api.openai.com/v1` | `gpt-3.5-turbo` | `OPENAI_API_KEY` |

所有国内模型均兼容 OpenAI API 格式，`base_url` 会自动使用预设值，无需手动配置。

## 配置示例

### DeepSeek (默认推荐)
```yaml
model:
  type: deepseek
  api_key: "your-deepseek-api-key"
  model: "deepseek-chat"    # 或 deepseek-reasoner
```

### Kimi (月之暗面)
```yaml
model:
  type: kimi
  api_key: "your-kimi-api-key"
  model: "kimi-k3"          # 或 moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
```

### GLM (智谱AI - 有免费模型)
```yaml
model:
  type: glm
  api_key: "your-glm-api-key"
  model: "glm-4-flash"     # 免费! 或 glm-4, glm-4-air
```

### Qwen (通义千问)
```yaml
model:
  type: qwen
  api_key: "your-qwen-api-key"
  model: "qwen-plus"        # 或 qwen-max, qwen-turbo
```

### OpenAI
```yaml
model:
  type: openai
  api_key: "your-openai-api-key"
  model: "gpt-4o"           # 或 gpt-4o-mini, gpt-3.5-turbo
```

### 本地模型 (LLaMA)
```yaml
model:
  type: llama
  path: "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
```

## API Key 获取方式

| 提供商 | 获取地址 |
|--------|----------|
| DeepSeek | https://platform.deepseek.com/ |
| Kimi | https://platform.moonshot.cn/ |
| GLM | https://open.bigmodel.cn/ |
| Qwen | https://dashscope.aliyun.com/ |
| OpenAI | https://platform.openai.com/ |

## 使用环境变量

除了在配置文件中设置 API Key，也可以使用环境变量：

```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY = "your-key"
python main.py

# 或在 userconfig.yaml 中省略 api_key，程序会自动读取环境变量
```

## 命令行操作

### 查看当前模型
```
/model
```

### 切换模型提供商
```
/model deepseek
/model kimi
/model glm
/model qwen
/model openai
/model llama
```

### 设置 API Key
```
/set model.api_key your-actual-key
/reload
```

### 修改生成参数
```
/set generation.temperature 0.5
/set generation.max_tokens 2048
/reload
```

### 联网搜索
```
/search Python 异步编程最佳实践
```

### 查看帮助
```
/help
```

## Qwen 特殊参数

Qwen 支持独有的扩展参数，在 `userconfig.yaml` 的 `generation` 中配置：

```yaml
generation:
  enable_thinking: true     # 启用深度推理
  thinking_budget: 4096      # 思考token上限
  enable_search: true        # 启用联网搜索
```

## 常见问题

### 1. API Key 错误
确保 `userconfig.yaml` 中的 `api_key` 正确，或设置对应的环境变量。

### 2. 网络连接问题
国内模型 API 通常在中国境内可直连。OpenAI 可能需要代理。

### 3. llama.dll 加载失败
`llama-cpp-python` 需要 Visual C++ Redistributable。如不需要本地模型，使用 API 提供商即可。
