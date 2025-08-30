from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import partial
from itertools import count
from time import sleep
from types import MappingProxyType
from typing import Final, Self, assert_never, cast, override

from pymem.pattern import pattern_scan_all, pattern_scan_module
from pymem.process import module_from_name

from trainerbase.logger import logger
from trainerbase.process import pm


ARCH: Final[int] = 64 if pm.is_64_bit else 32
POINTER_SIZE: Final[int] = 8 if pm.is_64_bit else 4


type ConvertibleToAddress = AbstractAddress | int | bytes | str


read_pointer = cast(Callable[[int], int], pm.read_ulonglong if pm.is_64_bit else pm.read_uint)


logger.debug(f"Process arch is {ARCH}")


class AbstractAddress(ABC):
    @abstractmethod
    def resolve(self) -> int:
        pass


class AOBScan(AbstractAddress):
    # Constant from re. Like re._special_chars_map, but without dot (`.`).
    _SPECIAL_CHARS_MAP = MappingProxyType({i: "\\" + chr(i) for i in b"()[]{}?*+-|^$\\&~# \t\n\r\v\f"})

    def __init__(
        self,
        aob: bytes | str,
        *,
        add: int = 0,
        module_name: str | None = None,
        multiple_result_index: int | None = None,
        should_cache: bool = True,
        should_escape: bool = True,
        any_byte_marker: str = "??",
        check_memory_protection: bool = True,
    ):
        self._should_cache = should_cache
        self._saved_scan_result: int | None = None

        if isinstance(aob, str):
            aob = bytes.fromhex(aob.replace(any_byte_marker, "2E"))  # 2E is hex(46), 46 is ord(".")

        if should_escape:
            aob = self._escape_aob(aob)

        self.aob = aob
        self.add = add
        self.module_name = module_name
        self.multiple_result_index = multiple_result_index
        self.check_memory_protection = check_memory_protection

    def __add__(self, extra_add: int) -> Self:
        new_add = self.add + extra_add
        return self.inherit(new_add=new_add)

    @override
    def resolve(self) -> int:
        if self._saved_scan_result is not None:
            return self._saved_scan_result

        return_multiple = self.multiple_result_index is not None

        if self.module_name is None:
            find_aob = partial(pattern_scan_all, pm.process_handle, return_multiple=return_multiple)
        else:
            module = module_from_name(pm.process_handle, self.module_name)

            if module is None:
                raise ValueError(f"Module not found: {self.module_name}")

            find_aob = partial(pattern_scan_module, pm.process_handle, module, return_multiple=return_multiple)

        scan_result: list[int] | int | None = find_aob(self.aob, check_memory_protection=self.check_memory_protection)

        if not scan_result:
            raise ValueError(f"AOB not found: {self.aob}")

        if isinstance(scan_result, list):
            result_address = scan_result[cast(int, self.multiple_result_index)]
        else:
            result_address = scan_result

        result_address += self.add

        if self._should_cache:
            self._saved_scan_result = result_address

        return result_address

    def inherit(self, *, new_add: int | None = None) -> Self:
        new_address = self.__class__(
            self.aob,
            add=self.add,
            module_name=self.module_name,
            multiple_result_index=self.multiple_result_index,
            should_cache=self._should_cache,
        )

        if new_add is not None:
            new_address.add = new_add

        return new_address

    @classmethod
    def _escape_aob(cls, pattern: bytes) -> bytes:
        """
        Escape special characters in a string.

        Forked re.escape. Simplified. Only for bytes.
        """

        return pattern.decode("latin1").translate(cls._SPECIAL_CHARS_MAP).encode("latin1")


class Address(AbstractAddress):
    def __init__(self, base_address: int, offsets: list[int] | None = None, add: int = 0):
        self.base_address = base_address
        self.offsets = [] if offsets is None else offsets
        self.add = add

    def __add__(self, other: int | list[int]) -> Self:
        match other:
            case int(extra_add):
                new_add = self.add + extra_add
                return self.inherit(new_add=new_add)
            case list(extra_offsets):
                return self.inherit(extra_offsets=extra_offsets)
            case _:
                assert_never(other)

    @override
    def resolve(self) -> int:
        pointer = self.base_address
        for offset in self.offsets:
            pointer = read_pointer(pointer) + offset

        return pointer + self.add

    def inherit(self, *, extra_offsets: list[int] | None = None, new_add: int | None = None) -> Self:
        new_address = self.__class__(self.base_address, self.offsets.copy(), self.add)

        if extra_offsets is not None:
            new_address.offsets.extend(extra_offsets)

        if new_add is not None:
            new_address.add = new_add

        return new_address


def ensure_address(obj: ConvertibleToAddress) -> AbstractAddress:
    match obj:
        case AbstractAddress():
            return obj
        case int():
            return Address(obj)
        case bytes() | str():
            return AOBScan(obj)
        case _:
            raise TypeError(f"Cannot create AbstractAddress from {type(obj)}")


def allocate(size: int = POINTER_SIZE, count: int = 1) -> int:
    total = size * count
    logger.debug(f"Allocating {total} bytes.")

    return pm.allocate(total)


def get_module_address(module_name: str, *, delay: float = 2, retry_limit: int | None = 4) -> int:
    """
    Returns module address.
    Raises RuntimeError if the address was not found and retry_limit is reached.

    Set retry_limit to None or negative value if you need infinite retry cycle.
    Set retry_limit to 0 if you want to disable retries.
    """

    logger.info(f"Looking for {module_name}...")

    for try_counter in count():
        module_info = module_from_name(pm.process_handle, module_name)

        if module_info is not None:
            logger.info(f"Successfully found {module_name} at 0x{module_info.lpBaseOfDll:X}")
            return module_info.lpBaseOfDll

        if try_counter == retry_limit:
            raise RuntimeError(f"Failed to find module: {module_name}, tried {try_counter + 1} time(s).")

        logger.info(f"Failed to find {module_name}. I will retry in {delay} s. Retry limit is {retry_limit}")

        sleep(delay)

    raise RuntimeError("This code must be unreachable!")


def ensure_resolved(
    address: AbstractAddress,
    verbose_name: str,
    *,
    delay: float = 2,
    retry_limit: int | None = 4,
) -> int:
    """
    Returns resolved address.
    Raises RuntimeError if the address was not found and retry_limit is reached.

    Set retry_limit to None or negative value if you need infinite retry cycle.
    Set retry_limit to 0 if you want to disable retries.
    """

    logger.info(f"Looking for {verbose_name}...")

    for try_counter in count():
        try:
            resolved = address.resolve()
        except ValueError as e:
            if try_counter == retry_limit:
                raise RuntimeError(f"Failed to resolve {verbose_name}, tried {try_counter + 1} time(s).") from e

            logger.info(f"Failed to resolve {verbose_name}. I will retry in {delay} s. Retry limit is {retry_limit}")

            sleep(delay)
            continue

        logger.info(f"Successfully found {verbose_name} at 0x{resolved:X}")
        return resolved

    raise RuntimeError("This code must be unreachable!")


mainaob = partial(AOBScan, module_name=pm.process_base.name)
