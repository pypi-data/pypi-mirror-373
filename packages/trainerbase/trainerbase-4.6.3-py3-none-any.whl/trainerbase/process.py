from collections.abc import Iterable
from contextlib import suppress
from itertools import cycle
from os import _exit as force_exit
from time import sleep
from typing import cast

from psutil import Process, pid_exists, process_iter
from pymem import Pymem
from pymem.exception import ProcessError

from trainerbase.config import config
from trainerbase.logger import logger


def find_processes(process_name: str, *, exact_match: bool, ignore_case: bool) -> list[Process]:
    if ignore_case:
        process_name = process_name.lower()

    result_process_list = []

    for process in process_iter():
        name = process.name()

        if ignore_case:
            name = name.lower()

        condition = process_name == name if exact_match else process_name in name

        if condition:
            result_process_list.append(process)

    return result_process_list


def select_one_process(processes: Iterable[Process]) -> Process:
    processes = sorted(processes, key=lambda process: process.memory_info().rss, reverse=True)

    if not processes:
        raise ValueError("Cannot select from empty sequence!")

    if len(processes) > 1:
        logger.debug("Multiple processes found! Selecting one with highest Resident Set Size.")

    return next(iter(processes))


def get_target_pid(process_names: Iterable[str], *, exact_match: bool, ignore_case: bool) -> int:
    logger.info(f"Waiting for process in: {process_names}")

    for process_name in cycle(process_names):
        found_processes = find_processes(process_name, exact_match=exact_match, ignore_case=ignore_case)

        if found_processes:
            pid = select_one_process(found_processes).pid
            logger.info(f"Found {process_name}, pid: {pid}")

            return pid

    raise RuntimeError("This place must be unreachable! `process_names` is probably empty.")


def ensure_main_module_is_initialized(pm: Pymem) -> int:
    while True:
        try:
            return pm.base_address
        except ProcessError:
            logger.debug("Main module is not initialized. Waiting...")
            sleep(0.25)


def attach_to_process() -> Pymem:
    if not config.process.names:
        raise ValueError("Empty process name list")

    with suppress(KeyboardInterrupt):
        pid = get_target_pid(
            config.process.names,
            exact_match=config.process.exact_match,
            ignore_case=config.process.ignore_case,
        )

        pm = Pymem(pid)
        ensure_main_module_is_initialized(pm)

        return pm

    force_exit(0)


def shutdown_if_process_exited():
    if not pid_exists(cast(int, pm.process_id)):
        logger.info("Game process exited. Shutting down.")
        force_exit(0)


def kill_game_process():
    logger.info("Killing game process.")
    Process(pm.process_id).kill()


pm = attach_to_process()
