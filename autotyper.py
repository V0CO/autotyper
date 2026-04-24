import sys
import time
import random
import logging
from evdev import UInput, ecodes as e

STARTUP_DELAY = 3  # seconds to switch to your target window

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("autotyper.log"),
    ],
)
log = logging.getLogger(__name__)

# Build character -> (keycode, needs_shift) map
CHAR_MAP = {}

for c in "abcdefghijklmnopqrstuvwxyz":
    CHAR_MAP[c] = (getattr(e, f"KEY_{c.upper()}"), False)

for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    CHAR_MAP[c] = (getattr(e, f"KEY_{c}"), True)

for d in "0123456789":
    CHAR_MAP[d] = (getattr(e, f"KEY_{d}"), False)

CHAR_MAP.update({
    " ":  (e.KEY_SPACE,      False),
    "\n": (e.KEY_ENTER,      False),
    "\t": (e.KEY_TAB,        False),
    ".":  (e.KEY_DOT,        False),
    ",":  (e.KEY_COMMA,      False),
    ";":  (e.KEY_SEMICOLON,  False),
    "'":  (e.KEY_APOSTROPHE, False),
    "/":  (e.KEY_SLASH,      False),
    "\\": (e.KEY_BACKSLASH,  False),
    "[":  (e.KEY_LEFTBRACE,  False),
    "]":  (e.KEY_RIGHTBRACE, False),
    "-":  (e.KEY_MINUS,      False),
    "=":  (e.KEY_EQUAL,      False),
    "`":  (e.KEY_GRAVE,      False),
    "!":  (e.KEY_1,          True),
    "@":  (e.KEY_2,          True),
    "#":  (e.KEY_3,          True),
    "$":  (e.KEY_4,          True),
    "%":  (e.KEY_5,          True),
    "^":  (e.KEY_6,          True),
    "&":  (e.KEY_7,          True),
    "*":  (e.KEY_8,          True),
    "(":  (e.KEY_9,          True),
    ")":  (e.KEY_0,          True),
    "_":  (e.KEY_MINUS,      True),
    "+":  (e.KEY_EQUAL,      True),
    "{":  (e.KEY_LEFTBRACE,  True),
    "}":  (e.KEY_RIGHTBRACE, True),
    ":":  (e.KEY_SEMICOLON,  True),
    '"':  (e.KEY_APOSTROPHE, True),
    "<":  (e.KEY_COMMA,      True),
    ">":  (e.KEY_DOT,        True),
    "?":  (e.KEY_SLASH,      True),
    "|":  (e.KEY_BACKSLASH,  True),
    "~":  (e.KEY_GRAVE,      True),
})

ALL_KEYS = set(CHAR_MAP.values())
CAPABILITIES = {e.EV_KEY: list({k for k, _ in CHAR_MAP.values()}) + [e.KEY_LEFTSHIFT, e.KEY_BACKSPACE]}

def send_char(ui, char):
    if char not in CHAR_MAP:
        log.warning(f"No mapping for char {repr(char)}, skipping.")
        return
    keycode, shift = CHAR_MAP[char]
    if shift:
        ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
        ui.syn()
    ui.write(e.EV_KEY, keycode, 1)
    ui.syn()
    ui.write(e.EV_KEY, keycode, 0)
    ui.syn()
    if shift:
        ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
        ui.syn()

def send_backspace(ui):
    ui.write(e.EV_KEY, e.KEY_BACKSPACE, 1)
    ui.syn()
    ui.write(e.EV_KEY, e.KEY_BACKSPACE, 0)
    ui.syn()

def type_file(path, delay=0.10):
    log.info(f"Loading file: {path}")
    try:
        with open(path, "r") as f:
            text = f.read()
    except FileNotFoundError:
        log.error(f"File not found: {path}")
        sys.exit(1)

    log.info(f"Loaded {len(text)} characters. Base delay: {delay}s (will vary 0.10–0.5s per char).")
    log.info(f"Starting in {STARTUP_DELAY} seconds — switch to your target window now...")
    time.sleep(STARTUP_DELAY)

    with UInput(CAPABILITIES, name="autotyper") as ui:
        log.info("Typing started.")
        word_count = 0
        next_break_at = random.randint(100, 150)
        chars_since_typo = 0
        next_typo_at = random.randint(25, 50)
        for i, char in enumerate(text):
            # Simulate typo: type 3 random letters then delete them
            if chars_since_typo >= next_typo_at:
                log.debug(f"Simulating typo at char index {i}")
                typo_chars = [random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(3)]
                for tc in typo_chars:
                    send_char(ui, tc)
                    time.sleep(random.uniform(0.10, 0.5))
                for _ in range(3):
                    send_backspace(ui)
                    time.sleep(random.uniform(0.10, 0.5))
                chars_since_typo = 0
                next_typo_at = random.randint(25, 50)
            try:
                send_char(ui, char)
            except Exception as ex:
                log.warning(f"Error at index {i} char {repr(char)}: {ex}")
            chars_since_typo += 1
            time.sleep(random.uniform(0.10, 0.5))
            if char == " ":
                word_count += 1
                if word_count >= next_break_at:
                    pause = random.uniform(1, 3)
                    log.info(f"Taking a {pause:.1f}s break after {word_count} words.")
                    time.sleep(pause)
                    next_break_at = word_count + random.randint(100, 150)

    log.info("Typing complete.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        log.error("Usage: python3 autotyper.py <file.txt> [delay_seconds]")
        sys.exit(1)
    delay = float(sys.argv[2]) if len(sys.argv) >= 3 else 0.10
    type_file(sys.argv[1], delay)

