CommandAI – 命令行智能助手
CommandAI – Command‑Line AI Agent

https://img.shields.io/badge/python-3.8+-blue.svg
https://img.shields.io/badge/License-MIT-yellow.svg

简介 / Introduction
CommandAI 是一个轻量级、可离线运行的命令行 AI 助手。它能够在资源受限的设备（如 4GB 内存的老旧电脑）上顺畅运行，让您通过终端与本地大语言模型对话，同时支持联网搜索、动态配置和多模型后端。

CommandAI is a lightweight, offline‑capable AI agent that runs in your terminal. It works smoothly on low‑spec devices (e.g., 4GB RAM) and lets you chat with local large language models, with built‑in web search, dynamic configuration, and multiple backends.

特性 / Features
轻量化 – 最小依赖，内存占用低，适合低配电脑（4GB 内存可运行 TinyLlama/Qwen2-0.5B 等模型）。
Lightweight – minimal dependencies and low memory footprint; runs on 4GB machines with models like TinyLlama/Qwen2‑0.5B.

多后端支持 – 支持 llama-cpp-python（GGUF 量化）、transformers（HuggingFace，含 4‑bit）、Ollama 和 OpenAI 兼容 API，可自由切换。
Multiple backends – llama‑cpp‑python (GGUF), transformers (HuggingFace with 4‑bit), Ollama, and OpenAI‑compatible APIs.

联网搜索 – 通过 /search 命令实时获取网络信息（DuckDuckGo、维基百科、天气查询等），让 AI 基于搜索结果回答。
Web search – use /search to fetch real‑time information (DuckDuckGo, Wikipedia, weather) and let the AI answer with the results.

灵活配置 – YAML 配置文件管理模型路径、生成参数（temperature, top_p, max_tokens 等），支持动态重载。
Flexible configuration – YAML file for model path, generation parameters; hot‑reload with /reload.

交互友好 – 内置命令：/clear 清空历史，/config 查看配置，/set 修改参数，/help 帮助。
User‑friendly CLI – built‑in commands: /clear, /config, /set, /help, etc.

跨平台 – Windows / Linux / macOS 均可运行。
Cross‑platform – works on Windows, Linux, and macOS.

快速开始 / Quick Start
1. 安装依赖 / Install Dependencies
bash
# 克隆项目
git clone https://github.com/yourusername/CommandAI.git
cd CommandAI

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 安装核心依赖
pip install -r requirements.txt
注意：若仅使用 llama 后端，只需 llama-cpp-python 和 pyyaml。其他后端为可选（见 requirements.txt）。
Note: For llama backend only llama-cpp-python and pyyaml are required; other backends are optional.

2. 下载模型 / Download a Model
推荐使用 GGUF 量化模型（如 TinyLlama-1.1B-Chat Q4_K_M 或 Qwen2.5-0.5B-Instruct Q4_K_M），将模型文件放入 models/ 目录（或任意位置）。

Recommended GGUF models: TinyLlama-1.1B or Qwen2.5-0.5B. Place the .gguf file in models/ or anywhere.

3. 配置 / Configure
首次运行会自动生成 userconfig.yaml，编辑其中的 model.path 指向你的模型文件：

yaml
model:
  type: llama               # 后端类型：llama / transformers / ollama / openai
  path: models/qwen2.5-0.5b-instruct-q4_k_m.gguf
generation:
  max_tokens: 512
  temperature: 0.7
  top_p: 0.9
  repeat_penalty: 1.1
context:
  max_history_turns: 10
  system_prompt: "You are a helpful AI assistant."
4. 运行 / Run
bash
python main.py
启动后即可在 >> 提示符下与 AI 对话。

使用指南 / Usage Guide
内置命令 / Built‑in Commands
命令 / Command	说明 / Description
/exit /quit	退出程序 / Exit
/clear	清空对话历史 / Clear history
/reload	重新加载模型（读取配置文件） / Reload model from config
/config	显示当前配置 / Show current config
/set key value	修改配置项（如 /set generation.temperature 0.8） / Change a config key
/search <query>	联网搜索并让 AI 基于结果回答 / Web search + AI answer
/help	显示帮助 / Show help
普通对话 / Normal Chat
直接输入任意文本，AI 会结合上下文回复。例如：

text
>> 你好，请介绍一下自己
你好！我是 CommandAI，一个运行在命令行的 AI 助手……
联网搜索示例 / Search Example
text
>> /search 2026年世界杯举办地
正在搜索: 2026年世界杯举办地 ...
[AI 根据搜索到的信息回答]
模型推荐（低配电脑） / Model Recommendations (Low‑Spec)
模型 / Model	参数量 / Params	量化 / Quant	内存占用 / RAM	备注 / Note
TinyLlama‑1.1B‑Chat	1.1B	Q4_K_M	~700 MB	最佳平衡 / Best balance
Qwen2.5‑0.5B‑Instruct	0.5B	Q4_K_M	~500 MB	对中文友好 / Good for Chinese
Phi‑3‑mini‑4k‑instruct	3.8B	Q4_K_M	~2.2 GB	更智能，需 >4GB 内存 / Smarter, needs >4GB
项目结构 / Project Structure
text
CommandAI/
├── main.py                 # 入口 / Entry point
├── cli.py                  # 命令行界面 / CLI
├── agent.py                # AI 核心逻辑 / Agent logic
├── config.py               # 配置管理 / Config manager
├── userconfig.yaml         # 用户配置文件 / User config
├── requirements.txt        # 依赖 / Dependencies
├── utils/
│   ├── logger.py           # 日志 / Logging
│   ├── file_utils.py       # 文件工具 / File helpers
│   └── search.py           # 联网搜索 / Web search
└── backends/               # 模型后端 / Model backends
    ├── base.py
    ├── llama_backend.py
    ├── transformers_backend.py
    ├── ollama_backend.py
    └── openai_backend.py
扩展与定制 / Extending & Customizing
添加新后端：在 backends/ 下实现 ModelBackend 抽象类，并在 __init__.py 中注册。
Add a new backend: implement ModelBackend in backends/ and register it.

修改系统提示：调整 userconfig.yaml 中的 context.system_prompt。
Change system prompt via context.system_prompt in config.

自定义搜索源：修改 utils/search.py，增加或替换搜索接口。
Customize search sources by editing utils/search.py.

常见问题 / FAQ
Q: 模型加载失败 / Model fails to load?
A: 检查 model.path 是否正确，模型文件是否存在，以及是否安装了对应的后端库（如 llama-cpp-python）。

Q: 搜索超时或失败 / Search timeout or fails?
A: 可能是网络问题。程序会自动尝试 DuckDuckGo、维基百科和百度作为备用。若仍失败，可检查代理设置或改用 wttr.in（天气查询除外）。
Network issues. The program falls back to multiple sources; try setting a proxy or check connectivity.

Q: 内存不足 / Out of memory?
A: 使用更小的模型（如 Qwen2‑0.5B）或降低 n_ctx（在配置中加 llama_kwargs: {n_ctx: 1024}）。
Use a smaller model or reduce n_ctx.

贡献 / Contributing
欢迎提交 Issue 和 Pull Request。请确保代码风格与现有保持一致，并添加必要的测试。
Issues and PRs are welcome. Please maintain code style and add tests if needed.

许可证 / License
MIT License. See LICENSE for details.

致谢 / Acknowledgements
llama-cpp-python

Transformers

DuckDuckGo Search

wttr.in

Enjoy your CommandAI! 🚀

