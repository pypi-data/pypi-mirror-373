from __future__ import annotations

import time
from typing import Tuple

import cv2
import numpy as np

from .config import BatchRecorderConfig
from .keylog import KeyLogger

__all__ = ["encode_frame"]


def encode_frame(
    ts: float,
    bgr: np.ndarray,
    cursor: Tuple[int, int],
    *,
    cfg: BatchRecorderConfig,
    key_logger: KeyLogger,
    show_click: bool = False,
):
    """Draw cursor & key-bar, return (filename, png_bytes)."""

    cx, cy = cursor
    if 0 <= cx < bgr.shape[1] and 0 <= cy < bgr.shape[0]:
        cv2.circle(bgr, (cx, cy), 8, (0, 0, 255), -1)
        if show_click:
            cv2.putText(bgr, "CLICK", (cx + 12, cy + 5), cfg.font, 0.8, (0, 255, 0), 2)

    h, w = bgr.shape[:2]
    canvas = np.zeros((h + cfg.bar_height, w, 3), dtype=np.uint8)
    canvas[:h] = bgr
    cv2.rectangle(canvas, (0, h), (w, h + cfg.bar_height), (0, 0, 0), -1)

    now = time.time()
    x = cfg.left_margin
    with key_logger._lock:  # pylint: disable=protected-access
        buf = list(key_logger.buffer)
    for tok, tok_ts in buf:
        if now - tok_ts > cfg.key_lifetime:
            continue
        col = (0, 255, 0) if now - tok_ts < cfg.green_seconds else (255, 255, 255)
        cv2.putText(canvas, tok, (x, h + cfg.bar_height - 10), cfg.font, cfg.font_scale, col, cfg.font_thickness)
        tw, _ = cv2.getTextSize(tok, cfg.font, cfg.font_scale, cfg.font_thickness)[0]
        x += tw + 5

    ok, png = cv2.imencode(".png", canvas, [int(cv2.IMWRITE_PNG_COMPRESSION), 1])
    if not ok:
        raise RuntimeError("Failed to encode image")
    fname = f"frame_{int(ts * 1000)}.png"
    return fname, png.tobytes() 