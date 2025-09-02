"""ScreenCaptureController – remote function to start/stop screen capture recorder.

Formerly `ImageBatchRecorderFunction`. Controls lifecycle of
`ImageBatchRecorder` running in a background thread.
"""

from __future__ import annotations

import logging
import os
import threading
from typing import Literal, Optional
import queue, time, threading, math

import requests
from pydantic import BaseModel, Field

from .image_batch_recorder import BatchRecorderConfig, ImageBatchRecorder

logger = logging.getLogger(__name__)


class ControllerArgs(BaseModel):
    action: Literal["start", "stop", "status"]
    interval: Optional[float] = Field(None, description="Seconds between captures")
    batch_size: Optional[int] = Field(None, description="Images per batch")
    session_id: Optional[int] = Field(None, description="Recording session ID")


class ScreenCaptureController:  # callable
    """Manage a single ImageBatchRecorder instance (start/stop/status)."""

    def __init__(self):
        self._recorder: Optional[ImageBatchRecorder] = None
        self._thread: Optional[threading.Thread] = None
        self._log_endpoint: str | None = None
        self._queue: queue.Queue | None = None
        self._sender_thread: Optional[threading.Thread] = None
        self._stop_sender = threading.Event()

    # --------------------------------------------------------------

    def __call__(self, **kwargs):
        args = ControllerArgs(**kwargs)
        if args.action == "start":
            return self._start(args)
        if args.action == "stop":
            return self._stop()
        if args.action == "status":
            return self._status()
        raise ValueError("Invalid action")

    # --------------------------------------------------------------

    def _start(self, args: ControllerArgs):
        if self._recorder and self._thread and self._thread.is_alive():
            return {"success": False, "message": "Recorder already running"}

        cfg = BatchRecorderConfig()
        if not cfg.api_base_url:
            return {"success": False, "message": "BACKEND_API_BASE_URL env var not set"}
        if args.interval is not None:
            cfg.capture_interval = args.interval
        if args.batch_size is not None:
            cfg.batch_size = args.batch_size
        if args.session_id is not None:
            cfg.session_id = args.session_id

        self._log_endpoint = cfg.log_endpoint

        # Queue and sender thread
        self._queue = queue.Queue(maxsize=int(os.getenv("CUA_QUEUE_MAXSIZE", "50")))
        self._stop_sender.clear()
        self._sender_thread = threading.Thread(target=self._sender_loop, daemon=True)
        self._sender_thread.start()

        self._recorder = ImageBatchRecorder(cfg, work_queue=self._queue)
        self._thread = threading.Thread(target=self._recorder.run, daemon=True)
        self._thread.start()
        logger.info("ScreenCaptureController started (endpoint=%s)", cfg.batch_endpoint)
        return {"success": True, "message": "Recorder started"}

    def _stop(self):
        if not self._recorder or not self._thread:
            return {"success": False, "message": "Recorder not running"}

        # Signal recorder to stop but don't block the RPC
        self._recorder.request_stop()

        # Spawn a daemon thread to finish cleanup in background so the
        # server call returns immediately and avoids 30-second timeout.
        threading.Thread(target=self._finalize_stop, daemon=True).start()

        return {"success": True, "message": "Stopping recorder"}

    # --------------------------------------------------------------
    # Internal helper to flush queue and shutdown threads
    # --------------------------------------------------------------

    def _finalize_stop(self):
        """Background cleanup after stop request."""
        try:
            self._thread.join()

            if self._queue:
                self._queue.join()

            self._stop_sender.set()
            if self._sender_thread:
                self._sender_thread.join()

            logger.info("Recorder fully stopped and queue flushed")

            # ------------------------------------------------------------------
            # Notify backend that capture is complete (handshake)
            # ------------------------------------------------------------------
            try:
                if self._recorder:
                    cfg = self._recorder.cfg
                    if cfg.api_base_url and cfg.session_id:
                        url = cfg.api_base_url.rstrip('/') + '/screenshare/recording-finished'
                        payload = {"session_id": cfg.session_id}
                        headers = {}
                        if cfg.secret_key:
                            headers["X-Secret-Key"] = cfg.secret_key

                        max_attempts = 5
                        backoff = 1.0
                        for attempt in range(1, max_attempts + 1):
                            try:
                                resp = requests.post(url, json=payload, headers=headers, timeout=10)
                                resp.raise_for_status()
                                logger.info("Sent recording-finished handshake (session %s)", cfg.session_id)
                                break
                            except Exception as exc:
                                if attempt == max_attempts:
                                    logger.warning("Failed to send recording-finished after %d attempts: %s", attempt, exc)
                                else:
                                    time.sleep(backoff)
                                    backoff = min(backoff * 2, 8)
            except Exception as exc:
                logger.warning("Unexpected error sending recording-finished: %s", exc)
        except Exception as exc:
            logger.warning("Finalize stop encountered error: %s", exc)
        finally:
            self._recorder = None
            self._thread = None
            self._sender_thread = None

    def _status(self):
        running = self._thread.is_alive() if self._thread else False
        return {"success": True, "running": running}

    # --------------------------------------------------------------
    # Sender loop
    # --------------------------------------------------------------

    def _sender_loop(self):
        """Continuously send WorkItems from the queue with retry & backoff."""
        secret_key = os.getenv("SECRET_KEY", "")
        base_backoff = float(os.getenv("CUA_SENDER_BASE_BACKOFF", "1"))
        max_attempts = int(os.getenv("CUA_SENDER_MAX_ATTEMPTS", "5"))

        while not self._stop_sender.is_set():
            try:
                item = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            success = self._send_work_item(item, secret_key)
            if success:
                self._queue.task_done()
                continue

            item.attempt += 1
            if item.attempt >= max_attempts:
                logger.error("Dropping batch s=%s b=%s after %d attempts", item.session_id, item.batch_id, item.attempt)
                self._queue.task_done()
                continue

            backoff = min(base_backoff * math.pow(2, item.attempt - 1), 60)
            time.sleep(backoff)
            self._queue.put(item)

    def _send_work_item(self, item, secret_key: str) -> bool:
        # Send key logs first (smaller payload) ---------------------------------
        try:
            log_headers = {"X-Secret-Key": secret_key} if secret_key else {}
            resp_logs = requests.post(
                self._recorder.cfg.log_endpoint,
                json={"session_id": item.session_id, "batch_id": item.batch_id, "logs": item.key_logs},
                headers=log_headers,
                timeout=15,
            )
            resp_logs.raise_for_status()
        except Exception as exc:
            logger.warning("Key log send failed: %s", exc)
            return False

        # Then send the ZIP ------------------------------------------------------
        headers = {
            "Content-Type": "application/zip",
            "X-Session-Id": str(item.session_id),
            "X-Batch-Id": str(item.batch_id),
        }
        if secret_key:
            headers["X-Secret-Key"] = secret_key

        try:
            resp_imgs = requests.post(
                self._recorder.cfg.batch_endpoint,
                data=item.images_zip,
                headers=headers,
                timeout=30,
            )
            resp_imgs.raise_for_status()
        except Exception as exc:
            logger.warning("Image batch send failed: %s", exc)
            return False

        logger.info("Sent batch s=%s b=%s (attempt %d)", item.session_id, item.batch_id, item.attempt)
        return True 