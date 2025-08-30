from traceback import print_exc
from typing import override
from uuid import uuid4

from dearpygui import dearpygui as dpg
from keyboard import add_hotkey
from pymem.exception import MemoryReadError, MemoryWriteError

from trainerbase.codeinjection import AbstractCodeInjection
from trainerbase.gui.types import AbstractUIComponent
from trainerbase.tts import say


class CodeInjectionUI(AbstractUIComponent):
    DPG_TAG_PREFIX = "injection__"

    def __init__(
        self,
        injection: AbstractCodeInjection,
        label: str,
        hotkey: str | None = None,
        *,
        tts_on_hotkey: bool = True,
    ):
        self.injection = injection
        self.pure_label = label
        self.label_with_hotkey = label if hotkey is None else f"[{hotkey}] {label}"
        self.hotkey = hotkey
        self.tts_on_hotkey = tts_on_hotkey

        self.dpg_tag = f"{self.DPG_TAG_PREFIX}{uuid4()}"

    @override
    def add_to_ui(self) -> None:
        if self.hotkey is not None:
            add_hotkey(self.hotkey, self.on_hotkey_press)

        dpg.add_checkbox(label=self.label_with_hotkey, tag=self.dpg_tag, callback=self.on_codeinjection_state_change)

    def on_codeinjection_state_change(self):
        change_codeinjection_state = self.injection.inject if dpg.get_value(self.dpg_tag) else self.injection.eject

        try:
            change_codeinjection_state()
        except (MemoryReadError, MemoryWriteError, ValueError):
            dpg.set_value(self.dpg_tag, not dpg.get_value(self.dpg_tag))
            print_exc()

    def on_hotkey_press(self):
        dpg.set_value(self.dpg_tag, not dpg.get_value(self.dpg_tag))
        self.on_codeinjection_state_change()

        if self.tts_on_hotkey:
            status = "applied" if dpg.get_value(self.dpg_tag) else "removed"
            say(f"CodeInjection {self.pure_label} {status}")
