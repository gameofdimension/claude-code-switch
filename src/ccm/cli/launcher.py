"""Launcher module for CCM (ccc command).

This module implements the 'ccc' command that switches to a provider
and launches Claude Code.
"""

import os
import subprocess
import sys

from rich.console import Console

from ccm.core.config import load_config
from ccm.core.exports import ShellExportGenerator
from ccm.core.providers import get_provider, normalize_region

console = Console(stderr=True)


def main():
    """Main entry point for ccc command."""
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)

    args = sys.argv[1:]
    model = args[0]
    remaining_args = args[1:]

    # Handle open mode
    if model == "open":
        if len(args) < 2:
            console.print("[red]Usage: ccc open <provider> [claude-options][/red]")
            sys.exit(1)
        open_provider = args[1]
        remaining_args = args[2:]
        switch_and_launch_openrouter(open_provider, remaining_args)
        return

    # Check if it's a known model
    result = get_provider(model)

    if result is None:
        console.print(f"[red]❌ Unknown model: {model}[/red]")
        console.print("[yellow]Run 'ccc' without arguments to see available models.[/yellow]")
        sys.exit(1)

    # Switch to provider and launch
    region_or_variant = None
    if remaining_args and not remaining_args[0].startswith("-"):
        # Check if it's a region or variant
        provider_config, _ = result
        if provider_config.regions:
            try:
                region_or_variant = normalize_region(remaining_args[0])
                remaining_args = remaining_args[1:]
            except ValueError:
                pass
        elif provider_config.variants:
            if remaining_args[0].lower() in provider_config.variants:
                region_or_variant = remaining_args[0].lower()
                remaining_args = remaining_args[1:]

    switch_and_launch(model, region_or_variant, remaining_args)


def show_usage():
    """Display usage information."""
    console.print("""
[bold]Usage:[/bold] ccc <model> [region|variant] [claude-options]
       ccc open <provider> [claude-options]

[bold]Examples:[/bold]
  ccc deepseek                              # Launch with DeepSeek
  ccc open kimi                             # Launch with OpenRouter (kimi)
  ccc kimi china                            # Launch with Kimi (China region)
  ccc glm --dangerously-skip-permissions    # Pass options to Claude Code

[bold]Available models:[/bold]
  Official: deepseek, glm, kimi, qwen, seed|doubao, claude, minimax
  OpenRouter: open <provider>
""")


def apply_env(env: dict[str, str]):
    """Apply environment variables from resolved dict."""
    # First, unset managed variables
    for var in ShellExportGenerator.ENV_VARS:
        os.environ.pop(var, None)

    # Apply new values
    for key, value in env.items():
        if key == "__unset__":
            # Handle special unset directive
            for var in value.split(","):
                os.environ.pop(var.strip(), None)
        else:
            os.environ[key] = value


def switch_and_launch(model: str, region: str | None, claude_args: list[str]):
    """Switch to provider and launch Claude Code."""
    config = load_config()
    generator = ShellExportGenerator(config)

    env, success = generator.get_env_for_provider(model, region)

    if not success:
        error_msg = env.get("error", "Unknown error")
        console.print(f"[red]❌ {error_msg}[/red]")
        sys.exit(1)

    # Apply environment variables to current process
    apply_env(env)

    console.print()
    console.print(f"[green]🚀 Launching Claude Code...[/green]")
    console.print(f"   [blue]Model:[/blue] {os.environ.get('ANTHROPIC_MODEL', '(unset)')}")
    console.print(f"   [blue]Base URL:[/blue] {os.environ.get('ANTHROPIC_BASE_URL', 'Default (Anthropic)')}")
    console.print()

    # Launch Claude Code
    launch_claude(claude_args)


def switch_and_launch_openrouter(provider: str, claude_args: list[str]):
    """Switch to OpenRouter provider and launch Claude Code."""
    config = load_config()
    generator = ShellExportGenerator(config)

    env, success = generator.get_env_for_openrouter(provider)

    if not success:
        error_msg = env.get("error", "Unknown error")
        console.print(f"[red]❌ {error_msg}[/red]")
        sys.exit(1)

    # Apply environment variables to current process
    apply_env(env)

    console.print()
    console.print(f"[green]🚀 Launching Claude Code with OpenRouter ({provider})...[/green]")
    console.print(f"   [blue]Model:[/blue] {os.environ.get('ANTHROPIC_MODEL', '(unset)')}")
    console.print()

    # Launch Claude Code
    launch_claude(claude_args)


def launch_claude(args: list[str]):
    """Launch Claude Code CLI."""
    # Check if claude CLI exists
    try:
        subprocess.run(["claude", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("[red]❌ 'claude' CLI not found.[/red]")
        console.print("[yellow]Install it first: npm install -g @anthropic-ai/claude-code[/yellow]")
        sys.exit(127)

    # Launch claude with arguments
    try:
        if args:
            os.execvp("claude", ["claude"] + args)
        else:
            os.execvp("claude", ["claude"])
    except OSError as e:
        console.print(f"[red]❌ Failed to launch Claude Code: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
