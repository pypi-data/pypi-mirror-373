import os
from typing import Dict


class DataPool:
    """
    Runtime abstraction for a mounted data pool at /var/runtime/datapool.
    """

    def __init__(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path \"{path}\" does not exist")

        if not os.path.isdir(path):
            raise NotADirectoryError(f"Path \"{path}\" is not a directory")

        self._path = path
        self._name = os.path.basename(path)

    @property
    def name(self) -> str:
        """
        Returns the name of the data pool.
        """
        return self._name

    @property
    def path(self) -> str:
        """
        Returns the path to the data pool.
        """
        return self._path

    def list_files(self) -> Dict[str, str]:
        """
        List all files in the data pool directory.
        """
        files = {}

        for file_name in os.listdir(self._path):
            file_path = os.path.join(self._path, file_name)
            if os.path.isfile(file_path):
                files[file_name] = file_path

        return files

    def open(self, name: str, mode: str = 'r'):
        """
        Open a file from the data pool by its name, supporting context manager usage.
        Usage: with data_pool.open("filename") as f:
        """
        file_path = os.path.join(self._path, name)

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File \"{name}\" not found in data pool")

        return open(file_path, mode)
