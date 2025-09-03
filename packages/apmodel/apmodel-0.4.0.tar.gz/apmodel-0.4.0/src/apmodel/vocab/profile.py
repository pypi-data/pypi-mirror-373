from dataclasses import dataclass, field
from typing import Union
from ..types import Undefined
from ..core.object import Object

@dataclass
class Profile(Object):
    type: Union[str, Undefined] = field(default="Profile")
    describes: Object | Undefined = field(default_factory=Undefined)