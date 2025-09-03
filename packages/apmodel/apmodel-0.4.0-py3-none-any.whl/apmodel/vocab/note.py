from dataclasses import dataclass, field
from typing import Union
from ..types import Undefined
from ..core.object import Object

@dataclass
class Note(Object):
    type: Union[str, Undefined] = field(default="Note")
