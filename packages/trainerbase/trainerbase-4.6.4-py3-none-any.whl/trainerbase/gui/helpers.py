from collections.abc import Callable
from functools import wraps
from typing import Final

from dearpygui import dearpygui as dpg

from trainerbase.common.rainbow import Color, gradient_updater
from trainerbase.config import config
from trainerbase.gui.rainbow import RainbowUI
from trainerbase.gui.types import AbstractUIComponent
from trainerbase.logger import logger


ICON_PATH: Final[str] = str(config.vendor.folder / "trainerbase.ico")


def add_components(*components: AbstractUIComponent):
    for component in components:
        component.add_to_ui()


def simple_trainerbase_menu(
    window_title: str,
    width: int,
    height: int,
    rainbow_initial_color: Color = (1, 255, 125),
    rainbow_initial_delta: tuple[int, int, int] = (1, 1, 1),
    rainbow_color_length: int = 3,
):
    def menu_decorator(initializer: Callable[[], None]):
        @wraps(initializer)
        def run_menu_wrapper(on_initialized: Callable[[], None], on_shutdown: Callable[[], None]):
            dpg.create_context()
            dpg.create_viewport(
                title=window_title,
                width=width,
                height=height,
                resizable=False,
                small_icon=ICON_PATH,
            )
            dpg.setup_dearpygui()

            with dpg.window(
                label=window_title,
                tag="menu",
                min_size=[width, height],
                no_close=True,
                no_move=True,
                no_title_bar=True,
                horizontal_scrollbar=True,
                autosize=True,
            ):
                gradient_updater.setup(
                    initial_color=rainbow_initial_color,
                    initial_delta=rainbow_initial_delta,
                    color_length=rainbow_color_length,
                )

                add_components(RainbowUI(width, gradient_updater))

                initializer()

            dpg.set_primary_window("menu", value=True)
            dpg.show_viewport()

            on_initialized()

            logger.debug("Showing Window")

            dpg.start_dearpygui()

            logger.debug("Window has been closed")

            on_shutdown()  # it's better to call it here, because after destroy_context it may not be possible

            dpg.destroy_context()

        return run_menu_wrapper

    return menu_decorator
