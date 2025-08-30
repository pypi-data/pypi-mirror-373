from enum import StrEnum, auto
from time import sleep
from typing import override

from keyboard import press as press_keyboard_key
from keyboard import release as release_keyboard_key
from mouse import press as press_mouse_button
from mouse import release as release_mouse_button

from trainerbase.abc import Switchable
from trainerbase.scriptengine import ScriptEngine


class TappingDevice(StrEnum):
    MOUSE = auto()
    KEYBOARD = auto()


class Tapper(Switchable):
    def __init__(
        self,
        default_delay: float,
        tap_button: str = "left",
        device: TappingDevice = TappingDevice.MOUSE,
        duration: float = 0.15,
    ):
        self._delay = default_delay
        self._duration = duration
        self.button = tap_button
        self.device = device
        self.tapper_script_engine: ScriptEngine | None = None
        self.tapper_function = (
            self._send_mouse_click_with_duration
            if device is TappingDevice.MOUSE
            else self._send_keyboard_press_and_release_with_duration
        )

    @override
    def enable(self):
        self.disable()

        self.tapper_script_engine = ScriptEngine(self._delay)
        self.tapper_script_engine.simple_script(self.tapper_function, enabled=True)
        self.tapper_script_engine.start()

    @override
    def disable(self):
        if self.tapper_script_engine is not None:
            self.tapper_script_engine.stop()

    def _send_mouse_click_with_duration(self):
        press_mouse_button(self.button)
        sleep(self._duration)
        release_mouse_button(self.button)

    def _send_keyboard_press_and_release_with_duration(self):
        press_keyboard_key(self.button)
        sleep(self._duration)
        release_keyboard_key(self.button)

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, new_delay: float):
        if self.tapper_script_engine is not None:
            self.tapper_script_engine.delay = new_delay

        self._delay = new_delay

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, new_duration: float):
        self._duration = new_duration
