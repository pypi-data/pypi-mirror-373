from collections.abc import Sequence
from typing import override
from uuid import uuid4

from dearpygui import dearpygui as dpg

from trainerbase.common.keyboard import ReleaseHotkeySwitch
from trainerbase.common.tapper import Tapper
from trainerbase.gui.helpers import add_components
from trainerbase.gui.misc import HotkeyHandlerUI, TextUI
from trainerbase.gui.types import AbstractUIComponent


class TapperUI(AbstractUIComponent):
    DPG_TAG_TAPPER_DELAY_INPUT_PREFIX = "tag_tapper_delay_input"
    DPG_TAG_TAPPER_DELAY_PRESET_INPUT_PREFIX = "tag_tapper_delay_preset_input"
    DPG_TAG_TAPPER_DURATION_INPUT_PREFIX = "tag_tapper_duration_input"
    DPG_TAG_TAPPER_DURATION_PRESET_INPUT_PREFIX = "tag_tapper_duration_preset_input"

    DELAY_PRESETS: tuple[float, ...] = (0.05, 0.15, 0.25, 0.3, 0.5, 0.7, 1, 2, 5, 10)
    DURATION_PRESETS: tuple[float, ...] = (0.0, 0.15, 0.3, 0.5, 0.75, 1, 1.5, 5.0)

    def __init__(
        self,
        tapper: Tapper | None = None,
        key: str = "PageUp",
        default_delay: float = 0.15,
        default_duration: float = 0.15,
    ):
        if tapper is None:
            self.tapper = Tapper(default_delay, duration=default_duration)
            self.default_delay = default_delay
            self.default_duration = default_duration
        else:
            self.tapper = tapper
            self.default_delay = tapper.delay
            self.default_duration = tapper.duration

        self.key = key
        self.dpg_tag_tapper_delay_input = f"{self.DPG_TAG_TAPPER_DELAY_INPUT_PREFIX}_{uuid4()}"
        self.dpg_tag_tapper_delay_preset_input = f"{self.DPG_TAG_TAPPER_DELAY_PRESET_INPUT_PREFIX}_{uuid4()}"
        self.dpg_tag_tapper_duration_input = f"{self.DPG_TAG_TAPPER_DELAY_INPUT_PREFIX}_{uuid4()}"
        self.dpg_tag_tapper_duration_preset_input = f"{self.DPG_TAG_TAPPER_DELAY_PRESET_INPUT_PREFIX}_{uuid4()}"

    @override
    def add_to_ui(self) -> None:
        add_components(
            TextUI(f"Tapper for {self.tapper.device} {self.tapper.button}"),
            HotkeyHandlerUI(ReleaseHotkeySwitch(self.tapper, self.key), "Tapper"),
        )

        dpg.add_input_double(
            tag=self.dpg_tag_tapper_delay_input,
            label="Delay",
            min_value=0.0,
            max_value=60.0,
            default_value=self.default_delay,
            min_clamped=True,
            max_clamped=True,
            callback=self.on_delay_change,
        )

        dpg.add_slider_int(
            tag=self.dpg_tag_tapper_delay_preset_input,
            label="Delay Preset",
            min_value=0,
            max_value=len(self.DELAY_PRESETS) - 1,
            clamped=True,
            default_value=self.get_closest_preset_index(self.DELAY_PRESETS, self.default_delay),
            callback=self.on_delay_preset_change,
        )

        dpg.add_separator()

        dpg.add_input_double(
            tag=self.dpg_tag_tapper_duration_input,
            label="Duration",
            min_value=0.0,
            max_value=5.0,
            default_value=self.default_duration,
            min_clamped=True,
            max_clamped=True,
            callback=self.on_duration_change,
        )

        dpg.add_slider_int(
            tag=self.dpg_tag_tapper_duration_preset_input,
            label="Duration Preset",
            min_value=0,
            max_value=len(self.DURATION_PRESETS) - 1,
            clamped=True,
            default_value=self.get_closest_preset_index(self.DURATION_PRESETS, self.default_delay),
            callback=self.on_duration_preset_change,
        )

    def on_delay_preset_change(self):
        new_delay = self.DELAY_PRESETS[dpg.get_value(self.dpg_tag_tapper_delay_preset_input)]
        self.tapper.delay = new_delay
        dpg.set_value(self.dpg_tag_tapper_delay_input, new_delay)

    def on_delay_change(self):
        new_delay = dpg.get_value(self.dpg_tag_tapper_delay_input)
        closest_preset_index = self.get_closest_preset_index(self.DELAY_PRESETS, new_delay)
        self.tapper.delay = new_delay
        dpg.set_value(self.dpg_tag_tapper_delay_preset_input, closest_preset_index)

    def on_duration_preset_change(self):
        new_duration = self.DURATION_PRESETS[dpg.get_value(self.dpg_tag_tapper_duration_preset_input)]
        self.tapper.duration = new_duration
        dpg.set_value(self.dpg_tag_tapper_duration_input, new_duration)

    def on_duration_change(self):
        new_duration = dpg.get_value(self.dpg_tag_tapper_duration_input)
        closest_preset_index = self.get_closest_preset_index(self.DELAY_PRESETS, new_duration)
        self.tapper.duration = new_duration
        dpg.set_value(self.dpg_tag_tapper_duration_preset_input, closest_preset_index)

    def get_closest_preset_index(self, presests: Sequence[float], value: float) -> int:
        closest_preset = min(presests, key=lambda preset: abs(preset - value))
        return presests.index(closest_preset)
