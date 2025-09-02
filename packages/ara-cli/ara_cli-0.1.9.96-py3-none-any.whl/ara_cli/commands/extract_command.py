from ara_cli.commands.command import Command
from ara_cli.prompt_extractor import extract_responses
import os

class ExtractCommand(Command):
    def __init__(self, file_name, force=False, write=False, output=None):
        self.file_name = file_name
        self.force = force
        self.write = write
        self.output = output    # Callable for standard output (optional)

    def execute(self, *args, **kwargs):
        extract_responses(self.file_name, True, force=self.force, write=self.write)
        if self.output:
            self.output("End of extraction")
