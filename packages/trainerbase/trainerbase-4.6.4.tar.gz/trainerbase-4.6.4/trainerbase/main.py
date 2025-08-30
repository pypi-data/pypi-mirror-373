from collections.abc import Callable
from os import _exit as force_exit
from traceback import print_exc
from typing import NoReturn

from trainerbase.codeinjection import safely_eject_all_code_injections
from trainerbase.common.rainbow import gradient_updater
from trainerbase.gameobject import update_frozen_objects
from trainerbase.gui.objects import update_displayed_objects
from trainerbase.logger import logger
from trainerbase.process import shutdown_if_process_exited
from trainerbase.scriptengine import (
    enabled_by_default,
    process_healthcheck_script_engine,
    rainbow_script_engine,
    system_script_engine,
)
from trainerbase.speedhack import SpeedHack
from trainerbase.tts import tts_manager


type Callback = Callable[[], None]


def run(  # pylint: disable=too-complex
    run_gui: Callable[[Callback, Callback], None],
    on_gui_initialized_hook: Callback | None = None,
    on_shutdown_hook: Callback | None = None,
) -> NoReturn:
    def on_shutdown() -> NoReturn:
        logger.info("Shutting down...")

        logger.debug("Ejecting Code Injections.")
        safely_eject_all_code_injections()

        logger.debug("Disabling SpeedHack")
        SpeedHack.disable()

        logger.debug("Stopping Script Engines.")
        rainbow_script_engine.stop()
        system_script_engine.stop()
        process_healthcheck_script_engine.stop()

        if on_shutdown_hook is not None:
            logger.debug("on_shutdown_hook provided. Calling.")
            on_shutdown_hook()

        force_exit(0)

    def on_gui_initialized() -> None:
        logger.debug("GUI has been initialized. Starting Script Engines.")

        system_script_engine.start()
        process_healthcheck_script_engine.start()
        rainbow_script_engine.start()

        if on_gui_initialized_hook is not None:
            logger.debug("on_gui_initialized_hook provided. Calling.")

            try:
                on_gui_initialized_hook()
            except Exception:
                logger.error("Exception occurred while calling on_gui_initialized_hook. See stderr.")
                print_exc()
                on_shutdown()

    logger.info("Starting...")
    logger.debug("Registering core scripts")
    system_script_engine.simple_script(update_frozen_objects, enabled=True)
    system_script_engine.simple_script(update_displayed_objects, enabled=True)
    system_script_engine.register_script(enabled_by_default(tts_manager))
    rainbow_script_engine.register_script(enabled_by_default(gradient_updater))
    process_healthcheck_script_engine.simple_script(shutdown_if_process_exited, enabled=True)

    logger.debug("Running GUI")

    try:
        run_gui(on_gui_initialized, on_shutdown)
    except Exception:
        print_exc()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt (Ctrl+C)")
        pass

    on_shutdown()
