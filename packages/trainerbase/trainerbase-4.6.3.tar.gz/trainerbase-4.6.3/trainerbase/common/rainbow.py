from collections.abc import Iterable, Iterator
from itertools import cycle
from typing import override

from dearpygui import dearpygui as dpg

from trainerbase.scriptengine import AbstractBaseScript


type TagList = list[int | str]
type Color = tuple[int, int, int]
type Colors = Iterable[Color]


class GradientUpdater(AbstractBaseScript):
    def __init__(self):
        self.tags: TagList | None = None
        self.colors: list[Color] | None = None
        self.index_iter: Iterator[int] | None = None
        self.initial_color: Color | None = None
        self.initial_delta: tuple[int, int, int] | None = None
        self.color_length: int | None = None

    @override
    def __call__(self):
        if self.tags is None or self.colors is None:
            raise RuntimeError("Call setup(...)")

        for tag, color in zip(self.tags, self.get_colors(len(self.tags)), strict=False):
            dpg.configure_item(tag, color=color)

    def setup(
        self,
        *,
        tags: TagList | None = None,
        initial_color: Color | None = None,
        initial_delta: tuple[int, int, int] | None = None,
        color_length: int | None = None,
    ) -> None:
        if tags is not None:
            self.tags = tags
            self.colors = self.generate_colors(len(tags))
            self.index_iter = cycle(range(len(self.colors)))

        if initial_color is not None:
            self.initial_color = initial_color

        if initial_delta is not None:
            self.initial_delta = initial_delta

        if color_length is not None:
            self.color_length = color_length

    def generate_colors(self, length: int) -> list[Color]:
        if self.initial_color is None or self.initial_delta is None or self.color_length is None:
            raise RuntimeError("Call setup(...)")

        red, green, blue = self.initial_color
        delta_red, delta_green, delta_blue = self.initial_delta

        colors = []

        for _ in range(length // 2):
            for _ in range(self.color_length):
                colors.append((red, green, blue))

            red, delta_red = self.next_color_channel_value(red, delta_red)
            green, delta_green = self.next_color_channel_value(green, delta_green)
            blue, delta_blue = self.next_color_channel_value(blue, delta_blue)

        colors = colors + colors[::-1]

        return colors

    def get_colors(self, n: int) -> Colors:
        if self.colors is None or self.index_iter is None:
            raise RuntimeError("Call setup(...)")

        index = next(self.index_iter)

        colors = self.colors[index : index + n]

        if len(colors) < n:
            colors += self.colors[: n - len(colors)]

        return colors

    def next_color_channel_value(self, current: int, delta: int) -> tuple[int, int]:
        if not (0 <= current + delta <= 255):
            delta = -delta

        return current + delta, delta


gradient_updater = GradientUpdater()
