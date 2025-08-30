from abc import ABC, abstractmethod
from contextlib import suppress
from functools import lru_cache
from pathlib import Path
from subprocess import DEVNULL
from subprocess import run as run_executable
from tempfile import TemporaryDirectory
from typing import ClassVar, Final, Self, override

from pymem.exception import MemoryWriteError

from trainerbase.config import config
from trainerbase.logger import logger
from trainerbase.memory import ARCH, ConvertibleToAddress, allocate, ensure_address
from trainerbase.process import pm


FASM_EXECUTABLE_PATH: Final[Path] = config.vendor.folder / "FASM.EXE"
ORIGINAL_CODE_PLACEHOLDER: Final[str] = "__original_code__"
BASE_ADDRESS_PLACEHOLDER: Final[str] = "__base_address__"
MOVE_X64_MACROS: Final[str] = "__move_x64__"


type Code = bytes | str


class AbstractCodeInjection(ABC):
    created_code_injections: ClassVar[list[Self]] = []

    def __new__(cls, *_args, **_kwargs):
        instance = super().__new__(cls)
        AbstractCodeInjection.created_code_injections.append(instance)

        return instance

    @abstractmethod
    def inject(self):
        pass

    @abstractmethod
    def eject(self):
        pass


class CodeInjection(AbstractCodeInjection):
    def __init__(
        self,
        address: ConvertibleToAddress,
        code_to_inject: Code,
    ):
        self.address = ensure_address(address)
        self.code_to_inject = compile_asm(code_to_inject)
        self.original_code: bytes = b""
        self.injection_point: int = 0
        self._injected = False

    @override
    def inject(self):
        self.injection_point = self.address.resolve()
        self.original_code = pm.read_bytes(self.injection_point, len(self.code_to_inject))

        logger.debug(f"Injecting {len(self.code_to_inject)} byte(s) at 0x{self.injection_point:X}")

        pm.write_bytes(self.injection_point, self.code_to_inject, len(self.code_to_inject))
        self._injected = True

    @override
    def eject(self):
        if self._injected:
            logger.debug(f"Ejecting {len(self.code_to_inject)} byte(s) from 0x{self.injection_point:X}")

            pm.write_bytes(self.injection_point, self.original_code, len(self.original_code))
            self._injected = False
        else:
            logger.debug("Nothing to eject")


class AllocatingCodeInjection(AbstractCodeInjection):
    def __init__(
        self,
        address: ConvertibleToAddress,
        code_to_inject: Code,
        *,
        original_code_length: int = 0,
        new_memory_size: int = 1024,
        is_long_x64_jump_needed: bool | None = None,
    ):
        if is_long_x64_jump_needed is None:
            is_long_x64_jump_needed = pm.is_64_bit

        self.is_long_x64_jump_needed = is_long_x64_jump_needed
        self.address = ensure_address(address)
        self.code_to_inject = code_to_inject

        self.original_code: bytes = b""

        self.original_code_length = original_code_length
        self.new_memory_size = new_memory_size
        self.new_memory_address: int = 0
        self.injection_point: int = 0

    @override
    def inject(self):
        self.injection_point = self.address.resolve()
        self.new_memory_address: int = allocate(self.new_memory_size)
        self.original_code = pm.read_bytes(self.injection_point, self.original_code_length)

        code_to_inject = self.code_to_inject

        if isinstance(code_to_inject, str):
            code_to_inject = preprocess_asm(
                code_to_inject,
                original_code=self.original_code,
                base_address=pm.base_address,
            )

        if isinstance(code_to_inject, bytearray):
            raise TypeError("Code to inject must not be bytearray")

        code_to_inject = compile_asm(code_to_inject)

        if self.is_long_x64_jump_needed:
            code_to_inject = compile_asm("pop rax") + code_to_inject + compile_asm("push rax")
            jump_to_new_mem = compile_asm(get_long_x64_jump_to_new_mem_code(self.new_memory_address))
            jumper_length = len(jump_to_new_mem)
            jump_back_address = self.injection_point + jumper_length - 1
            jump_back = compile_asm(get_long_x64_jump_back_code(jump_back_address))
        else:
            jump_to_new_mem = compile_asm(get_simple_jump_code(self.new_memory_address, self.injection_point))
            jumper_length = len(jump_to_new_mem)
            jump_back_address = self.injection_point + jumper_length
            jump_back = compile_asm(
                get_simple_jump_code(jump_back_address, self.new_memory_address + len(code_to_inject)),
            )

        if jumper_length < self.original_code_length:
            jump_to_new_mem += b"\x90" * (self.original_code_length - len(jump_to_new_mem))
        elif jumper_length > self.original_code_length:
            raise ValueError(f"Jumper length > original code length: {jumper_length} > {self.original_code_length}")

        code_to_inject = code_to_inject + jump_back

        logger.debug(f"Injecting {len(code_to_inject)} byte(s) (INJECTION) at 0x{self.new_memory_address:X}")
        pm.write_bytes(self.new_memory_address, code_to_inject, len(code_to_inject))

        logger.debug(f"Injecting {len(jump_to_new_mem)} byte(s) (JUMPER) at 0x{self.injection_point:X}")
        pm.write_bytes(self.injection_point, jump_to_new_mem, len(jump_to_new_mem))

    @override
    def eject(self):
        if self.new_memory_address and self.injection_point:
            logger.debug(f"Ejecting {self.original_code_length} byte(s) (JUMPER) from 0x{self.injection_point:X}")
            pm.write_bytes(self.injection_point, self.original_code, self.original_code_length)

            logger.debug(f"Freeing memory at 0x{self.new_memory_address:X}")
            pm.free(self.new_memory_address)
            self.new_memory_address = 0
            self.injection_point = 0
        else:
            logger.debug("Nothing to eject")


class MultipleCodeInjection(AbstractCodeInjection):
    def __init__(self, *injections: AbstractCodeInjection):
        self._injections = injections

    @override
    def inject(self):
        for injection in self._injections:
            injection.inject()

    @override
    def eject(self):
        for injection in self._injections:
            injection.eject()


def preprocess_asm(code: str, *, original_code: bytes | None, base_address: int | None) -> str:
    new_lines = []

    for line in code.splitlines():
        if original_code is not None:
            formatted_bytes = ", ".join(map(hex, original_code))
            formatted_original_code = f"db {formatted_bytes}"

            line = line.replace(ORIGINAL_CODE_PLACEHOLDER, formatted_original_code)

        if base_address is not None:
            line = line.replace(BASE_ADDRESS_PLACEHOLDER, hex(base_address))

        if MOVE_X64_MACROS in line:
            _, address, register = line.strip().split()
            line = get_move_x64_register_to_memory_code(address, register)

        new_lines.append(line)

    return "\n".join(new_lines)


@lru_cache
def compile_asm(code: Code) -> bytes:
    if isinstance(code, str):
        logger.debug(f"Assembling for x{ARCH}:\n{code}")

        fasm_mode = f"use{ARCH}"
        with TemporaryDirectory() as tmp_dir:
            asm_file = Path(tmp_dir) / "injection.asm"

            asm_file.write_text(f"{fasm_mode}\n{code}", encoding="utf-8")

            run_executable([FASM_EXECUTABLE_PATH, asm_file], stdout=DEVNULL, check=True)
            code = asm_file.with_suffix(".bin").read_bytes()

    if not isinstance(code, bytes):
        raise TypeError("code must be bytes | str")

    return code


def get_simple_jump_code(address: int, ip: int) -> str:
    return f"""
        jmp {address - ip}
    """


def get_long_x64_jump_to_new_mem_code(address: int) -> str:
    return f"""
        push rax
        mov rax, {address}
        push rax
        ret
        pop rax
    """


def get_long_x64_jump_back_code(address: int) -> str:
    return f"""
        mov rax, {address}
        push rax
        ret
    """


def get_move_x64_register_to_memory_code(address: int | str, register: str) -> str:
    temporary_register = "rbx" if register == "rax" else "rax"
    code = f"""
        push {temporary_register}
        mov {temporary_register}, {address}
        mov [{temporary_register}], {register}
        pop {temporary_register}
    """

    return code


def safely_eject_all_code_injections() -> None:
    for injection in AbstractCodeInjection.created_code_injections:
        with suppress(MemoryWriteError):
            injection.eject()
