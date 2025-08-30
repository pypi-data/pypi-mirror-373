from collections.abc import Hashable
from itertools import repeat, starmap
from math import sqrt
from operator import add, mul
from typing import Self

from pymem.exception import MemoryReadError

from trainerbase.common.helpers import Number
from trainerbase.gameobject import GameObject
from trainerbase.scriptengine import system_script_engine


type Coords[T: (int, float)] = tuple[T, T, T]


class Vector3:
    def __init__(self, x: Number, y: Number, z: Number):
        self.x = x
        self.y = y
        self.z = z

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __abs__(self) -> Number:
        return sqrt(sum(d * d for d in self))

    def __mul__(self, other) -> Self:
        return self.__apply_binary_function(other, mul)

    def __add__(self, other) -> Self:
        return self.__apply_binary_function(other, add)

    def __apply_binary_function(self, other, function) -> Self:
        if isinstance(other, float | int):
            other = repeat(other, 3)
        elif not isinstance(other, self.__class__):
            raise TypeError(f"Can't apply function {function}. Wrong type: {type(other)}")

        return self.__class__(*starmap(function, zip(self, other, strict=False)))

    @classmethod
    def from_coords(cls, x1, y1, z1, x2, y2, z2) -> Self:
        return cls(x2 - x1, y2 - y1, z2 - z1)

    def get_normalized(self) -> Self:
        length = abs(self)
        return self.__class__(*(d / length for d in self))


class Teleport:
    def __init__(
        self,
        player_x: GameObject,
        player_y: GameObject,
        player_z: GameObject,
        labels: dict[str, Coords] | None = None,
        dash_coefficients: Vector3 | None = None,
        minimal_movement_vector_length: float = 0.1,
    ):
        self.player_x = player_x
        self.player_y = player_y
        self.player_z = player_z
        self.labels = {} if labels is None else labels

        self.saved_positions: dict[Hashable, Coords] = {}

        self.dash_coefficients = Vector3(5, 5, 5) if dash_coefficients is None else dash_coefficients
        self.previous_position: Coords | None = None
        self.current_position: Coords | None = None
        self.movement_vector = Vector3(0, 0, 0)
        self.minimal_movement_vector_length = minimal_movement_vector_length

        system_script_engine.simple_script(self.update_movement_vector, enabled=True)

    def set_coords(self, x: Number, y: Number, z: Number = 100) -> None:
        self.player_x.value = x
        self.player_y.value = y
        self.player_z.value = z

    def get_coords(self) -> Coords:
        return self.player_x.value, self.player_y.value, self.player_z.value

    def goto(self, label: str) -> None:
        if label not in self.labels:
            return

        self.set_coords(*self.labels[label])

    def save_position(self, key: Hashable = 0) -> None:
        self.saved_positions[key] = self.get_coords()

    def restore_saved_position(self, key: Hashable = 0) -> bool:
        """
        Returns False if position is not saved else True
        """

        saved_position = self.saved_positions.get(key)

        if saved_position is None:
            return False

        self.set_coords(*saved_position)

        return True

    def update_movement_vector(self) -> None:
        try:
            self.current_position = self.get_coords()
        except MemoryReadError:
            return

        if self.previous_position is None:
            self.previous_position = self.current_position
            return

        movement_vector = Vector3.from_coords(*self.previous_position, *self.current_position)

        if abs(movement_vector) < self.minimal_movement_vector_length:
            return

        self.movement_vector = movement_vector.get_normalized()
        self.previous_position = self.current_position

    def dash(self) -> None:
        dash_movement_vector = self.movement_vector * self.dash_coefficients
        new_coords = Vector3(*self.get_coords()) + dash_movement_vector
        self.set_coords(*new_coords)
