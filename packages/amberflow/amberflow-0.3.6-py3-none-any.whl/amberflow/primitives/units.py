from abc import ABCMeta, abstractmethod
from typing import Any, Union

__all__ = [
    "Molar",
    "ns",
]


class Unit(metaclass=ABCMeta):
    pass


class Molar(Unit):
    pass


class ns(Unit):
    pass
