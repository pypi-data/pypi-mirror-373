from __future__ import annotations

import ctypes
import os
import time
from typing import Tuple

import cv2
import mss
import numpy as np

__all__ = ["FrameGrabber"]

# ---------------------------------------------------------------------------
# DPI awareness (Windows) so cursor coordinates match MSS frame pixels
# ---------------------------------------------------------------------------

if os.name == "nt":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # type: ignore[attr-defined]
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()  # type: ignore[attr-defined]
        except Exception:
            pass


class _POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


_GetCursorPos = ctypes.windll.user32.GetCursorPos  # type: ignore[attr-defined]


class FrameGrabber:
    """Capture raw BGR frames and cursor position using MSS."""

    def __init__(self):
        # Monitor geometry will be detected lazily on first grab
        self._mon = None

    # ------------------------------------------------------------------

    def grab(self) -> Tuple[float, np.ndarray, Tuple[int, int]]:
        with mss.mss() as sct:
            if self._mon is None:
                # Cache primary monitor geometry once
                self._mon = sct.monitors[1]
            ts = time.time()
            rgbx = sct.grab(self._mon)
        bgr = cv2.cvtColor(np.array(rgbx), cv2.COLOR_BGRA2BGR)
        pt = _POINT()
        _GetCursorPos(ctypes.byref(pt))
        cx, cy = pt.x - self._mon["left"], pt.y - self._mon["top"]
        return ts, bgr, (cx, cy) 