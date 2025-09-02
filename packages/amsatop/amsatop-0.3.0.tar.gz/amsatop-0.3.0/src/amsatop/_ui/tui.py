import pyfiglet
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Footer, Header, Static

from amsatop._htop.htop import Htop
from amsatop._ui.state import UiState


class HtopTUI(App[None]):
    BINDINGS = [
        Binding("p", "toggle_view('processes')", "Processes", show=True),
        Binding("r", "toggle_view('priorities')", "Priorities", show=True),
        Binding("h", "toggle_view('hup')", "Ignored hup", show=True),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, htop: Htop, refresh_seconds: int):
        super().__init__()
        self.state = UiState(htop)
        self.refresh_seconds = refresh_seconds

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(pyfiglet.figlet_format("AMSA25-26"), id="ascii")
        yield DataTable(id="process_table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(selector=DataTable)
        table.add_columns("PID", "Command", "Type", "Priority")
        self.update_table()
        self.set_interval(interval=self.refresh_seconds, callback=self.update_table)

    def update_table(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for process in self.state.processes:
            priority = str(process.priority) if process.priority is not None else "N/A"
            table.add_row(
                str(process.pid), process.command, process.type.value, priority
            )

    def action_toggle_view(self, view: str) -> None:
        self.state.change_view(mode=view)
        self.update_table()
