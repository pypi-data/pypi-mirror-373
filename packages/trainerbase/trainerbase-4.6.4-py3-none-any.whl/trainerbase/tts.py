from collections import deque
from typing import override

from pyttsx3 import init as init_tts_engine

from trainerbase.scriptengine import AbstractBaseScript


class TTSManager(AbstractBaseScript):
    def __init__(self, queue_length_limit: int = 10):
        self.__engine = init_tts_engine()
        self.__queue = deque(maxlen=queue_length_limit)

    @override
    def __call__(self):
        if not self.__queue:
            return

        try:
            self.__say_sync(*self.__queue[0])
        except RuntimeError:
            return

        self.__queue.popleft()

    def __say_sync(self, text: str, rate: int = 210, volume: float = 1.0):
        self.__engine.setProperty("rate", rate)
        self.__engine.setProperty("volume", volume)
        self.__engine.say(text)
        self.__engine.runAndWait()

    @property
    def queue_length_limit(self):
        return self.__queue.maxlen

    @queue_length_limit.setter
    def queue_length_limit(self, limit: int):
        self.__queue = deque(self.__queue, maxlen=limit)

    def schedule(self, text: str, rate: int = 210, volume: float = 1.0, *, allow_task_stacking: bool = False):
        task_params = (text, rate, volume)

        if not self.__queue or self.__queue[-1] != task_params or allow_task_stacking:
            self.__queue.append(task_params)


tts_manager = TTSManager()
say = say_sync = tts_manager.schedule
