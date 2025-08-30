import datetime
import logging
import logging.handlers
import os
import time
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any

from rich.console import RenderableType
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.style import Style
from rich.text import Text

FILE_NAME_FORMAT = "{year:04d}{month:02d}{day:02d}-" + "{hour:02d}{minute:02d}{second:02d}.log"
LOGGER_PATH = "logs"
DATE_FORMAT = "%d %b %Y | %H:%M:%S"
LOGGER_FORMAT = "%(asctime)s | %(message)s"

LEVEL_ENUM = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

TIME_ENUM = {
    "s": 1,
    "ms": 1e3,
    "us": 1e6,
    "ns": 1e9,
    "min": 1 / 60,
    "h": 1 / 3600,
    "day": 1 / 86400,
}

SIZE_ENUM = {
    "T": 10**12,
    "G": 10**9,
    "M": 10**6,
    "k": 10**3,
}


CUSTOM_LOGGERS = [
    logging.getLogger("lightning.pytorch"),
    logging.getLogger("lightning.fabric"),
    logging.getLogger("lightning.pytorch.core"),
]


class LoggerConfig:
    def __init__(self, handlers, log_format, date_format=None, level="info"):
        self.handlers = handlers
        self.log_format = log_format
        self.date_format = date_format
        self.level = LEVEL_ENUM[level.lower()]


@lru_cache
def get_logger_config(min_level, override, **kwargs):
    t = datetime.datetime.now()

    file_name = FILE_NAME_FORMAT.format(
        year=t.year, month=t.month, day=t.day, hour=t.hour, minute=t.minute, second=t.second
    )

    Path(LOGGER_PATH).mkdir(parents=True, exist_ok=True)

    file_name = os.path.join(LOGGER_PATH, file_name)

    output_file_handler = logging.handlers.RotatingFileHandler(file_name, maxBytes=1024**2, backupCount=100)

    handler_format = logging.Formatter(LOGGER_FORMAT, datefmt=DATE_FORMAT)
    output_file_handler.setFormatter(handler_format)

    rich_handler = RichHandler(
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        show_time=False,
        markup=True,
        **kwargs,
    )

    if override:
        for log in CUSTOM_LOGGERS:
            log.handlers.clear()
            log.addHandler(output_file_handler)
            log.addHandler(rich_handler)

    return LoggerConfig(
        handlers=[
            rich_handler,
            output_file_handler,
        ],
        log_format=LOGGER_FORMAT,
        date_format=DATE_FORMAT,
        level=min_level,
    )


def setup_logger(min_level="info", override=True, **kwargs):
    """Setup the logger.

    Parameters
    ----------
    min_level : str, optional
        Minimum level of logging, by default INFO.
    override : bool, optional
        Whether to override the default loggers, by default True.
    kwargs : dict, optional
        Additional arguments for the rich handler (see [2]), by default {}.

    References
    [1] - https://www.pythonbynight.com/blog/sharpen-your-code
    [2] - https://rich.readthedocs.io/en/stable/reference/logging.html#logging

    """
    logger_config = get_logger_config(min_level, override, **kwargs)

    logging.basicConfig(
        level=logger_config.level,
        format=logger_config.log_format,
        datefmt=logger_config.date_format,
        handlers=logger_config.handlers,
    )


def timeit(unit="s", repeat=1):
    """Decorator to measure the time a function takes to execute.

    Parameters
    ----------
    unit : str, optional
        Units of time, by default "min".
    repeat : int, optional
        Number of times to repeat the function, by default 1.

    References
    ----------
    [1] - https://stackoverflow.com/questions/5929107/decorators-with-parameters
    [2] - https://stackoverflow.com/questions/1622943/timeit-versus-timing-decorator

    Returns
    -------
    function
        Wrapped function.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            ts = time.time()
            for _ in range(repeat):
                result = f(*args, **kw)
            te = time.time()

            delta = (te - ts) * TIME_ENUM[unit]

            logging.info(f"Function [b]{f.__name__}[/b] took {delta:.3f} {unit}.")

            return result

        return wrapper

    return decorator


def get_progress():
    progress_columns = (
        SpinnerColumn(style="green"),
        TextColumn("[progress.description]{task.description}"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        BarColumn(bar_width=None),
        MofNCompleteColumn(),
        TextColumn("Elapsed:"),
        TimeElapsedColumn(),
        TextColumn("Remaining:"),
        TimeRemainingColumn(),
    )
    return Progress(*progress_columns, auto_refresh=True)


class BatchesProcessedColumn(ProgressColumn):
    def __init__(self, style: str | Style) -> None:
        self.style = style
        super().__init__()

    def render(self, task: Any) -> RenderableType:
        return Text(f"Batch: {int(task.completed)}", style=self.style)


def get_batch_progress() -> Progress:
    progress_columns = (
        SpinnerColumn(spinner_name="aesthetic", speed=1.0, style="bold green"),
        TextColumn("[progress.description]{task.description} |"),
        BatchesProcessedColumn(style="white"),
        TextColumn("|"),
        TextColumn("Elapsed:"),
        TimeElapsedColumn(),
    )
    return Progress(*progress_columns, auto_refresh=True)
