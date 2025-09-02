from ara_cli.commands.command import Command
from ara_cli.file_loaders.file_loader import FileLoaderFactory
from ara_cli.file_loaders.binary_file_loader import BinaryFileLoader


class LoadCommand(Command):
    def __init__(
        self,
        chat_instance,
        file_path: str,
        prefix: str = "",
        suffix: str = "",
        block_delimiter: str = "",
        extract_images: bool = False,
        output=None
    ):
        self.chat = chat_instance
        self.file_path = file_path
        self.prefix = prefix
        self.suffix = suffix
        self.block_delimiter = block_delimiter
        self.extract_images = extract_images
        self.output = output or print

    def execute(self) -> bool:
        loader = FileLoaderFactory.create_loader(self.file_path, self.chat)

        if isinstance(loader, BinaryFileLoader):
            # Determine mime type for binary files
            file_name_lower = self.file_path.lower()
            mime_type = None
            for extension, mt in FileLoaderFactory.BINARY_TYPE_MAPPING.items():
                if file_name_lower.endswith(extension):
                    mime_type = mt
                    break

            if not mime_type:
                self.output(
                    f"Could not determine mime type for {self.file_path}")
                return False

            success = loader.load(
                self.file_path,
                mime_type=mime_type,
                prefix=self.prefix,
                suffix=self.suffix
            )
        elif hasattr(loader, 'load'):
            success = loader.load(
                self.file_path,
                prefix=self.prefix,
                suffix=self.suffix,
                block_delimiter=self.block_delimiter,
                extract_images=self.extract_images
            )
        else:
            return False

        if success:
            if self.extract_images and not isinstance(loader, BinaryFileLoader):
                self.output(
                    f"Loaded contents of file {self.file_path} with images extracted")
            else:
                self.output(f"Loaded contents of file {self.file_path}")
        return success
