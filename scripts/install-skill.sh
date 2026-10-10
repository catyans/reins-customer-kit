#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: install-skill.sh --target /absolute/customer/repo --assistant codex|claude|both [--dry-run] [--force] [--uninstall]

Copies the same reins-integrate skill into the chosen repository:
  Codex:      .agents/skills/reins-integrate/
  Claude Code: .claude/skills/reins-integrate/

--dry-run only prints planned changes. Repeated installation is a no-op when
the target copy is identical. --force replaces a modified copy. --uninstall
removes only this skill directory; a modified copy requires --force.
EOF
}

target=''
assistant=''
dry_run=0
force=0
uninstall=0
while (($#)); do
  case "$1" in
    --target) target="${2:-}"; shift 2 ;;
    --assistant) assistant="${2:-}"; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    --force) force=1; shift ;;
    --uninstall) uninstall=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done

if [[ -z "$target" || ! -d "$target" ]]; then
  echo 'Target must be an existing repository directory.' >&2
  exit 2
fi
case "$assistant" in
  codex|claude|both) ;;
  *) echo 'Choose --assistant codex, claude, or both.' >&2; exit 2 ;;
esac

source_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../skills/reins-integrate" && pwd)"
target="$(cd "$target" && pwd -P)"
destinations=()
if [[ "$assistant" == codex || "$assistant" == both ]]; then
  destinations+=("$target/.agents/skills/reins-integrate")
fi
if [[ "$assistant" == claude || "$assistant" == both ]]; then
  destinations+=("$target/.claude/skills/reins-integrate")
fi

for destination in "${destinations[@]}"; do
  # A linked skills directory could send an install or uninstall outside the
  # requested repository, even when the destination itself looks local.
  relative="${destination#"$target"/}"
  IFS='/' read -r -a components <<< "$relative"
  current="$target"
  for component in "${components[@]}"; do
    current="$current/$component"
    if [[ -L "$current" ]]; then
      echo "Refusing a symlinked skill path: $current" >&2
      exit 3
    fi
  done
  if [[ -e "$destination" && "$force" -eq 0 ]] && ! diff -qr "$source_dir" "$destination" >/dev/null; then
    echo "Refusing to replace a modified skill: $destination (use --force)" >&2
    exit 3
  fi
done

for destination in "${destinations[@]}"; do
  if [[ "$uninstall" -eq 1 ]]; then
    [[ "$dry_run" -eq 1 ]] && echo "Would remove $destination" && continue
    if [[ -e "$destination" ]]; then rm -rf "$destination"; fi
    echo "Removed $destination"
  elif [[ -e "$destination" ]] && diff -qr "$source_dir" "$destination" >/dev/null; then
    echo "Already installed: $destination"
  elif [[ "$dry_run" -eq 1 ]]; then
    echo "Would install $destination"
  else
    mkdir -p "$(dirname "$destination")"
    if [[ -e "$destination" ]]; then rm -rf "$destination"; fi
    cp -R "$source_dir" "$destination"
    echo "Installed $destination"
  fi
done
