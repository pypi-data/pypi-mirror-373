from dataclasses import dataclass
from typing import TypeVar

from .context import LDContext

T = TypeVar("T", bound="ActivityPubModel")

class Undefined:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Undefined, cls).__new__(cls)
        return cls._instance

    def __repr__(self):
        return 'undefined'

    def __str__ (self):
        return 'undefined'

@dataclass
class ActivityPubModel:
    def __post_init__(self):
        if hasattr(self, "_context"):
            self._context = LDContext(self._context)

    def to_json(self) -> dict: ...