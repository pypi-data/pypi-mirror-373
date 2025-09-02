import logging
logger = logging.getLogger(__name__)

from pynput import keyboard
import time
import shlex
from pydantic import BaseModel

from cua_client.computer_use import execute_x_keysym_string, _get_screenshot_base64


class SendKeysArgs(BaseModel):
    input_sequence: str

class SendKeysFunction():
    def __init__(self, screenshot_delay: float = 1.0):        
        self.screenshot_delay = screenshot_delay 
    
    def __call__(self, **kwargs) -> dict:  
        args = SendKeysArgs(**kwargs)
        
        # Use shlex.split so quoted strings like "John Doe" are treated as single arguments
        tokens = shlex.split(args.input_sequence)

        if len(tokens) % 2 != 0:
            logger.error("Invalid sequence provided: %s", args.input_sequence)
            raise ValueError("Invalid input_sequence provided")

        controller = keyboard.Controller()

        for cmd, arg in zip(tokens[::2], tokens[1::2]):
            if cmd == "type":
                controller.type(arg)
            elif cmd == "key":
                execute_x_keysym_string(arg)
            else:
                logger.warning(f"Unknown command '{cmd}' in sequence; Allowed commands are 'type' and 'key'.")
                
            # delay so that UI can process the input
            time.sleep(0.25)
        
        # delay screenshot
        time.sleep(self.screenshot_delay)
        post_action_image_base64 = _get_screenshot_base64()
        
        return {
            "success": True,
            "post_action_image_base64": post_action_image_base64
        }
