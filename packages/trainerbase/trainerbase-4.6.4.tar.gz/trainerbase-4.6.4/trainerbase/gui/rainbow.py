from typing import override

from dearpygui import dearpygui as dpg

from trainerbase.common.rainbow import GradientUpdater
from trainerbase.gui.types import AbstractUIComponent


class RainbowUI(AbstractUIComponent):
    def __init__(self, width: int, gradient_updater: GradientUpdater) -> None:
        self.gradient_updater = gradient_updater
        self.width = width

    @override
    def add_to_ui(self) -> None:
        dpg.add_spacer()
        dpg.add_spacer()
        tags = [dpg.draw_line([-10.0 + i, 0.0], [1.0 + i, 0.0], thickness=2) for i in range(self.width)]

        self.gradient_updater.setup(tags=tags)

        return super().add_to_ui()
