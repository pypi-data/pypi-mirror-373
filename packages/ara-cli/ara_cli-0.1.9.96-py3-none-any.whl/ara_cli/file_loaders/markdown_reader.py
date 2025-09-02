import os
import re
from typing import Optional
from charset_normalizer import from_path
from ara_cli.file_loaders.image_processor import ImageProcessor


class MarkdownReader:
    """Handles markdown file reading with optional image extraction"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.base_dir = os.path.dirname(file_path)
        self.image_processor = ImageProcessor()

    def read(self, extract_images: bool = False) -> str:
        """Read markdown file and optionally extract/describe images"""
        # Detect and use the most appropriate encoding
        result = from_path(self.file_path).best()
        if not result:
            print(f"Failed to detect encoding for {self.file_path}")
            return ""
        content = str(result)

        if not extract_images:
            return content

        return self._process_images(content)

    def _process_images(self, content: str) -> str:
        """Process all images in markdown content"""
        # Pattern to match markdown images: ![alt text](url or path)
        image_pattern = re.compile(r"!\[([^\]]*)\]\(([^\)]+)\)")
        base64_pattern = re.compile(r"data:image/([^;]+);base64,([^)]+)")

        # Process each image reference
        for match in image_pattern.finditer(content):
            image_ref = match.group(2)
            replacement = self._process_single_image(image_ref, base64_pattern)

            if replacement:
                content = content.replace(match.group(0), replacement, 1)

        return content

    def _process_single_image(
        self, image_ref: str, base64_pattern: re.Pattern
    ) -> Optional[str]:
        """Process a single image reference"""
        try:
            # Try base64 first
            result = self.image_processor.process_base64_image(
                image_ref, base64_pattern
            )
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
                image_ref, self.base_dir
            )
            if error:
                print(f"Warning: {error}")
            return result

        except Exception as e:
            print(f"Warning: Could not process image {image_ref}: {e}")
            return None
