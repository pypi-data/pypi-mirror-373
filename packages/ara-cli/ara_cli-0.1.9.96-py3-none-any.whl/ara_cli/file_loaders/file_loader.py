from abc import ABC, abstractmethod
from typing import Optional


class FileLoader(ABC):
    """Abstract base class for file loaders"""

    def __init__(self, chat_instance):
        self.chat = chat_instance

    @abstractmethod
    def load(self, file_path: str, **kwargs) -> bool:
        """Load file with specific implementation"""
        pass

    def add_prompt_tag_if_needed(self):
        """Add prompt tag to chat if needed"""
        self.chat.add_prompt_tag_if_needed(self.chat.chat_name)


class FileLoaderFactory:
    """Factory for creating appropriate file loaders"""
    BINARY_TYPE_MAPPING = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }

    DOCUMENT_TYPE_EXTENSIONS = [".docx", ".doc", ".odt", ".pdf"]

    @staticmethod
    def create_loader(file_name: str, chat_instance) -> Optional[FileLoader]:
        """Create appropriate loader based on file type"""
        from ara_cli.file_loaders.binary_file_loader import BinaryFileLoader
        from ara_cli.file_loaders.text_file_loader import TextFileLoader
        from ara_cli.file_loaders.document_file_loader import DocumentFileLoader

        file_name_lower = file_name.lower()

        # Check if it's a binary file
        for extension, mime_type in FileLoaderFactory.BINARY_TYPE_MAPPING.items():
            if file_name_lower.endswith(extension):
                return BinaryFileLoader(chat_instance)

        # Check if it's a document
        if any(file_name_lower.endswith(ext) for ext in FileLoaderFactory.DOCUMENT_TYPE_EXTENSIONS):
            return DocumentFileLoader(chat_instance)

        # Default to text file loader
        return TextFileLoader(chat_instance)
