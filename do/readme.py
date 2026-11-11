#!/usr/bin/env python3
"""Build README from an explicit template, curated Markdown, and bin/Git facts."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import html
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]

def git(root, *args):
    try:
        p = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                           text=True, check=False)
        return p.stdout.strip() if p.returncode == 0 else ""
    except FileNotFoundError:
        return ""

def scan(root):
    directory = root / "bin"
    if not directory.is_dir():
        raise ValueError("bin/ is missing; run in your repository")
    entries = []
    for path in sorted(directory.iterdir()):
        if path.name.startswith(".") or path.is_symlink() or not path.is_file():
            continue
        data = path.read_bytes()
        # Only inspect bytes; never run scripts, including --help.
        line = data.split(b"\n", 1)[0].decode("utf-8", "replace")
        language = "other"
        if line.startswith("#!"):
            try:
                words = shlex.split(line[2:])
                if words:
                    language = Path(words[0]).name
                    if language == "env":
                        language = next((w for w in words[1:] if not w.startswith("-") and "=" not in w), "other")
            except ValueError:
                pass
        language = "python" if language.startswith("python") else language
        stamp = git(root, "log", "-1", "--format=%ct", "--", "bin/" + path.name)
        updated = datetime.fromtimestamp(int(stamp), timezone.utc).strftime("%Y-%m-%d") if stamp.isdigit() else None
        entries.append(dict(name=path.name, executable=bool(path.stat().st_mode & 0o111),
                            size=len(data), lines=len(data.splitlines()), language=language,
                            updated=updated, epoch=int(stamp) if stamp.isdigit() else 0))
    return entries

def link(name):
    return "[" + html.escape(name).replace("|", "&#124;").replace("[", "&#91;").replace("]", "&#93;") + "](bin/" + quote(name, safe="") + ")"

def statistics(entries):
    executable = sum(e["executable"] for e in entries)
    out = ["| In the collection | |", "| :-- | --: |",
           f"| Files in bin/ | **{len(entries)}** |",
           f"| Executable files | **{executable}** |"]
    known = [e for e in entries if e.get("size") is not None]
    if known:
        largest = sorted(known, key=lambda e: (-e["size"], e["name"]))[0]
        out += [f'| Largest by bytes | {link(largest["name"])} · {largest["size"]:,} B |',
                f'| Total source lines | {sum(e["lines"] for e in known):,} |']
    else:
        out += ["| Largest file / source lines | Available after local scan |"]
    languages = Counter(e.get("language", "unknown") for e in entries)
    if entries:
        out += ["", "**Interpreters:** " + " · ".join(f"{html.escape(k)} {v}" for k,v in sorted(languages.items()))]
    recent = sorted((e for e in entries if e.get("updated")), key=lambda e: (-e["epoch"], e["name"]))[:5]
    out += ["", "**Recently committed**", ""]
    if recent:
        out += [f'- {link(e["name"])} — {e["updated"]}' for e in recent]
    else:
        out += ["Git dates will appear here when commit history is available."]
    out += ["", "<sub>Counts cover regular, non-hidden files directly in bin/; symlinks are excluded. "
            "Recency uses the latest commit touching each current path, in UTC—not checkout timestamps. "
            "Sizes and line counts reflect the current working tree.</sub>"]
    return "\n".join(out)

def render(root, entries):
    sources = root / "docs" / "readme"
    sections = {name: (sources / (name + ".md")).read_text() for name in ("intro", "highlights", "install")}
    sections["maintainer"] = (root / "docs" / "maintainer.md").read_text()
    sections["stats"] = statistics(entries)
    sections["catalog"] = "\n".join([
        "| Command | |", "| :-- | :-- |",
        *[f'| {link(e["name"])} | {"Executable" if e["executable"] else "Not executable"} |' for e in entries]])
    template = (sources / "template.md").read_text()
    def replace(match):
        key = match.group(1)
        if key not in sections:
            raise ValueError(f"unknown template slot: {key}")
        return sections[key].strip()
    return re.sub(r"{{\s*([a-z_]+)\s*}}", replace, template).rstrip() + "\n"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, help="default: ROOT/README.md")
    parser.add_argument("--check", action="store_true", help="exit 1 if output is missing or stale; do not write")
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / "README.md"
    try:
        entries = scan(root)
        entries = sorted(entries, key=lambda e: e["name"])
        result = render(root, entries)
        if args.check:
            return 0 if output.is_file() and output.read_text() == result else 1
        # Do not replace a symlink or leave half-written Markdown on failure.
        if output.is_symlink():
            raise ValueError("output must not be a symlink")
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent,
                                             prefix=".readme-", delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(result)
            temporary.chmod(0o644)
            temporary.replace(output)
        finally:
            if temporary:
                temporary.unlink(missing_ok=True)
        print(f"Built {output}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"readme: {error}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())

