#!/usr/bin/env python3

import hashlib
import colorsys
import random
import subprocess
import sys


def ansi_color(text, fg=None, bg=None, bold=False):
    codes = []

    if bold:
        codes.append("1")

    if fg is not None:
        r, g, b = fg
        codes += ["38", "2", str(r), str(g), str(b)]

    if bg is not None:
        r, g, b = bg
        codes += ["48", "2", str(r), str(g), str(b)]

    if not codes:
        return text

    return f"\033[{';'.join(codes)}m{text}\033[0m"


def random_rgb():
    return tuple(random.randint(70, 255) for _ in range(3))


def subject_rgb(subject):
    # SHA-256 gives deterministic avalanche behavior:
    # tiny subject changes produce unrelated colors.
    digest = hashlib.sha256(subject.encode("utf-8")).digest()

    # Use 24 bits for hue.
    hue = int.from_bytes(digest[0:3], "big") / 16777216.0

    # Extremely saturated and reasonably bright.
    saturation = 0.90 + digest[3] / 255.0 * 0.10
    value = 0.65 + digest[4] / 255.0 * 0.20

    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)

    return (
        round(r * 255),
        round(g * 255),
        round(b * 255),
    )


def contrast_fg(r, g, b):
    # Perceived brightness of the actual background.
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return (0, 0, 0) if luminance >= 150 else (255, 255, 255)


body = sys.stdin.buffer.read()

subject = "empty subject"

try:
    result = subprocess.run(
        ["jq", "-c", "."],
        input=body,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    formatted_body = result.stdout.decode("utf-8", errors="replace")

    subject_result = subprocess.run(
        [
            "jq",
            "-r",
            'if (.subject | type) == "string" then .subject else "empty subject" end',
        ],
        input=body,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    subject = subject_result.stdout.decode(
        "utf-8", errors="replace"
    ).strip()

    if not subject:
        subject = "empty subject"

except (subprocess.CalledProcessError, FileNotFoundError):
    print("not json", file=sys.stderr)
    formatted_body = body.decode("utf-8", errors="replace")


# Hash the original subject so case changes also produce different colors.
subject_bg = subject_rgb(subject)

# Display subject uppercase.
display_subject = subject.upper()

# Choose black/white foreground based on the colored background.
subject_fg = contrast_fg(*subject_bg)

subject_out = ansi_color(
    display_subject,
    fg=subject_fg,
    bg=subject_bg,
    bold=True,
)

# Payload gets an independent random foreground color.
body_rgb = random_rgb()

body_out = ansi_color(
    formatted_body.rstrip("\n"),
    fg=body_rgb,
)

sys.stdout.write(subject_out + ": " + body_out + "\n")
sys.stdout.flush()
