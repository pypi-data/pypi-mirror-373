from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import suppress
from sys import stderr
from threading import Thread
from time import sleep
from typing import Any, override

from pymem.exception import MemoryReadError, MemoryWriteError

from trainerbase.abc import Switchable


class AbstractBaseScript(Switchable, ABC):
    enabled: bool = False

    @abstractmethod
    def __call__(self) -> Any:
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}: enabled={self.enabled}>"

    @override
    def enable(self):
        self.enabled = True

    @override
    def disable(self):
        self.enabled = False


class SimpleScript(AbstractBaseScript):
    def __init__(self, callback: Callable[[], None], *, enabled: bool = False):
        self._callback = callback
        self.enabled = enabled

    def __repr__(self):
        return f"<Script {getattr(self._callback, '__name__', 'Anon function-based script')}: enabled={self.enabled}>"

    @override
    def __call__(self):
        self._callback()


class ScriptEngine:
    def __init__(self, delay: float = 0.05):
        self.delay = delay
        self.should_run = False
        self.thread = Thread(target=self.script_loop)
        self.scripts: list[AbstractBaseScript] = []

    def __repr__(self):
        return f"<ScriptEngine delay={self.delay} should_run={self.should_run} scripts={len(self.scripts)}>"

    def start(self):
        self.should_run = True
        self.thread.start()

    def stop(self):
        self.should_run = False

        with suppress(RuntimeError):
            self.thread.join()

    def script_loop(self):
        while self.should_run:
            for script in self.scripts:
                if not script.enabled:
                    continue

                try:
                    script()
                except (MemoryReadError, MemoryWriteError):
                    continue
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(e, file=stderr)
                    self.stop()

            sleep(self.delay)

    def register_script[T: AbstractBaseScript](self, script: T) -> T:
        self.scripts.append(script)
        return script

    def simple_script(self, executor: Callable[[], None], *, enabled: bool = False) -> AbstractBaseScript:
        return self.register_script(SimpleScript(executor, enabled=enabled))


def enabled_by_default[T: AbstractBaseScript](script: T) -> T:
    script.enable()
    return script


system_script_engine = ScriptEngine()
rainbow_script_engine = ScriptEngine(delay=0.0025)
process_healthcheck_script_engine = ScriptEngine(delay=3)
