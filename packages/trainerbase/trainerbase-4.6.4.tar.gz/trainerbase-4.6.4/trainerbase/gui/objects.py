from collections.abc import Callable
from contextlib import suppress
from typing import Any, ClassVar, Self, override
from uuid import uuid4

from dearpygui import dearpygui as dpg
from keyboard import add_hotkey
from pymem.exception import MemoryReadError, MemoryWriteError

from trainerbase.gameobject import (
    GameBool,
    GameByte,
    GameDouble,
    GameFloat,
    GameInt,
    GameLongLong,
    GameObject,
    GameShort,
    GameUnsignedInt,
    GameUnsignedLongLong,
    GameUnsignedShort,
)
from trainerbase.gui.types import AbstractUIComponent
from trainerbase.tts import say


class GameObjectUI(AbstractUIComponent):
    DPG_TAG_PREFIX = "object__"
    DPG_TAG_POSTFIX_IS_FROZEN = "__frozen"
    DPG_TAG_POSTFIX_GETTER = "__getter"
    DPG_TAG_POSTFIX_SETTER = "__setter"

    displayed_objects: ClassVar[list[Self]] = []

    def __init__(
        self,
        gameobject: GameObject,
        label: str,
        freeze_hotkey: str | None = None,
        set_hotkey: str | None = None,
        *,
        default_setter_input_value: Any = 0,
        before_set: Callable | None = None,
        tts_on_hotkey: bool = True,
        setter_input_width: int = 220,
    ):
        if not gameobject.is_tracked:
            freeze_hotkey = None

        self.gameobject = gameobject
        self.pure_label = label
        self.label_with_hotkey = label if freeze_hotkey is None else f"[{freeze_hotkey}] {label}"
        self.freeze_hotkey = freeze_hotkey
        self.set_hotkey = set_hotkey
        self.default_setter_input_value = default_setter_input_value
        self.before_set = before_set
        self.tts_on_hotkey = tts_on_hotkey
        self.setter_input_width = setter_input_width

        dpg_tag = f"{self.DPG_TAG_PREFIX}{uuid4()}"
        self.dpg_tag_frozen = f"{dpg_tag}{self.DPG_TAG_POSTFIX_IS_FROZEN}"
        self.dpg_tag_getter = f"{dpg_tag}{self.DPG_TAG_POSTFIX_GETTER}"
        self.dpg_tag_setter = f"{dpg_tag}{self.DPG_TAG_POSTFIX_SETTER}"

    @override
    def add_to_ui(self) -> None:
        if self.freeze_hotkey is not None:
            add_hotkey(self.freeze_hotkey, self.on_freeze_hotkey_press)

        if self.set_hotkey is not None:
            add_hotkey(self.set_hotkey, self.on_value_set)

        with dpg.group(horizontal=True):
            if self.gameobject.is_tracked:
                dpg.add_checkbox(tag=self.dpg_tag_frozen, callback=self.on_frozen_state_change)

            dpg.add_text(self.label_with_hotkey)
            dpg.add_input_text(width=220, tag=self.dpg_tag_getter, readonly=True)

            self.add_setter_input()

            setter_button_text = "Set" if self.set_hotkey is None else f"[{self.set_hotkey}] Set"

            dpg.add_button(label=setter_button_text, callback=self.on_value_set)

        GameObjectUI.displayed_objects.append(self)

    def add_setter_input(self):
        default_kwargs = {
            "tag": self.dpg_tag_setter,
            "width": self.setter_input_width,
            "default_value": self.default_setter_input_value,
        }

        if self.gameobject.value_range is not None:
            min_value, max_value = self.gameobject.value_range
            default_kwargs["min_clamped"] = True
            default_kwargs["max_clamped"] = True
            default_kwargs["min_value"] = min_value
            default_kwargs["max_value"] = max_value

        match self.gameobject:
            case GameFloat():
                dpg.add_input_float(**default_kwargs)
            case GameDouble():
                dpg.add_input_double(**default_kwargs)
            case (
                GameByte()
                | GameShort()
                | GameInt()
                | GameLongLong()
                | GameUnsignedShort()
                | GameUnsignedInt()
                | GameUnsignedLongLong()
            ):
                # There is no input for integers that are not simple `signed long int`.
                # TODO: Use better input component if it's already added to dpg. Remove this crutch.

                assert GameInt.value_range is not None, "GameInt must have value_range"
                min_value = default_kwargs.pop("min_value", GameInt.value_range[0])
                max_value = default_kwargs.pop("max_value", GameInt.value_range[1])

                if self.gameobject.value_range is not None:
                    min_value = max(min_value, GameInt.value_range[0])  # type: ignore
                    max_value = min(max_value, GameInt.value_range[1])  # type: ignore

                dpg.add_input_int(min_value=min_value, max_value=max_value, **default_kwargs)
            case GameBool():
                dpg.add_checkbox(
                    tag=self.dpg_tag_setter,
                    default_value=bool(self.default_setter_input_value),
                )
            case _:
                dpg.add_input_text(**default_kwargs)

    def on_frozen_state_change(self):
        try:
            self.gameobject.frozen = self.gameobject.value if dpg.get_value(self.dpg_tag_frozen) else None
        except MemoryReadError:
            dpg.set_value(self.dpg_tag_frozen, value=False)

    def on_value_set(self):
        raw_new_value = dpg.get_value(self.dpg_tag_setter)
        new_value = raw_new_value if self.before_set is None else self.before_set(raw_new_value)

        if self.gameobject.frozen is None:
            with suppress(MemoryWriteError, ValueError):
                self.gameobject.value = new_value
        else:
            self.gameobject.frozen = new_value

    def on_freeze_hotkey_press(self):
        dpg.set_value(self.dpg_tag_frozen, not dpg.get_value(self.dpg_tag_frozen))

        self.on_frozen_state_change()

        if self.tts_on_hotkey:
            status = "released" if self.gameobject.frozen is None else "frozen"
            say(f"GameObject {self.pure_label} {status}")


def update_displayed_objects():
    for game_object_ui in GameObjectUI.displayed_objects:
        try:
            new_value = game_object_ui.gameobject.value
        except MemoryReadError:
            new_value = "<Unresolved>"

        dpg.set_value(game_object_ui.dpg_tag_getter, new_value)
