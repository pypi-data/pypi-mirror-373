import os
from os.path import join, exists, isdir, dirname, basename
# from ara_cli.directory_searcher import DirectorySearcher


class DirectoryNavigator:
    def __init__(self, target_directory='ara'):
        self.target_directory = target_directory

    def exists(self, dir_path):
        """Check if a directory exists."""
        return exists(dir_path) and isdir(dir_path)

    def build_relative_path(self, relative_path):
        """Constructs a path relative to the target directory."""
        return join(os.getcwd(), relative_path)

    def navigate_to_target(self):
        """Navigates to target directory from current or parent directories. Returns original directory."""
        original_directory = os.getcwd()

        if basename(original_directory) == self.target_directory:
            return original_directory

        current_directory = original_directory
        while current_directory != dirname(current_directory):  # Ensure loop breaks at root
            potential_path = join(current_directory, self.target_directory)
            if self.exists(potential_path):
                os.chdir(potential_path)
                return original_directory
            current_directory = dirname(current_directory)

        # If the loop completes, the target directory was not found
        user_input = input(f"Unable to locate the '{self.target_directory}' directory. Do you want to create an 'ara' folder in the working directory? (y/N): ").strip().lower()

        if user_input == '' or user_input == 'y':
            ara_folder_path = join(original_directory, 'ara')
            os.makedirs(ara_folder_path, exist_ok=True)
            print(f"'ara' folder created at {ara_folder_path}")
            os.chdir(ara_folder_path)
            return original_directory
        else:
            print(f"Unable to locate the '{self.target_directory}' directory and user declined to create 'ara' folder.")
            sys.exit(0)

    def navigate_to_relative(self, relative_path):
        """Change directory to a path relative to the target directory."""
        if relative_path == self.target_directory:
            # If the desired directory is the target directory, ensure we're in it and exit early
            self.navigate_to_target()
            return

        if relative_path.startswith(self.target_directory + os.sep):
            relative_path = relative_path[len(self.target_directory)+1:]
        path = self.build_relative_path(relative_path)
        if self.exists(path):
            os.chdir(path)
        else:
            raise Exception(f"Unable to navigate to '{relative_path}' relative to the target directory.")

    # debug version
    # def get_ara_directory(self):
    #     """Returns the full path of the "ara" directory without navigating to it."""
    #     print("Starting search for the 'ara' directory...")

    #     # Use DirectorySearcher to find the ara directory
    #     ara_directory = DirectorySearcher.find_directory(self.target_directory, os.getcwd())

    #     if ara_directory:
    #         print(f"'ara' directory found at: {ara_directory}")
    #         return ara_directory

    #     print(f"Unable to locate the '{self.target_directory}' directory.")
    #     raise Exception(f"Unable to locate the '{self.target_directory}' directory.")
