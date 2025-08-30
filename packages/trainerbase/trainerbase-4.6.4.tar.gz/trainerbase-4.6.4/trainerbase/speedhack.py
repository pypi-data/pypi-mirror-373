from contextlib import suppress
from pathlib import Path
from typing import Final, Self, cast

from pymem.exception import MemoryWriteError
from trainerbase_injector import inject

from trainerbase.config import config
from trainerbase.gameobject import GameDouble
from trainerbase.memory import ARCH, get_module_address
from trainerbase.process import pm


SPEEDHACK_DLL_MODULE_NAME: Final[str] = f"speedhack{ARCH}.dll"
SPEEDHACK_DLL_PATH: Final[Path] = config.vendor.folder / SPEEDHACK_DLL_MODULE_NAME
SPEED_MODIFIER_OFFSET: Final[int] = (
    config.vendor.speedhack.offset_x32 if ARCH == 32 else config.vendor.speedhack.offset_x64
)


class SpeedHack:
    _instance: Self | None = None

    def __new__(cls, *_args, **_kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        self._dll_injection_address = self._inject()
        self._speed_modifier = GameDouble(self._dll_injection_address + SPEED_MODIFIER_OFFSET)

        self.factor = 1.0

    def _inject(self) -> int:
        inject(cast(int, pm.process_id), str(SPEEDHACK_DLL_PATH))
        return get_module_address(SPEEDHACK_DLL_MODULE_NAME)

    @property
    def factor(self):
        return self._speed_modifier.value

    @factor.setter
    def factor(self, value: float):
        self._speed_modifier.value = value

    @classmethod
    def disable(cls):
        if cls._instance is None:
            return

        with suppress(MemoryWriteError):
            cls._instance.factor = 1.0
