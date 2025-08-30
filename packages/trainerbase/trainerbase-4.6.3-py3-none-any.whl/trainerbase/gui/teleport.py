from collections.abc import Hashable
from functools import partial
from typing import override

from dearpygui import dearpygui as dpg
from keyboard import add_hotkey

from trainerbase.common.helpers import suppress_memory_exceptions
from trainerbase.common.teleport import Teleport
from trainerbase.gui.helpers import add_components
from trainerbase.gui.objects import GameObjectUI
from trainerbase.gui.types import AbstractUIComponent
from trainerbase.tts import say


class TeleportUI(AbstractUIComponent):
    DPG_TAG_TELEPORT_LABELS = "__teleport_labels"
    DPG_TAG_TELEPORT_LABEL_FILTER_INPUT = "__dpg_tag_teleport_label_filter_input"
    POSITION_ID_MANUAL_PRIMARY = "__position_id_manual_primary"
    POSITION_ID_MANUAL_SECONDARY = "__position_id_manual_secondary"
    POSITION_ID_BEFORE_DASH = "__position_id_before_dash"

    def __init__(
        self,
        tp: Teleport,
        hotkey_save_position: str | None = "Insert",
        hotkey_set_saved_position: str | None = "Home",
        hotkey_dash: str | None = "End",
        hotkey_secondary_position_modifier: str = "Shift",
        hotkey_dash_rollback: str = "Shift+End",
        *,
        tts_on_hotkey: bool = True,
    ):
        self.tp = tp
        self.hotkey_save_position = hotkey_save_position
        self.hotkey_set_saved_position = hotkey_set_saved_position
        self.hotkey_secondary_position_modifier = hotkey_secondary_position_modifier
        self.hotkey_dash = hotkey_dash
        self.hotkey_dash_rollback = hotkey_dash_rollback
        self.tts_on_hotkey = tts_on_hotkey

    @override
    def add_to_ui(self) -> None:
        self._tp_add_save_set_position_hotkeys_if_needed()
        self._tp_add_dash_hotkeys_if_needed()

        add_components(
            GameObjectUI(self.tp.player_x, "X"),
            GameObjectUI(self.tp.player_y, "Y"),
            GameObjectUI(self.tp.player_z, "Z"),
        )

        self._tp_add_labels_if_needed()

        dpg.add_button(label="Clip Coords", callback=self.on_clip_coords)

    @suppress_memory_exceptions
    def on_clip_coords(self):
        dpg.set_clipboard_text(repr(self.tp.get_coords()))

    @suppress_memory_exceptions
    def on_hotkey_save_position_press(self, key: Hashable):
        self.tp.save_position(key)

        if self.tts_on_hotkey:
            say("Position saved", allow_task_stacking=True)

    @suppress_memory_exceptions
    def on_hotkey_set_saved_position_press(self, key: Hashable):
        is_position_restored = self.tp.restore_saved_position(key)

        if self.tts_on_hotkey:
            say("Position restored" if is_position_restored else "Save position at first")

    @suppress_memory_exceptions
    def on_hotkey_dash_press(self):
        self.tp.save_position(self.POSITION_ID_BEFORE_DASH)
        self.tp.dash()

        if self.tts_on_hotkey:
            say("Dash!")

    @suppress_memory_exceptions
    def on_hotkey_dash_rollback_press(self):
        self.tp.restore_saved_position(self.POSITION_ID_BEFORE_DASH)

        if self.tts_on_hotkey:
            say("Dash Rollback!")

    @suppress_memory_exceptions
    def on_goto_label(self):
        self.tp.goto(dpg.get_value(self.DPG_TAG_TELEPORT_LABELS))

    def _tp_add_save_set_position_hotkeys_if_needed(self):
        if self.hotkey_save_position is None or self.hotkey_set_saved_position is None:
            return

        add_hotkey(
            self.hotkey_save_position,
            partial(self.on_hotkey_save_position_press, self.POSITION_ID_MANUAL_PRIMARY),
        )
        add_hotkey(
            self.hotkey_set_saved_position,
            partial(self.on_hotkey_set_saved_position_press, self.POSITION_ID_MANUAL_PRIMARY),
        )

        hotkey_secondary_position_hint = ""
        if self.hotkey_secondary_position_modifier:
            hotkey_save_secondary_position = f"{self.hotkey_secondary_position_modifier} + {self.hotkey_save_position}"
            hotkey_set_secondary_saved_position = (
                f"{self.hotkey_secondary_position_modifier} + {self.hotkey_set_saved_position}"
            )
            hotkey_secondary_position_hint = f"[{self.hotkey_secondary_position_modifier} +] "
            add_hotkey(
                hotkey_save_secondary_position,
                partial(self.on_hotkey_save_position_press, self.POSITION_ID_MANUAL_SECONDARY),
            )
            add_hotkey(
                hotkey_set_secondary_saved_position,
                partial(self.on_hotkey_set_saved_position_press, self.POSITION_ID_MANUAL_SECONDARY),
            )

        dpg.add_text(f"[{hotkey_secondary_position_hint}{self.hotkey_save_position}] Save Position")
        dpg.add_text(f"[{hotkey_secondary_position_hint}{self.hotkey_set_saved_position}] Restore Position")

    def _tp_add_dash_hotkeys_if_needed(self):
        if self.hotkey_dash is None:
            return

        with dpg.group(horizontal=True):
            add_hotkey(self.hotkey_dash, self.on_hotkey_dash_press)
            dpg.add_text(f"[{self.hotkey_dash}] Dash")

            if self.hotkey_dash_rollback is None:
                return

            add_hotkey(self.hotkey_dash_rollback, self.on_hotkey_dash_rollback_press)
            dpg.add_text(f"/ [{self.hotkey_dash_rollback}] Dash Rollback")

    def _tp_add_labels_if_needed(self):
        if not self.tp.labels:
            return

        dpg.add_input_text(
            label="Search",
            tag=self.DPG_TAG_TELEPORT_LABEL_FILTER_INPUT,
            callback=self._on_apply_filter,
        )

        with dpg.group(horizontal=True):
            dpg.add_button(label="Go To", callback=self.on_goto_label)
            dpg.add_combo(label="Labels", tag=self.DPG_TAG_TELEPORT_LABELS)

        self._on_apply_filter()

    def _on_apply_filter(self):
        label_name_part = dpg.get_value(self.DPG_TAG_TELEPORT_LABEL_FILTER_INPUT)
        new_labels = {
            label: coords for label, coords in self.tp.labels.items() if label_name_part.lower() in label.lower()
        }

        new_label_names = sorted(new_labels.keys())

        default_value = new_label_names[0] if new_label_names else "<No results!>"

        dpg.configure_item(self.DPG_TAG_TELEPORT_LABELS, items=new_label_names, default_value=default_value)
