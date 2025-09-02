import logging
logger = logging.getLogger(__name__)

from pynput import keyboard
import time
import io
import base64
from PIL import Image
import pyautogui
from pydantic import BaseModel
import os

class FileUploadArgs(BaseModel):
    file_name: str
    file_base64: str

class FileUploadFunction():
    def __init__(self, upload_dir: str = "C:\\Users\\azureadmin\\Uploads"):      
        self.upload_dir = upload_dir
        # Ensure upload directory exists
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def __call__(self, **kwargs) -> dict:  
        args = FileUploadArgs(**kwargs)
        
        # Get the base name and extension
        name, ext = os.path.splitext(args.file_name)
        
        # Start with the original filename
        final_filename = args.file_name
        file_path = os.path.join(self.upload_dir, final_filename)
        
        # If file exists, find the next available number
        counter = 1
        while os.path.exists(file_path):
            final_filename = f"{name}({counter}){ext}"
            file_path = os.path.join(self.upload_dir, final_filename)
            counter += 1
        
        # Save the file
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(args.file_base64))
        
        logger.info(f"File saved as: {final_filename}")
        return {"file_path": file_path}