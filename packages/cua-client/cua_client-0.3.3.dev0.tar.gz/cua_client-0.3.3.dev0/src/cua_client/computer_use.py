import logging
logger = logging.getLogger(__name__)

from pynput import keyboard
import time
import io
import base64
from PIL import Image
import pyautogui
from pydantic import BaseModel
from typing import Literal


WINDOWS_SCROLL_AMOUNT_PER_CLICK = int(120) # value for Windows VW machines

class ComputerUseArgs(BaseModel):
    action: str
    coordinate: tuple[int, int] | None = None
    text: str | None = None
    scroll_direction: Literal["up", "down"] | None = None
    scroll_amount: int | None = None
    duration: float | None = None

class ComputerUseFunction():
    def __init__(self, screenshot_delay: float = 1.0):        
        logger.info("Take initial screenshot to determine screen size")
        self.screen_size = _take_screenshot().size
        logger.info(f"Screen size: {self.screen_size}")    
        self.screenshot_delay = screenshot_delay 
    
    def __call__(self, **kwargs) -> dict:  
        args = ComputerUseArgs(**kwargs)
        
        if args.coordinate:
            args.coordinate = self._transform_to_native_coordinates(args.coordinate)
        
        pre_action_image_base64 = _get_screenshot_base64()
        
        logger.info(f"Executing action: {args.action}")
        
        match args.action:
            case "get_screen_size":
                return {"screen_size": self.screen_size}
            case "screenshot":
                return {"success": True, "pre_action_image_base64": pre_action_image_base64, "post_action_image_base64": pre_action_image_base64}
            case "mouse_move":
                pyautogui.moveTo(args.coordinate[0], args.coordinate[1])
            case "left_click":
                pyautogui.click(args.coordinate[0], args.coordinate[1], button='left')
            case "right_click":
                pyautogui.click(args.coordinate[0], args.coordinate[1], button='right')
            case "double_click":
                pyautogui.click(args.coordinate[0], args.coordinate[1], button='left', clicks=2)
            case "triple_click":
                pyautogui.click(args.coordinate[0], args.coordinate[1], button='left', clicks=3)
            case "scroll":
                # Ensure we have a sane default
                if args.scroll_amount is None:
                    args.scroll_amount = 1

                # Number of *wheel notches* to scroll – let pyautogui convert to OS-specific units.
                if args.scroll_direction == "up":
                    clicks = abs(args.scroll_amount) * WINDOWS_SCROLL_AMOUNT_PER_CLICK
                    logger.info(f"Scrolling up {clicks} clicks")
                elif args.scroll_direction == "down":
                    clicks = -abs(args.scroll_amount) * WINDOWS_SCROLL_AMOUNT_PER_CLICK
                    logger.info(f"Scrolling down {abs(clicks)} clicks")
                else:
                    logger.warning("scroll_direction not provided – defaulting to up")
                    clicks = abs(args.scroll_amount) * WINDOWS_SCROLL_AMOUNT_PER_CLICK

                # Move the mouse to the target location first to improve reliability across OSes
                if args.coordinate:
                    pyautogui.moveTo(args.coordinate[0], args.coordinate[1])

                # Perform the scroll. x,y left None so current pointer location is used.
                pyautogui.scroll(clicks)
            case "type":
                keyboard.Controller().type(args.text)
            case "key":
                execute_x_keysym_string(args.text)
            case "wait":
                time.sleep(args.duration)
            case _:
                logger.error(f"Unknown action: {args.action}")
                raise ValueError(f"Unknown action: {args.action}")
            
        # delay screenshot
        time.sleep(self.screenshot_delay)
        
        post_action_image_base64 = _get_screenshot_base64()
        
        return {
            "success": True,
            "pre_action_image_base64": pre_action_image_base64,
            "post_action_image_base64": post_action_image_base64
        }
    
    def _tool_screenshot(self) -> dict:
        screenshot = _take_screenshot()
        
        # Convert PIL Image to PNG bytes
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        png_bytes = buffer.getvalue()
        
        # Encode PNG bytes to base64
        base64_screenshot = base64.b64encode(png_bytes).decode("utf-8")
        
        return {"success": True, "base64_png": base64_screenshot}
    
    def _transform_to_native_coordinates(self, coordinate: tuple[int, int]) -> tuple[int, int]:
        # Get actual screen size
        actual_screen_size = pyautogui.size()
        actual_width, actual_height = actual_screen_size
        
        # If you need to transform coordinates based on screen size differences:
        scale_x = actual_width / self.screen_size[0]
        scale_y = actual_height / self.screen_size[1]
        transformed_x = int(coordinate[0] * scale_x)
        transformed_y = int(coordinate[1] * scale_y)
        return (transformed_x, transformed_y)
        
def _get_screenshot_base64() -> str:
    screenshot = _take_screenshot()
    
    # Convert PIL Image to PNG bytes
    buffer = io.BytesIO()
    screenshot.save(buffer, format='PNG')
    png_bytes = buffer.getvalue()
    
    # Encode PNG bytes to base64
    base64_screenshot = base64.b64encode(png_bytes).decode("utf-8")
    
    return base64_screenshot

def _take_screenshot(max_width: int = 1280, max_height: int = 800, save_path: str = None) -> Image.Image:
    # Take screenshot using pyautogui
    screenshot = pyautogui.screenshot()
    
    # Get current dimensions
    current_width, current_height = screenshot.size
    
    # Check if rescaling is needed
    if current_width > max_width or current_height > max_height:
        # Calculate scaling ratios for both dimensions
        width_ratio = max_width / current_width
        height_ratio = max_height / current_height
        
        # Use the smaller ratio to ensure both dimensions fit within bounds
        scale_ratio = min(width_ratio, height_ratio)
        
        # Calculate new dimensions
        new_width = int(current_width * scale_ratio)
        new_height = int(current_height * scale_ratio)
        
        # Resize the image while maintaining aspect ratio
        screenshot = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Save screenshot if path is provided
    if save_path:
        screenshot.save(save_path)
    
    return screenshot

# map X Keysym to pyautogui
keymap = {
    "cmd": "command",
    "opt": "option",
    # Common X-Keysym → PyAutoGUI translations
    "Page_Up": "pageup",
    "Page_Down": "pagedown",
    "Home": "home",
    "End": "end",
    "Left": "left",
    "Right": "right",
    "Up": "up",
    "Down": "down",
    "Return": "enter",
    "BackSpace": "backspace",
    "Escape": "esc",
    "Delete": "delete"
}

def x_keysym_string_to_pyautogui_keys(keysym_string):
    keys = keysym_string.split("+")
    for key in keys:
        if key in keymap:
            keys[keys.index(key)] = keymap[key]
    return keys

def execute_x_keysym_string(keysym_string):
    keys = x_keysym_string_to_pyautogui_keys(keysym_string)
    for k in keys:
        pyautogui.keyDown(k)
    for k in reversed(keys):
        pyautogui.keyUp(k)
