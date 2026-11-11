### ☀ lumen — brightness without the monitor buttons

My proudest invention in this collection: one command to control brightness across a laptop panel and supported external monitors. Built around brightnessctl and ddcutil, with cached display discovery and rescanning when the detected connection state changes.

**One brightness setting. All supported screens.**  
[Read lumen →](bin/lumen)

### ● tty-notify — an alarm that finds my terminals

An attention signal for every accessible local terminal owned by the current user—including terminal tabs and SSH PTYs. A building block for my future alarm daemon.

Messages can carry a severity and a terminal bell. Optional duplicate suppression and rate limits keep repeated signals manageable. Delivery reaches the terminal; acknowledgment is still a separate problem.

[Read tty-notify →](bin/tty-notify)

### ▰ hud / hud2 — a little status-bar daydream

Experiments in making personal status visible in the terminal.

<details>
<summary>See the hud2 sketch</summary>

```text
water    ▕🬋🬋🬋🬋🬋🬋🬋🬋🬋
hunger   ▕🬋🬋🬋🬋🬋🬋🬋🬋🬋🬋🬋🬋🬋🬋
strength ▕🬋🬋🬋🬋🬋
```

</details>

[Read hud](bin/hud) · [Read hud2](bin/hud2)

### ✦ Small pleasures

| Script | A reason to open it |
| :-- | :-- |
| [emoji](bin/emoji) | A small parade of symbols to see how a terminal renders them. |
| [weather](bin/weather) | A glance outside, without leaving the terminal. |
| [txtin](bin/txtin) | Turn several lines of input into one line of text. |

<details>
<summary>Three tiny demos</summary>

Selected output from the supplied examples; shell prompts and unrelated fields omitted.

**emoji**
```text
😀😃😄  😅😆😂  🤣😊😇
🌈🌟✨  💖💙💚  ⚡
```

**weather** — sample output, not a live forecast
```text
☀️  +3°C
```

**txtin**
```text
Enter your text (press Ctrl+D to finish):
multi
line
input

multi line input
```

</details>

