from __future__ import annotations

import io
import logging
import queue
import time
import zipfile
from collections import deque
from typing import Deque, List, Tuple

import numpy as np

from .config import BatchRecorderConfig
from .frame_grabber import FrameGrabber
from .keylog import KeyLogger, ClickTracker
from .overlay import encode_frame
from .work_item import WorkItem

__all__ = ["ImageBatchRecorder", "BatchRecorderConfig", "WorkItem"]

logger = logging.getLogger(__name__)

CACHING_INTERVAL = 0.10  # seconds between raw frame captures


class ImageBatchRecorder:
    """High-level coordinator that turns raw frames into backend batches."""

    def __init__(self, cfg: BatchRecorderConfig | None = None, *, work_queue: queue.Queue | None = None):
        self.cfg = cfg or BatchRecorderConfig()
        if not self.cfg.batch_endpoint:
            raise ValueError("BACKEND_API_BASE_URL not set – cannot send batches")
        if not self.cfg.secret_key:
            raise ValueError("SECRET_KEY not set – authentication is required")

        self._queue = work_queue  # may be None for direct send (tests)

        # Helpers ---------------------------------------------------------
        self._fg = FrameGrabber()
        self._kl = KeyLogger(event_callback=self._register_event); self._kl.start()
        self._ct = ClickTracker(self._kl, event_callback=self._register_event); self._ct.start()

        # Internal state --------------------------------------------------
        self._frame_cache: Deque[Tuple[float, np.ndarray, Tuple[int, int]]] = deque(maxlen=int(3 / CACHING_INTERVAL))
        self._event_queue: queue.Queue[float] = queue.Queue()
        self._batch: List[Tuple[str, bytes]] = []
        self._last_token_index = 0
        self._running = True
       
        self._last_periodic_ts: float = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def request_stop(self):
        """Signal the recorder loop to finish current batch and exit."""
        self._running = False

    def run(self):
        logger.info("ImageBatchRecorder started – endpoint: %s", self.cfg.batch_endpoint)

        try:
            while self._running:
                loop_start = time.time()
                try:
                    # 1) Capture raw frame ---------------------------------------------
                    raw = self._fg.grab()
                    self._frame_cache.append(raw)

                    # 2) Handle click / ENTER events ----------------------------------
                    event_frame_added = False
                    while not self._event_queue.empty():
                        evt_ts = self._event_queue.get_nowait()
                        selected = self._frame_before(evt_ts)
                        if selected:
                            fname, png = encode_frame(*selected, cfg=self.cfg, key_logger=self._kl, show_click=True)
                            self._batch.append((fname, png))
                            event_frame_added = True

                    # 3) Periodic capture ---------------------------------------------
                    now = time.time()
                    if event_frame_added:
                        self._last_periodic_ts = now
                    elif (now - self._last_periodic_ts) >= self.cfg.capture_interval:
                        fname, png = encode_frame(*raw, cfg=self.cfg, key_logger=self._kl)
                        self._batch.append((fname, png))
                        self._last_periodic_ts = now

                    # 4) Dispatch batch ------------------------------------------------
                    if len(self._batch) >= self.cfg.batch_size:
                        self._enqueue_batch()
                        self._batch.clear()

                    # 5) Throttle loop -------------------------------------------------
                    elapsed = time.time() - loop_start
                    time.sleep(max(0.0, CACHING_INTERVAL - elapsed))
                except Exception:
                    logger.exception("Recorder loop error – aborting")
                    self._running = False
                    break
        finally:
            if self._batch:
                self._enqueue_batch()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _frame_before(self, ts: float):
        for fts, bgr, cursor in reversed(self._frame_cache):
            if fts <= ts:
                return fts, bgr.copy(), cursor
        if self._frame_cache:
            fts, bgr, cursor = self._frame_cache[0]
            return fts, bgr.copy(), cursor
        return None

    def _register_event(self, ts: float):
        try:
            self._event_queue.put_nowait(ts)
        except queue.Full:
            logger.warning("Event queue full; dropping event at %s", ts)

    # ------------------------------------------------------------------
    # Batch helpers
    # ------------------------------------------------------------------

    def _enqueue_batch(self):
        if not self._queue:
            return self._send_direct()

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for fname, data in self._batch:
                zf.writestr(fname, data)
        buffer.seek(0)

        tokens_slice = self._kl._all_tokens[self._last_token_index :]
        self._last_token_index = len(self._kl._all_tokens)
        key_log_str = " ".join(tokens_slice)

        batch_id = int(time.time() * 1000)

        item = WorkItem(
            session_id=self.cfg.session_id,
            batch_id=batch_id,
            images_zip=buffer.getvalue(),
            key_logs=key_log_str,
        )
        try:
            self._queue.put(item, timeout=5)
            logger.info(
                "Enqueued batch s=%s b=%s (imgs=%d, keys=%d)",
                self.cfg.session_id,
                batch_id,
                len(self._batch),
                len(tokens_slice),
            )
        except queue.Full:
            logger.error("Work queue full – dropping batch")

    def _send_direct(self):
        import requests  # local import to avoid cost when queue is provided

        headers = {
            "Content-Type": "application/zip",
            "X-Secret-Key": self.cfg.secret_key,
            "X-Session-Id": str(self.cfg.session_id),
        }
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for fname, data in self._batch:
                zf.writestr(fname, data)
        buffer.seek(0)
        try:
            requests.post(self.cfg.batch_endpoint, data=buffer.getvalue(), headers=headers, timeout=30)
        except Exception as exc:
            logger.error("Direct send failed: %s", exc)
