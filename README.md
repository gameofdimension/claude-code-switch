# Claude Code Switch (ccm)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Switch Claude Code between AI providers with one command.

[中文文档](README_CN.md) | [Python Version Guide](docs/PYTHON_VERSION.md)

## Quick Start

```bash
# 1. Install
git clone https://github.com/gameofdimension/claude-code-switch.git
cd claude-code-switch
uv tool install .

# 2. Configure API keys
ccm config

# 3. Switch and use
ccm glm global        # switch to GLM (sets env vars)
ccc glm global        # switch + launch Claude Code
```

---

## Installation

```bash
git clone https://github.com/gameofdimension/claude-code-switch.git
cd claude-code-switch
uv tool install .
```

### Shell Integration (Optional)

For automatic env var handling, run the installer:

```bash
./install.sh              # User-level (default)
./install.sh --system     # System-level
./install.sh --project    # Project-only
./install.sh --no-rc      # Skip shell rc injection
```

### Uninstall

```bash
./uninstall.sh
```

### Upgrade

After pulling latest changes:

```bash
uv tool install . --reinstall
# or
./install.sh
```

---

## First-Time Setup

### 1. Configure API Keys

```bash
ccm config
```

This opens `~/.ccm_config`. Add your API keys:

```bash
DEEPSEEK_API_KEY=sk-...
KIMI_API_KEY=...
GLM_API_KEY=...
QWEN_API_KEY=...
MINIMAX_API_KEY=...
ARK_API_KEY=...           # For Doubao/Seed
STEPFUN_API_KEY=...       # For StepFun
OPENROUTER_API_KEY=...    # For OpenRouter
CLAUDE_API_KEY=...        # Optional, for Claude API
```

### 2. Verify Setup

```bash
ccm status
```

---

## Basic Usage

### Switch Provider (sets env vars in current shell)

```bash
ccm glm global        # GLM global (default)
ccm glm china         # GLM China
ccm deepseek          # DeepSeek
ccm kimi global       # Kimi global
ccm kimi china        # Kimi China
ccm qwen global       # Qwen global
ccm minimax           # MiniMax
ccm stepfun           # StepFun
ccm seed              # Doubao/Seed
ccm claude            # Claude official
```

### Switch + Launch Claude Code

```bash
ccc glm global        # Switch to GLM, then launch
ccc open glm          # Via OpenRouter
```

### Other Commands

```bash
ccm status            # Show current configuration
ccm help              # Show all commands
```

---

## Providers Reference

### Direct Providers

| Provider | Command | Region | Base URL |
|----------|---------|--------|----------|
| GLM | `ccm glm [global\|china]` | global (default) | `api.z.ai/api/anthropic` |
| | | china | `open.bigmodel.cn/api/anthropic` |
| DeepSeek | `ccm deepseek` | - | `api.deepseek.com/anthropic` |
| Kimi | `ccm kimi [global\|china]` | global (default) | `api.moonshot.ai/anthropic` |
| | | china | `api.kimi.com/coding` |
| Qwen | `ccm qwen [global\|china]` | global (default) | `coding-intl.dashscope.aliyuncs.com/apps/anthropic` |
| | | china | `coding.dashscope.aliyuncs.com/apps/anthropic` |
| MiniMax | `ccm minimax [global\|china]` | global (default) | `api.minimax.io/anthropic` |
| | | china | `api.minimaxi.com/anthropic` |
| StepFun | `ccm stepfun` | - | `api.stepfun.ai/v1/anthropic` |
| Seed/Doubao | `ccm seed [variant]` | - | `ark.cn-beijing.volces.com/api/coding` |
| Claude | `ccm claude` | - | `api.anthropic.com` |

> **GLM Coding Plan**: [bigmodel.cn/glm-coding](https://www.bigmodel.cn/glm-coding?ic=5XMIOZPPXB)
>
> **Doubao Coding Plan**: [volcengine.com](https://volcengine.com/L/rLv5d5OWXgg/) (Invite code: `ZP5PZMEY`)

### Seed Variants

```bash
ccm seed              # ark-code-latest (default)
ccm seed doubao       # doubao-seed-code
ccm seed glm          # glm-5
ccm seed deepseek     # deepseek-v3.2
ccm seed kimi         # kimi-k2.5
```

### OpenRouter

```bash
ccm open claude       # Claude via OpenRouter
ccm open glm          # GLM via OpenRouter
ccm open kimi         # Kimi via OpenRouter
ccm open deepseek     # DeepSeek via OpenRouter
ccm open qwen         # Qwen via OpenRouter
ccm open minimax      # MiniMax via OpenRouter
ccm open stepfun      # StepFun via OpenRouter
```

**Available:** `claude`, `glm`, `kimi`, `deepseek`, `qwen`, `minimax`, `stepfun`

---

## Advanced Features

### User-Level Settings (Highest Priority)

Write to `~/.claude/settings.json`. Overrides everything.

```bash
ccm user glm global      # GLM for all projects
ccm user reset           # Restore env var control
```

**When to use:**
- Other tools modify `~/.claude/settings.json`
- You want persistent defaults across shell restarts

### Project-Only Override

Override settings for a specific project:

```bash
ccm project glm global   # GLM for this project only
ccm project reset        # Remove project override
```

Creates `.claude/settings.local.json` in the project.

---

## Configuration

### Priority Order (highest to lowest)

1. `~/.claude/settings.json` - User-level settings
2. `.claude/settings.local.json` - Project-level settings
3. `~/.ccm_config` - Config file (reloads on each command)
4. Environment variables

### Full Config Example

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

# Model overrides (optional)
DEEPSEEK_MODEL=deepseek-chat
KIMI_MODEL=kimi-k2.5
GLM_MODEL=glm-5
MINIMAX_MODEL=MiniMax-M2.5
CLAUDE_MODEL=claude-sonnet-4-5-20250929
OPUS_MODEL=claude-opus-4-6
HAIKU_MODEL=claude-haiku-4-5-20251001
```

---

## Without Shell Function

If using `--no-rc` or calling binary directly:

```bash
eval "$(ccm glm global)"
```

---

## Notes

- **7 env vars exported**: `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`, `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL`
- **Claude official**: Uses subscription by default, or `CLAUDE_API_KEY` if set
- **OpenRouter**: Requires explicit `ccm open <provider>` command

---

## Development

```bash
git clone https://github.com/gameofdimension/claude-code-switch.git
cd claude-code-switch
uv sync --dev

uv run ccm --help         # Test locally
uv run pytest tests/ -v   # Run tests
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
