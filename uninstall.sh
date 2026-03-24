#!/usr/bin/env bash
set -euo pipefail

# Uninstaller for Claude Code Model Switcher (CCM)
# - Uninstalls Python package (uv tool)
# - Removes ccm/ccc function blocks from shell rc files
# - Removes old bash wrappers and data dirs (legacy cleanup)

BEGIN_MARK="# >>> ccm function begin >>>"
END_MARK="# <<< ccm function end <<<"

log_info() {
  echo "==> $*"
}

log_warn() {
  echo "Warning: $*" >&2
}

remove_block() {
  local rc="$1"
  [[ -f "$rc" ]] || return 0
  if grep -qF "$BEGIN_MARK" "$rc"; then
    local tmp
    tmp="$(mktemp)"
    awk -v b="$BEGIN_MARK" -v e="$END_MARK" '
      $0==b {inblock=1; next}
      $0==e {inblock=0; next}
      !inblock {print}
    ' "$rc" > "$tmp" && mv "$tmp" "$rc"
    echo "🗑️  Removed ccm and ccc functions from: $rc"
  fi
}

needs_sudo() {
  local dir="$1"
  [[ -d "$dir" && ! -w "$dir" ]]
}

run_cmd() {
  local dir="$1"
  shift
  if needs_sudo "$dir"; then
    sudo "$@"
  else
    "$@"
  fi
}

find_candidate_bin_dirs() {
  local bins=()
  if [[ -n "${XDG_BIN_HOME:-}" ]]; then
    bins+=("$XDG_BIN_HOME")
  fi
  bins+=("$HOME/.local/bin" "$HOME/bin" "/usr/local/bin")
  if command -v brew >/dev/null 2>&1; then
    bins+=("$(brew --prefix)/bin")
  fi
  echo "${bins[*]}"
}

is_ccm_wrapper() {
  local path="$1"
  [[ -f "$path" ]] || return 1
  if [[ -L "$path" ]]; then
    local target
    target="$(readlink "$path" 2>/dev/null || true)"
    if [[ "$target" == *"/ccm.sh" || "$target" == *".ccm/ccm.sh" ]]; then
      return 0
    fi
  fi
  if grep -q "ccm error: missing" "$path" && grep -q "CCM_SH=" "$path"; then
    return 0
  fi
  return 1
}

is_ccc_wrapper() {
  local path="$1"
  [[ -f "$path" ]] || return 1
  if grep -q "ccc error: cannot find ccm CLI" "$path"; then
    return 0
  fi
  return 1
}

remove_wrappers() {
  local removed_any=false
  local bin_dirs
  bin_dirs=( $(find_candidate_bin_dirs) )
  local bin_dir
  for bin_dir in "${bin_dirs[@]:-}"; do
    [[ -d "$bin_dir" ]] || continue
    local ccm_path="$bin_dir/ccm"
    local ccc_path="$bin_dir/ccc"
    if is_ccm_wrapper "$ccm_path"; then
      run_cmd "$bin_dir" rm -f "$ccm_path"
      echo "🗑️  Removed ccm wrapper: $ccm_path"
      removed_any=true
    fi
    if is_ccc_wrapper "$ccc_path"; then
      run_cmd "$bin_dir" rm -f "$ccc_path"
      echo "🗑️  Removed ccc wrapper: $ccc_path"
      removed_any=true
    fi
  done

  if ! $removed_any; then
    log_warn "No PATH-installed ccm/ccc wrappers detected"
  fi
}

remove_data_dirs() {
  local user_dir="${XDG_DATA_HOME:-$HOME/.local/share}/ccm"
  local legacy_dir="$HOME/.ccm"
  local system_dir="/usr/local/share/ccm"

  if [[ -d "$user_dir" ]]; then
    rm -rf "$user_dir"
    echo "🗑️  Removed installed ccm assets at: $user_dir"
  fi

  if [[ -d "$legacy_dir" ]]; then
    rm -rf "$legacy_dir"
    echo "🗑️  Removed legacy ccm assets at: $legacy_dir"
  fi

  if [[ -d "$system_dir" ]]; then
    run_cmd "$system_dir" rm -rf "$system_dir"
    echo "🗑️  Removed system ccm assets at: $system_dir"
  fi
}

uninstall_python_package() {
  # Uninstall via uv tool
  if command -v uv >/dev/null 2>&1; then
    if uv tool list 2>/dev/null | grep -q "^ccm "; then
      uv tool uninstall ccm
      echo "🗑️  Uninstalled ccm via uv tool"
      return 0
    fi
  fi

  return 0
}

main() {
  log_info "Uninstalling CCM..."

  # Uninstall Python package
  uninstall_python_package

  # Remove rc function blocks from .zshrc and .bashrc
  local rc
  for rc in "$HOME/.zshrc" "$HOME/.bashrc"; do
    if [[ -f "$rc" ]]; then
      remove_block "$rc"
    fi
  done

  # Remove old bash wrappers (legacy)
  remove_wrappers

  # Remove data directories (legacy)
  remove_data_dirs

  echo ""
  echo "✅ Uninstall complete. Run 'source ~/.zshrc' or 'source ~/.bashrc' to reload your shell."
}

main "$@"
