import base64
import os
from ara_cli.file_loaders.file_loader import FileLoader


class BinaryFileLoader(FileLoader):
    """Loads binary files (images)"""

    def load(
        self,
        file_path: str,
        mime_type: str,
        prefix: str = "",
        suffix: str = "",
        block_delimiter: str = "",
        extract_images: bool = False
    ) -> bool:
        """Load binary file as base64"""

        with open(file_path, 'rb') as file:
            file_content = file.read()

        base64_image = base64.b64encode(file_content).decode("utf-8")

        if block_delimiter:
            file_content = f"{block_delimiter}\n{file_content}\n{block_delimiter}"

        write_content = f"{prefix}![{os.path.basename(file_path)}](data:{mime_type};base64,{base64_image}){suffix}\n"

        with open(self.chat.chat_name, 'a', encoding='utf-8') as chat_file:
            chat_file.write(write_content)

        return True
