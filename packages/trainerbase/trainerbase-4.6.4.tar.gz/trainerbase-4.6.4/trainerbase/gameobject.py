from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import suppress
from ctypes import c_bool, c_byte, c_double, c_float, c_int, c_longlong, c_short, sizeof
from typing import ClassVar, Self, cast, override

from pymem.exception import MemoryWriteError

from trainerbase.abc import Switchable
from trainerbase.memory import ConvertibleToAddress, ensure_address
from trainerbase.process import pm


class AbstractReadableObject[T](ABC):
    @property
    @abstractmethod
    def value(self) -> T:
        pass


class GameObject[PymemType, TrainerBaseType](AbstractReadableObject[TrainerBaseType]):
    tracked_objects: ClassVar[list[Self]] = []
    value_range: tuple[TrainerBaseType, TrainerBaseType] | None = None
    ctype_size: int

    @staticmethod
    @abstractmethod
    def pm_read(address: int, /) -> PymemType:
        pass

    @staticmethod
    @abstractmethod
    def pm_write(address: int, value: PymemType, /) -> None:
        pass

    def __init__(
        self,
        address: ConvertibleToAddress,
        *,
        frozen: TrainerBaseType | None = None,
        is_tracked: bool = True,
        value_range: None | tuple[TrainerBaseType, TrainerBaseType] = None,
    ):
        if is_tracked:
            GameObject.tracked_objects.append(self)

        self.address = ensure_address(address)
        self.frozen = frozen
        self.is_tracked = is_tracked

        if value_range is not None:
            self.value_range = value_range

    def __repr__(self):
        return f"<{self.__class__.__name__} at {hex(self.address.resolve())}: value={self.value}, frozen={self.frozen}>"

    def after_read(self, value: PymemType) -> TrainerBaseType:
        return cast(TrainerBaseType, value)

    def before_write(self, value: TrainerBaseType) -> PymemType:
        return cast(PymemType, value)

    def validate_range(self, value: TrainerBaseType) -> bool:
        if self.value_range is None:
            return True

        if not isinstance(value, int | float):
            raise TypeError(f"Unable to validate range for non-numeric value: {value} (type: {type(value)})")

        min_value, max_value = self.value_range

        return cast(int | float, min_value) <= value <= cast(int | float, max_value)

    @property
    @override
    def value(self) -> TrainerBaseType:
        return self.after_read(self.pm_read(self.address.resolve()))

    @value.setter
    def value(self, new_value: TrainerBaseType):
        if not self.validate_range(new_value):
            raise ValueError(f"Wrong value for type {type(self)}: {new_value} not in range {self.value_range}")

        self.pm_write(self.address.resolve(), self.before_write(new_value))


class GameFloat(GameObject[float, float]):
    value_range = (-3.4e38, 3.4e38)
    ctype_size = sizeof(c_float)
    pm_read = cast(Callable[[int], float], pm.read_float)
    pm_write = pm.write_float

    @override
    def before_write(self, value):
        return float(value)


class GameDouble(GameObject[float, float]):
    value_range = (-1.7e308, 1.7e308)
    ctype_size = sizeof(c_double)
    pm_read = cast(Callable[[int], float], pm.read_double)
    pm_write = pm.write_double

    @override
    def before_write(self, value):
        return float(value)


class GameByte(GameObject[bytes, int]):
    value_range = (0, 255)
    ctype_size = sizeof(c_byte)

    @staticmethod
    @override
    def pm_read(address: int) -> bytes:
        return pm.read_bytes(address, length=1)

    @staticmethod
    @override
    def pm_write(address: int, value: bytes) -> None:
        pm.write_bytes(address, value, length=1)

    @override
    def before_write(self, value: int) -> bytes:
        return value.to_bytes(length=1, byteorder="little")

    @override
    def after_read(self, value: bytes) -> int:
        return int.from_bytes(value, byteorder="little")


class GameInt(GameObject[int, int]):
    value_range = (-2_147_483_648, 2_147_483_647)
    ctype_size = sizeof(c_int)

    pm_read = cast(Callable[[int], int], pm.read_int)
    pm_write = pm.write_int


class GameShort(GameObject[int, int]):
    value_range = (-32_768, 32_767)
    ctype_size = sizeof(c_short)

    pm_read = cast(Callable[[int], int], pm.read_short)
    pm_write = pm.write_short


class GameLongLong(GameObject[int, int]):
    value_range = (-(2**63), (2**63) - 1)
    ctype_size = sizeof(c_longlong)

    pm_read = cast(Callable[[int], int], pm.read_longlong)
    pm_write = pm.write_longlong


class GameUnsignedInt(GameObject[int, int]):
    value_range = (0, 4_294_967_295)
    ctype_size = sizeof(c_int)

    pm_read = cast(Callable[[int], int], pm.read_uint)
    pm_write = pm.write_uint


class GameUnsignedShort(GameObject[int, int]):
    value_range = (0, 65_535)
    ctype_size = sizeof(c_short)

    pm_read = cast(Callable[[int], int], pm.read_ushort)
    pm_write = pm.write_ushort


class GameUnsignedLongLong(GameObject[int, int]):
    value_range = (0, 18_446_744_073_709_551_615)
    ctype_size = sizeof(c_longlong)

    pm_read = cast(Callable[[int], int], pm.read_ulonglong)
    pm_write = pm.write_ulonglong


class GameBool(GameObject[bool, bool], Switchable):
    value_range = (False, True)
    ctype_size = sizeof(c_bool)

    pm_read = cast(Callable[[int], bool], pm.read_bool)
    pm_write = pm.write_bool

    @override
    def enable(self):
        self.value = True  # pylint: disable=attribute-defined-outside-init

    @override
    def disable(self):
        self.value = False  # pylint: disable=attribute-defined-outside-init


class ReadonlyGameObjectSumGetter(AbstractReadableObject[int | float]):
    def __init__(self, *game_numbers: GameInt | GameFloat):
        self.game_numbers = game_numbers

    @property
    def value(self) -> int | float:
        return sum(number.value for number in self.game_numbers)


def update_frozen_objects():
    for game_object in GameObject.tracked_objects:
        if game_object.frozen is None:
            continue

        with suppress(MemoryWriteError, ValueError):
            game_object.value = game_object.frozen
