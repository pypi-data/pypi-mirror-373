# This file makes the client directory a Python package
"""
CUA Client - Computer Use Automation Client

A Python package for remote function execution and computer automation tasks
via WebSocket connections.
"""

from .remote_function_client import RemoteFunctionClient, RemoteFunctionRouter
from .computer_use import ComputerUseFunction
from .reset_windows import reset_cli
from .capture import ImageBatchRecorder, ScreenCaptureController

__version__ = "0.3.3.dev0"
__author__ = "168x Project"
__email__ = "admin@168x.com"

__all__ = [
    "RemoteFunctionClient",
    "RemoteFunctionRouter", 
    "ComputerUseFunction",
    "reset_cli",
    "ImageBatchRecorder",
    "ScreenCaptureController",
] 