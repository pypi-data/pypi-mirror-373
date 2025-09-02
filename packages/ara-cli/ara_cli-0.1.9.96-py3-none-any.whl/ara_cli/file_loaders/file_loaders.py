import os
import base64
from abc import ABC, abstractmethod
from typing import Optional
from ara_cli.file_loaders.markdown_reader import MarkdownReader
from ara_cli.file_loaders.document_readers import DocumentReaderFactory


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


class TextFileLoader(FileLoader):
    """Loads text files"""
    
    def load(self, file_path: str, prefix: str = "", suffix: str = "", 
             block_delimiter: str = "", extract_images: bool = False) -> bool:
        """Load text file with optional markdown image extraction"""
        
        is_md_file = file_path.lower().endswith('.md')
        
        if is_md_file and extract_images:
            reader = MarkdownReader(file_path)
            file_content = reader.read(extract_images=True)
        else:
            with open(file_path, 'r', encoding='utf-8', errors="replace") as file:
                file_content = file.read()
        
        if block_delimiter:
            file_content = f"{block_delimiter}\n{file_content}\n{block_delimiter}"
        
        write_content = f"{prefix}{file_content}{suffix}\n"
        
        with open(self.chat.chat_name, 'a', encoding='utf-8') as chat_file:
            chat_file.write(write_content)
            
        return True


class BinaryFileLoader(FileLoader):
    """Loads binary files (images)"""
    
    def load(self, file_path: str, mime_type: str, prefix: str = "", suffix: str = "") -> bool:
        """Load binary file as base64"""
        
        with open(file_path, 'rb') as file:
            file_content = file.read()
            
        base64_image = base64.b64encode(file_content).decode("utf-8")
        write_content = f"{prefix}![{os.path.basename(file_path)}](data:{mime_type};base64,{base64_image}){suffix}\n"
        
        with open(self.chat.chat_name, 'a', encoding='utf-8') as chat_file:
            chat_file.write(write_content)
            
        return True


class DocumentFileLoader(FileLoader):
    """Loads document files (PDF, DOCX, ODT)"""
    
    def load(self, file_path: str, prefix: str = "", suffix: str = "", 
             block_delimiter: str = "```", extract_images: bool = False) -> bool:
        """Load document file with optional image extraction"""
        
        reader = DocumentReaderFactory.create_reader(file_path)
        
        if not reader:
            print("Unsupported document type.")
            return False
        
        text_content = reader.read(extract_images=extract_images)
        
        if block_delimiter:
            text_content = f"{block_delimiter}\n{text_content}\n{block_delimiter}"
        
        write_content = f"{prefix}{text_content}{suffix}\n"
        
        with open(self.chat.chat_name, 'a', encoding='utf-8') as chat_file:
            chat_file.write(write_content)
            
        return True


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