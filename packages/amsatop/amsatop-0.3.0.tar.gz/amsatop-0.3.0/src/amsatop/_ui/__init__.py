from amsatop._htop.htop import Htop
from amsatop._htop.htop_mock import HtopMock
from amsatop._ui.tui import HtopTUI


def run_ui(htop: Htop = None, refresh: int = 2) -> None:
    """
    Given an instance of htop, run the tui interface.
    By default, if no parameter is given, it launches the HtopMock implementation.

    :param htop: An instance of your htop implementation
    :param refresh: The seconds between each table refresh, 2 by default
    """
    if htop is None:
        htop = HtopMock()
    app = HtopTUI(htop=htop, refresh_seconds=refresh)
    app.run()


__all__ = ["run_ui"]
