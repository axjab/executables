#!/usr/bin/env bash

set -euo pipefail

if [[ $# -eq 0 ]]; then
    echo "Usage: e <file>..."
    exit 1
fi

editor="${EDITOR:-vi}"

needs_sudo=()

for file in "$@"; do
    # Existing file
    if [[ -e "$file" ]]; then
        if [[ ! -w "$file" ]]; then
            needs_sudo+=("$file")
        fi
        continue
    fi

    # New file: check whether its parent directory is writable.
    dir=$(dirname -- "$file")
    [[ -d "$dir" ]] || dir=$(dirname -- "$(realpath -m -- "$file")")

    if [[ ! -w "$dir" ]]; then
        needs_sudo+=("$file")
    fi
done

use_sudo=false

if ((${#needs_sudo[@]} > 0)); then
    echo "The following files require elevated privileges to edit:"
    printf '  %s\n' "${needs_sudo[@]}"
    echo

    if gum confirm "Edit privileged files with sudo?"; then
        use_sudo=true
    fi
fi

for file in "$@"; do
    if $use_sudo; then
        if printf '%s\0' "${needs_sudo[@]}" | grep -Fxzq -- "$file"; then
            sudo "$editor" "$file"
            continue
        fi
    fi

    "$editor" "$file"
done
