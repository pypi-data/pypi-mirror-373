from typing import Literal, Union
from dataclasses import field, dataclass

from ..types import Undefined
from ..core.object import Object

@dataclass
class Event(Object):
    type: Union[str, Undefined] = field(default="Event")

@dataclass
class Place(Object):
    type: Union[str, Undefined] = field(default="Place")
    accuracy: float | Undefined = field(default_factory=Undefined)
    altitude: float | Undefined = field(default_factory=Undefined)
    latitude: float | Undefined = field(default_factory=Undefined)
    longitude: float | Undefined = field(default_factory=Undefined)
    radius: float | Undefined = field(default_factory=Undefined)
    units: str | Literal["cm", "feet", "inches", "km", "m", "miles"] | Undefined = field(default_factory=Undefined)