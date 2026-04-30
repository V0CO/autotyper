# autotyper

Simulates human typing by replaying a text file through a virtual keyboard device (`evdev`/`UInput`). Includes randomized delays, occasional simulated typos with auto-correction, and random pauses between word bursts.

## Requirements

- Linux (requires `/dev/uinput` access)
- Python 3
- [`evdev`](https://pypi.org/project/evdev/)

```bash
pip install evdev
```

You may need to add your user to the `input` group or run with `sudo`:

```bash
sudo usermod -aG input $USER
```

## Usage

```bash
python3 autotyper.py <file.txt>
```

You have **3 seconds** after launching to switch to the target window before typing begins.

## Behaviour

| Feature | Detail |
|---|---|
| Per-character delay | `0.10 – 0.25 s` (random) |
| Typo simulation | Every 25–100 chars: types 3 random letters then deletes them |
| Word-burst pauses | Every 100–150 words: pauses `1–3 s` |

## Logs

Runtime output is written to both stdout and `autotyper.log` (excluded from git).
