"""Profiling tools for use to measure performance of RegScale-CLI."""

import cProfile
import csv
import gc
import platform
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from contextlib import suppress
from pstats import Stats
from typing import Callable, List, Tuple

from click.testing import CliRunner
from rich.console import Console
from rich.progress import track
from rich.table import Table

from regscale.dev.dirs import trim_relative_subpath, PROFILING_DIRS


@contextmanager
def suppress_system_exit():
    """Suppress SystemExit exceptions when profiling functions in the CLI

    :yields: Generator
    """
    with suppress(SystemExit):
        yield


def parse_time(output: str, time_type: str) -> float:
    """Parse the time from the output of the time command

    :param str output: The output of the time command
    :param str time_type: The type of time to parse
    :return: The parsed time
    :rtype: float
    """
    time_type_2 = "total" if time_type == "real" else time_type
    match = re.search(rf"{time_type}\s+(?:(\d+)m)?(\d+\.\d+)s", output) or re.search(
        rf"(?:(\d+)m)?(\d+\.\d+)s\s+{time_type_2}", output
    )
    if match:
        return sum(float(x) * 60**i if x is not None else 0 for i, x in enumerate(reversed(match.groups())))
    return 0


def profile_my_function(func: Callable, *args: Tuple, iterations: int = 100, **kwargs: dict) -> None:
    """Profile a function using cProfile

    :param Callable func: The function to profile
    :param Tuple *args: The args to pass to the function
    :param int iterations: The number of times to run the function, defaults to 100
    :param dict **kwargs: The kwargs to pass to the function
    :rtype: None
    """
    stats_list: List[Stats] = []
    for _ in track(
        range(iterations),
        description=f"Timing RegScale-CLI function {func.__name__} {iterations} times...",
    ):
        gc.collect()
        profiler = cProfile.Profile()
        profiler.enable()
        with suppress_system_exit():
            profiler.runcall(func, *args, **kwargs)
        profiler.disable()
        stats = Stats(profiler)
        stats_list.append(stats)

    master_stats = Stats()

    for stats in stats_list:
        master_stats.add(stats)

    master_stats.dump_stats("profile_stats.pstat")
    # initialize summary variables
    total_time: float = 0
    all_times: List[float] = []
    # write the stats to a CSV file
    with open("profile_stats.csv", "w") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(
            [
                "Module",
                "Function",
                "Primitive Calls",
                "Total Calls",
                "Time",
                "Cumulative Time",
                "Percentage",
            ]
        )
        for func_info, func_stats in master_stats.stats.items():
            _, _, func_name = func_info
            cc, nc, tt, ct, _ = func_stats
            total_time += tt
            all_times.append(tt)

        for func_info, func_stats in master_stats.stats.items():
            filename, _, func_name = func_info
            cc, nc, tt, ct, _ = func_stats
            percentage = "{:.3f}%".format(((tt * 1000) / (total_time / 1000)) * 100)
            row = [
                trim_relative_subpath(filename, PROFILING_DIRS) or filename,  # trim the relative path from the filename
                func_name,
                cc,
                nc,
                "{:.8f}".format(tt),
                "{:.8f}".format(ct),
                percentage,
            ]
            csv_writer.writerow(row)


def profile_about_command() -> None:
    """Profile the about command

    :rtype: None
    """
    runner = CliRunner()
    from regscale.regscale import cli

    _ = runner.invoke(cli, ["about"])


def calculate_cli_import_time() -> float:
    """Calculate the import time for the CLI

    :return: The import time
    :rtype: float
    """
    start_time = time.time()
    # pylint: disable=unused-import

    # pylint: enable=unused-import
    end_time = time.time()
    return end_time - start_time


def calculate_load_times(command: str = "regscale about", iterations: int = 100, no_output: bool = False) -> dict:
    """Calculate the load times for a command

    :param str command: The command to run
    :param int iterations: The number of times to run the command
    :param bool no_output: Whether to output the results to the console
    :return: The load times
    :rtype: dict
    """
    total_user, min_user, max_user = 0, float("inf"), 0
    total_sys, min_sys, max_sys = 0, float("inf"), 0
    total_real, min_real, max_real = 0, float("inf"), 0
    if platform.system() == "Windows":
        console = Console()
        console.print("[red]Calculating start time on Windows is not supported.")
        sys.exit(0)
    else:
        sub_process_command = f'bash -c "time {command}"'
    for _ in track(range(iterations), description=f"Timing RegScale-CLI load {iterations} times..."):
        result = subprocess.run(
            sub_process_command,
            shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        output = result.stderr.decode("utf-8")
        # extract user, sys, and real time using regular expressions
        user_time = parse_time(output, "user")
        sys_time = parse_time(output, "sys")
        real_time = parse_time(output, "real")

        # update total, min, and max values
        total_user += user_time
        min_user = min(min_user, user_time)
        max_user = max(max_user, user_time)
        total_sys += sys_time
        min_sys = min(min_sys, sys_time)
        max_sys = max(max_sys, sys_time)
        total_real += real_time
        min_real = min(min_real, real_time)
        max_real = max(max_real, real_time)

    avg_user = round(total_user / iterations, 3)
    avg_sys = round(total_sys / iterations, 3)
    avg_real = round(total_real / iterations, 3)

    if not no_output:
        console = Console()
        table = Table(title=f"Load times over {iterations} iterations")
        table.add_column("Metric")
        table.add_column("User Time (s)")
        table.add_column("Sys Time (s)")
        table.add_column("Real Time (s)")
        table.add_row(
            "[green]Min",
            f"[green]{min_user}",
            f"[green]{min_sys}",
            f"[green]{min_real}",
        )
        table.add_row("[red]Max", f"[red]{max_user}", f"[red]{max_sys}", f"[red]{max_real}")
        table.add_row(
            "[yellow]Avg",
            f"[yellow]{avg_user}",
            f"[yellow]{avg_sys}",
            f"[yellow]{avg_real}",
        )
        console.print(table)
        sys.exit(0)
    return {
        "Avg User Time": avg_user,
        "Avg Sys Time": avg_sys,
        "Avg Real Time": avg_real,
    }
