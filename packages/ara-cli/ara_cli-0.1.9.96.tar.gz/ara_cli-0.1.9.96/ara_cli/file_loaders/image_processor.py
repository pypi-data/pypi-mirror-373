import os
import base64
import tempfile
import requests
from typing import Optional, Tuple
import re
from ara_cli.prompt_handler import describe_image


class ImageProcessor:
    """Handles image processing operations"""
    
    @staticmethod
    def process_base64_image(image_ref: str, base64_pattern: re.Pattern) -> Optional[Tuple[str, str]]:
        """Process base64 encoded image and return description"""
        base64_match = base64_pattern.match(image_ref)
        if not base64_match:
            return None
            
        image_format = base64_match.group(1)
        base64_data = base64_match.group(2)
        image_data = base64.b64decode(base64_data)
        
        # Create a temporary file to send to LLM
        with tempfile.NamedTemporaryFile(suffix=f'.{image_format}', delete=False) as tmp_file:
            tmp_file.write(image_data)
            tmp_file_path = tmp_file.name
        
        try:
            description = describe_image(tmp_file_path)
            return f"Image: (base64 embedded {image_format} image)\n[{description}]", None
        finally:
            os.unlink(tmp_file_path)
    
    @staticmethod
    def process_url_image(image_ref: str) -> Tuple[str, Optional[str]]:
        """Process image from URL and return description"""
        if not image_ref.startswith(('http://', 'https://')):
            return "", None
            
        try:
            response = requests.get(image_ref, timeout=10)
            response.raise_for_status()
            
            # Determine file extension from content-type
            content_type = response.headers.get('content-type', '')
            ext = ImageProcessor._get_extension_from_content_type(content_type, image_ref)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name
            
            try:
                description = describe_image(tmp_file_path)
                return f"Image: {image_ref}\n[{description}]", None
            finally:
                os.unlink(tmp_file_path)
                
        except Exception as e:
            error_msg = f"Could not download image: {str(e)}"
            return f"Image: {image_ref}\n[{error_msg}]", error_msg
    
    @staticmethod
    def process_local_image(image_ref: str, base_dir: str) -> Tuple[str, Optional[str]]:
        """Process local image file and return description"""
        if os.path.isabs(image_ref):
            local_image_path = image_ref
        else:
            local_image_path = os.path.join(base_dir, image_ref)
        
        if os.path.exists(local_image_path):
            description = describe_image(local_image_path)
            return f"Image: {image_ref}\n[{description}]", None
        else:
            error_msg = f"Image file not found"
            return f"Image: {image_ref}\n[{error_msg}]", f"Local image not found: {local_image_path}"
    
    @staticmethod
    def _get_extension_from_content_type(content_type: str, url: str) -> str:
        """Determine file extension from content type or URL"""
        if 'image/jpeg' in content_type:
            return '.jpg'
        elif 'image/png' in content_type:
            return '.png'
        elif 'image/gif' in content_type:
            return '.gif'
        else:
            return os.path.splitext(url)[1] or '.png'