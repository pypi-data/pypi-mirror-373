from collections.abc import Callable
from typing import override

from trainerbase.abc import Switchable


class SimpleSwitchable(Switchable):
    def __init__(self, on_enabled: Callable[[], None], on_disabled: Callable[[], None]):
        self._on_enabled = on_enabled
        self._on_disabled = on_disabled

    @override
    def enable(self):
        self._on_enabled()

    @override
    def disable(self):
        self._on_disabled()
