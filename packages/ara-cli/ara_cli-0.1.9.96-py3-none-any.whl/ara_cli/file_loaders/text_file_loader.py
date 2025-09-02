import os
import re
import base64
import tempfile
from typing import Optional, Tuple
import requests
from charset_normalizer import from_path
from ara_cli.prompt_handler import describe_image
from ara_cli.file_loaders.file_loader import FileLoader


class TextFileLoader(FileLoader):
    """Loads text files"""
    def load(self, file_path: str, prefix: str = "", suffix: str = "",
             block_delimiter: str = "", extract_images: bool = False, **kwargs) -> bool:
        """Load text file with optional markdown image extraction"""

        is_md_file = file_path.lower().endswith('.md')

        if is_md_file and extract_images:
            reader = MarkdownReader(file_path)
            file_content = reader.read(extract_images=True)
        else:
            # Use charset-normalizer to detect encoding
            encoded_content = from_path(file_path).best()
            if not encoded_content:
                print(f"Failed to detect encoding for {file_path}")
                return False
            file_content = str(encoded_content)

        if block_delimiter:
            file_content = f"{block_delimiter}\n{file_content}\n{block_delimiter}"

        write_content = f"{prefix}{file_content}{suffix}\n"

        with open(self.chat.chat_name, 'a', encoding='utf-8') as chat_file:
            chat_file.write(write_content)

        return True


class MarkdownReader:
    """Handles markdown file reading with optional image extraction"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.base_dir = os.path.dirname(file_path)
        self.image_processor = ImageProcessor()

    def read(self, extract_images: bool = False) -> str:
        """Read markdown file and optionally extract/describe images"""
        with open(self.file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        if not extract_images:
            return content

        return self._process_images(content)

    def _process_images(self, content: str) -> str:
        """Process all images in markdown content"""
        # Pattern to match markdown images: ![alt text](url or path)
        image_pattern = re.compile(r'!\[([^\]]*)\]\(([^\)]+)\)')
        base64_pattern = re.compile(r'data:image/([^;]+);base64,([^)]+)')

        # Process each image reference
        for match in image_pattern.finditer(content):
            image_ref = match.group(2)
            replacement = self._process_single_image(image_ref, base64_pattern)

            if replacement:
                content = content.replace(match.group(0), replacement, 1)

        return content

    def _process_single_image(self, image_ref: str, base64_pattern: re.Pattern) -> Optional[str]:
        """Process a single image reference"""
        try:
            # Try base64 first
            result = self.image_processor.process_base64_image(
                image_ref, base64_pattern)
            if result:
                return result[0]

            # Try URL
            result, error = self.image_processor.process_url_image(image_ref)
            if result:
                if error:
                    print(f"Warning: {error}")
                return result

            # Try local file
            result, error = self.image_processor.process_local_image(
                image_ref, self.base_dir)
            if error:
                print(f"Warning: {error}")
            return result

        except Exception as e:
            print(f"Warning: Could not process image {image_ref}: {e}")
            return None


class ImageProcessor:
    """Handles image processing operations"""

    @staticmethod
    def process_base64_image(
        image_ref: str,
        base64_pattern: re.Pattern
    ) -> Optional[Tuple[str, str]]:
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
            ext = ImageProcessor._get_extension_from_content_type(
                content_type, image_ref)

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
