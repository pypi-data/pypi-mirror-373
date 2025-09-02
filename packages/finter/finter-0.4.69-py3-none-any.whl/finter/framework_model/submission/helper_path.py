import inspect
import os
import shutil

from finter.settings import logger


class FileManager:
    file_paths = []

    @classmethod
    def get_path(cls, relative_path):
        """
        Returns the full path of the file and stores it.

        Args:
        relative_path (str): Relative path of the file

        Returns:
        str: Full file path

        Raises:
        FileNotFoundError: If the file does not exist
        """
        base_path = os.path.dirname(os.path.abspath("__file__"))
        full_path = os.path.join(base_path, relative_path)

        if (
            not os.path.isfile(full_path)
            or base_path == "/locdisk/code/cc/framework/ops/submission"
        ):
            caller_frame = inspect.stack()[1]
            caller_file = caller_frame.filename
            base_path = os.path.dirname(os.path.abspath(caller_file))
            full_path = os.path.join(base_path, relative_path)

        if not os.path.isfile(full_path):
            logger.error(f"File does not exist: {full_path}")
            raise FileNotFoundError(f"File not found: {full_path}")
        cls.file_paths.append(full_path)
        return full_path

    @classmethod
    def copy_files_to(cls, destination_directory):
        """
        Copies files from all stored paths to the specified directory.
        If a file already exists in the destination, it will be overwritten.

        Args:
        destination_directory (str): Target directory to copy files to
        """
        if not os.path.exists(destination_directory):
            os.makedirs(destination_directory)

        for path in cls.file_paths:
            if os.path.isfile(path):
                dest_path = os.path.join(destination_directory, os.path.basename(path))
                if os.path.isfile(dest_path):
                    os.remove(dest_path)
                    logger.info(f"File replaced: {os.path.abspath(dest_path)}")
                shutil.copy(path, dest_path)
                logger.info(f"File copied from: {os.path.abspath(path)}")
                logger.info(f"File copied to: {os.path.abspath(dest_path)}")
            else:
                logger.error(f"File does not exist: {path}")

    @classmethod
    def clear_paths(cls):
        """
        Clears all stored file paths.
        """
        cls.file_paths = []


# Example usage
if __name__ == "__main__":
    try:
        # Get file paths
        file_path1 = FileManager.get_path("data/myfile1.csv")
        file_path2 = FileManager.get_path("data/myfile2.csv")

        # Print file paths
        print(file_path1)
        print(file_path2)

        # Copy files to specified directory
        FileManager.copy_files_to("/path/to/destination/directory")
    except FileNotFoundError as e:
        print(f"Error: {e}")
