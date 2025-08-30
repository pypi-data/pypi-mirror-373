from typing import override
from uuid import uuid4

from dearpygui import dearpygui as dpg
from keyboard import add_hotkey

from trainerbase.gui.types import AbstractUIComponent
from trainerbase.scriptengine import AbstractBaseScript
from trainerbase.tts import say


class ScriptUI[T: AbstractBaseScript](AbstractUIComponent):
    DPG_TAG_PREFIX = "script__"

    def __init__(
        self,
        script: T,
        label: str,
        hotkey: str | None = None,
        *,
        tts_on_hotkey: bool = True,
    ):
        self.script = script
        self.pure_label = label
        self.label_with_hotkey = label if hotkey is None else f"[{hotkey}] {label}"
        self.hotkey = hotkey
        self.tts_on_hotkey = tts_on_hotkey

        self.dpg_tag = f"{self.DPG_TAG_PREFIX}{uuid4()}"

    @override
    def add_to_ui(self) -> None:
        if self.hotkey is not None:
            add_hotkey(self.hotkey, self.on_hotkey_press)

        dpg.add_checkbox(
            label=self.label_with_hotkey,
            tag=self.dpg_tag,
            callback=self.on_script_state_change,
            default_value=self.script.enabled,
        )

    def on_script_state_change(self):
        self.script.enabled = dpg.get_value(self.dpg_tag)

    def on_hotkey_press(self):
        dpg.set_value(self.dpg_tag, not dpg.get_value(self.dpg_tag))

        self.on_script_state_change()

        if self.tts_on_hotkey:
            status = "enabled" if self.script.enabled else "disabled"
            say(f"Script {self.pure_label} {status}")
