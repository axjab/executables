#!/usr/bin/env sh

set -e

if command -v wl-copy >/dev/null 2>&1; then
    exec wl-copy
elif command -v xclip >/dev/null 2>&1; then
    exec xclip -selection clipboard
elif command -v xsel >/dev/null 2>&1; then
    exec xsel --clipboard --input
elif command -v pbcopy >/dev/null 2>&1; then
    exec pbcopy
elif command -v clip.exe >/dev/null 2>&1; then
    exec clip.exe
elif command -v clip >/dev/null 2>&1; then
    exec clip
else
    echo "Error: no supported clipboard program found." >&2
    exit 1
fi
