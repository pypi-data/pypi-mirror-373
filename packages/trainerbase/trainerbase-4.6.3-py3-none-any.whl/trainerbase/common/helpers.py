from collections.abc import Callable, Iterator, Sequence
from contextlib import suppress
from functools import wraps
from typing import overload
from uuid import uuid4

from pymem.exception import MemoryReadError, MemoryWriteError

from trainerbase.gameobject import AbstractReadableObject, GameObject
from trainerbase.memory import POINTER_SIZE, Address, allocate
from trainerbase.process import pm


type Number = int | float


class ASMArrayManager(Sequence):
    def __init__(
        self,
        array_length: int,
        element_size: int,
        offsets: None | list[int] = None,
        add: int = 0,
    ) -> None:
        if offsets:
            assert element_size == POINTER_SIZE, "If `offsets` is not None, `element_size` must be `POINTER_SIZE`"

        self.array_length = array_length
        self.element_size = element_size
        self.offsets = [] if offsets is None else offsets
        self.add = add

        self.array_address = allocate(element_size, array_length)
        self.array_index_pointer = allocate()

    def __len__(self) -> int:
        return self.array_length

    @overload
    def __getitem__(self, index: int) -> Address: ...

    @overload
    def __getitem__(self, index: slice) -> list[Address]: ...

    def __getitem__(self, index: int | slice) -> Address | list[Address]:
        if isinstance(index, int):
            return self.get_address_of_element(index)

        return [self.get_address_of_element(i) for i in range(index.start, index.stop, index.step)]

    def __iter__(self) -> Iterator[Address]:
        for index in range(len(self)):
            yield self[index]

    def get_pointer_to_element(self, index: int) -> int:
        return self.array_address + self.element_size * index

    def get_address_of_element(self, index: int) -> Address:
        element_address = self.get_pointer_to_element(index)
        target_address = Address(element_address, self.offsets, self.add)

        return Address(target_address.resolve())

    def generate_asm_append_code(self, from_register: str) -> str:
        array_address_register = "rbx" if pm.is_64_bit else "ebx"
        array_index_register = "rcx" if pm.is_64_bit else "ecx"
        reserve_register = "rax" if pm.is_64_bit else "eax"

        if from_register == array_address_register:
            array_address_register = reserve_register

        if from_register == array_index_register:
            array_index_register = reserve_register

        assert len({from_register, array_address_register, array_index_register}) == 3, "Registers must be unique"

        label_continue = f"__label_continue_{uuid4().hex}"

        # In version 3.8.1, a bug was found
        # due to which addresses hardcoded in [] were incorrectly compiled under x64.
        # The solution was to first save the address into a register before reading/writing a value from it.
        # In order not to use another register, existing ones were reused,
        # which, unfortunately, can be misleading.
        # But it was decided that using a new register would make the code even less clear
        # and potentially more error-prone.

        asm = f"""
            push {array_address_register}
            push {array_index_register}

            mov {array_address_register}, {self.array_address}

            ; Fixes bug in 3.8.1
            mov {array_index_register}, {self.array_index_pointer}
            mov {array_index_register}, [{array_index_register}]

            mov [{array_address_register} + {array_index_register} * {self.element_size}], {from_register}

            inc {array_index_register}

            cmp {array_index_register}, {self.array_length}
            jl {label_continue}

            mov {array_index_register}, 0

            {label_continue}:

            ; Fixes bug in 3.8.1
            mov {array_address_register}, {self.array_index_pointer}
            mov [{array_address_register}], {array_index_register}

            pop {array_index_register}
            pop {array_address_register}
        """

        return asm


def regenerate(
    current_value: GameObject,
    max_value: AbstractReadableObject,
    percent: Number,
    min_value: Number = 1,
):
    if current_value.value < max_value.value:
        current_value.value += max(round(max_value.value * percent / 100), min_value)


def suppress_memory_exceptions[**P, T](callback: Callable[P, T]) -> Callable[P, T | None]:
    @wraps(callback)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
        with suppress(MemoryReadError, MemoryWriteError):
            return callback(*args, **kwargs)

    return wrapper
