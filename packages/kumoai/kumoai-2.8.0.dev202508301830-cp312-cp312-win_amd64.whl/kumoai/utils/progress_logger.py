import time
from typing import Any, List, Optional, Union

from rich.console import Console, ConsoleOptions, RenderResult
from rich.live import Live
from rich.padding import Padding
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text
from typing_extensions import Self


class ProgressLogger:
    def __init__(self, msg: str) -> None:
        self.msg = msg
        self.logs: List[str] = []

        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    @property
    def duration(self) -> float:
        assert self.start_time is not None
        if self.end_time is not None:
            return self.end_time - self.start_time
        return time.perf_counter() - self.start_time

    def log(self, msg: str) -> None:
        self.logs.append(msg)

    def __enter__(self) -> Self:
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.end_time = time.perf_counter()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.msg})'


class InteractiveProgressLogger(ProgressLogger):
    def __init__(
        self,
        msg: str,
        verbose: bool = True,
        refresh_per_second: int = 10,
    ) -> None:
        super().__init__(msg=msg)

        self.verbose = verbose
        self.refresh_per_second = refresh_per_second

        self._live: Optional[Live] = None
        self._exception: bool = False

    def __enter__(self) -> Self:
        super().__enter__()

        if self.verbose:
            self._live = Live(
                self,
                refresh_per_second=self.refresh_per_second,
                vertical_overflow='visible',
            )
            self._live.start()

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        super().__exit__(exc_type, exc_val, exc_tb)

        if exc_type is not None:
            self._exception = True

        if self._live is not None:
            self._live.update(self, refresh=True)
            self._live.stop()
            self._live = None

    def __rich_console__(
        self,
        console: Console,
        options: ConsoleOptions,
    ) -> RenderResult:

        table = Table.grid(padding=(0, 1))

        icon: Union[Text, Padding]
        if self._exception:
            style = 'red'
            icon = Text('❌', style=style)
        elif self.end_time is not None:
            style = 'green'
            icon = Text('✅', style=style)
        else:
            style = 'cyan'
            icon = Padding(Spinner('dots', style=style), (0, 1, 0, 0))

        title = Text.from_markup(
            f'{self.msg} ({self.duration:.2f}s)',
            style=style,
        )
        table.add_row(icon, title)

        for log in self.logs:
            table.add_row('', Text(f'↳ {log}', style='dim'))

        yield table
