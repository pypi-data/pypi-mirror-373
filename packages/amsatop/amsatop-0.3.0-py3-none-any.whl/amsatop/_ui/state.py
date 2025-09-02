from dataclasses import dataclass
from enum import Enum
from typing import List, Literal

from amsatop._htop.htop import Htop
from amsatop._htop.process import Process


class ViewMode(Enum):
    PROCESSES = "processes"
    PRIORITIES = "priorities"
    HUP = "hup"

    @staticmethod
    def from_str(s: str) -> "ViewMode":
        for mode in ViewMode:
            if s == mode.value:
                return mode
        raise ValueError(f"Invalid ViewMode, can't convert it from string: {s}")


@dataclass
class UiState:
    __htop: Htop
    __mode: ViewMode = ViewMode.PROCESSES

    def change_view(
        self, mode: Literal["processes", "priorities", "hup"] | str
    ) -> None:
        self.__mode = ViewMode.from_str(mode)

    @property
    def processes(self) -> List[Process]:
        match self.__mode:
            case ViewMode.PROCESSES:
                return self.__htop.get_processes()
            case ViewMode.PRIORITIES:
                return self.__htop.get_priorities()
            case ViewMode.HUP:
                return self.__htop.get_hup()
            case _:
                raise NotImplementedError()
