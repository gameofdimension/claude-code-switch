# Claude Code Switch (ccm)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一条命令切换 Claude Code 的 AI 提供商。

[English](README.md)

## 快速开始

```bash
# 1. 安装
git clone https://github.com/gameofdimension/claude-code-switch.git
cd claude-code-switch
uv tool install .

# 2. 配置 API 密钥
ccm config

# 3. 切换并使用
ccm glm              # 切换到 GLM（设置环境变量）
ccc glm global       # 切换 + 启动 Claude Code
```

---

## 安装

```bash
git clone https://github.com/gameofdimension/claude-code-switch.git
cd claude-code-switch
uv tool install .
```

### Shell 集成（可选）

如需自动处理环境变量，运行安装脚本：

```bash
./install.sh              # 用户级（默认）
./install.sh --system     # 系统级
./install.sh --project    # 项目级
./install.sh --no-rc      # 不注入 shell rc
```

### 卸载

```bash
./uninstall.sh
```

---

## 首次配置

### 1. 配置 API 密钥

```bash
ccm config
```

这会用编辑器打开 `~/.ccm_config`，添加你的 API 密钥：

```bash
DEEPSEEK_API_KEY=sk-...
KIMI_API_KEY=...
GLM_API_KEY=...
QWEN_API_KEY=...
MINIMAX_API_KEY=...
ARK_API_KEY=...           # 豆包/Seed
STEPFUN_API_KEY=...       # StepFun
OPENROUTER_API_KEY=...    # OpenRouter
CLAUDE_API_KEY=...        # 可选，用于 Claude API
```

### 2. 验证配置

```bash
ccm status
```

---

## 基本用法

### 切换提供商（设置环境变量）

```bash
ccm glm global        # GLM 海外（默认）
ccm glm china         # GLM 国内
ccm deepseek          # DeepSeek
ccm kimi global       # Kimi 海外
ccm kimi china        # Kimi 国内
ccm qwen global       # Qwen 海外
ccm minimax           # MiniMax
ccm stepfun           # StepFun
ccm seed              # 豆包/Seed
ccm claude            # Claude 官方
```

### 切换 + 启动 Claude Code

```bash
ccc glm global        # 切换到 GLM，然后启动
ccc open glm          # 通过 OpenRouter
```

### 其他命令

```bash
ccm status            # 查看当前配置
ccm help              # 显示所有命令
```

---

## 提供商参考

### 直连提供商

| 提供商 | 命令 | 区域 | Base URL |
|--------|------|------|----------|
| GLM | `ccm glm [global\|china]` | global（默认） | `api.z.ai/api/anthropic` |
| | | china | `open.bigmodel.cn/api/anthropic` |
| DeepSeek | `ccm deepseek` | - | `api.deepseek.com/anthropic` |
| Kimi | `ccm kimi [global\|china]` | global（默认） | `api.moonshot.ai/anthropic` |
| | | china | `api.kimi.com/coding` |
| Qwen | `ccm qwen [global\|china]` | global（默认） | `coding-intl.dashscope.aliyuncs.com/apps/anthropic` |
| | | china | `coding.dashscope.aliyuncs.com/apps/anthropic` |
| MiniMax | `ccm minimax [global\|china]` | global（默认） | `api.minimax.io/anthropic` |
| | | china | `api.minimaxi.com/anthropic` |
| StepFun | `ccm stepfun` | - | `api.stepfun.ai/v1/anthropic` |
| 豆包/Seed | `ccm seed [variant]` | - | `ark.cn-beijing.volces.com/api/coding` |
| Claude | `ccm claude` | - | `api.anthropic.com` |

> **GLM Coding 套餐**：[bigmodel.cn/glm-coding](https://www.bigmodel.cn/glm-coding?ic=5XMIOZPPXB)
>
> **豆包 Coding Plan**：[volcengine.com](https://volcengine.com/L/rLv5d5OWXgg/)（邀请码：`ZP5PZMEY`）

### Seed 变体

```bash
ccm seed              # ark-code-latest（默认）
ccm seed doubao       # doubao-seed-code
ccm seed glm          # glm-5
ccm seed deepseek     # deepseek-v3.2
ccm seed kimi         # kimi-k2.5
```

### OpenRouter

```bash
ccm open claude       # 通过 OpenRouter 使用 Claude
ccm open glm          # 通过 OpenRouter 使用 GLM
ccm open kimi         # 通过 OpenRouter 使用 Kimi
ccm open deepseek     # 通过 OpenRouter 使用 DeepSeek
ccm open qwen         # 通过 OpenRouter 使用 Qwen
ccm open minimax      # 通过 OpenRouter 使用 MiniMax
ccm open stepfun      # 通过 OpenRouter 使用 StepFun
```

**可用提供商：** `claude`, `glm`, `kimi`, `deepseek`, `qwen`, `minimax`, `stepfun`

---

## 进阶功能

### 用户级设置（最高优先级）

写入 `~/.claude/settings.json`，覆盖一切。

```bash
ccm user glm global      # 所有项目使用 GLM
ccm user reset           # 恢复环境变量控制
```

**适用场景：**
- 其他工具修改了 `~/.claude/settings.json`
- 想要持久化的默认设置

### 项目级覆盖

为特定项目覆盖设置：

```bash
ccm project glm global   # 仅此项目使用 GLM
ccm project reset        # 移除项目覆盖
```

在项目中创建 `.claude/settings.local.json`。

---

## 配置

### 优先级（从高到低）

1. `~/.claude/settings.json` - 用户级设置
2. `.claude/settings.local.json` - 项目级设置
3. `~/.ccm_config` - 配置文件（每次命令都重新加载）
4. 环境变量

### 完整配置示例

```bash
# API Keys
DEEPSEEK_API_KEY=sk-...
KIMI_API_KEY=...
GLM_API_KEY=...
QWEN_API_KEY=...
MINIMAX_API_KEY=...
ARK_API_KEY=...
STEPFUN_API_KEY=...
OPENROUTER_API_KEY=...
CLAUDE_API_KEY=...

# 模型覆盖（可选）
DEEPSEEK_MODEL=deepseek-chat
KIMI_MODEL=kimi-k2.5
GLM_MODEL=glm-5
MINIMAX_MODEL=MiniMax-M2.5
CLAUDE_MODEL=claude-sonnet-4-5-20250929
OPUS_MODEL=claude-opus-4-6
HAIKU_MODEL=claude-haiku-4-5-20251001
```

---

## 不使用 Shell 函数

如果使用 `--no-rc` 或直接调用二进制：

```bash
eval "$(ccm glm global)"
```

---

## 备注

- **每个提供商导出 7 个环境变量**：`ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_MODEL`、`ANTHROPIC_DEFAULT_OPUS_MODEL`、`ANTHROPIC_DEFAULT_SONNET_MODEL`、`ANTHROPIC_DEFAULT_HAIKU_MODEL`、`CLAUDE_CODE_SUBAGENT_MODEL`
- **Claude 官方**：默认使用订阅，或使用 `CLAUDE_API_KEY`（如果设置了）
- **OpenRouter**：需要显式使用 `ccm open <provider>` 命令

---

## 开发

```bash
git clone https://github.com/gameofdimension/claude-code-switch.git
cd claude-code-switch
uv sync --dev

uv run ccm --help         # 本地测试
uv run pytest tests/ -v   # 运行测试
```

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE)。
