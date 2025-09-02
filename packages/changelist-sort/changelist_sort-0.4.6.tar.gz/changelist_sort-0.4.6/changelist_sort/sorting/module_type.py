""" Manage Different Types of Modules
"""
from enum import Enum, auto


class ModuleType(Enum):
    MODULE = auto()
    ROOT = auto()
    GRADLE = auto()
    HIDDEN = auto()
