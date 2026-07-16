#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd "$script_dir/.." && pwd -P)"
agents_skills="$HOME/.agents/skills"
claude_skills="$HOME/.claude/skills"
codex_skills="${CODEX_HOME:-$HOME/.codex}/skills"

sources=(
  "$repo_root/grill-me"
  "$repo_root/grill-walk"
  "$repo_root/grill-me-claude"
  "$repo_root/grill-walk"
)

destinations=(
  "$agents_skills/grill-me"
  "$agents_skills/grill-walk"
  "$claude_skills/grill-me"
  "$claude_skills/grill-walk"
)

legacy_codex_paths=(
  "$codex_skills/grill-me"
  "$codex_skills/grill-walk"
)

for source_path in "${sources[@]}"; do
  if [ ! -f "$source_path/SKILL.md" ]; then
    echo "Source skill does not exist: $source_path" >&2
    exit 1
  fi
done

for legacy_path in "${legacy_codex_paths[@]}"; do
  if [ -e "$legacy_path" ] || [ -L "$legacy_path" ]; then
    echo "Refusing to install while duplicate Codex-specific skill exists: $legacy_path" >&2
    echo "Back it up, remove it, and rerun this installer." >&2
    exit 1
  fi
done

for index in "${!destinations[@]}"; do
  source_path="${sources[$index]}"
  destination_path="${destinations[$index]}"
  if [ -L "$destination_path" ]; then
    existing_target="$(readlink "$destination_path")"
    if [ "$existing_target" != "$source_path" ]; then
      echo "Refusing to replace $destination_path: symlink targets $existing_target, expected $source_path" >&2
      exit 1
    fi
  elif [ -e "$destination_path" ]; then
    echo "Refusing to replace $destination_path: path exists and is not a symlink" >&2
    exit 1
  fi
done

for index in "${!destinations[@]}"; do
  source_path="${sources[$index]}"
  destination_path="${destinations[$index]}"
  if [ ! -L "$destination_path" ]; then
    mkdir -p "$(dirname "$destination_path")"
    ln -s "$source_path" "$destination_path"
  fi
done

echo "Installed canonical grill-me and grill-walk links for Codex and Claude."
