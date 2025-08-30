from collections.abc import Callable
from typing import Any, override

from dearpygui import dearpygui as dpg

from trainerbase.common.keyboard import (
    AbstractKeyboardHandler,
    GameBoolReleaseHotkeySwitch,
    ReleaseHotkeySwitch,
    ShortLongHotkeyPressSwitch,
    SimpleHotkeyHandler,
)
from trainerbase.gameobject import GameBool
from trainerbase.gui.helpers import add_components
from trainerbase.gui.objects import GameObjectUI
from trainerbase.gui.types import AbstractUIComponent


class SeparatorUI(AbstractUIComponent):
    def __init__(self, empty_lines_before: int = 1, empty_lines_after: int = 0):
        self._empty_lines_before = empty_lines_before
        self._empty_lines_after = empty_lines_after

    @override
    def add_to_ui(self) -> None:
        for _ in range(self._empty_lines_before):
            dpg.add_text()

        dpg.add_separator()

        for _ in range(self._empty_lines_after):
            dpg.add_text()


class TextUI(AbstractUIComponent):
    def __init__(self, text: str = ""):
        self.text = text

    @override
    def add_to_ui(self) -> None:
        dpg.add_text(self.text)


class HotkeyHandlerUI(AbstractUIComponent):
    def __init__(
        self,
        handler: AbstractKeyboardHandler,
        label: str,
    ):
        self.handler = handler
        self.label = label

    @override
    def add_to_ui(self) -> None:
        match self.handler:
            case ShortLongHotkeyPressSwitch():
                dpg.add_text(f"Press/Hold [{self.handler.hotkey}] Toggle/Enable {self.label}")
            case ReleaseHotkeySwitch():
                dpg.add_text(f"[{self.handler.hotkey}] Toggle {self.label}")
            case SimpleHotkeyHandler():
                dpg.add_button(
                    label=f"[{self.handler.hotkey}] {self.label}",
                    callback=self._ensure_callable_has_dunder_code(self.handler.callback),
                )
            case _:
                dpg.add_text(f"[{self.handler.hotkey}] {self.label}")

        self.handler.handle()

    @staticmethod
    def _ensure_callable_has_dunder_code(callable_object: Callable[[], None]) -> Callable[[], None]:
        """
        DPG add_button has `callback` arg. In this case `callback.__code__` is required.
        """

        if hasattr(callable, "__code__"):
            callback_with_dunder_code = callable_object
        else:

            def callback_with_dunder_code():
                callable_object()

        return callback_with_dunder_code


class HorizontalUI(AbstractUIComponent):
    def __init__(self, *components: AbstractUIComponent):
        self.components = components

    @override
    def add_to_ui(self) -> None:
        with dpg.group(horizontal=True):
            add_components(*self.components)

        return super().add_to_ui()


class SwitchableGameBoolUI(AbstractUIComponent):
    def __init__(
        self,
        gameobject: GameBool,
        toggle_hotkey: str,
        label: str,
        freeze_hotkey: str | None = None,
        set_hotkey: str | None = None,
        *,
        default_setter_input_value: Any = 0,
        before_set: Callable | None = None,
        tts_on_hotkey: bool = True,
        setter_input_width: int = 220,
        toggle_text: str = "Toggle",
    ):
        self.gameobject = gameobject
        self.toggle_hotkey = toggle_hotkey
        self.toggle_text = toggle_text

        self.pure_label = label
        self.freeze_hotkey = freeze_hotkey
        self.set_hotkey = set_hotkey
        self.default_setter_input_value = default_setter_input_value
        self.before_set = before_set
        self.tts_on_hotkey = tts_on_hotkey
        self.setter_input_width = setter_input_width

    @override
    def add_to_ui(self) -> None:
        add_components(
            HorizontalUI(
                HotkeyHandlerUI(GameBoolReleaseHotkeySwitch(self.gameobject, self.toggle_hotkey), self.toggle_text),
                GameObjectUI(
                    self.gameobject,
                    self.pure_label,
                    self.freeze_hotkey,
                    self.set_hotkey,
                    default_setter_input_value=self.default_setter_input_value,
                    before_set=self.before_set,
                    tts_on_hotkey=self.tts_on_hotkey,
                    setter_input_width=self.setter_input_width,
                ),
            )
        )

        return super().add_to_ui()
