# Claude Code Switch (ccm)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Switch Claude Code between AI providers with one command.

[中文文档](README_CN.md) | [Python Version Guide](docs/PYTHON_VERSION.md)

## Quick Start

```bash
# 1. Install from source
git clone https://github.com/gameofdimension/claude-code-switch.git
cd claude-code-switch
uv tool install .

# 2. Configure your API keys
ccm config

# 3. Switch and use
ccm glm global             # switch to GLM (sets env vars in current shell)
ccc glm global             # switch + launch Claude Code (one command)

# Advanced: User-level settings (highest priority, overrides everything)
ccm user glm global        # Set GLM as default for all projects
ccm user reset             # Restore environment variable control

# Advanced: Project-only override
ccm project glm china      # GLM for this project only

```

## 🆕 Python Version (v3.0)

CCM has been migrated to Python for better maintainability, testing, and cross-platform support.

### Install

```bash
# From source
git clone https://github.com/gameofdimension/claude-code-switch.git
cd claude-code-switch
uv tool install .
```

### Python Version Features

- Modern CLI with Typer/Rich
- Type-safe with Pydantic
- 62 unit & integration tests
- Project & user-level settings

See [Python Version Guide](docs/PYTHON_VERSION.md) for full documentation.

---

## Installation

### From Source
```bash
git clone https://github.com/gameofdimension/claude-code-switch.git
cd claude-code-switch
uv tool install .
```

### Install Modes

| Mode | Command | Use Case |
|------|---------|----------|
| **User** (default) | `./install.sh` | Personal use, available everywhere |
| **System** | `./install.sh --system` | Shared machine, all users |
| **Project** | `./install.sh --project` | Project-specific, isolated setup |

### Install Options
```bash
./install.sh --no-rc           # Skip shell rc injection
./install.sh --cleanup-legacy  # Remove old installation
./install.sh --help            # Show all options
```

### Uninstall
```bash
./uninstall.sh
```

---

## First-Time Setup

### 1. Configure API Keys
```bash
ccm config
```

This opens `~/.ccm_config` in your editor. Add your API keys:

```bash
# Required for each provider you want to use
DEEPSEEK_API_KEY=sk-...
KIMI_API_KEY=...
GLM_API_KEY=...
QWEN_API_KEY=...
MINIMAX_API_KEY=...
ARK_API_KEY=...           # For Doubao/Seed
OPENROUTER_API_KEY=...    # For OpenRouter
CLAUDE_API_KEY=...        # Optional, for Claude API (vs subscription)
```

### 2. Verify Setup
```bash
ccm status    # Check current configuration
```

---

## Basic Usage

### Switch Provider (in current shell)
```bash
ccm glm global        # GLM global (default)
ccm glm china         # GLM China
ccm deepseek          # DeepSeek
ccm kimi global       # Kimi global
ccm kimi china        # Kimi China
ccm qwen global       # Qwen global
ccm minimax           # MiniMax
ccm seed              # Doubao/Seed
ccm claude            # Claude official
```

### Switch + Launch Claude Code
```bash
ccc glm global        # Switch to GLM global, then launch
ccc glm china         # Switch to GLM China, then launch
ccc open glm          # Via OpenRouter
```

### Check Status
```bash
ccm status             # Show current model and API key status
```

### Update Config
When model IDs change in new versions, update your config:
```bash
ccm update-config      # Update outdated model IDs to latest defaults
```

### Get Help
```bash
ccm help               # Show all commands
ccc                    # Show ccc usage (no args)
```

---

## Providers Reference

### Direct Providers (API Key Required)

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
ccm open              # Show help
ccm open claude       # Claude via OpenRouter
ccm open glm          # GLM via OpenRouter
ccm open kimi         # Kimi via OpenRouter
ccm open deepseek     # DeepSeek via OpenRouter
ccm open qwen         # Qwen via OpenRouter
ccm open minimax      # MiniMax via OpenRouter
ccm open stepfun      # StepFun via OpenRouter
ccm open sf-free      # StepFun free tier
```

**Available providers:** `claude`, `glm`, `kimi`, `deepseek`, `qwen`, `minimax`, `stepfun`

**Free tier:** `stepfun-free` or `sf-free` for StepFun's free model

---

## Advanced Features

### User-Level Settings (Highest Priority)
Write settings directly to `~/.claude/settings.json`. This overrides everything including environment variables and is useful when you have other tools (like Quotio) that also modify this file.

```bash
# Set provider at user level
ccm user glm global      # GLM global for all projects
ccm user glm china       # GLM China for all projects
ccm user deepseek        # DeepSeek for all projects
ccm user claude          # Claude official for all projects

# Reset to environment variable control
ccm user reset           # Remove ccm settings, use env vars instead
```

**When to use:**
- You have Quotio or another proxy that sets `~/.claude/settings.json`
- You want a persistent default that survives shell restarts
- Environment variables are being overridden by something else

### Project-Only Override
Override settings for a specific project (keeps global settings intact):

```bash
# In your project directory
ccm project glm global    # Use GLM for this project only
ccm project glm china     # Use GLM China for this project
ccm project reset         # Remove project override
```

This creates/removes `.claude/settings.local.json` in the current project.

---

## Configuration

### Priority Order (highest to lowest)
1. `~/.claude/settings.json` (env section) - User-level settings
2. `.claude/settings.local.json` - Project-level settings
3. `~/.ccm_config` file - **Always reloads on each ccm command**
4. Environment variables (only used if config value is a placeholder)

### Config File Location
```
~/.ccm_config
```

### Full Config Example
```bash
# API Keys (required for each provider)
DEEPSEEK_API_KEY=sk-...
KIMI_API_KEY=...
GLM_API_KEY=...
QWEN_API_KEY=...
MINIMAX_API_KEY=...
ARK_API_KEY=...
OPENROUTER_API_KEY=...
CLAUDE_API_KEY=...

# Model ID Overrides (optional)
DEEPSEEK_MODEL=deepseek-chat
KIMI_MODEL=kimi-k2.5
KIMI_CN_MODEL=kimi-k2.5
QWEN_MODEL=qwen3-max-2026-01-23
GLM_MODEL=glm-5
MINIMAX_MODEL=MiniMax-M2.5
SEED_MODEL=ark-code-latest
CLAUDE_MODEL=claude-sonnet-4-5-20250929
OPUS_MODEL=claude-opus-4-6
HAIKU_MODEL=claude-haiku-4-5-20251001
```

---

## Without Shell Function (Advanced)

If you installed with `--no-rc` or call `ccm` binary directly, use eval to apply env vars:

```bash
# Direct binary call requires eval
eval "$(ccm glm global)"

# Or run from source without installing
uv run ccm glm china
uv run ccc glm china     # Switch + launch
```

> **Note:** After normal installation (`./install.sh`), the shell function handles this automatically. Just run `ccm glm global` directly.

---

## Notes

- **7 env vars exported per provider**: `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`, `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL`
- **Claude official**: Uses your Claude Code subscription by default, or `CLAUDE_API_KEY` if set
- **OpenRouter**: Requires explicit `ccm open <provider>` command
- **Project override**: Only affects the current project via `.claude/settings.local.json`

---

## Contributing

Contributions are welcome! Here's how you can help:

### Report Issues
Found a bug or have a feature request? Please open an issue.

### Submit Code
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

### Development
```bash
git clone https://github.com/gameofdimension/claude-code-switch.git
cd claude-code-switch
uv run ccm --help    # Test locally without installing
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

This tool is inspired by the need to easily switch between AI providers while using Claude Code. Thanks to all contributors and the open-source community.
