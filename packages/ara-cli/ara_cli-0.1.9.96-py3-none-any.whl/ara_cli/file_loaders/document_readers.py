import os
from abc import ABC, abstractmethod
from typing import Tuple, Optional


class DocumentReader(ABC):
    """Abstract base class for document readers"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.base_dir = os.path.dirname(file_path)
    
    @abstractmethod
    def read(self, extract_images: bool = False) -> str:
        """Read document and optionally extract images"""
        pass
    
    def create_image_data_dir(self, extension_suffix: str) -> str:
        """
        Create data directory for images with file extension suffix to avoid conflicts.
        
        Returns:
            str: Path to images directory
        """
        file_name_with_ext = os.path.splitext(os.path.basename(self.file_path))[0] + f"_{extension_suffix}"
        data_dir = os.path.join(self.base_dir, f"{file_name_with_ext}.data")
        images_dir = os.path.join(data_dir, "images")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        return images_dir
    
    def save_and_describe_image(self, image_data: bytes, image_format: str, 
                               save_dir: str, image_counter: int) -> Tuple[str, str]:
        """
        Save image data and get its description from LLM.
        
        Returns:
            tuple: (relative_image_path, description)
        """
        from ara_cli.prompt_handler import describe_image
        
        # Save image
        image_filename = f"{image_counter}.{image_format}"
        image_path = os.path.join(save_dir, image_filename)
        
        with open(image_path, "wb") as image_file:
            image_file.write(image_data)
        
        # Get image description from LLM
        description = describe_image(image_path)
        
        # Get relative path
        relative_image_path = os.path.relpath(image_path, self.base_dir)
        
        return relative_image_path, description


class DocxReader(DocumentReader):
    """Reader for DOCX files"""
    
    def read(self, extract_images: bool = False) -> str:
        import docx
        
        doc = docx.Document(self.file_path)
        text_content = '\n'.join(para.text for para in doc.paragraphs)
        
        if not extract_images:
            return text_content
        
        from PIL import Image
        import io
        
        # Create data directory for images
        images_dir = self.create_image_data_dir("docx")
        
        # Extract and process images
        image_descriptions = []
        image_counter = 1
        
        for rel in doc.part.rels.values():
            if "image" in rel.reltype:
                image_data = rel.target_part.blob
                
                # Determine image format
                image = Image.open(io.BytesIO(image_data))
                image_format = image.format.lower()
                
                # Save and describe image
                relative_path, description = self.save_and_describe_image(
                    image_data, image_format, images_dir, image_counter
                )
                
                # Add formatted description to list
                image_description = f"\nImage: {relative_path}\n[{description}]\n"
                image_descriptions.append(image_description)
                
                image_counter += 1
        
        # Combine text content with image descriptions
        if image_descriptions:
            text_content += "\n\n### Extracted Images\n" + "\n".join(image_descriptions)
        
        return text_content


class PdfReader(DocumentReader):
    """Reader for PDF files"""
    
    def read(self, extract_images: bool = False) -> str:
        import pymupdf4llm
        
        if not extract_images:
            return pymupdf4llm.to_markdown(self.file_path, write_images=False)
        
        import fitz  # PyMuPDF
        
        # Create images directory
        images_dir = self.create_image_data_dir("pdf")
        
        # Extract text without images first
        text_content = pymupdf4llm.to_markdown(self.file_path, write_images=False)
        
        # Extract and process images
        doc = fitz.open(self.file_path)
        image_descriptions = []
        image_counter = 1
        
        for page_num, page in enumerate(doc):
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                # Extract image
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Save and describe image
                relative_path, description = self.save_and_describe_image(
                    image_bytes, image_ext, images_dir, image_counter
                )
                
                # Add formatted description to list
                image_description = f"\nImage: {relative_path}\n[{description}]\n"
                image_descriptions.append(image_description)
                
                image_counter += 1
        
        doc.close()
        
        # Combine text content with image descriptions
        if image_descriptions:
            text_content += "\n\n### Extracted Images\n" + "\n".join(image_descriptions)
        
        return text_content


class OdtReader(DocumentReader):
    """Reader for ODT files"""
    
    def read(self, extract_images: bool = False) -> str:
        import pymupdf4llm
        
        if not extract_images:
            return pymupdf4llm.to_markdown(self.file_path, write_images=False)
        
        import zipfile
        from PIL import Image
        import io
        
        # Create data directory for images
        images_dir = self.create_image_data_dir("odt")
        
        # Get text content
        text_content = pymupdf4llm.to_markdown(self.file_path, write_images=False)
        
        # Extract and process images from ODT
        image_descriptions = []
        image_counter = 1
        
        try:
            with zipfile.ZipFile(self.file_path, 'r') as odt_zip:
                # List all files in the Pictures directory
                picture_files = [f for f in odt_zip.namelist() if f.startswith('Pictures/')]
                
                for picture_file in picture_files:
                    # Extract image data
                    image_data = odt_zip.read(picture_file)
                    
                    # Determine image format
                    image = Image.open(io.BytesIO(image_data))
                    image_format = image.format.lower()
                    
                    # Save and describe image
                    relative_path, description = self.save_and_describe_image(
                        image_data, image_format, images_dir, image_counter
                    )
                    
                    # Add formatted description to list
                    image_description = f"\nImage: {relative_path}\n[{description}]\n"
                    image_descriptions.append(image_description)
                    
                    image_counter += 1
        except Exception as e:
            print(f"Warning: Could not extract images from ODT: {e}")
        
        # Combine text content with image descriptions
        if image_descriptions:
            text_content += "\n\n### Extracted Images\n" + "\n".join(image_descriptions)
        
        return text_content


class DocumentReaderFactory:
    """Factory for creating appropriate document readers"""
    
    @staticmethod
    def create_reader(file_path: str) -> Optional[DocumentReader]:
        """Create appropriate reader based on file extension"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        readers = {
            '.docx': DocxReader,
            '.pdf': PdfReader,
            '.odt': OdtReader
        }
        
        reader_class = readers.get(ext)
        if reader_class:
            return reader_class(file_path)
        
        return None