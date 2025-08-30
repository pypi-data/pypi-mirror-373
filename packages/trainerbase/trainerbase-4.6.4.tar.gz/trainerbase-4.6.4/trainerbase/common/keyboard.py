from collections.abc import Callable
from time import time
from typing import override

from keyboard import add_hotkey, on_press_key, on_release_key

from trainerbase.abc import AbstractKeyboardHandler, Switchable
from trainerbase.gameobject import GameBool


class SimpleHotkeyHandler(AbstractKeyboardHandler):
    def __init__(self, callback: Callable[[], None], hotkey: str):
        self.callback = callback
        self._hotkey = hotkey

    @property
    @override
    def hotkey(self) -> str:
        return self._hotkey

    @override
    def handle(self):
        add_hotkey(self._hotkey, self.callback)


class ReleaseHotkeySwitch(AbstractKeyboardHandler):
    def __init__(self, switchable: Switchable, key: str):
        self._key = key
        self._switchable = switchable
        self._enabled = False

    def _on_release(self, _):
        if self._enabled:
            self._switchable.disable()
        else:
            self._switchable.enable()

        self._enabled = not self._enabled

    @property
    @override
    def hotkey(self):
        return self._key

    @override
    def handle(self):
        on_release_key(self._key, self._on_release)


class GameBoolReleaseHotkeySwitch(AbstractKeyboardHandler):
    def __init__(self, game_bool: GameBool, key: str):
        self._key = key
        self._game_bool = game_bool

    def _on_release(self, _):
        if self._game_bool.value:
            self._game_bool.disable()
        else:
            self._game_bool.enable()

    @property
    @override
    def hotkey(self):
        return self._key

    @override
    def handle(self):
        on_release_key(self._key, self._on_release)


class ShortLongHotkeyPressSwitch(AbstractKeyboardHandler):
    def __init__(self, switchable: Switchable, key: str, short_press_max_delta: float = 0.3):
        self._key = key
        self._press_timestamp = None
        self._short_press_max_delta = short_press_max_delta
        self._switchable = switchable
        self._enabled = False

    def _on_press(self, _):
        if self._press_timestamp is None:
            self._press_timestamp = time()
        self.on_press()

    def _on_release(self, _):
        if self._is_short_delta():
            self.on_short_press()
        else:
            self.on_long_press()

        self._press_timestamp = None

    def _get_press_delta(self):
        if self._press_timestamp is None:
            return 0

        return time() - self._press_timestamp

    def _is_short_delta(self):
        return self._get_press_delta() <= self._short_press_max_delta

    def on_press(self):
        self._switchable.enable()

    def on_short_press(self):
        if self._enabled:
            self._enabled = False
            self._switchable.disable()
        else:
            self._enabled = True
            self._switchable.enable()

    def on_long_press(self):
        self._enabled = False
        self._switchable.disable()

    @property
    @override
    def hotkey(self):
        return self._key

    @override
    def handle(self):
        on_release_key(self._key, self._on_release)
        on_press_key(self._key, self._on_press)
