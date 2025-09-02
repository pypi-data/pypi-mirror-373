from ara_cli.file_loaders.document_reader import DocumentReaderFactory
from ara_cli.file_loaders.file_loader import FileLoader


class DocumentFileLoader(FileLoader):
    """Loads document files (PDF, DOCX, ODT)"""

    def load(
        self,
        file_path: str,
        prefix: str = "",
        suffix: str = "",
        block_delimiter: str = "```",
        extract_images: bool = False
    ) -> bool:
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
