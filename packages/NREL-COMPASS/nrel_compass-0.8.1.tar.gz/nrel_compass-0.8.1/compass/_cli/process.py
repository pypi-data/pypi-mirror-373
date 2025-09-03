"""COMPASS CLI process subcommand"""

import asyncio
import logging
import warnings
import multiprocessing

import click
from rich.live import Live
from rich.theme import Theme
from rich.logging import RichHandler
from rich.console import Console

from compass.pb import COMPASS_PB
from compass.scripts.process import process_jurisdictions_with_openai
from compass.utilities.logs import AddLocationFilter
from compass.utilities.parsing import load_config


@click.command
@click.option(
    "--config",
    "-c",
    required=True,
    type=click.Path(exists=True),
    help="Path to ordinance configuration JSON or JSON5 file. This file "
    "should contain any/all the arguments to pass to "
    ":func:`compass.scripts.process.process_jurisdictions_with_openai`.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Show logs on the terminal. Add extra libraries to get logs from by "
    "increasing the input (-v, -vv, -vvv). Does not affect log level, which "
    "is controlled via the config input.",
)
@click.option(
    "-np",
    "--no_progress",
    is_flag=True,
    help="Flag to hide progress bars during processing.",
)
def process(config, verbose, no_progress):
    """Download and extract ordinances for a list of jurisdictions"""
    config = load_config(config)

    custom_theme = Theme({"logging.level.trace": "rgb(94,79,162)"})
    console = Console(theme=custom_theme)

    _setup_cli_logging(
        console, verbose, log_level=config.get("log_level", "INFO")
    )

    # Need to set start method to "spawn" instead of "fork" for unix
    # systems. If this call is not present, software hangs when process
    # pool executor is launched.
    # More info here: https://stackoverflow.com/a/63897175/20650649
    multiprocessing.set_start_method("spawn")

    # asyncio.run(...) doesn't throw exceptions correctly for some
    # reason...
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if no_progress:
        loop.run_until_complete(process_jurisdictions_with_openai(**config))
        return

    # warnings will be logged to file (and terminal if verbose >= 1)
    warnings.filterwarnings("ignore")

    COMPASS_PB.console = console
    live_display = Live(
        COMPASS_PB.group,
        console=console,
        refresh_per_second=20,
        transient=True,
    )
    with live_display:
        total_seconds, total_cost, out_dir = loop.run_until_complete(
            process_jurisdictions_with_openai(**config)
        )

    runtime = _elapsed_time_as_str(total_seconds)
    total_cost = (
        f"\nTotal cost: [#71906e]${total_cost:,.2f}[/#71906e]"
        if total_cost
        else ""
    )

    console.print(
        f"✅ Scraping complete!\nOutput Directory: {out_dir}\n"
        f"Total runtime: {runtime} {total_cost}"
    )
    COMPASS_PB.console = None


def _setup_cli_logging(console, verbosity_level, log_level="INFO"):
    """Setup logging for CLI"""
    libs = []
    if verbosity_level >= 1:
        libs.append("compass")
    if verbosity_level >= 2:  # noqa: PLR2004
        libs.append("elm")
    if verbosity_level >= 3:  # noqa: PLR2004
        libs.append("openai")
    if verbosity_level >= 4:  # noqa: PLR2004
        libs.extend(("networkx", "pytesseract", "pdf2image", "pdftotext"))

    for lib in libs:
        logger = logging.getLogger(lib)
        handler = RichHandler(
            level=log_level,
            console=console,
            rich_tracebacks=True,
            omit_repeated_times=True,
            markup=True,
        )
        fmt = logging.Formatter(
            fmt="[[magenta]%(location)s[/magenta]]: %(message)s",
            defaults={"location": "main"},
        )
        handler.setFormatter(fmt)
        handler.addFilter(AddLocationFilter())
        logger.addHandler(handler)
        logger.setLevel(log_level)


def _elapsed_time_as_str(seconds_elapsed):
    """Format elapsed time into human readable string"""
    days, seconds = divmod(int(seconds_elapsed), 24 * 3600)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    time_str = f"{hours:d}:{minutes:02d}:{seconds:02d}"
    if days:
        time_str = f"{days:,d} day{'s' if abs(days) != 1 else ''}, {time_str}"
    return time_str
