"""Shell export generation for CCM.

This module generates shell-compatible export statements that can be
eval'd by the parent shell to set environment variables.
"""

from dataclasses import dataclass

from ccm.core.config import Config, load_config
from ccm.core.providers import (
    OPENROUTER_PROVIDERS,
    get_openrouter_provider,
    get_provider,
    normalize_region,
)


@dataclass
class ExportConfig:
    """Configuration for export generation."""

    base_url: str | None = None
    auth_token_var: str | None = None
    model: str | None = None
    # Default model overrides
    sonnet_model: str | None = None
    opus_model: str | None = None
    haiku_model: str | None = None
    # User model overrides (from CLAUDE_MODEL, OPUS_MODEL, HAIKU_MODEL)
    override_model: str | None = None
    override_opus: str | None = None
    override_haiku: str | None = None
    # Whether to unset API_KEY (for official Claude)
    unset_api_key: bool = False


class ShellExportGenerator:
    """Generates shell-compatible export statements."""

    # All environment variables we manage
    ENV_VARS = [
        "ANTHROPIC_BASE_URL",
        "ANTHROPIC_API_URL",
        "ANTHROPIC_AUTH_TOKEN",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_MODEL",
        "ANTHROPIC_SMALL_FAST_MODEL",
        "ANTHROPIC_DEFAULT_SONNET_MODEL",
        "ANTHROPIC_DEFAULT_OPUS_MODEL",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL",
        "CLAUDE_CODE_SUBAGENT_MODEL",
        "API_TIMEOUT_MS",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
    ]

    def __init__(self, config: Config | None = None):
        """Initialize with optional config (will load if not provided)."""
        self._config = config

    @property
    def config(self) -> Config:
        """Get config, loading if necessary."""
        if self._config is None:
            self._config = load_config()
        return self._config

    def _escape(self, value: str) -> str:
        """Escape a value for shell export."""
        # Use single quotes and escape any single quotes
        return value.replace("'", "'\\''")

    def _config_source(self) -> str:
        """Generate the config source line."""
        return 'if [ -f "$HOME/.ccm_config" ]; then . "$HOME/.ccm_config" >/dev/null 2>&1; fi'

    def _unset_all(self) -> str:
        """Generate unset statement for all managed variables."""
        return f"unset {' '.join(self.ENV_VARS)}"

    def _export(self, name: str, value: str) -> str:
        """Generate an export statement."""
        escaped = self._escape(value)
        return f"export {name}='{escaped}'"

    def _export_var(self, name: str, var_name: str) -> str:
        """Generate an export statement using a variable reference."""
        return f"export {name}=\"${{{var_name}}}\""

    def _unset(self, name: str) -> str:
        """Generate an unset statement."""
        return f"unset {name}"

    def generate_exports(self, export_config: ExportConfig) -> str:
        """Generate complete export statement block."""
        lines: list[str] = []

        # Start with unset
        lines.append(self._unset_all())

        # Base URL
        if export_config.base_url:
            lines.append(self._export("ANTHROPIC_BASE_URL", export_config.base_url))

        # Source config file to get API keys
        lines.append(self._config_source())

        # Auth token
        if export_config.auth_token_var:
            lines.append(self._export_var("ANTHROPIC_AUTH_TOKEN", export_config.auth_token_var))

        # Unset API_KEY if needed (for official Claude)
        if export_config.unset_api_key:
            lines.append(self._unset("ANTHROPIC_API_URL"))
            lines.append(self._unset("ANTHROPIC_API_KEY"))

        # Model
        if export_config.model:
            lines.append(self._export("ANTHROPIC_MODEL", export_config.model))

        # Default models — overrides take priority
        sonnet_value = export_config.override_model or export_config.sonnet_model
        opus_value = export_config.override_opus or export_config.opus_model
        haiku_value = export_config.override_haiku or export_config.haiku_model

        if sonnet_value:
            lines.append(self._export("ANTHROPIC_DEFAULT_SONNET_MODEL", sonnet_value))
        if opus_value:
            lines.append(self._export("ANTHROPIC_DEFAULT_OPUS_MODEL", opus_value))
        if haiku_value:
            lines.append(self._export("ANTHROPIC_DEFAULT_HAIKU_MODEL", haiku_value))

        # Subagent model (same as main model by default)
        if export_config.model:
            lines.append(self._export("CLAUDE_CODE_SUBAGENT_MODEL", export_config.model))

        return "\n".join(lines)

    def generate_for_provider(
        self, provider_name: str, region: str | None = None, variant: str | None = None
    ) -> tuple[str, bool]:
        """Generate exports for a provider.

        Returns (export_string, success).
        If success is False, export_string contains an error message.
        """
        result = get_provider(provider_name)
        if result is None:
            return f"# Unknown provider: {provider_name}", False

        provider, canonical_name = result

        # Handle region-aware providers
        if provider.regions:
            try:
                region = normalize_region(region)
            except ValueError as e:
                return f"# {e}", False

            # Check API key
            if not self.config.is_set(provider.auth_token_var or ""):
                return f"# Please configure {provider.auth_token_var}", False

            base_url = provider.get_base_url(region)
            model_env = provider.get_model_env(region)
            model_default = provider.get_model_default(region)

            # Get model from config or use default
            model = self.config.get(model_env or "") or model_default

            return self.generate_exports(ExportConfig(
                base_url=base_url,
                auth_token_var=provider.auth_token_var,
                model=model,
                sonnet_model=model,
                opus_model=model,
                haiku_model=model,
            )), True

        # Handle variant providers (like seed)
        if provider.variants and variant:
            variant_lower = variant.lower()
            if variant_lower not in provider.variants:
                return f"# Unknown variant: {variant}\n# Valid variants: {', '.join(provider.variants.keys())}", False

            if not self.config.is_set(provider.auth_token_var or ""):
                return f"# Please configure {provider.auth_token_var}", False

            model = provider.variants[variant_lower]

            return self.generate_exports(ExportConfig(
                base_url=provider.base_url,
                auth_token_var=provider.auth_token_var,
                model=model,
                sonnet_model=model,
                opus_model=model,
                haiku_model=model,
            )), True

        # Standard provider
        if not self.config.is_set(provider.auth_token_var or ""):
            # Special case: Claude can work without API key (Pro subscription)
            if canonical_name == "claude":
                model = self.config.get("CLAUDE_MODEL") or provider.model_default or "claude-sonnet-4-5-20250929"
                opus_model = self.config.get("OPUS_MODEL") or "claude-opus-4-6"
                haiku_model = self.config.get("HAIKU_MODEL") or "claude-haiku-4-5-20251001"

                return self.generate_exports(ExportConfig(
                    base_url=provider.base_url,
                    auth_token_var=provider.auth_token_var,  # Will be set if available
                    model=model,
                    sonnet_model=model,
                    opus_model=opus_model,
                    haiku_model=haiku_model,
                    unset_api_key=True,
                )), True

            return f"# Please configure {provider.auth_token_var}", False

        model = self.config.get(provider.model_env or "") or provider.model_default
        if not model:
            return f"# No model configured for {provider_name}", False

        # For Claude, also get opus and haiku models
        sonnet_model = model
        opus_model = model
        haiku_model = model

        if canonical_name == "claude":
            opus_model = self.config.get("OPUS_MODEL") or "claude-opus-4-6"
            haiku_model = self.config.get("HAIKU_MODEL") or "claude-haiku-4-5-20251001"

        # Handle seed provider without variant
        if canonical_name == "seed" and not variant:
            model = self.config.get("SEED_MODEL") or provider.model_default or "ark-code-latest"

        return self.generate_exports(ExportConfig(
            base_url=provider.base_url,
            auth_token_var=provider.auth_token_var,
            model=model,
            sonnet_model=sonnet_model,
            opus_model=opus_model,
            haiku_model=haiku_model,
        )), True

    def get_env_for_provider(
        self, provider_name: str, region: str | None = None, variant: str | None = None
    ) -> tuple[dict[str, str], bool]:
        """Get resolved environment variables for a provider.

        Returns (env_dict, success).
        If success is False, env_dict may contain an 'error' key.
        """
        result = get_provider(provider_name)
        if result is None:
            return {"error": f"Unknown provider: {provider_name}"}, False

        provider, canonical_name = result
        env: dict[str, str] = {}

        # Handle region-aware providers
        if provider.regions:
            try:
                region = normalize_region(region)
            except ValueError as e:
                return {"error": str(e)}, False

            # Check API key
            if not self.config.is_set(provider.auth_token_var or ""):
                return {"error": f"Please configure {provider.auth_token_var}"}, False

            # Get the actual API key value
            auth_token = self.config.get(provider.auth_token_var or "")
            if not auth_token:
                return {"error": f"Please configure {provider.auth_token_var}"}, False

            base_url = provider.get_base_url(region)
            model_env = provider.get_model_env(region)
            model_default = provider.get_model_default(region)
            model = self.config.get(model_env or "") or model_default

            env["ANTHROPIC_BASE_URL"] = base_url
            env["ANTHROPIC_AUTH_TOKEN"] = auth_token
            env["ANTHROPIC_MODEL"] = model
            env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = model
            env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = model
            env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = model
            env["CLAUDE_CODE_SUBAGENT_MODEL"] = model

            return env, True

        # Handle variant providers (like seed)
        if provider.variants and variant:
            variant_lower = variant.lower()
            if variant_lower not in provider.variants:
                return {"error": f"Unknown variant: {variant}. Valid: {', '.join(provider.variants.keys())}"}, False

            if not self.config.is_set(provider.auth_token_var or ""):
                return {"error": f"Please configure {provider.auth_token_var}"}, False

            auth_token = self.config.get(provider.auth_token_var or "")
            if not auth_token:
                return {"error": f"Please configure {provider.auth_token_var}"}, False

            model = provider.variants[variant_lower]

            env["ANTHROPIC_BASE_URL"] = provider.base_url
            env["ANTHROPIC_AUTH_TOKEN"] = auth_token
            env["ANTHROPIC_MODEL"] = model
            env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = model
            env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = model
            env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = model
            env["CLAUDE_CODE_SUBAGENT_MODEL"] = model

            return env, True

        # Standard provider
        if not self.config.is_set(provider.auth_token_var or ""):
            # Special case: Claude can work without API key (Pro subscription)
            if canonical_name == "claude":
                model = self.config.get("CLAUDE_MODEL") or provider.model_default or "claude-sonnet-4-5-20250929"
                opus_model = self.config.get("OPUS_MODEL") or "claude-opus-4-6"
                haiku_model = self.config.get("HAIKU_MODEL") or "claude-haiku-4-5-20251001"

                env["ANTHROPIC_MODEL"] = model
                env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = model
                env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = opus_model
                env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = haiku_model
                env["CLAUDE_CODE_SUBAGENT_MODEL"] = model
                # Unset API key for official Claude
                env["__unset__"] = "ANTHROPIC_API_URL,ANTHROPIC_API_KEY"

                return env, True

            return {"error": f"Please configure {provider.auth_token_var}"}, False

        auth_token = self.config.get(provider.auth_token_var or "")
        if not auth_token and canonical_name != "claude":
            return {"error": f"Please configure {provider.auth_token_var}"}, False

        model = self.config.get(provider.model_env or "") or provider.model_default
        if not model:
            return {"error": f"No model configured for {provider_name}"}, False

        # For Claude, also get opus and haiku models
        sonnet_model = model
        opus_model = model
        haiku_model = model

        if canonical_name == "claude":
            opus_model = self.config.get("OPUS_MODEL") or "claude-opus-4-6"
            haiku_model = self.config.get("HAIKU_MODEL") or "claude-haiku-4-5-20251001"

        # Handle seed provider without variant
        if canonical_name == "seed" and not variant:
            model = self.config.get("SEED_MODEL") or provider.model_default or "ark-code-latest"

        if provider.base_url:
            env["ANTHROPIC_BASE_URL"] = provider.base_url
        if auth_token:
            env["ANTHROPIC_AUTH_TOKEN"] = auth_token
        env["ANTHROPIC_MODEL"] = model
        env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = sonnet_model
        env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = opus_model
        env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = haiku_model
        env["CLAUDE_CODE_SUBAGENT_MODEL"] = model

        return env, True

    def generate_for_openrouter(self, provider_name: str) -> tuple[str, bool]:
        """Generate exports for OpenRouter provider.

        Returns (export_string, success).
        """
        provider_config = get_openrouter_provider(provider_name)
        if provider_config is None:
            available = ", ".join(OPENROUTER_PROVIDERS.keys())
            return f"# Unknown OpenRouter provider: {provider_name}\n# Available: {available}", False

        if not self.config.is_set("OPENROUTER_API_KEY"):
            return "# Please configure OPENROUTER_API_KEY", False

        model = provider_config["model"]

        lines = [
            self._unset_all(),
            self._export("ANTHROPIC_BASE_URL", "https://openrouter.ai/api"),
            self._config_source(),
            self._export_var("ANTHROPIC_AUTH_TOKEN", "OPENROUTER_API_KEY"),
            self._unset("ANTHROPIC_API_KEY"),  # Avoid conflicts
            self._export("ANTHROPIC_MODEL", model),
            self._export("ANTHROPIC_DEFAULT_SONNET_MODEL", model),
            self._export("ANTHROPIC_DEFAULT_OPUS_MODEL", model),
            self._export("ANTHROPIC_DEFAULT_HAIKU_MODEL", model),
            self._export("CLAUDE_CODE_SUBAGENT_MODEL", model),
        ]

        return "\n".join(lines), True

    def get_env_for_openrouter(self, provider_name: str) -> tuple[dict[str, str], bool]:
        """Get resolved environment variables for OpenRouter provider.

        Returns (env_dict, success).
        """
        provider_config = get_openrouter_provider(provider_name)
        if provider_config is None:
            available = ", ".join(OPENROUTER_PROVIDERS.keys())
            return {"error": f"Unknown OpenRouter provider: {provider_name}. Available: {available}"}, False

        if not self.config.is_set("OPENROUTER_API_KEY"):
            return {"error": "Please configure OPENROUTER_API_KEY"}, False

        auth_token = self.config.get("OPENROUTER_API_KEY")
        if not auth_token:
            return {"error": "Please configure OPENROUTER_API_KEY"}, False

        model = provider_config["model"]

        env = {
            "ANTHROPIC_BASE_URL": "https://openrouter.ai/api",
            "ANTHROPIC_AUTH_TOKEN": auth_token,
            "ANTHROPIC_MODEL": model,
            "ANTHROPIC_DEFAULT_SONNET_MODEL": model,
            "ANTHROPIC_DEFAULT_OPUS_MODEL": model,
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": model,
            "CLAUDE_CODE_SUBAGENT_MODEL": model,
            "__unset__": "ANTHROPIC_API_KEY",  # Avoid conflicts
        }

        return env, True
