"""
Logging configuration for the CUA client.

*   **Only a file handler** – no console handler is ever attached, so the
    task can run via *pythonw.exe* without spawning a console window.
*   Un‑caught exceptions are routed into the same file via
    ``sys.excepthook``.
*   **Console hiding** – If any library (like pyautogui) creates a console
    window after pythonw.exe starts, we immediately hide it using Windows API.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Final
import ctypes, platform

_LOG_DIR: Final = Path(r"C:\cua-management\logs")
_LOG_DIR.mkdir(parents=True, exist_ok=True)
_LOG_FILE: Final = _LOG_DIR / "client.log"

# ---------------------------------------------------------------------------
#  CRITICAL: Hide console window if one appears
#  This simple solution handles cases where libraries like pyautogui create
#  a console window even when running under pythonw.exe
# ---------------------------------------------------------------------------
if platform.system() == "Windows":
    try:
        GetConsoleWindow = ctypes.windll.kernel32.GetConsoleWindow  # type: ignore[attr-defined]
        ShowWindow = ctypes.windll.user32.ShowWindow  # type: ignore[attr-defined]
        SW_HIDE = 0
        hwnd = GetConsoleWindow()
        if hwnd:
            ShowWindow(hwnd, SW_HIDE)
    except Exception:
        # Best-effort; ignore if anything goes wrong (e.g. DLL missing)
        pass

# ---------------------------------------------------------------------------
#  Formatter – plain, timestamped lines suitable for tail & parsing
# ---------------------------------------------------------------------------
_plain_fmt = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def setup_logging(level: str = "DEBUG") -> None:  # noqa: D401 (imperative mood)
    """Configure global logging (file‑only; no console handler).

    Parameters
    ----------
    level : str, default "DEBUG"
        The minimum level for the *client* logger family.  Third‑party
        loggers stay at WARNING to avoid noise.
    """

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(logging.WARNING)  # suppress most third‑party chatter
    root.handlers.clear()

    # --- File handler -------------------------------------------------------
    file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(_plain_fmt)
    root.addHandler(file_handler)

    # --- cua_client.* logger (more verbose) --------------------------------
    client_logger = logging.getLogger("cua_client")
    client_logger.setLevel(numeric_level)
    client_logger.propagate = True  # still goes through root -> file handler

    # --- tame noisy libraries ---------------------------------------------
    for noisy in (
        "sqlalchemy",
        "sqlalchemy.engine",
        "sqlalchemy.engine.Engine",
    ):
        lg = logging.getLogger(noisy)
        lg.setLevel(logging.WARNING)
        lg.propagate = True

    client_logger.info(
        "Logging configured – client.log path: %s – level: %s",
        _LOG_FILE,
        level.upper(),
    )
    client_logger.debug("Debug logging enabled for cua_client components")

    # --- capture uncaught exceptions --------------------------------------
    def _log_excepthook(exc_type, exc_value, tb):  # type: ignore[pep8-naming]
        client_logger.exception("Uncaught exception", exc_info=(exc_type, exc_value, tb))

    sys.excepthook = _log_excepthook
