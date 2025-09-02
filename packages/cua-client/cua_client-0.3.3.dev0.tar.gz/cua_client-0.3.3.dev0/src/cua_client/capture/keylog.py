from __future__ import annotations

import time
import threading
import logging
from collections import deque
from typing import Deque, Tuple, List, Callable

from pynput import keyboard, mouse
from pynput.keyboard import Key, KeyCode

__all__ = ["KeyLogger", "ClickTracker"]

logger = logging.getLogger(__name__)


class KeyLogger:
    """Collect keyboard tokens and expose them for on-screen overlay & backend."""

    def __init__(
        self,
        *,
        maxlen: int = 100,
        debounce: float = 0.05,
        event_callback: Callable[[float], None] | None = None,
    ):
        self._buf: Deque[Tuple[str, float]] = deque(maxlen=maxlen)
        self._debounce = debounce
        self._lock = threading.Lock()
        self._shift = self._ctrl = self._alt = False
        self._last_time: dict[str, float] = {}
        self._all_tokens: List[str] = []
        self._event_cb = event_callback

        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            daemon=True,
        )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def start(self):
        if not self._listener.is_alive():
            self._listener.start()
            logger.debug("KeyLogger started")

    @property
    def buffer(self) -> Deque[Tuple[str, float]]:
        return self._buf

    def full_log_string(self) -> str:
        return " ".join(self._all_tokens)

    def add_token(self, token: str):
        now = time.time()
        with self._lock:
            self._buf.append((token, now))
            self._all_tokens.append(token)

    # ------------------------------------------------------------------
    # Listener callbacks
    # ------------------------------------------------------------------

    def _on_press(self, k):  # noqa: C901
        with self._lock:
            if k in (Key.shift, Key.shift_l, Key.shift_r):
                self._shift = True
                return
            if k in (Key.ctrl, Key.ctrl_l, Key.ctrl_r):
                self._ctrl = True
                return
            if k in (Key.alt, Key.alt_l, Key.alt_r):
                self._alt = True
                return

            tok = self._fmt(k)
            if not tok:
                return

            if self._ctrl or self._alt:
                mods: List[str] = []
                if self._ctrl:
                    mods.append("CTRL")
                if self._alt:
                    mods.append("ALT")
                tok = f"<{'+'.join(mods)}+{tok.strip('<>').upper()}>"

            now = time.time()
            if tok in self._last_time and now - self._last_time[tok] < self._debounce:
                return

            # Let recorder know *before* we add ENTER so that it grabs the frame
            if tok == "<ENTER>" and self._event_cb:
                try:
                    self._event_cb(now)
                except Exception:  # pragma: no cover – never break logging
                    logger.exception("event_callback failed in KeyLogger")

            self._last_time[tok] = now
            self._buf.append((tok, now))
            self._all_tokens.append(tok)

    def _on_release(self, k):
        with self._lock:
            if k in (Key.shift, Key.shift_l, Key.shift_r):
                self._shift = False
            elif k in (Key.ctrl, Key.ctrl_l, Key.ctrl_r):
                self._ctrl = False
            elif k in (Key.alt, Key.alt_l, Key.alt_r):
                self._alt = False

    # ------------------------------------------------------------------

    def _fmt(self, k):  # noqa: C901
        if isinstance(k, KeyCode):
            c = k.char
            if c is None:
                return None
            if c == " ":
                return "<SPACE>"
            if c == "\t":
                return "<TAB>"
            if c in ("\n", "\r"):
                return "<ENTER>"
            if c.isprintable():
                return c.upper() if self._shift and c.isalpha() else c
            if self._ctrl and ord(c) < 32:
                return chr(ord(c) + 64)
            return f"<{ord(c)}>"
        if isinstance(k, Key):
            name = k.name.upper()
            return name if len(name) == 1 else f"<{name}>"
        return str(k).upper()


class ClickTracker:
    """Lightweight mouse-click detector that feeds the KeyLogger."""

    def __init__(
        self,
        key_logger: KeyLogger,
        *,
        event_callback: Callable[[float], None] | None = None,
    ):
        self._kl = key_logger
        self._event_cb = event_callback
        self._last_click = 0.0
        self._listener = mouse.Listener(on_click=self._on_click, daemon=True)

    # ------------------------------------------------------------------

    def start(self):
        if not self._listener.is_alive():
            self._listener.start()
            logger.debug("ClickTracker started")

    def _on_click(self, _x, _y, _button, pressed):
        """Mouse callback (Windows).

        We trigger only on the *press* portion of the click to avoid duplicate
        frames when the listener later emits the matching release event.
        """

        if not pressed:
            return

        ts = time.time()
        # Debounce press/release race (extremely small, but safe):
        if (ts - self._last_click) < 0.05:
            return

        self._last_click = ts

        if self._event_cb:
            try:
                self._event_cb(ts)
            except Exception:
                logger.exception("event_callback failed in ClickTracker")

        # Add token after the event so the pre-click frame doesn't include it
        self._kl.add_token("<CLICK>")

    # ------------------------------------------------------------------

    def recently_clicked(self, window: float = 1.0) -> bool:
        return (time.time() - self._last_click) < window 