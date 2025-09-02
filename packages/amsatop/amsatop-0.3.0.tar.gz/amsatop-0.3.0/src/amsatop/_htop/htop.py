import os
from abc import ABC, abstractmethod
from typing import List

from amsatop._htop.process import Process


class Htop(ABC):
    """
    Abstract base class representing a simplified version of the Unix 'htop' utility.

    This class defines the interface for interacting with system process information.
    It is designed to be subclassed by students or developers who will provide
    concrete implementations for the defined methods.

    Attributes:
        proc_folder (str): Path to the directory containing process information.
            Defaults to "/proc", but can be overridden by setting the "PROC_FOLDER"
            environment variable. You should *allways* use this variable and not "/proc".
    """

    proc_folder: str

    def __init__(self, proc_folder: str = os.getenv("PROC_FOLDER", "/proc")) -> None:
        """
        Initialize the Htop base class with a specified process folder.

        :param proc_folder: Path to the proc filesystem used to read process information.
                           If not provided, it defaults to the value of the "PROC_FOLDER"
                           environment variable, or "/proc" if the variable is unset.
        """
        super().__init__()
        self.proc_folder = proc_folder

    @abstractmethod
    def get_processes(self) -> List[Process]:
        """
        Retrieve all system processes, without the priority field

        :return: A list of Process objects representing all running processes.
        :raises NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError("Prac-2.1")

    @abstractmethod
    def get_priorities(self) -> List[Process]:
        """
        Retrieve all system processes along with their scheduling priorities.

        :return: A list of Process objects with priority information.
        :raises: NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError("Prac-2.2")

    @abstractmethod
    def get_hup(self) -> List[Process]:
        """
        Retrieve processes that are eligible to ignore the SIGHUP signal.

        :return: A list of Process objects that ignore the SIGHUP signal.
        :raises: NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError("Prac-2.3")
