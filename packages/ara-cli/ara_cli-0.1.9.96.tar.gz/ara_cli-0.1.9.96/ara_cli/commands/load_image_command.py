from ara_cli.commands.command import Command
from ara_cli.file_loaders.binary_file_loader import BinaryFileLoader


class LoadImageCommand(Command):
    def __init__(
        self,
        chat_instance,
        file_path: str,
        mime_type: str,
        prefix: str = "",
        suffix: str = "",
        output=None
    ):
        self.chat = chat_instance
        self.file_path = file_path
        self.mime_type = mime_type
        self.prefix = prefix
        self.suffix = suffix
        self.output = output or print

    def execute(self) -> bool:
        loader = BinaryFileLoader(self.chat)
        success = loader.load(
            self.file_path,
            mime_type=self.mime_type,
            prefix=self.prefix,
            suffix=self.suffix
        )

        if success:
            self.output(f"Loaded image file {self.file_path}")

        return success
